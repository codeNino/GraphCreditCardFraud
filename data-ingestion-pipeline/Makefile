# Makefile

# The name of the virtual environment
VENV_NAME := ingestenv

# The desired Python version (e.g., Python 3.8)
PYTHON_VERSION := 3.8.10

.PHONY: setup run clean

# Set up the virtual environment and install dependencies
setup: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: requirements.txt
	pip install --upgrade pip
	pip install virtualenv
	virtualenv -p python$(PYTHON_VERSION) $(VENV_NAME)
	$(VENV_NAME)/bin/pip install -r requirements.txt
	touch $(VENV_NAME)/bin/activate

# Run the Python script using the virtual environment
run: setup
	$(VENV_NAME)/bin/python pipeline.py

# Clean up the virtual environment
clean:
	rm -rf $(VENV_NAME)
