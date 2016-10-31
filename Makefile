build: init style lint test

init:
	pip install --upgrade -r requirements.txt

style:
	pep8 --show-source --config=.pep8_setup.cfg --show-pep8 .

lint:
	pylint --rcfile=.pylintrc --reports=n *.py cloud4rpi/*.py examples/*.py test/*.py

test:
	python -m unittest discover test

ci: style lint test

clean:
	rm -rf build/*
	rm -rf *.egg-info/*
	rm -rf dist/*

release: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: init style lint test release
