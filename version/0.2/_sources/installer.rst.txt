Usage instructions
##################

Installing the ``Ansys Python Manager``
=======================================

First step is installing the ``Ansys Python Manager``. In order to do so, follow the next steps.

#. Download the necessary installer from the `latest available release <https://github.com/ansys/python-installer-qt-gui/releases/latest>`_.
   The file should be named ``Ansys-Python-Manager-Setup-v*.exe``.

#. Execute the installer.

#. Search for the ``Ansys Python Manager`` and run it.

The ``Ansys Python Manager`` window should appear at this stage.

Installing Python on Windows
============================

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

* Python 3.8
* Python 3.9
* Python 3.10
* Python 3.11
* Python 3.12

.. warning::

  In the case of having selected ``Conda (miniforge)``, only Python 3.10 is available.


Managing Python environments
============================

Through the ``Ansys Python Manager``, users can also have access to their different Python
installations. Have a look at how to access it here:

#. Search for the ``Ansys Python Manager`` and run it.

#. Access the ``Manage Python Environments`` tab.

#. Select your desired ``Python`` environment and start one of the listed options.


On the ``Launching options`` section, the following options are available:

* ``Launch Console``: this option starts a console window with the command ``python`` pointing
  towards your selected Python environment.
* ``Launch JupyterLab``: this option starts a ``JupyterLab`` session. If ``JupyterLab`` is
  not installed, then the ``Ansys Python Manager`` installs it for you.
* ``Launch Jupyter Notebook``: this option starts a ``Jupyter Notebook`` session. If
  ``Jupyter Notebook`` is not installed, then the ``Ansys Python Manager`` installs it for you.
* ``Launch Spyder``: this option starts a Spyder IDE session. If Spyder is not installed,
  then the ``Ansys Python Manager`` installs it for you.

On the ``Package management`` section, the following options are available:

* ``Install Python default packages``: by selecting this option, your selected Python install
  receives the latest compatible versions for ``numpy``, ``scipy``, ``pandas``, ``matplotlib``
  and  ``scikit-learn``.
* ``Install PyAnsys``: by selecting this option, your selected Python install has access to
  the latest, compatible PyAnsys metapackage installation. This metapackage provides you with
  access to the latest public PyAnsys libraries in their compatible version with the latest
  Ansys products.
* ``List installed packages``: by selecting this option, a list of the installed packages on
  your selected Python install is provided. This might be useful for identifying potential problems.
