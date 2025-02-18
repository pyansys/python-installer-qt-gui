# Simple makefile to simplify repetitive build env management tasks under posix
.PHONY: setup install tests doc build clean fresh-build

setup:
	@echo "Installing uv..."
	pip install -U pip uv

install: setup
	@echo "Installing..."
	uv pip install -e .[freeze]
	@echo "Installation complete."

tests: setup
	@echo "Installing test dependencies..."
	uv pip install -e .[tests]
	@echo "Running tests..."
	uv run pytest
	@echo "Tests complete."

doc: setup
	@echo "Installing documentation dependencies..."
	uv pip install -e .[doc]
	@echo "Building documentation..."
	cd doc && make clean && make html && cd ..
	@echo "Documentation complete."

build: setup
	@echo "Freezing using pyinstaller"
	uv run pyinstaller frozen.spec

clean:
	@echo "Cleaning up build files..."
	rm -rf build dist

fresh-build: clean build
