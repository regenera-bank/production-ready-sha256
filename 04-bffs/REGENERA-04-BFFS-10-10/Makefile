SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c

.PHONY: clean validate test security build verify-release all

clean:
	rm -rf dist evidence/*.tmp evidence/RELEASE-VERIFICATION.json

validate:
	python3 tools/validate.py

test:
	python3 tools/run_tests.py

security:
	python3 tools/security_scan.py

build:
	python3 tools/build.py

verify-release:
	python3 tools/verify_release.py

all: clean validate test security build verify-release
