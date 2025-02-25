Usage instructions
##################

Installing the ``Ansys Python Manager``
=======================================

.. tab-set::

  .. tab-item:: Windows

    First step is installing the ``Ansys Python Manager``. In order to do so, follow the next steps.

    #. Download the necessary installer from the `latest available release <https://github.com/ansys/python-installer-qt-gui/releases/latest>`_.
       The file should be named ``Ansys-Python-Manager-Setup-v*.exe``.

    #. Execute the installer.

    #. Search for the ``Ansys Python Manager`` and run it.

    The ``Ansys Python Manager`` window should appear at this stage.

  .. tab-item:: Linux

    .. tab-set::

      .. tab-item:: Ubuntu

        Prerequisites:

        #. **OS** supported for **Ubuntu(20.04 and 22.04)**.

        #. Update ``apt-get`` repository and install the following packages with **sudo** privileges:
           **wget, gnome, libffi-dev, libssl-dev, libsqlite3-dev, libxcb-xinerama0 and build-essential** packages with **sudo** privileges

           .. code:: shell

             sudo apt-get update -y
             sudo apt-get install wget gnome libffi-dev libssl-dev libsqlite3-dev libxcb-xinerama0 build-essential -y

        #. Install **zlib** package

           .. code:: shell

             wget https://zlib.net/current/zlib.tar.gz
             tar xvzf zlib.tar.gz
             cd zlib-*
             make clean
             ./configure
             make
             sudo make install

        To install the ``Ansys Python Manager``, follow below steps.

        #. Download the necessary installer from the `latest available release <https://github.com/ansys/python-installer-qt-gui/releases/latest>`_.
           The file should be named ``Ansys-Python-Manager_*.zip``.

        #. Execute the below command on the terminal

           .. code:: shell

             unzip Ansys-Python-Manager_*.zip
             ./installer.sh

        #. Search for the ``Ansys Python Manager`` and run it.

        The ``Ansys Python Manager`` window should appear at this stage.

        To uninstall the ``Ansys Python Manager``, follow below steps.

        #. Go to File menu. Click Uninstall option.

        #. In the pop up window:

           * If you want to remove all virtual environments which were created by
             the Ansys Python Manager as part of uninstallation, mark
             ``Delete virtual environments`` checkbox

           * If you want to remove all configurations as part of
             uninstallation, mark ``Delete configurations`` checkbox

           * If you want to remove all Python installations which were installed by
             the Ansys Python Manager as part of uninstallation, mark
             ``Delete Python installations`` checkbox

        #. Click ``Uninstall`` button.


      .. tab-item:: CentOS9, RHEL9

        Prerequisites:

        #. **OS** supported for **CentOS9** and **RHEL9**.

        #. Update ``yum`` repository and install the following packages with **sudo** privileges:
           **wget, gnome-terminal, Development Tools, libffi-devel, openssl-devel, rpm-build, sqlite-devel, sqlite-libs, libXinerama-devel, coreutils**

           .. code:: shell

             sudo yum update -y;
             sudo yum groupinstall 'Development Tools' -y;
             sudo yum install wget gnome-terminal libffi-devel openssl-devel rpm-build sqlite-devel sqlite-libs libXinerama-devel coreutils -y;

        #. Install **zlib** package using **wget**

           .. code:: shell

             sudo yum install wget -y
             wget https://zlib.net/current/zlib.tar.gz
             tar xvzf zlib.tar.gz
             cd zlib-*
             make clean
             ./configure
             make
             sudo make install

        To install the ``Ansys Python Manager``, follow below steps.

        #. Download the necessary installer from the `latest available release <https://github.com/ansys/python-installer-qt-gui/releases/latest>`_.
           The file should be named ``Ansys-Python-Manager_linux_centos_*.zip``.

        #. Execute the below command on the terminal

           .. code:: shell

             unzip Ansys-Python-Manager_linux_centos_*.zip
             ./installer_CentOS.sh

        #. Search for the ``Ansys Python Manager`` and run it.

        The ``Ansys Python Manager`` window should appear at this stage.

        To uninstall the ``Ansys Python Manager``, follow below steps.

        #. Go to File menu. Click Uninstall option.

        #. In the pop up window:

           * If you want to remove all virtual environments which were created by
             the Ansys Python Manager as part of uninstallation, mark
             ``Delete virtual environments`` checkbox

           * If you want to remove all configurations as part of
             uninstallation, mark ``Delete configurations`` checkbox

           * If you want to remove all Python installations which were installed by
             the Ansys Python Manager as part of uninstallation, mark
             ``Delete Python installations`` checkbox

        #. Click ``Uninstall`` button.

        #. Follow the uninstaller script & provide sudo permission to uninstall the application.

      .. tab-item:: Fedora39

        Prerequisites:

        #. **OS** supported for **Fedora39**.

        #. Update ``yum`` repository and install the following packages with **sudo** privileges:
           **wget, gnome-terminal, Development Tools, libffi-devel, openssl-devel, rpm-build, sqlite-devel, sqlite-libs, libXinerama-devel, coreutils**

           .. code:: shell

             sudo yum update -y;
             sudo yum groupinstall 'Development Tools' -y;
             sudo yum install wget gnome-terminal libffi-devel openssl-devel rpm-build sqlite-devel sqlite-libs libXinerama-devel coreutils -y;

        #. Install **zlib** package using **wget**

           .. code:: shell

             sudo yum install wget -y
             wget https://zlib.net/current/zlib.tar.gz
             tar xvzf zlib.tar.gz
             cd zlib-*
             make clean
             ./configure
             make
             sudo make install

        To install the ``Ansys Python Manager``, follow below steps.

        #. Download the necessary installer from the `latest available release <https://github.com/ansys/python-installer-qt-gui/releases/latest>`_.
           The file should be named ``Ansys-Python-Manager_linux_fedora_*.zip``.

        #. Execute the below command on the terminal

           .. code:: shell

             unzip Ansys-Python-Manager_linux_fedora_*.zip
             ./installer_Fedora.sh

        #. Search for the ``Ansys Python Manager`` and run it.

        The ``Ansys Python Manager`` window should appear at this stage.

        To uninstall the ``Ansys Python Manager``, follow below steps.

        #. Go to File menu. Click Uninstall option.

        #. In the pop up window:

           * If you want to remove all virtual environments which were created by
             the Ansys Python Manager as part of uninstallation, mark
             ``Delete virtual environments`` checkbox

           * If you want to remove all configurations as part of
             uninstallation, mark ``Delete configurations`` checkbox

           * If you want to remove all Python installations which were installed by
             the Ansys Python Manager as part of uninstallation, mark
             ``Delete Python installations`` checkbox

        #. Click ``Uninstall`` button.

        #. Follow the uninstaller script & provide sudo permission to uninstall the application.


