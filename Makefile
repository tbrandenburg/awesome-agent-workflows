DAGU ?= dagu
DAGU_FLAGS ?=
WORKFLOW ?= workflows/latest-issue-resolution.yml
WORKFLOWS := $(sort $(wildcard workflows/*.yaml workflows/*.yml))

.PHONY: run validate

run:
	$(DAGU) start $(DAGU_FLAGS) "$(WORKFLOW)"

validate:
	@status=0; \
	for workflow in $(WORKFLOWS); do \
		printf '\nValidating %s\n' "$$workflow"; \
		$(DAGU) validate $(DAGU_FLAGS) "$$workflow" || status=1; \
	done; \
	exit $$status
