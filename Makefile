.PHONY: dist

dist:
	python3 setup.py sdist bdist_wheel
