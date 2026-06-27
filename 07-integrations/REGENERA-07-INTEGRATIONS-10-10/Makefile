SHELL := /bin/bash
PYTHON ?= python3

.PHONY: clean validate test security build verify-release all

clean:
	@rm -rf dist .build-tmp
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@find . -type f -name '*.pyc' -delete

validate:
	@$(PYTHON) scripts/validate.py

test:
	@$(PYTHON) scripts/run_tests.py

security:
	@$(PYTHON) scripts/security_scan.py

build: validate test security
	@$(PYTHON) scripts/build_release.py

verify-release:
	@$(PYTHON) scripts/verify_release.py

all: clean validate test security build verify-release
