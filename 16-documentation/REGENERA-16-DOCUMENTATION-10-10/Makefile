PYTHON ?= python3 -B

.PHONY: clean validate test security build evidence verify-release all

clean:
	@$(PYTHON) tools/clean.py
validate:
	@$(PYTHON) tools/validate.py

test:
	@$(PYTHON) tools/run_tests.py

security:
	@$(PYTHON) tools/security_scan.py

build:
	@$(PYTHON) tools/build.py

evidence:
	@$(PYTHON) tools/evidence.py

verify-release:
	@$(PYTHON) tools/verify_release.py

all: clean validate test security build evidence verify-release
