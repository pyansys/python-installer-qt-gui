# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Search for Python or miniforge installations within the Windows registry."""

import logging
import os
import subprocess

from ansys.tools.path import get_available_ansys_installations

from ansys.tools.installer.configure_json import ConfigureJson
from ansys.tools.installer.constants import ANSYS_SUPPORTED_PYTHON_VERSIONS
from ansys.tools.installer.linux_functions import (
    find_ansys_installed_python_linux,
    find_miniforge_linux,
    is_linux_os,
)

# only used on windows
try:
    import winreg
except ModuleNotFoundError:
    pass


LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")


def find_miniforge():
    """Find all installations of miniforge within the Windows registry.

    Returns
    -------
    dict
        Dictionary containing a key for each path and a ``tuple``
        containing ``(version_str, is_admin)``.

    """
    if os.name == "nt":
        paths = _find_miniforge_win(True)
        paths.update(_find_miniforge_win(False))
    else:
        paths = find_miniforge_linux()
    return paths


def _find_miniforge_win(admin=False):
    """Search for any miniforge installations in the registry."""
    if admin:
        root_key = winreg.HKEY_LOCAL_MACHINE
    else:
        root_key = winreg.HKEY_CURRENT_USER

    paths = {}
    key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
    try:
        with winreg.OpenKey(
            root_key,
            key,
            access=winreg.KEY_READ,
        ) as reg_key:
            info = winreg.QueryInfoKey(reg_key)
            for i in range(info[0]):
                subkey_name = winreg.EnumKey(reg_key, i)
                if "Miniforge" in subkey_name:
                    with winreg.OpenKey(
                        root_key,
                        key + "\\" + subkey_name,
                        access=winreg.KEY_READ,
                    ) as sub_key:
                        ver = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                        uninstall_exe = winreg.QueryValueEx(sub_key, "UninstallString")[
                            0
                        ].replace('"', "")
                        miniforge_path = os.path.dirname(uninstall_exe)
                        paths[miniforge_path] = (ver, admin)
    except FileNotFoundError:
        pass

    return paths


def _find_installed_python_win(admin=False):
    """Check the windows registry for any installed instances of Python."""
    if admin:
        root_key = winreg.HKEY_LOCAL_MACHINE
    else:
        root_key = winreg.HKEY_CURRENT_USER

    paths = {}
    try:
        base_key = "SOFTWARE\\Python\\PythonCore"
        with winreg.OpenKey(
            root_key,
            base_key,
            access=winreg.KEY_READ,
        ) as reg_key:
            info = winreg.QueryInfoKey(reg_key)
            for i in range(info[0]):
                name = winreg.EnumKey(reg_key, i)
                ver, path = _get_python_info_win(f"{base_key}\\{name}", root_key)
                if ver is not None and path is not None:
                    paths[path] = (ver, admin)

    except FileNotFoundError:
        pass

    return paths


def _find_installed_ansys_python_win():
    """Check the Ansys installation folder for installed Python."""
    installed_ansys = get_available_ansys_installations()
    paths = {}
    for ver in installed_ansys:
        ansys_path = installed_ansys[ver]
        for ansys_py_ver in ANSYS_SUPPORTED_PYTHON_VERSIONS:
            path = os.path.join(
                ansys_path,
                f"commonfiles\\CPython\\{ansys_py_ver}\\winx64\\Release\\python",
            )
            if os.path.exists(path):
                try:
                    version_output = subprocess.check_output(
                        [f"{path}\\python.exe", "--version"], text=True
                    ).strip()
                    version = version_output.split()[1]
                    paths[path] = (version, False)
                except Exception as err:
                    LOG.error(f"Failed to retrieve Python version: {str(err)}")
                    pass

    return paths


def _find_installed_python_linux():
    """
    Find all installed Python versions on Linux.

    Returns
    -------
    dict
        Dictionary containing a key for each path and a tuple
        containing ``(version: str, admin: bool)``.

    Examples
    --------
    >>> installed_pythons = find_installed_python_linux()
    >>> installed_pythons
    {'/home/user/python/py311/bin/python': ('3.11.3', False),
     '/home/user/python/py311/bin/python3': ('3.11.3', False),
     '/usr/bin/python3.12': ('3.12.0', True),

    """
    LOG.debug("Identifying all installed versions of python on Linux")

    pythons = {}
    version_names = ["python", "python3"] + [f"python3.{i}" for i in range(7, 13)]
    previous_found_version = ""

    for version_name in version_names:
        try:
            path = subprocess.check_output(["which", version_name], text=True).strip()
            version_output = subprocess.check_output(
                [path, "--version"], text=True
            ).strip()
            version = version_output.split()[1]
            admin = path.startswith("/usr")
            if version != previous_found_version:
                pythons[path] = (version, admin)
                LOG.debug("Identified %s at %s", version, path)
                previous_found_version = version
        except:
            # Ignore if the command fails (e.g., if the Python version is not installed)
            pass

    return pythons


def _get_python_info_win(key, root_key):
    """For a given windows key, read the install path and python version."""
    with winreg.OpenKey(root_key, key, access=winreg.KEY_READ) as reg_key:
        try:
            ver = winreg.QueryValueEx(reg_key, "Version")[0]
        except FileNotFoundError:
            ver = None

        try:
            with winreg.OpenKey(
                root_key, f"{key}\\InstallPath", access=winreg.KEY_READ
            ) as path_key:
                path = winreg.QueryValueEx(path_key, None)[0]
        except FileNotFoundError:
            path = None

    return ver, path


def find_all_python():
    """Find any installed instances of python.

    Returns
    -------
    dict
        Dictionary containing a key for each path and a ``tuple``
        containing ``(version_str, is_admin)``.

    """
    if os.name == "nt":
        paths = _find_installed_python_win(True)
        paths.update(_find_installed_python_win(False))
        paths.update(_find_installed_ansys_python_win())
    else:
        paths = _find_installed_python_linux()
        paths.update(find_ansys_installed_python_linux())

    return paths


def get_all_python_venv():
    """Get a list of all created python virtual environments.

    Returns
    -------
    dict
        Dictionary containing a key for each path and a ``tuple``
        containing ``(version_str, is_admin)``.
    """
    paths = {}
    script_path = "bin" if is_linux_os() else "Scripts"
    configure = ConfigureJson()
    for venv_dir in configure.venv_search_path:
        try:
            for venv_dir_name in os.listdir(venv_dir):
                if os.path.isfile(
                    os.path.join(venv_dir, venv_dir_name, script_path, "activate")
                ) or (
                    not os.path.isdir(os.path.join(venv_dir, venv_dir_name, "condabin"))
                    and os.path.isdir(
                        os.path.join(venv_dir, venv_dir_name, "conda-meta")
                    )
                ):

                    path = os.path.join(venv_dir, venv_dir_name, script_path)
                    paths[path] = (
                        venv_dir_name,
                        False,
                    )  # venvs will always be user-like, hence False
        except:
            pass
    return paths
