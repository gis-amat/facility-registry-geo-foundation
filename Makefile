PYTHON ?= python

.PHONY: setup build qa map test

setup:
	$(PYTHON) -m pip install -r requirements.txt

build:
	$(PYTHON) scripts/00_generate_raw_data.py
	$(PYTHON) scripts/01_clean_normalize.py
	$(PYTHON) scripts/02_optional_geocode.py
	$(PYTHON) scripts/03_run_qaqc.py
	$(PYTHON) scripts/04_export_outputs.py
	$(PYTHON) scripts/05_make_static_map.py

qa:
	$(PYTHON) scripts/03_run_qaqc.py

map:
	$(PYTHON) scripts/05_make_static_map.py

test:
	$(PYTHON) -m pytest -q
