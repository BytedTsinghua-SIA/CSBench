PYTHON ?= python3
TASK ?= cs000280
JOB ?= jobs

.PHONY: setup generate smoke smoke-agent harbor-run original-run summarize test

setup:
	scripts/bootstrap.sh

generate:
	.venv/bin/python scripts/generate_dataset.py --overwrite

smoke:
	SMOKE_TASK="$(TASK)" SMOKE_AGENT=nop scripts/smoke_test.sh

smoke-agent:
	SMOKE_TASK="$(TASK)" SMOKE_AGENT=codeact scripts/smoke_test.sh

harbor-run:
	scripts/run_harbor.sh

original-run:
	$(PYTHON) main.py

summarize:
	$(PYTHON) scripts/summarize_harbor_results.py "$(JOB)"

test:
	.venv/bin/python -m pytest tests
