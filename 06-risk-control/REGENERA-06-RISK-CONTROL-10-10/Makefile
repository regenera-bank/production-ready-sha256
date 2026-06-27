SHELL := /bin/bash
PYTHON := python3 -B

.PHONY: clean validate test security build verify-release all

clean:
	@rm -rf build dist
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@find . -type f \( -name '*.pyc' -o -name '.DS_Store' \) -delete

validate:
	@PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/validate.py

test:
	@PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/run_tests.py

security:
	@PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/security_scan.py

build:
	@PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/build_evidence.py

verify-release:
	@PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/verify_release.py

all: clean validate test security build verify-release
