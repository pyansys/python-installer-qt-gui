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

"""Linux functions."""

import getpass
import logging
import os
from pathlib import Path
import shutil
import subprocess

from ansys.tools.path.misc import is_linux
from github import Github
from packaging import version

from ansys.tools.installer import CACHE_DIR
from ansys.tools.installer.constants import ANSYS_FULL_LINUX_PATH, ASSETS_PATH

LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")
try:
    ansys_linux_path = ANSYS_FULL_LINUX_PATH
    Path(f"{ansys_linux_path}").mkdir(parents=True, exist_ok=True)
except:
    user_name = getpass.getuser()
    ansys_linux_path = f"/home/{user_name}/.local/ansys"


def is_linux_os():
    """
    Create OS is Linux or Not.

    Returns
    -------
    Boolean value

    Examples
    --------
    >>> is_linux_os = is_linux_os()
    >>> is_linux_os
    True
    """
    try:
        if is_linux():
            return is_linux()
        return False
    except:
        return False


def get_vanilla_url_and_filename(selected_version):
    """
    Create URL and filename to download vanilla python for Linux.

    Returns
    -------
    url and filename in String format

    Examples
    --------
    >>> url, filename = get_vanilla_url_and_filename("3.8.11")
    >>> url
    'https://www.python.org/ftp/python/3.8.11/Python-3.8.11.tar.xz'
    >>> filename
    'Python-3.8.11.tar.xz'

    """
    url = f"https://www.python.org/ftp/python/{selected_version}/Python-{selected_version}.tar.xz"
    filename = f"Python-{selected_version}.tar.xz"
    return url, filename


def get_conda_url_and_filename(version):
    """
    Create URL and filename to download miniforge python for Linux.

    Returns
    -------
    url and filename in String format

    Examples
    --------
    >>> url, filename = get_conda_url_and_filename("23.1.0-4")
    >>> url
    'https://github.com/conda-forge/miniforge/releases/download/23.1.0-4/Miniforge3-23.1.0-4-Linux-x86_64.sh'
    >>> filename
    'Miniforge3-23.1.0-4-Linux-x86_64.sh'

    """
    url = f"https://github.com/conda-forge/miniforge/releases/download/{version}/Miniforge3-{version}-Linux-x86_64.sh"
    filename = f"Miniforge3-{version}-Linux-x86_64.sh"

    return url, filename


def install_python_linux(filename):
    """
    Install python on linux.

    Examples
    --------
    >>> install_python_linux("Miniforge3-23.1.0-4-Linux-x86_64.sh")

    """
    if "Miniforge" in filename:
        execute_linux_command(f"bash {filename} -b -u -p {ansys_linux_path}/conda")
    else:
        tar_dir, file = os.path.split(filename)
        untar_dirname = filename.replace(".tar.xz", "")
        cwd = os.getcwd()
        os.chdir(tar_dir)
        execute_linux_command(f"tar xvf {file}")
        file = file.replace(".tar.xz", "")
        file = file.lower()
        execute_linux_command(
            f"cd {untar_dirname};mkdir -p {ansys_linux_path}/{file};make clean;./configure --prefix={ansys_linux_path}/{file};make;make install;cp {ansys_linux_path}/{file}/bin/python3 {ansys_linux_path}/{file}/bin/python"
        )
        os.chdir(cwd)
    return 0


def find_miniforge_linux(ansys_manager_installed_only=False):
    """
    Find miniforge installation on the host machine.

    Parameters
    ----------
    ansys_manager_installed_only : bool, optional
        If this value is True, then the Python versions installed via Ansys Python Manager will be returned.

    Returns
    -------
    dict
        Dictionary containing a key for each path and a tuple
        containing ``(version: str, admin: bool)``.

    Examples
    --------
    >>> installed_pythons = find_miniforge_linux()
    >>> installed_pythons
    {'/home/user/python/py311/bin/python': ('3.11.3', False),
     '/home/user/python/py311/bin/python3': ('3.11.3', False),
     '/usr/bin/python3.7': ('3.7.16', True),
     '/usr/bin/python3.8': ('3.8.16', True),
     '/usr/bin/python3.9': ('3.9.16', True)}

    """
    paths = {}
    if not ansys_manager_installed_only:
        try:
            subprocess.check_output("printenv | grep CONDA_PYTHON_EXE > /tmp/conda.txt")
            with open("/tmp/conda.txt") as f:
                conda_system_path = f.read()
                conda_system_path = conda_system_path.replace("CONDA_PYTHON_EXE=", "")
                conda_system_path = conda_system_path.replace("/bin/python", "").strip()
                version = subprocess.check_output([f"conda", "--version"])
                version = version.split()[1].decode("utf-8")
                paths[conda_system_path] = (version, True)
            os.remove("/tmp/conda.txt")
        except:
            pass
    try:
        version = subprocess.check_output(
            [f"{ansys_linux_path}/conda/bin/conda", "--version"]
        )
        version = version.split()[1].decode("utf-8")
        if not f"{ansys_linux_path}/conda" in paths:
            paths[f"{ansys_linux_path}/conda"] = (version, False)
    except Exception as e:
        LOG.debug(e)
    return paths


