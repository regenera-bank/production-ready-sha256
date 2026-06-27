.PHONY: clean validate test security build verify-release all
export PYTHONDONTWRITEBYTECODE=1
clean:
	python3 tools/clean.py
validate:
	python3 tools/validate.py
test:
	PYTHONPATH=src python3 tools/run_tests.py
security:
	python3 tools/security_scan.py
build:
	python3 tools/build.py
verify-release:
	python3 tools/verify_release.py
all: clean validate test security build verify-release
