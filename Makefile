# Simple developer commands

.PHONY: help install dev-install test typecheck lint format check release-notes

PYTHON ?= python3
SRC := src/newyearscards
TESTS := tests

help:
	@echo "Available targets:"
	@echo "  install         Install runtime deps (editable)"
	@echo "  dev-install     Install dev deps (pytest, mypy)"
	@echo "  test            Run test suite"
	@echo "  typecheck       Run mypy on source"
	@echo "  lint            Run Ruff if available (optional)"
	@echo "  format          Run Ruff formatter if available (optional)"
	@echo "  check           Lint + typecheck + tests"
	@echo "  release-notes   Generate release notes from CHANGELOG (VERSION=...)"
	@echo "  run-download    Run CLI download without install (YEAR=YYYY)"
	@echo "  run-build       Run CLI build-labels without install (YEAR=YYYY)"

install:
	pip install -e .

dev-install:
	pip install -e .[dev]

test:
	pytest -q

coverage:
	@# If pytest-cov is installed in current env, use it; otherwise, try uv with dev extra.
	@if $(PYTHON) -c "import pytest_cov" >/dev/null 2>&1; then \
		pytest --cov=$(SRC) --cov-report=term-missing -q; \
	elif command -v uv >/dev/null 2>&1; then \
		echo "pytest-cov not in current env; running via 'uv run --extra dev'..."; \
		uv run --extra dev pytest --cov=$(SRC) --cov-report=term-missing -q; \
	else \
		echo "pytest-cov not installed. Install dev extras first:"; \
		echo "  pip install -e .[dev]"; \
		echo "  or: uv pip install -e .[dev]"; \
		exit 2; \
	fi

typecheck:
	mypy $(SRC)

lint:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check $(SRC) $(TESTS); \
	else \
		echo "ruff not installed; install with 'pip install ruff' or 'uv pip install ruff'"; \
		echo "skipping lint"; \
	fi

format:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format $(SRC) $(TESTS); \
	else \
		echo "ruff not installed; install with 'pip install ruff' or 'uv pip install ruff'"; \
		echo "skipping format"; \
	fi

check:
	@echo "==> Ruff lint"
	@$(MAKE) --no-print-directory lint
	@echo
	@echo "==> Mypy typecheck"
	@$(MAKE) --no-print-directory typecheck
	@echo
	@echo "==> Pytest"
	@$(MAKE) --no-print-directory test

release-notes:
	@[ -n "$(VERSION)" ] || (echo "Error: VERSION is required, e.g. make release-notes VERSION=0.2.1"; exit 1)
	$(PYTHON) scripts/generate_release_notes.py --version $(VERSION) --out release_notes.md
	@echo "Wrote release_notes.md for v$(VERSION)"

run-download:
	@[ -n "$(YEAR)" ] || (echo "Error: YEAR is required, e.g. make run-download YEAR=2025"; exit 1)
	PYTHONPATH=src $(PYTHON) -m newyearscards.cli download --year $(YEAR) $(ARGS)

run-build:
	@[ -n "$(YEAR)" ] || (echo "Error: YEAR is required, e.g. make run-build YEAR=2025"; exit 1)
	PYTHONPATH=src $(PYTHON) -m newyearscards.cli build-labels --year $(YEAR) $(ARGS)
