.PHONY: clean venv

clean:
	@rm -rf dist **.egg-info

venv:
	python3 -m venv .venv

build:
	.venv/bin/pip install build
	.venv/bin/python3 -m build
