VENV_NAME = .venv
PYTHON = $(VENV_NAME)/bin/python3
PIP = $(PYTHON) -m pip
REQ_FILE = requirements.txt

all: install

$(VENV_NAME):
	python3 -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip

install: $(VENV_NAME)
	$(PIP) install -r $(REQ_FILE)
	$(PIP) install flake8 mypy pytest
	@touch $(VENV_NAME)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf $(VENV_NAME)

.PHONY: all install clean