def create_venv_linux(venv_dir, py_path):
    """
    Create virtual environment.

    Examples
    --------
    >>> create_venv_linux(
    ...     "/home/sha/.local/ansys/.ansys_python_venvs/myenv/bin",
    ...     "/home/sha/.local/ansys/python-3.8.10/bin/python3",
    ... )

    """
    execute_linux_command(f"{py_path} -m pip install -U pip uv")
    execute_linux_command(f"{py_path} -m uv venv {venv_dir}")


def create_venv_linux_conda(venv_dir, py_path):
    """
    Create virtual environment for Miniforge.

    Examples
    --------
    >>> create_venv_linux_conda(
    ...     "/home/sha/.local/ansys/.ansys_python_venvs/myenv/bin",
    ...     "/home/sha/.local/ansys/python-3.8.10/bin/python3",
    ... )

    """
    # execute_linux_command(f"{py_path}/bin/conda create --prefix {venv_dir} python -y")
    execute_linux_command(
        f"{py_path}/bin/mamba -V || {py_path}/bin/conda install mamba -y"
    )
    execute_linux_command(f"{py_path}/bin/mamba create --prefix {venv_dir} python -y")


def delete_venv_conda(miniforge_path, parent_path):
    """
    Delete virtual environments for Miniforge.

    Examples
    --------
    >>> delete_venv_conda(
    ...     "/home/sha/.local/ansys/.ansys_python_venvs/myenv/bin",
    ...     "/home/sha/.local/ansys/python-3.8.10/bin/python3",
    ... )

    """
    execute_linux_command(f"{miniforge_path} env remove --prefix {parent_path} --yes")


def run_linux_command(pypath, extra, venv=False):
    """
    Run pip command on Linux terminal.

    Examples
    --------
    >>> run_linux_command("/home/sha/.local/ansys/python-3.8.10/bin/python3", "uv pip list")

    """

    # Update package manager before executing commands
    execute_linux_command(f"{pypath} -m pip install -U pip uv")

    prefix = f"{pypath}"
    extra = extra.replace("timeout", "sleep")
    python_name = prefix.split("/")[-1]
    major_version = (
        list(python_name)[-1] if list(python_name)[-1].isnumeric() and not venv else ""
    )
    if not extra:
        extra = "bash"
    if "sleep" not in extra and extra != "bash":
        extra += '; read -p "Press Enter to Continue.... " confirm || exit 1'
    if venv:
        prefix = f". {pypath}/bin/activate; "
    else:
        prefix = "/".join(prefix.split("/")[:-1]) + "/"
        # extra = extra.replace("pip", f"pip{major_version}")
    execute_linux_command(f"cd ~ ; {prefix}{extra}", wait=False)


def run_linux_command_conda(pypath, extra, venv=False):
    """
    Run conda command on Linux terminal.

    Examples
    --------
    >>> run_linux_command_conda("/home/sha/.local/ansys/python-3.8.10/bin/python3", "uv pip list")

    """
    venvParam = ""
    extra = extra.replace("timeout", "sleep")
    extra = extra.replace("conda install --yes", "mamba install --yes")
    # extra = extra.replace("conda update conda --yes", "python -m pip install -U pip uv")
    extra = extra.replace(
        "conda update conda --yes", "mamba update -n base mamba --yes"
    )
    if not extra:
        extra = "bash"
    if "sleep" not in extra and extra != "bash":
        extra += '; read -p "Press Enter to Continue.... " confirm || exit 1'
    conda_path = f"{pypath}/bin/"
    if venv:
        with open(os.path.join(pypath, "conda-meta", "history"), "r") as f:
            for line in f:
                if line.startswith("# cmd:"):
                    line = line.lstrip("# cmd: ")
                    path = line.strip().split("create --prefix")[0]
                    miniforge_path = path.strip().split("Scripts")[0].rstrip("\\")
                    miniforge_path = miniforge_path.replace(
                        "bin/mamba", "etc/profile.d/conda.sh"
                    )
                    conda_path = ""
                    break
        venvParam = f"; . {miniforge_path}; . {miniforge_path.replace('conda.sh', 'mamba.sh')} ;mamba activate {pypath}"
    else:
        extra = extra.replace("uv pip", f" {pypath}/bin/pip")
    execute_linux_command(f"cd ~ {venvParam} ; {conda_path}{extra} ", wait=False)


