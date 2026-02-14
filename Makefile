VENV_NAME = .venv
PYTHON = $(VENV_NAME)/bin/python3
PIP = $(PYTHON) -m pip
REQ_FILE = requirements.txt

.PHONY: all install run debug clean lint lint-strict

all: install run

$(VENV_NAME):
	python3 -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip

install: $(VENV_NAME)
	$(PIP) install -r $(REQ_FILE)
	$(PIP) install flake8 mypy pytest
	@touch $(VENV_NAME)

run: $(VENV_NAME)
	$(PYTHON) fly-in.py

debug: $(VENV_NAME)
	$(PYTHON) -m pdb fly-in.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache $(VENV_NAME)

lint: $(VENV_NAME)
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: $(VENV_NAME)
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict