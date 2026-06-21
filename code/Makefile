# EJOR reproduction entry points.
PY=python3
CFG?=configs/ejor_pilot.yaml      # use configs/ejor_final.yaml for full scale

.PHONY: reproduce_all protocol paper clean test smoke manuscript-check

test:
	python -m pytest -q

smoke:
	python run_protocol.py --config configs/_smoke.yaml --stage all

manuscript-check:
	$(PY) scripts/check_manuscript_numbers.py \
		--paper ../paper --results ../results/protocol

## Regenerate the original manuscript experiments + the full validation protocol
reproduce_all: protocol
	$(PY) run_all.py

## Run the EJOR validation protocol (all stages) from the frozen config
protocol:
	$(PY) run_protocol.py --config $(CFG) --stage all
	$(PY) scripts/generate_auditability.py

## Individual protocol stages
benchmark redundancy probes gates direct stochastic multistakeholder report:
	$(PY) run_protocol.py --config $(CFG) --stage $@

paper:
	cd ../paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && \
	  pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex

clean:
	rm -f ../paper/*.aux ../paper/*.log ../paper/*.out ../paper/*.blg
