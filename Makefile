DAGU ?= dagu
DAGU_FLAGS ?=
WORKFLOWS := $(sort $(wildcard workflows/*.yaml workflows/*.yml))

.PHONY: validate

validate:
	@status=0; \
	for workflow in $(WORKFLOWS); do \
		printf '\nValidating %s\n' "$$workflow"; \
		$(DAGU) validate $(DAGU_FLAGS) "$$workflow" || status=1; \
	done; \
	exit $$status
