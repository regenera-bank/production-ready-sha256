export PYTHONDONTWRITEBYTECODE := 1
PYTHON ?= python3

.PHONY: doctor validate test security build verify-release all clean

doctor:
	@$(PYTHON) tools/doctor.py

validate: doctor
	@$(PYTHON) tools/validate.py

test: doctor
	@$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

security: doctor
	@$(PYTHON) tools/security_scan.py

build: doctor
	@$(PYTHON) tools/build.py

verify-release: doctor
	@$(PYTHON) tools/verify_release.py

all: validate test security build verify-release

clean:
	@$(PYTHON) tools/clean.py
