# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Main installer window."""


from math import floor
import os
import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import certifi
from packaging import version
import requests

from ansys.tools.installer import CACHE_DIR, __version__
from ansys.tools.installer.auto_updater import query_gh_latest_release
from ansys.tools.installer.common import protected
from ansys.tools.installer.configure import Configure
from ansys.tools.installer.constants import (
    ABOUT_TEXT,
    ANSYS_FAVICON,
    ASSETS_PATH,
    CONDA_PYTHON_VERSION,
    INSTALL_TEXT,
    LOG,
    PRE_COMPILED_PYTHON_WARNING,
    PYTHON_VERSION_TEXT,
    UNABLE_TO_RETRIEVE_LATEST_VERSION_TEXT,
    VANILLA_PYTHON_VERSIONS,
    UV_PYTHON_VERSIONS,
)
from ansys.tools.installer.create_virtual_environment import CreateVenvTab
from ansys.tools.installer.installed_table import InstalledTab
from ansys.tools.installer.installer import install_python
from ansys.tools.installer.linux_functions import (
    check_python_asset_linux,
    get_conda_url_and_filename,
    get_vanilla_url_and_filename,
    is_linux_os,
    query_gh_latest_release_linux,
    update_app,
)
from ansys.tools.installer.misc import ImageWidget, PyAnsysDocsBox, enable_logging
from ansys.tools.installer.progress_bar import ProgressBar
from ansys.tools.installer.uninstall import Uninstall
from ansys.tools.installer.windows_functions import run_ps


