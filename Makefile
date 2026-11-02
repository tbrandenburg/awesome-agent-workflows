PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
RUFF ?= $(if $(wildcard .venv/bin/ruff),.venv/bin/ruff,ruff)
YAMLLINT ?= $(if $(wildcard .venv/bin/yamllint),.venv/bin/yamllint,yamllint)
PRETTIER ?= node_modules/.bin/prettier

.PHONY: install format format-check lint validate clean

install:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install -r requirements-dev.txt
	npm ci

format:
	$(PRETTIER) --write .
	$(RUFF) format scripts

format-check:
	$(PRETTIER) --check .
	$(RUFF) format --check scripts

lint: format-check
	$(YAMLLINT) --strict workflows .github/workflows .prettierrc.yaml .yamllint.yaml
	$(RUFF) check scripts
	$(PYTHON) scripts/lint_embedded.py --ruff "$(RUFF)" workflows/*.yaml .github/workflows/*.yml
	@command -v shellcheck
	actionlint

validate: lint
	@for file in workflows/*.yaml; do dagu validate "$$file" || exit 1; done

clean:
	rm -rf .ruff_cache
