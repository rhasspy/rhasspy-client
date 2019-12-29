.PHONY: dist check venv

dist:
	python3 setup.py sdist bdist_wheel

check:
	flake8 rhasspyclient/*.py
	pylint rhasspyclient/*.py

venv:
	rm -rf .venv/
	python3 -m venv .venv
	.venv/bin/pip3 install wheel setuptools
	.venv/bin/pip3 install -r requirements_all.txt
