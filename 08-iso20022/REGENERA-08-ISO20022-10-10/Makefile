SHELL := /bin/sh
PYTHON ?= python3

.PHONY: all clean validate test security build verify-release

all: clean validate test security build verify-release

clean:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/clean.py

validate:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/validate_repo.py

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/run_tests.py

security:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/security_scan.py

build:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/build_release.py

verify-release:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) tools/verify_release.py