def find_ansys_installed_python_linux():
    """
    Find all installed Ansys Python Manager installed Python versions on Linux.

    Returns
    -------
    dict
        Dictionary containing a key for each path and a tuple
        containing ``(version: str, admin: bool)``.

    Examples
    --------
    >>> installed_pythons = find_ansys_installed_python_linux()
    >>> installed_pythons
    {'/home/user/python/py311/bin/python': ('3.11.3', False),
     '/home/user/python/py311/bin/python3': ('3.11.3', False),
     '/usr/bin/python3.7': ('3.7.16', True),
     '/usr/bin/python3.8': ('3.8.16', True),
     '/usr/bin/python3.9': ('3.9.16', True)}

    """
    LOG.debug(
        "Identifying all Ansys Python Manager installed versions of python on Linux"
    )

    pythons = {}
    ansys_path = f"{ansys_linux_path}"
    try:
        for files in [
            x
            for x in os.listdir(ansys_path)
            if "python" in x and x != ".ansys_python_venvs" and x != "conda"
        ]:
            version = files.replace("python-", "")
            major_version = version.split(".")[0]
            pythons[os.path.join(ansys_path, files, f"bin/python{major_version}")] = (
                version,
                False,
            )
            LOG.debug(
                "Identified %s at %s",
                version,
                os.path.join(ansys_path, files, f"bin/python{major_version}"),
            )

    except:
        # Ignore if the command fails (e.g., if the Python version is not installed)
        pass

    return pythons


def query_gh_latest_release_linux(token=None):
    """Check GitHub for updates.

    Compares the current version with the version on GitHub.

    Returns the version of the latest release and the download url of
    the executable installer for debian.

    Parameters
    ----------
    token : str, optional
        Token to perform the request. Not necessary, only used on testing
        to avoid reaching API request limit.

    Returns
    -------
    str
        Tag of the latest version.

    str
        Url of the latest release installer.

    """
    gh = Github(login_or_token=token)
    repo = gh.get_repo(f"ansys/python-installer-qt-gui")

    # Get the latest release and its tag name
    latest_release = repo.get_latest_release()
    latest_version_tag = latest_release.tag_name

    download_asset = None
    try:
        os_version = get_os_version()
        os_version = os_version.replace(".", "_")
        LOG.debug(f"os version : {os_version}")
        if os_version:
            for asset in latest_release.get_assets():
                if f"linux_{os_version}" in asset.name:
                    download_asset = asset
            download_url = None if download_asset is None else download_asset.url
            return version.parse(latest_version_tag), download_url
        return None, None
    except:
        return None, None


def execute_linux_command(command, wait=True):
    """
    Run linux command on gnome terminal.

    Examples
    --------
    >>> execute_linux_command("ls")

    """
    wait_command = ""
    if wait:
        wait_command = "--wait"
    LOG.debug(f"gnome-terminal {wait_command} -- sh -c '{command}'")
    os.system(f"gnome-terminal {wait_command} -- sh -c '{command}'")


def get_os_version():
    """
    Get OS version for linux.

    Returns
    -------
    str
        os version.

    """
    try:
        os_details = subprocess.check_output(["cat", "/etc/os-release"])
        os_details = os_details.decode("utf-8").split("\n")

        os_name = [x for x in os_details if "NAME" in x][0].split("=")[-1]
        if "Ubuntu" in os_name or any("UBUNTU" in x for x in os_details):
            os_version = (
                [x for x in os_details if "VERSION_ID" in x][0]
                .split("=")[-1]
                .replace('"', "")
            )
        elif "Fedora" in os_name:
            os_version = "fedora"
        elif (
            "Red Hat" in os_name
            or "CentOS" in os_name
            or any("REDHAT" in x for x in os_details)
        ):
            os_version = "centos"

        return os_version
    except:
        return ""


def update_app(filename):
    """
     Perform inplace update for linux.

    Parameters
     ----------
     filename : Downloaded zip file name with path

    """
    updater_path = f"{CACHE_DIR}/ansys-updater"
    Path(f"{updater_path}").mkdir(parents=True, exist_ok=True)
    os_version = get_os_version()
    if os_version == "centos":
        execute_linux_command(
            f"cd {updater_path};unzip -o {filename}; ./installer_CentOS.sh"
        )
    elif os_version == "fedora":
        execute_linux_command(
            f"cd {updater_path};unzip -o {filename}; ./installer_Fedora.sh"
        )
    else:
        execute_linux_command(f"cd {updater_path};unzip -o {filename}; ./installer.sh")


def check_python_asset_linux(version):
    """
    Check python asset is available for linux or not.

    Parameters
    ----------
        version : Version of the python

    Returns
    -------
    str
        confirmation.

    """
    os_version = get_os_version()
    assets_path = os.path.join(ASSETS_PATH)

    try:
        for folder_name in os.listdir(assets_path):
            if folder_name in os_version:
                for assets in os.listdir(os.path.join(assets_path, folder_name)):
                    if version in assets:
                        shutil.copyfile(
                            os.path.join(assets_path, folder_name, assets),
                            os.path.join(os.getcwd(), assets),
                        )
                        verify = install_python_linux_from_assets(assets)
                        return verify
    except Exception as e:
        LOG.debug(f"check_python_asset_linux {e}")
        pass
    return None


def install_python_linux_from_assets(file):
    """
    Install python on linux.

    Examples
    --------
    >>> install_python_linux("assets/python.tar.gz")

    """
    try:
        file_name = file.replace(".tar.gz", "")
        file_name = file_name.lower()
        execute_linux_command(
            f"mkdir -p {ansys_linux_path};tar xvf {file} -C {ansys_linux_path};"
        )
        os.remove(file)
        return "Success"
    except Exception as e:
        LOG.debug(f"install_python_linux_from_assets {e}")
        return None
