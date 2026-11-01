PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
RUFF ?= $(if $(wildcard .venv/bin/ruff),.venv/bin/ruff,ruff)

.PHONY: install test lint validate clean

install:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install -r requirements-dev.txt
	@printf 'Local environment installed; subsequent make commands use .venv automatically.\n'

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

lint:
	$(RUFF) check tests
	$(RUFF) format --check tests

validate: test lint
	@for file in workflows/*.yaml; do dagu validate "$$file" || exit 1; done

clean:
	rm -rf workspace/tmp .ruff_cache .pytest_cache