class AnsysPythonInstaller(QtWidgets.QMainWindow):
    """Main Ansys Python Manager class."""

    signal_error = QtCore.Signal(str)
    signal_open_pbar = QtCore.Signal(int, str)
    signal_increment_pbar = QtCore.Signal()
    signal_close_pbar = QtCore.Signal()
    signal_set_pbar_value = QtCore.Signal(int)
    signal_close = QtCore.Signal()

    def __init__(self, show=True):
        """Instantiate Ansys Python Manager main class."""
        super().__init__()
        self.setWindowTitle("Ansys Python Manager")
        self.setGeometry(50, 50, 500, 780)  # width should auto-update
        self._exceptions = []

        self._pbar = None
        self._err_message_box = None

        # Set the global font
        font = QtGui.QFont("Open Sans", -1, QtGui.QFont.Normal, False)
        QtWidgets.QApplication.setFont(font)

        # Create a QIcon object from an image file
        icon = QtGui.QIcon(ANSYS_FAVICON)
        # Set the application icon
        self.setWindowIcon(icon)

        # Create a menu bar
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        updates_action = QtGui.QAction("Check for updates", self)
        updates_action.triggered.connect(self.check_for_updates)
        file_menu.addAction(updates_action)

        configurations = QtGui.QAction("Configure", self)
        configurations.setShortcut(QtGui.QKeySequence("Ctrl+D"))
        configurations.triggered.connect(self.configure_application)
        file_menu.addAction(configurations)

        file_menu.addSeparator()  # -------------------------------------------

        if is_linux_os():
            uninstall_app = QtGui.QAction("Uninstall", self)
            uninstall_app.triggered.connect(self.uninstall_application)
            file_menu.addAction(uninstall_app)

        # Create an "Exit" action
        exit_action = QtGui.QAction("&Exit", self)
        exit_action.setShortcut(QtGui.QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(QtWidgets.QApplication.quit)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("&Help")

        # Create a "Visit Website" action
        visit_action = QtGui.QAction("&Online documentation", self)
        visit_action.triggered.connect(self.visit_website)
        help_menu.addAction(visit_action)

        # Create a "Report issue" action
        issue_action = QtGui.QAction("&Report issue", self)
        issue_action.triggered.connect(self.report_issue)
        help_menu.addAction(issue_action)

        # Create a "PyAnsys Documentation" action
        pyansys_docs_action = QtGui.QAction("&PyAnsys documentation", self)
        pyansys_docs_action.triggered.connect(self.pyansys_dialog)
        help_menu.addAction(pyansys_docs_action)

        help_menu.addSeparator()  # -------------------------------------------

        # Create an "About" action
        about_action = QtGui.QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)

        # Add the "About" action to the "Help" menu
        help_menu.addAction(about_action)

        # Header
        header_layout = QtWidgets.QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_widget = QtWidgets.QWidget()
        header_widget.setLayout(header_layout)

        # Header icon
        self.menu_heading = ImageWidget()
        pixmap = QtGui.QPixmap(os.path.join(ASSETS_PATH, "pyansys-light.png"))
        self.menu_heading.setPixmap(pixmap)
        header_layout.addWidget(self.menu_heading)

        # Main content
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_install_python = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_install_python, "Install Python")

        # Add tabs to the tab widget
        self.installed_table_tab = InstalledTab(self)
        self.venv_table_tab = CreateVenvTab(self)
        self.tab_widget.addTab(self.venv_table_tab, "Create virtual environments")
        self.tab_widget.addTab(self.installed_table_tab, "Manage Python environments")

        # Create the layout for the container
        container_layout = QtWidgets.QVBoxLayout()
        self.tab_install_python.setLayout(container_layout)

        # Form
        form = QtWidgets.QWidget()
        form_layout = QtWidgets.QVBoxLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form.setLayout(form_layout)

        # Group 1: Installation type
        installation_type_box = QtWidgets.QGroupBox("Installation type")
        installation_type_box_layout = QtWidgets.QVBoxLayout()
        installation_type_box_layout.setContentsMargins(10, 20, 10, 20)
        installation_type_box.setLayout(installation_type_box_layout)

        installation_type = QtWidgets.QWidget()
        installation_type_layout = QtWidgets.QVBoxLayout()
        installation_type_layout.setContentsMargins(0, 0, 0, 0)
        installation_type.setLayout(installation_type_layout)

        installation_type_text = QtWidgets.QLabel(INSTALL_TEXT)
        installation_type_text.setOpenExternalLinks(True)
        installation_type_layout.addWidget(installation_type_text)

        self.installation_type_select = QtWidgets.QComboBox()
        self.installation_type_select.addItem("Standard", "vanilla")
        self.installation_type_select.addItem("Conda (miniforge)", "miniconda")
        self.installation_type_select.addItem("Astral UV", "uv")

        installation_type_layout.addWidget(self.installation_type_select)
        self.installation_type_select.currentIndexChanged.connect(
            self._install_type_changed
        )

        installation_type_box_layout.addWidget(installation_type)
        form_layout.addWidget(installation_type_box)

        # Group 2: Python version
        python_version_box = QtWidgets.QGroupBox("Python version")
        python_version_box_layout = QtWidgets.QVBoxLayout()
        python_version_box_layout.setContentsMargins(10, 20, 10, 20)
        python_version_box.setLayout(python_version_box_layout)

        python_version_text = QtWidgets.QLabel(PYTHON_VERSION_TEXT)
        python_version_text.setWordWrap(True)
        python_version_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignJustify)
        python_version_box_layout.addWidget(python_version_text)

        # Python version
        python_version = QtWidgets.QWidget()
        python_version_layout = QtWidgets.QVBoxLayout()
        python_version_layout.setContentsMargins(0, 0, 0, 0)
        python_version.setLayout(python_version_layout)

        self.python_version_select = QtWidgets.QComboBox()
        
        self._install_type_changed()
        # Set the default selection to the last Python version
        
        default_index = self.python_version_select.findText(
            list(VANILLA_PYTHON_VERSIONS.keys())[-1]
        )
        self.python_version_select.setCurrentIndex(default_index)
        python_version_layout.addWidget(self.python_version_select)

        python_version_box_layout.addWidget(python_version)
        form_layout.addWidget(python_version_box)

        # Linux Warning/Note for Python pre-compiled version
        if is_linux_os():
            python_version_warning = QtWidgets.QLabel(PRE_COMPILED_PYTHON_WARNING)
            python_version_warning.setWordWrap(True)
            python_version_warning.setAlignment(QtCore.Qt.AlignmentFlag.AlignJustify)
            python_version_box_layout.addWidget(python_version_warning)

        # ensure content does not get squished
        form_layout.addStretch()

        # Submit button
        self.submit_button = QtWidgets.QPushButton("Install")
        self.submit_button.clicked.connect(self.download_and_install)
        form_layout.addWidget(self.submit_button)

        container_layout.addWidget(form)

        # Add menu and tab widget to main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(header_widget)
        main_layout.addWidget(self.tab_widget)

        # create central widget
        central_widget = QtWidgets.QWidget()
        self.setMaximumWidth(900)
        self.setMaximumHeight(900)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # connects
        self.signal_open_pbar.connect(self._pbar_open)
        self.signal_close_pbar.connect(self._pbar_close)
        self.signal_increment_pbar.connect(self._pbar_increment)
        self.signal_set_pbar_value.connect(self._pbar_set_value)
        self.signal_error.connect(self._show_error)
        self.signal_close.connect(self._close)

        if show:
            self.show()

    @protected
    def _exe_update(self, filename):
        """After downloading the update for this application, run the file and shutdown this application."""
        if is_linux_os():
            update_app(filename)
        else:
            run_ps(f"(Start-Process '{filename}')")

        # exiting
        LOG.debug("Closing...")
        self.close_emit()

    def close_emit(self):
        """Trigger the exit signal."""
        self.signal_close.emit()

    def _close(self):
        self.close()

    @protected
    def check_for_updates(self):
        """Check for Ansys Python Manager application updates."""
        LOG.debug("Checking for updates")
        try:
            if is_linux_os():
                (ver, url) = query_gh_latest_release_linux()
            else:
                (ver, url) = query_gh_latest_release()
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            LOG.info("Problem requesting version... ")
            ver = None

        cur_ver = version.parse(__version__)

        LOG.debug(f"Currently installed version: {cur_ver}")
        LOG.debug(f"Latest version: {ver}")

        if not ver:
            # Error occurred while requesting version... update check
            # cannot be automated. Referring to source.
            LOG.debug(
                "Update check cannot be automatically performed. Showing info message."
            )
            msgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information,
                "Information",
                UNABLE_TO_RETRIEVE_LATEST_VERSION_TEXT,
                QtWidgets.QMessageBox.Ok,
            )
            msgBox.setWindowIcon(QtGui.QIcon(ANSYS_FAVICON))
            pixmap = QPixmap(ANSYS_FAVICON).scaledToHeight(32, Qt.SmoothTransformation)
            msgBox.setIconPixmap(pixmap)
            msgBox.exec_()
        elif ver > cur_ver:
            LOG.debug("Update available.")
            pixmap = QPixmap(ANSYS_FAVICON).scaledToHeight(32, Qt.SmoothTransformation)

            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon(ANSYS_FAVICON))
            msgBox.setIconPixmap(pixmap)

            reply = msgBox.question(
                msgBox,
                "Update",
                f"The latest available version is {ver}. You are currently running version {cur_ver}. Do you want to update?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes,
            )

            if reply == QtWidgets.QMessageBox.Yes:
                if is_linux_os():
                    file = f"Ansys-Python-Manager-Setup-v{ver}.zip"
                    self._download(
                        url,
                        file,
                        when_finished=self._exe_update,
                    )
                else:
                    file = f"Ansys-Python-Manager-Setup-v{ver}.exe"
                    self._download(
                        url,
                        file,
                        when_finished=self._exe_update,
                    )
        else:
            LOG.debug("Up to date.")
            msgBox = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information,
                "Information",
                f"Ansys Python Installer is up-to-date.\n\nVersion is {__version__}",
                QtWidgets.QMessageBox.Ok,
            )
            msgBox.setWindowIcon(QtGui.QIcon(ANSYS_FAVICON))
            pixmap = QPixmap(ANSYS_FAVICON).scaledToHeight(32, Qt.SmoothTransformation)
            msgBox.setIconPixmap(pixmap)
            msgBox.exec_()

    @protected
    def configure_application(self):
        """Check for Ansys Python Manager application updates."""
        LOG.debug("Opening configuration...")
        self.setEnabled(False)
        Configure(self)
        self.setEnabled(True)

    @protected
    def uninstall_application(self):
        """Check for Ansys Python Manager application updates."""
        LOG.debug("Trigger uninstall..")
        Uninstall(self)

    def visit_website(self):
        """Access the Ansys Python Manager documentation."""
        url = QtCore.QUrl(
            "https://installer.docs.pyansys.com/version/dev/installer.html"
        )
        QtGui.QDesktopServices.openUrl(url)

    def report_issue(self):
        """Access the Ansys Python Manager issues tracker."""
        url = QtCore.QUrl("https://github.com/ansys/python-installer-qt-gui/issues")
        QtGui.QDesktopServices.openUrl(url)

    def show_about_dialog(self):
        """Display the Ansys Python Manager 'About' information."""
        mbox = QtWidgets.QMessageBox.about(self, "About", ABOUT_TEXT)

    def pyansys_dialog(self):
        """Display links to the PyAnsys documentation."""
        mbox = PyAnsysDocsBox(self)
        mbox.exec_()

    def _install_type_changed(self, *args):
        """Handle the installation type change."""
        self.python_version_select.clear()
        if self.installation_type_select.currentText() == "Standard":
            for elem_key, elem_value in VANILLA_PYTHON_VERSIONS.items():
                self.python_version_select.addItem(elem_key, elem_value)

            self.python_version_select.setEnabled(True)
        elif self.installation_type_select.currentText() == "Conda (miniforge)":
            default_index = self.python_version_select.findText("Python 3.10")
            self.python_version_select.setCurrentIndex(default_index)
            self.python_version_select.setEnabled(False)
        elif self.installation_type_select.currentText() == "Astral UV":  
            
            for elem_key, elem_value in UV_PYTHON_VERSIONS.items():

                self.python_version_select.addItem(elem_key, elem_value)      
            default_index = self.python_version_select.findText("Python 3.10 [uv]")
            self.python_version_select.setCurrentIndex(default_index)
            self.python_version_select.setEnabled(True)

    def pbar_increment(self):
        """Increment the progress bar.

        Thread safe.
        """
        self.signal_increment_pbar.emit()

    def _pbar_increment(self):
        """Increment the progress bar.

        Not to be accessed outside of the main thread.
        """
        if self._pbar is not None:
            self._pbar.increment()

    def pbar_open(self, nticks=5, label=""):
        """Open the progress bar.

        Parameters
        ----------
        nticks : int, default: 5
            Number of "ticks" to set the progress bar to.

        label : str, default: ""
            Label of the progress bar.

        """
        self.signal_open_pbar.emit(nticks, label)

    def _pbar_open(self, nticks, label):
        """Open the progress bar.

        Not to be accessed outside of the main thread.
        """
        if self._pbar is None:
            self._pbar = ProgressBar(self, nticks=nticks, label=label)

    def pbar_close(self):
        """Close the progress bar."""
        self.signal_close_pbar.emit()

    def _pbar_close(self):
        """Close the progress bar.

        Not to be accessed outside of the main thread.
        """
        if self._pbar is not None:
            self._pbar.close()
            self._pbar = None

    def pbar_set_value(self, value):
        """Set progress bar position.

        Thread safe.

        Parameters
        ----------
        value : int
            Value to set active progress bar to.

        """
        self.signal_set_pbar_value.emit(value)

    def _pbar_set_value(self, value):
        """Set progress bar position.

        Not to be accessed outside of the main thread.

        Parameters
        ----------
        value : int
            Value to set active progress bar to.

        """
        if self._pbar is not None:
            self._pbar.set_value(value)

    def _show_error(self, text):
        """Display an error.

        Not thread safe. Call ``show_error`` instead for thread safety.

        Parameters
        ----------
        text : str
            Message to display as an error.

        """
        if not isinstance(text, str):
            text = str(text)
        self._err_message_box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Critical, "Error", text, QtWidgets.QMessageBox.Ok
        )
        self._err_message_box.show()

    def show_error(self, text):
        """Thread safe show error.

        This can be called from any thread.

        Parameters
        ----------
        text : str
            Message to display as an error.

        """
        LOG.error(text)
        self.signal_error.emit(text)

    @protected
    def download_and_install(self):
        """Download and install.

        Called when ``self.submit_button.clicked`` is emitted.
        """
        self.setEnabled(False)
        QtWidgets.QApplication.processEvents()

        try:
            if self.installation_type_select.currentData() == "vanilla":
                selected_version = (
                    self.python_version_select.currentData()
                )  # should be major, minor, patch
                # OS based file download
                if is_linux_os():
                    try:
                        return_text = check_python_asset_linux(selected_version)
                        if return_text:
                            LOG.debug("Triggering table widget update")
                            self.installed_table_tab.update_table()
                            self.venv_table_tab.update_table()
                            self.setEnabled(True)
                            return 0
                    except Exception as e:
                        LOG.debug(f"download_and_install {e}")
                    url, filename = get_vanilla_url_and_filename(selected_version)
                else:
                    url = f"https://www.python.org/ftp/python/{selected_version}/python-{selected_version}-amd64.exe"
                    filename = f"python-{selected_version}-amd64.exe"
                LOG.info("Installing vanilla Python %s", selected_version)
            else:
                # OS based file download
                if is_linux_os():
                    LOG.info("Linux")
                    url, filename = get_conda_url_and_filename(CONDA_PYTHON_VERSION)
                else:
                    url = f"https://github.com/conda-forge/miniforge/releases/download/{CONDA_PYTHON_VERSION}/Miniforge3-{CONDA_PYTHON_VERSION}-Windows-x86_64.exe"
                    filename = f"Miniforge3-{CONDA_PYTHON_VERSION}-Windows-x86_64.exe"
                LOG.info("Installing miniconda from %s", url)
            try:
                self._download(url, filename, when_finished=self._run_install_python)
            except Exception as err:
                if os.name == "nt":
                    LOG.warning(
                        "Download using requests library failed... Going to fallback method for Windows."
                    )
                    self._windows_fallback_download(
                        url, filename, when_finished=self._run_install_python
                    )
                else:
                    raise err
        except Exception as e:
            self.show_error(str(e))
            self.setEnabled(True)

    def _download(self, url, filename, when_finished=None, auth=None):
        """Download a file with a progress bar.

        Checks cache first. If cached file exists and is the same size
        as the file to be downloaded, uses cached file.

        ``when_finished`` must accept one parameter, the path of the file downloaded.

        Parameters
        ----------
        url : str
            File to download.

        filename : str
            The basename of the file to download.

        when_finished : callable, optional
            Function to call when complete. Function should accept one
            parameter: the full path of the file downloaded.

        auth : str, optional
            Authorization token for GitHub. This is used when
            downloading release artifacts from private/internal
            repositories.

        """
        request_headers = {"Accept": "application/octet-stream"}
        if auth:
            request_headers["Authorization"] = f"token {auth}"

        # initiate the download
        session = requests.Session()
        response = session.get(
            url,
            allow_redirects=True,
            stream=True,
            headers=request_headers,
            verify=certifi.where(),
        )
        tsize = int(response.headers.get("Content-Length", 0))

        if response.status_code != 200:
            self.show_error(
                f"Unable to download {filename}.\n\nReceived {response.status_code} from {url}"
            )
            self.pbar_close()
            return

        output_path = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(output_path) and tsize:
            LOG.debug("%s exists at in %s", filename, CACHE_DIR)
            file_sz = os.path.getsize(output_path)
            if tsize == file_sz:
                LOG.debug("Sizes match. Using cached file from %s", output_path)
                if when_finished is not None:
                    when_finished(output_path)
                return

            LOG.debug("Sizes do not match. Ignoring cached file.")

        # size and current_bytes, current bar position
        total = [None, 0, 0]

        def update(b=1, bsize=1, tsize=None):
            """Update download progress."""
            if tsize:
                total[0] = tsize
            total[1] += bsize
            if total[0] is not None:
                val = floor(100 * total[1] / total[0])
                if total[2] != val:
                    self.pbar_set_value(val)

        self.pbar_open(100, f"Downloading {filename}")

        chunk_size = 200 * 1024  # 200kb
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size):
                f.write(chunk)
                update(0, chunk_size, tsize)
                tsize = None

        self.pbar_close()

        if when_finished is not None:
            when_finished(output_path)

    def _windows_fallback_download(self, url, filename, when_finished=None):
        """Download a file. Fallback method for Windows.

        Deletes any pre-existing output file with the same name. Then, performs
        the download using PowerShell and the Invoke-RestMethod command.

        ``when_finished`` must accept one parameter, the path of the file downloaded.

        Parameters
        ----------
        url : str
            File to download.
        filename : str
            The basename of the file to download.
        when_finished : callable, optional
            Function to call when complete. Function should accept one
            parameter: the full path of the file downloaded.
        """
        # Delete pre-existing cache. This is fail-safe mode
        output_path = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(output_path):
            os.remove(output_path)

        # Perform download using Invoke-RestMethod
        out, error_code = run_ps(
            f"Invoke-RestMethod '{url}' -Method 'GET' -OutFile '{output_path}'"
        )

        if error_code:
            LOG.error(
                f"Error while downloading Python on Windows fail-safe mode: {out}"
            )
            msg = QtWidgets.QMessageBox()
            msg.warning(
                self,
                "Error while downloading Python on Windows fail-safe mode!",
                f"Error message:\n\n {out}",
            )
            self.setEnabled(True)
            return

        if when_finished is not None:
            when_finished(output_path)

    def _run_install_python(self, filename):
        """Execute the installation process."""
        LOG.debug("Executing run_install_python")
        out, error_code = install_python(filename)

        if error_code:
            LOG.error(f"Error while installing Python: {out}")
            msg = QtWidgets.QMessageBox()
            msg.warning(
                self,
                "Error while installing Python!",
                f"Error message:\n\n {out}",
            )

        LOG.debug("Triggering table widget update")
        self.installed_table_tab.update_table()
        self.venv_table_tab.update_table()

        self.setEnabled(True)


