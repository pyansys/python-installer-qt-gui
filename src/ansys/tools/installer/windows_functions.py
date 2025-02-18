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

"""Windows functions."""

import logging
import os
import subprocess

LOG = logging.getLogger(__name__)


def create_venv_windows(venv_dir: str, py_path: str):
    r"""
    Create a virtual environment on Windows.

    Parameters
    ----------
    venv_dir : str
        Name of the virtual environment.
    py_path : str
        Path to the Python executable.

    Examples
    --------
    >>> create_venv_windows("my_venv", "C:\\Python39\\python.exe")

    """
    user_profile = os.path.expanduser("~")
    scripts_path = os.path.join(py_path, "Scripts")
    new_path = f"{py_path};{scripts_path};%PATH%"

    # Update the package managers
    subprocess.call(
        f'start /w /min cmd /K "set PATH={new_path} && python -m pip install --upgrade pip uv && exit"',
        shell=True,
        cwd=user_profile,
    )

    # Create venv using uv
    subprocess.call(
        f'start /w /min cmd /K "set PATH={new_path} && python -m uv venv {venv_dir} && exit"',
        shell=True,
        cwd=user_profile,
    )


def create_venv_windows_conda(venv_dir: str, py_path: str):
    r"""
    Create a virtual environment on Windows using conda.

    Parameters
    ----------
    venv_dir : str
        Name of the virtual environment.
    py_path : str
        Path to the Python executable.

    Examples
    --------
    >>> create_venv_windows_conda("my_venv", "C:\\Python39\\python.exe")

    """
    user_profile = os.path.expanduser("~")
    subprocess.call(
        f'start /w /min cmd /K "{py_path}\\Scripts\\activate.bat && conda create --prefix {venv_dir} python -y && exit"',
        shell=True,
        cwd=user_profile,
    )


def run_ps(command, full_path_to_ps=False):
    """Run a powershell command as admin."""
    ps = (
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        if full_path_to_ps
        else "powershell.exe"
    )
    ps_command = [ps, command]

    LOG.debug("Running: %s", str(ps_command))
    proc = subprocess.run(
        ps_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    # stderr goes through stdout too
    if proc.returncode:  # If return code != 0
        LOG.error("From powershell: %s", proc.stdout)
        if full_path_to_ps == False:
            return run_ps(command, full_path_to_ps=True)

    else:
        LOG.debug("From powershell: %s", proc.stdout)

    return proc.stdout.decode(), proc.returncode


def install_python_windows(filename: str, wait: bool) -> tuple[str, int]:
    """Install "vanilla" python for a single user.

    Parameters
    ----------
    filename : str
        Path to the Python installer.
    wait : bool
        Wait for the installation to complete.

    Returns
    -------
    str
        Output from the installation.
    int
        Return code from the installation.
    """
    wait_str = " -Wait" if wait else ""
    command = f"(Start-Process '{filename}' -ArgumentList '/passive InstallAllUsers=0' {wait_str})"
    return run_ps(command)
