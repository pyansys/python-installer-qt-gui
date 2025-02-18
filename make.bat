@ECHO OFF

pushd %~dp0

REM Simple make.bat to simplify repetitive build env management tasks under Windows

if "%1" == "install" goto install
if "%1" == "tests" goto tests
if "%1" == "doc" goto doc
if "%1" == "build" goto build
if "%1" == "clean" goto clean
if "%1" == "fresh-build" goto fresh-build

:setup
Echo ^>^>^> Setting up environment...
pip install -U pip uv
goto :eof

:install
call :setup
Echo ^>^>^> Installing...
uv pip install -e .[freeze]
Echo ^>^>^> Installation complete.
goto end

:tests
call :setup
Echo ^>^>^> Installing test dependencies...
uv pip install -e .[tests]
Echo ^>^>^> Running tests...
uv run pytest
goto end

:doc
call :setup
Echo ^>^>^> Installing documentation dependencies...
uv pip install -e .[doc]
Echo ^>^>^> Building documentation...
chdir /d doc
call make.bat clean
call make.bat html
chdir /d ..
Echo ^>^>^> Documentation complete.
goto end

:build
call :setup
Echo ^>^>^> Freezing using pyinstaller
uv run pyinstaller frozen.spec
goto end

:clean
Echo ^>^>^> Cleaning up build files...
rmdir /s /q build > /NUL 2>&1
rmdir /s /q dist > /NUL 2>&1
goto end

:fresh-build
call :clean
call :build
goto end

:end
popd
