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

"""Installed Python versions table module for Ansys Python Manager."""

import logging
import os
import shutil
import subprocess
import time

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox

from ansys.tools.installer.common import get_pkg_versions
from ansys.tools.installer.configure_json import ConfigureJson
from ansys.tools.installer.constants import PYANSYS_LIBS, SELECT_VENV_MANAGE_TAB
from ansys.tools.installer.find_python import (
    find_all_python,
    find_miniforge,
    get_all_python_venv,
)
from ansys.tools.installer.linux_functions import (
    delete_venv_conda,
    is_linux_os,
    run_linux_command,
    run_linux_command_conda,
)
from ansys.tools.installer.vscode import VSCode

ALLOWED_FOCUS_EVENTS = [QtCore.QEvent.Type.WindowActivate, QtCore.QEvent.Type.Show]
LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")


class DataTable(QtWidgets.QTableWidget):
    """Common Table of locally installed Python environments/Virtual Environments."""

    signal_update = QtCore.Signal()

    def __init__(
        self,
        parent=None,
        installed_python=False,
        installed_forge=False,
        created_venv=False,
    ):
        """Initialize the table by populating it."""
        super().__init__(1, 1, parent)

        self.installed_python = installed_python
        self.installed_forge = installed_forge
        self.created_venv = created_venv

        self._destroyed = False
        self._locked = True
        self.populate()
        self.signal_update.connect(self.populate)

    def update(self, timeout=1.0):
        """Update this table.

        Respects a lock to ensure no race conditions or multiple calls on the table.

        """
        tstart = time.time()
        while self._locked:
            time.sleep(0.001)
            if time.time() - tstart > timeout:
                return

        self.signal_update.emit()

    def populate(self):
        """Populate the table."""
        self._locked = True
        self.clear()

        if self._destroyed:
            return

        # Check for python & conda forge versions
        if self.installed_python or self.installed_forge:
            LOG.debug("Populating the table with python and conda forge versions.")
            python_lst = find_all_python()
            conda_lst = find_miniforge()

            tot = len(python_lst) + len(conda_lst)
            self.setRowCount(tot)
            self.setColumnCount(3)
            self.setHorizontalHeaderLabels(["Version", "Admin", "Path"])
            self.verticalHeader().setVisible(False)
            self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

            row = 0
            for path, (version, admin) in python_lst.items():
                self.setItem(row, 0, QtWidgets.QTableWidgetItem(f"Python {version}"))
                self.setItem(row, 1, QtWidgets.QTableWidgetItem(str(admin)))
                self.setItem(row, 2, QtWidgets.QTableWidgetItem(path))
                row += 1

            for path, (version, admin) in conda_lst.items():
                self.setItem(row, 0, QtWidgets.QTableWidgetItem(f"Conda {version}"))
                self.setItem(row, 1, QtWidgets.QTableWidgetItem(str(admin)))
                self.setItem(row, 2, QtWidgets.QTableWidgetItem(path))
                row += 1

        elif self.created_venv:
            LOG.debug("Populating the table with virtual environments.")
            # Check for virtual environments
            venv_lst = get_all_python_venv()
            tot = len(venv_lst)
            if tot == 0:
                venv_lst["None"] = (None, None)
                tot = 1
            self.setRowCount(tot)
            self.setColumnCount(3)
            self.setHorizontalHeaderLabels(["Virtual environment", "Admin", "Path"])
            self.verticalHeader().setVisible(False)
            self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

            row = 0
            for path, (version, admin) in venv_lst.items():
                self.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{version}"))
                self.setItem(row, 1, QtWidgets.QTableWidgetItem(str(admin)))
                self.setItem(row, 2, QtWidgets.QTableWidgetItem(path))
                row += 1

        self.resizeColumnsToContents()
        self.selectRow(0)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Fixed
        )

        self.destroyed.connect(self.stop)
        self._locked = False

    def stop(self):
        """Flag that this object is gone."""
        self._destroyed = True

    @property
    def active_version(self):
        """Version of the active row."""
        return self.item(self.currentRow(), 0).text()

    @property
    def active_admin(self):
        """Version of the active row."""
        return self.item(self.currentRow(), 1).text()

    @property
    def active_path(self):
        """Path of the active row."""
        return self.item(self.currentRow(), 2).text()


