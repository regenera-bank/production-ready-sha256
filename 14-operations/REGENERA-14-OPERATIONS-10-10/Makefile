.PHONY: all clean validate test security build verify

all:
	python3 tools/clean.py
	python3 tools/validate.py
	python3 tools/test_runner.py
	python3 tools/security_scan.py
	python3 tools/clean.py
	python3 tools/build.py
	python3 tools/verify_release.py
	python3 tools/clean.py

clean:
	python3 tools/clean.py

validate:
	python3 tools/validate.py

test:
	python3 tools/test_runner.py

security:
	python3 tools/security_scan.py

build:
	python3 tools/build.py

verify:
	python3 tools/verify_release.py
