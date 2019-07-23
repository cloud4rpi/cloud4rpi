.PHONY: init style lint test clean release

build: init style lint test

init:
	pip install --upgrade setuptools
	pip install --upgrade -r requirements.txt

style:
	pycodestyle --show-source --show-pep8 .

lint:
	pylint --rcfile=.pylintrc --reports=n cloud4rpi/ test/*.py examples/*.py

test:
	python -m unittest discover test

ci: style lint test

clean:
	rm -rf build/*
	rm -rf *.egg-info/*
	rm -rf dist/*

release: clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
