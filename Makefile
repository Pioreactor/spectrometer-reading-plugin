.PHONY: test test-file

VENV_PYTHON := .venv/bin/python
PYTEST := $(VENV_PYTHON) -m pytest

# Run all tests using this repo's venv Python.
test:
	$(PYTEST) -q

# Run a specific test path: make test-file TEST=tests/test_spectrometer_reading.py
test-file:
	@if [ -z "$(TEST)" ]; then \
		echo "Usage: make test-file TEST=<path-or-nodeid>"; \
		exit 2; \
	fi
	$(PYTEST) -q $(TEST)