Installing Python
=================

Now, instructions on how to install Python from the ``Ansys Python Manager`` are provided.

In order to do so, just follow the upcoming steps:

#. Search for the ``Ansys Python Manager`` and run it.

#. Go to the ``Install Python`` tab, and select your desired Python install, version and extra packages.

#. And follow the install process.


Configurable options for the installer
--------------------------------------

Two Python options for installation are available:

* ``Standard``: this mode installs the standard Python version from `python.org <https://www.python.org/>`_
* ``Conda (miniforge)``: this mode installs the Python version from `miniforge <https://github.com/conda-forge/miniforge>`_.
  This install is characterized for being a modified ``conda`` install in which you have access to the ``conda``
  package manager through the ``conda-forge`` channel.

Regarding the available Python versions, users can select among the following ones:

* Python 3.10
* Python 3.11
* Python 3.12

.. collapse:: Linux : Python installation

    1. Conda python installation:

      #. Bash scripts will be downloaded and executed on a machine directly from the official website.(https://github.com/conda-forge/miniforge?tab=readme-ov-file).

    2. Standard python installation happens in two ways:

      #. If the Debian version is 22.04 and Python 3.11 (recommended by Ansys) is specified, the installer will
         automatically install the pre-compiled version of Python available within the installer.

      #. Otherwise, Python will be installed following these steps:

        #. Download Python Tarball and Untar:

          i. The Python tar file will be downloaded from the Python FTP server (https://www.python.org/ftp/python)
             based on the version selected from the dropdown menu. Example: For Python version 3.12.0, the download link
             would be here(https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tar.xz).

          ii.  Decompress the downloaded file in the user’s cache directory.

        * Configure the Source:

          i. Following will be executed configure the installation:

            .. code:: shell

              ./configure --prefix=~/.local/ansys/{python_folder_name}

        * Build and install Python:

          i. Build and install Python using the make and make install commands.


.. warning::

  In the case of having selected ``Conda (miniforge)``, only Python 3.10 is available.

Create Python virtual environment
=================================

#. Search for the ``Ansys Python Manager`` and run it.

#. Access the ``Create Python Environments`` tab.

#. Select your desired ``Python version`` from the listed options.

#. Provide the name of the virtual environment in the ``Enter virtual environment name`` text box.

#. Finally, Click ``Create`` button to create.

By default, Ansys Python Manager create virtual environment under,

* ``{user directory}/.ansys_python_venvs`` for Windows
* ``{user directory}/.local/ansys/.ansys_python_venvs`` for Linux

To configure the default virtual environment creation path, go to the ``File >> Configure`` section
``(Ctrl + D)`` and provide your preferred path under the first text box. Then, click the ``Save`` button.


Managing Python environments
============================

Through the ``Ansys Python Manager``, users can also have access to their different Python
installations. Have a look at how to access it here:

#. Search for the ``Ansys Python Manager`` and run it.
#. Access the ``Manage Python Environments`` tab.
#. Select your desired ``Python`` environment and start one of the listed options.

By default, Ansys Python Manager list python environments available under,

* ``{user directory}/.ansys_python_venvs`` for Windows
* ``{user directory}/.local/ansys/.ansys_python_venvs`` for Linux

To manage this directory, go to the ``File >> Configure`` section ``(Ctrl + D)`` and make the appropriate changes.

#. To add a new default directory path, provide the path in the corresponding text box.
#. To add a new path where virtual environments are searched for, provide the path in the corresponding text box and click the ``Add`` button.
#. To remove directory path select the respective path that you want remove from the dropdown and click the ``Remove`` button.
#. Finally, click the ``Save`` button to save the configurations.

On the ``Launching options`` section, the following options are available:

* ``Launch Console``: this option starts a console window with the command ``python`` pointing
  towards your selected Python environment.
* ``Launch VSCode``: this option starts a ``Visual Studio Code``. If ``Visual Studio Code`` is
  not installed, then the ``Ansys Python Manager`` provides instructions to install it.
* ``Launch JupyterLab``: this option starts a ``JupyterLab`` session. If ``JupyterLab`` is
  not installed, then the ``Ansys Python Manager`` installs it for you.
* ``Launch Jupyter Notebook``: this option starts a ``Jupyter Notebook`` session. If
  ``Jupyter Notebook`` is not installed, then the ``Ansys Python Manager`` installs it for you.
* ``Launch Spyder``: this option starts a Spyder IDE session. If Spyder is not installed,
  then the ``Ansys Python Manager`` installs it for you.

On the ``Package management`` section, the following options are available:

* ``Install Python default packages``: by selecting this option, your selected Python install
  receives the latest compatible versions for ``numpy``, ``scipy``, ``pandas``, ``matplotlib``, ``pyvista``,
  and  ``scikit-learn``.
* ``Install PyAnsys``: by selecting this option, your selected Python install has access to
  the latest, compatible PyAnsys metapackage installation. This metapackage provides you with
  access to the latest public PyAnsys libraries in their compatible version with the latest
  Ansys products.
* ``List installed packages``: by selecting this option, a list of the installed packages on
  your selected Python install is provided. This might be useful for identifying potential problems.
