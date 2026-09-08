.PHONY: install install-dev install-global clean

install:
	@echo "Installing in virtual env ..."
	pip install .

install-dev:
	@echo "Installing in developer mode..."
	pip install -e .

install-global: install
	@echo "creating symlink in /usr/local/bin for global access..."
	sudo ln -sf $$(which cmatch) /usr/local/bin/cmatch
	@echo "Done! You can use 'cmatch' from any path."

clean:
	@echo "Cleaning temporary files..."
	rm -rf build/ dist/ *.egg-info/ __pycache__/ cmatch/__pycache__/
