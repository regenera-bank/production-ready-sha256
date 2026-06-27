SHELL := /usr/bin/env bash
PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: clean validate test security continuity build verify-release all

clean:
	@$(PYTHON) scripts/governance.py clean --out dist

validate:
	@$(PYTHON) scripts/governance.py validate

test:
	@$(PYTHON) -B -m unittest discover -s tests -p 'test_*.py' -v

security:
	@$(PYTHON) scripts/governance.py security

continuity:
	@$(PYTHON) -B -c "import sys,json;sys.path.insert(0,'reference-models');from continuity_model import restore_exercise;print(json.dumps(restore_exercise(b'regenera-dr-proof\n'*1000),indent=2))"

build: validate test security
	@$(PYTHON) scripts/governance.py build --out dist

verify-release:
	@$(PYTHON) scripts/governance.py verify-release --out dist

all: clean validate test security continuity build verify-release
