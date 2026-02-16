SHELL := /bin/bash

.PHONY: run install

install:
	python -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	# Run the helper script with bash so exec permission isn't required
	bash run_uvicorn.sh
