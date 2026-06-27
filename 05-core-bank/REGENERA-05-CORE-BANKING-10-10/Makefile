SHELL := /bin/sh
PYTHON := python3 -B

.PHONY: clean validate test security build verify-release all

clean:
	$(PYTHON) tools/clean.py

validate:
	$(PYTHON) tools/validate.py

test:
	$(PYTHON) tools/run_tests.py

security:
	$(PYTHON) tools/security_scan.py

build:
	$(PYTHON) tools/build.py
	$(PYTHON) tools/finalize_evidence.py

verify-release:
	$(PYTHON) tools/verify_release.py

all: clean validate test security build verify-release