def __restore_windows_dll_load():
    """Restore DLL loading on Windows.

    Notes
    -----
    PyInstaller on Windows may break DLL loading.
    This function restores the DLL loading on Windows.
    """
    import sys

    LOG.debug(f"sys.platform: {sys.platform}")
    if sys.platform == "win32":
        LOG.debug("Restoring DLL loading on Windows...")
        import ctypes

        ctypes.windll.kernel32.SetDllDirectoryA(None)


def open_gui():
    """Start the installer as a QT Application."""
    import argparse
    import ctypes

    # Enable logging early
    enable_logging()

    if os.name == "nt":
        import msvcrt

        # Restore DLL loading on Windows...
        __restore_windows_dll_load()

        kernel32 = ctypes.windll.kernel32

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--console", action="store_true", help="Open console window")
    try:
        args = parser.parse_args()
    except AttributeError:
        kernel32.AllocConsole()

        # Redirect stdout and stderr to the console
        sys.stdout = open("CONOUT$", "w")
        sys.stderr = open("CONOUT$", "w")

        try:
            args = parser.parse_args()
        except SystemExit:
            print("\nPress any key to continue...")
            msvcrt.getch()
            return

    # Allocate console if --console option is specified
    if args.console:
        kernel32.AllocConsole()

        # Redirect stdout and stderr to the console
        sys.stdout = open("CONOUT$", "w")
        sys.stderr = open("CONOUT$", "w")

    app = QtWidgets.QApplication(sys.argv)
    window = AnsysPythonInstaller()

    LOG.debug("Showing window...")
    window.show()
    sys.exit(app.exec())