class InstalledTab(QtWidgets.QWidget):
    """Installed Python versions tab."""

    def __init__(self, parent=None):
        """Initialize this tab."""
        super().__init__()
        self._parent = parent
        self._cached_versions = {}

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Group 1: Available Virtual Environments
        self.available_venv_box = QtWidgets.QGroupBox("Available virtual environments")
        available_venv_box_layout = QtWidgets.QVBoxLayout()
        self.available_venv_box.setLayout(available_venv_box_layout)

        # --> Add text for available virtual environments
        available_venv_box_text = QtWidgets.QLabel()
        available_venv_box_text.setText(SELECT_VENV_MANAGE_TAB)
        available_venv_box_text.setOpenExternalLinks(True)
        available_venv_box_text.setTextFormat(QtCore.Qt.TextFormat.RichText)
        available_venv_box_text.setWordWrap(True)
        available_venv_box_layout.addWidget(available_venv_box_text)

        # --> Add the virtual environment table
        self.venv_table = DataTable(created_venv=True)
        self.venv_table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)

        available_venv_box_layout.addWidget(self.venv_table)
        self.venv_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.venv_table.customContextMenuRequested.connect(
            self.delete_virtual_environment
        )
        layout.addWidget(self.available_venv_box)

        # EXTRA Group: Available Python installation
        self.available_python_install_box = QtWidgets.QGroupBox(
            "Available base Python versions"
        )
        available_python_install_box_layout = QtWidgets.QVBoxLayout()
        available_python_install_box_layout.setContentsMargins(10, 20, 10, 20)
        self.available_python_install_box.setLayout(available_python_install_box_layout)

        # Python Version, Forge Version Table
        self.table = DataTable(installed_python=True, installed_forge=True)
        self.table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        available_python_install_box_layout.addWidget(self.table)
        layout.addWidget(self.available_python_install_box)

        # Hide it at first
        self.available_python_install_box.hide()

        # EXTRA: Use general Python installations for the above actions
        self.check_box_opt = QtWidgets.QCheckBox(
            "NOT RECOMMENDED: Use base Python versions instead of virtual environments."
        )
        self.check_box_opt.setCheckState(QtCore.Qt.CheckState.Unchecked)
        layout.addWidget(self.check_box_opt)
        self.check_box_opt.stateChanged.connect(self.set_chk_box_focus)
        self.check_box_opt.stateChanged.connect(self.display_ctrl)

        ####### Launching and package management options #######

        # Group 2: Launching Options
        launching_options_box = QtWidgets.QGroupBox("Launch options")
        launching_options_box_layout = QtWidgets.QVBoxLayout()
        launching_options_box_layout.setContentsMargins(10, 20, 10, 20)
        launching_options_box.setLayout(launching_options_box_layout)

        hbox = QtWidgets.QHBoxLayout()
        launching_options_box_layout.addLayout(hbox)
        self.button_launch_cmd = QtWidgets.QPushButton("Launch console")
        self.button_launch_cmd.clicked.connect(self.launch_cmd)
        hbox.addWidget(self.button_launch_cmd)

        self.button_launch_cmd = QtWidgets.QPushButton("Launch VSCode")
        self.button_launch_cmd.clicked.connect(self.launch_vscode)
        hbox.addWidget(self.button_launch_cmd)

        self.button_launch_lab = QtWidgets.QPushButton("Launch Jupyterlab")
        self.button_launch_lab.clicked.connect(self.launch_jupyterlab)
        hbox.addWidget(self.button_launch_lab)

        self.button_launch_notebook = QtWidgets.QPushButton("Launch Jupyter Notebook")
        self.button_launch_notebook.clicked.connect(self.launch_jupyter_notebook)
        hbox.addWidget(self.button_launch_notebook)

        self.button_launch_spyder = QtWidgets.QPushButton("Launch Spyder")
        self.button_launch_spyder.clicked.connect(self.launch_spyder)
        hbox.addWidget(self.button_launch_spyder)

        layout.addWidget(launching_options_box)

        # Group 3: Package Management
        pkg_manage_box = QtWidgets.QGroupBox("General package management")
        pkg_manage_box_layout = QtWidgets.QVBoxLayout()
        pkg_manage_box_layout.setContentsMargins(10, 20, 10, 20)
        pkg_manage_box.setLayout(pkg_manage_box_layout)

        hbox_install = QtWidgets.QHBoxLayout()
        pkg_manage_box_layout.addLayout(hbox_install)

        self.button_install_defaults = QtWidgets.QPushButton(
            "Install Python default packages"
        )
        self.button_install_defaults.clicked.connect(self.install_defaults)
        hbox_install.addWidget(self.button_install_defaults)

        self.button_list_packages = QtWidgets.QPushButton("List installed packages")
        self.button_list_packages.clicked.connect(self.list_packages)
        hbox_install.addWidget(self.button_list_packages)

        layout.addWidget(pkg_manage_box)

        # Group 4: PyAnsys Package Management
        pyansys_pkg_manage_box = QtWidgets.QGroupBox("PyAnsys package management")
        pyansys_pkg_manage_box_layout = QtWidgets.QVBoxLayout()
        pyansys_pkg_manage_box_layout.setContentsMargins(10, 20, 10, 20)
        pyansys_pkg_manage_box.setLayout(pyansys_pkg_manage_box_layout)

        hbox_install_pyansys = QtWidgets.QHBoxLayout()
        pyansys_pkg_manage_box_layout.addLayout(hbox_install_pyansys)

        self.model = QStandardItemModel()
        self.packages_combo = QComboBox()
        self.packages_combo.setModel(self.model)

        self.versions_combo = QComboBox()
        self.button_launch_cmd = QtWidgets.QPushButton("Install")
        self.button_launch_cmd.clicked.connect(self.install_pyansys_packages)

        for library in PYANSYS_LIBS:
            self.model.appendRow(QStandardItem(library))

        self.packages_combo.currentIndexChanged.connect(self.update_package_combo)
        self.update_package_combo(0)

        hbox_install_pyansys.addWidget(self.packages_combo)
        hbox_install_pyansys.addWidget(self.versions_combo)
        hbox_install_pyansys.addWidget(self.button_launch_cmd)
        layout.addWidget(pyansys_pkg_manage_box)

        # ensure the table is always in focus
        self.installEventFilter(self)

    def update_table(self):
        """Update the Python version table."""
        self.table.update()
        self.venv_table.update()

    def display_ctrl(self):
        """Set the focus accordingly depending on check box."""
        if self.is_chk_box_active():
            self.available_python_install_box.show()
            self.available_venv_box.hide()
        else:
            self.available_python_install_box.hide()
            self.available_venv_box.show()

    def set_chk_box_focus(self, state):
        """Set the focus accordingly depending on check box."""
        self.table.setFocus() if state else self.venv_table.setFocus()

    def is_chk_box_active(self):
        """Get the value of the check box."""
        return (
            True
            if self.check_box_opt.checkState() is QtCore.Qt.CheckState.Checked
            else False
        )

    def eventFilter(self, source, event):
        """Filter events and ensure that the table always remains in focus."""
        if event.type() in ALLOWED_FOCUS_EVENTS and source is self:
            self.set_chk_box_focus(self.is_chk_box_active())
        return super().eventFilter(source, event)

    def launch_spyder(self):
        """Launch spyder IDE."""
        # handle errors
        error_msg = "(uv pip install spyder && spyder && exit 0) || echo Failed to launch. Try reinstalling spyder with pip install spyder --force-reinstall"
        self._update_pck_mnger()
        self.launch_cmd(
            f'uv pip list | {"grep" if is_linux_os() else "findstr"} "spyder" && spyder && exit 0 || {error_msg}'
        )

    def launch_jupyterlab(self):
        """Launch Jupyterlab."""
        # handle errors
        error_msg = "uv pip install jupyterlab && python -m jupyter lab || echo Failed to launch. Try reinstalling jupyterlab with pip install jupyterlab --force-reinstall"
        self._update_pck_mnger()
        self.launch_cmd(f"python -m jupyter lab || {error_msg}")

    def launch_vscode(self):
        """Launch VSCode."""
        vscode = VSCode(self)

    def launch_jupyter_notebook(self):
        """Launch Jupyter Notebook."""
        # handle errors
        error_msg = "uv pip install jupyter && python -m jupyter notebook || echo Failed to launch. Try reinstalling jupyter with pip install jupyter --force-reinstall"
        self._update_pck_mnger()
        self.launch_cmd(f"python -m jupyter notebook || {error_msg}")

    def install_defaults(self):
        """Install Python default packages."""
        cmd = "uv pip install numpy pandas scipy scikit-learn matplotlib pyvista[all] && timeout 3 && exit || echo Failed to install default Python packages. Try reinstalling it with pip install numpy pandas scipy scikit-learn matplotlib pyvista[all] --force-reinstall"
        self._update_pck_mnger()
        self.launch_cmd(cmd)

    def install_pyansys_packages(self):
        """Install PyAnsys - chosen packages."""
        chosen_pkg = self.packages_combo.currentText()
        chosen_ver = self.versions_combo.currentText()
        pck_ver = (
            f"{PYANSYS_LIBS[chosen_pkg]}=={chosen_ver}"
            if chosen_ver
            else f"{PYANSYS_LIBS[chosen_pkg]}"
        )
        cmd = f"uv pip install {pck_ver} && timeout 3 && exit || echo Failed to install this PyAnsys Library. Try reinstalling it with uv pip install {pck_ver} --force-reinstall"
        self._update_pck_mnger()
        self.launch_cmd(cmd, always_use_pip=True)

    def update_package_combo(self, index):
        """Update the dropdown of available versions based on the package chosen."""
        package_name = PYANSYS_LIBS[self.packages_combo.currentText()]
        if package_name not in self._cached_versions:
            self._cached_versions[package_name] = get_pkg_versions(package_name)

        # Populate the model with the fetched package versions and
        # set the model as the active model for the version dropdown
        versions_model = QStandardItemModel()
        for version in self._cached_versions[package_name]:
            versions_model.appendRow(QStandardItem(version))

        self.versions_combo.setModel(versions_model)
        self.versions_combo.setCurrentIndex(0)

    def list_packages(self):
        """List installed Python packages."""
        self.launch_cmd("uv pip list")

    def _update_pck_mnger(self):
        """Update package manager if needed.

        Notes
        -----
        Only working on base Python installations, for now.
        """
        if self.is_chk_box_active():
            if "Python" in self.table.active_version:
                cmd = "python -m pip install -U pip uv && exit"
            else:  # Otherwise, conda
                cmd = "conda update conda --yes && exit"
            self.launch_cmd(cmd, minimized_window=True)

    def find_env_type(self, table_name):
        """Find if this is a conda or vanilla python environment.

        Parameters
        ----------
        table_name : str
            The name of the table to be used ("venv_table" or "table")

        Returns
        -------
        tuple(str or bool, str or None, str or None)
            A tuple containing information on: if it is a pip environment or conda
            environment, the path to the Miniforge installation if any, and the path
            to the virtual environment's activation.
        """
        if table_name == "venv_table":
            sel_table = self.venv_table
        elif table_name == "table":
            sel_table = self.table
        else:
            LOG.error("No table provided. Internal tool error.")
            return None, None, None

        py_path = sel_table.active_path
        parent_path = os.path.dirname(py_path)  # No Scripts Folder
        # If py_path has a folder called conda-meta --> then it is a conda environment
        is_vanilla_python = False if "conda-meta" in os.listdir(parent_path) else True

        if is_vanilla_python:
            miniforge_path = ""
        else:
            py_path = os.path.dirname(py_path)  # No Scripts Folder
            # If it is a conda environment, then we need to get the path to the miniforge installation
            with open(os.path.join(py_path, "conda-meta", "history"), "r") as f:
                for line in f:
                    if line.startswith("# cmd:"):
                        line = line.lstrip("# cmd: ")
                        path = line.strip().split("create --prefix")[0]
                        miniforge_path = path.strip().split("Scripts")[0].rstrip("\\")
                        break
        # Fail-safe check
        if not is_vanilla_python and miniforge_path == "":
            LOG.error("Invalid type of virtual environment. Internal tool error.")
            return None, None, None

        return is_vanilla_python, miniforge_path, parent_path

    def delete_virtual_environment(self, point):
        """Delete virtual environments using right click."""
        # Get the cell that was right-clicked
        index = self.venv_table.indexAt(point)
        configure_json = ConfigureJson()
        if not index.isValid():
            return

        # Create the context menu
        menu = QtWidgets.QMenu(self)
        delete_action = menu.addAction("Delete virtual environment")

        # Show the context menu and handle the user's choice
        action = menu.exec(self.venv_table.mapToGlobal(point))

        # Get information on the venv type
        is_vanilla_python, miniforge_path, parent_path = self.find_env_type(
            "venv_table"
        )

        if is_vanilla_python and action == delete_action:
            try:
                # Delete the python virtual environment
                shutil.rmtree(parent_path)
            except:
                pass
        elif not is_vanilla_python and action == delete_action:
            try:
                # Delete the conda environment
                if is_linux_os():
                    delete_venv_conda(miniforge_path, parent_path)
                else:
                    subprocess.call(
                        f'start /w /min cmd /K "{miniforge_path}\\Scripts\\activate.bat && conda env remove --prefix {parent_path} --yes && exit"',
                        shell=True,
                    )
                if os.path.exists(parent_path):
                    shutil.rmtree(parent_path)
            except:
                pass

        # Finally, update the venv table
        self.venv_table.update()

    def launch_cmd(
        self,
        extra: str = "",
        minimized_window: bool = False,
        always_use_pip: bool = False,
    ):
        """Run a command in a new command prompt.

        Parameters
        ----------
        extra : str, default: ""
            Any additional command(s).
        minimized_window : bool, default: False
            Whether the window should run minimized or not.
        always_use_pip : bool, default: False
            Whether to always use pip for the command or not.
        """
        path = os.environ["PATH"].split(";")
        altered_path = path.copy()
        for p in path:
            if (
                "Ansys Python Manager\_internal" in p
                or "ansys_python_manager\_internal" in p
            ):
                altered_path.remove(p)
        myenv = ";".join(altered_path)

        # Handle unexpected bool parameter for linux
        if is_linux_os() and isinstance(extra, bool):
            extra = ""

        min_win = "/w /min" if minimized_window else ""

        # is_venv            -  True : virtual environment , False: base python installation
        # is_vanilla_python  -  True : Vanilla Python , False : Miniforge/Conda

        if self.is_chk_box_active():
            is_venv = False
            # when base python installation  is chosen in the table
            py_path = self.table.active_path
            py_version = self.table.active_version
            # chosen_general_base_is_python = True if "Python" in py_version else False

            miniforge_path = "" if "Python" in py_version else py_path
            is_vanilla_python = True if miniforge_path == "" else False
        else:
            is_venv = True
            is_vanilla_python, miniforge_path, py_path = self.find_env_type(
                "venv_table"
            )

        if is_vanilla_python and not is_venv:
            scripts_path = os.path.join(py_path, "Scripts")

            new_path = f"{py_path};{scripts_path};{myenv}"

            if extra:
                extra = extra.replace("uv pip install", "uv pip install --system")
                extra = extra.replace("uv pip list", "uv pip list --system")
                cmd = f"&& {extra}"
            else:
                cmd = f"&& echo Python set to {py_path}"

            if is_linux_os():
                run_linux_command(py_path, extra)
            else:
                # Update the package managers
                subprocess.call(
                    f'start /w /min cmd /K "set PATH={new_path} && python -m pip install --upgrade pip uv && exit"',
                    shell=True,
                )

                subprocess.call(
                    f'start {min_win} cmd /K "set PATH={new_path} && cd %userprofile% {cmd}"',
                    shell=True,
                )
        elif is_vanilla_python and is_venv:
            # Launch with active python virtual environment
            if extra:
                cmd = f"&& {extra}"
            else:
                cmd = f"&& echo Python set to {py_path}"
            if is_linux_os():
                run_linux_command(py_path, extra, True)
            else:
                subprocess.call(
                    f'start {min_win} cmd /K "set PATH={myenv} && {py_path}\\Scripts\\activate.bat && cd %userprofile% {cmd}"',
                    shell=True,
                )
        elif not is_vanilla_python and is_venv:
            # Launch with active conda virtual environment
            if extra:
                # Replace the pip install command for conda
                if not always_use_pip:
                    extra = extra.replace("uv pip", "conda")
                    extra = extra.replace("conda install", "conda install --yes")
                cmd = f"&& {extra}"
            else:
                cmd = f"&& echo Activating conda forge at path {py_path}"
            if is_linux_os():
                run_linux_command_conda(py_path, extra, True)
            else:
                subprocess.call(
                    f'start {min_win} cmd /K "set PATH={myenv} && {miniforge_path}\\Scripts\\activate.bat && conda activate {py_path} && cd %userprofile% {cmd}"',
                    shell=True,
                )
        else:
            # not is_vanilla_python and not is_venv
            if extra:
                # Replace the pip install command for conda
                if not always_use_pip:
                    extra = extra.replace("uv pip", "conda")
                    extra = extra.replace("conda install", "conda install --yes")
                cmd = f"&& {extra}"
            else:
                cmd = f"&& echo Activating conda forge at path {py_path}"
            if is_linux_os():
                run_linux_command_conda(py_path, extra, False)
            else:
                subprocess.call(
                    f'start {min_win} cmd /K "set PATH={myenv} && {miniforge_path}\\Scripts\\activate.bat && conda activate {py_path} && cd %userprofile% {cmd}"',
                    shell=True,
                )
