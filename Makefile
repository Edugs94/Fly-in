VENV_NAME = .venv

PYTHON = $(VENV_NAME)/bin/python3
PIP = $(VENV_NAME)/bin/pip

MAIN_FILE = main.py
CONFIG_FILE = maps/easy/03_basic_capacity.txt
REQ_FILE = requirements.txt

all: install run

install: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: $(REQ_FILE)
	@echo "Creating virtual environment and installing required dependencies..."
	python3 -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQ_FILE)
	$(PIP) install flake8
	$(PIP) install mypy
	$(PIP) install pytest
	touch $(VENV_NAME)/bin/activate

run: install
	@echo "Running simulation..."
	$(PYTHON) $(MAIN_FILE) $(CONFIG_FILE)

debug: install
	@echo "Debugging..."
	$(PYTHON) -m pdb $(MAIN_FILE) $(CONFIG_FILE)

test: install
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/

lint: install
	@echo "Linting..."
	@echo "Flake8: "
	$(PYTHON) -m flake8 $(MAIN_FILE) src
	@echo "Mypy: "
	$(PYTHON) -m mypy $(MAIN_FILE) src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	@echo "Linting strictly..."
	@echo "Flake8: "
	$(PYTHON) -m flake8 $(MAIN_FILE) src
	@echo "Mypy: "
	$(PYTHON) -m mypy $(MAIN_FILE) src --strict

clean:
	@echo "Cleaning temporary and cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf outputs/
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf $(VENV_NAME)

.PHONY: all run clean lint test debug