build: init pep8 lint test

init:
	pip install --upgrade -r requirements.txt

pep8:
	pep8 --show-source --config=.pep8_setup.cfg --show-pep8 .

lint:
	pylint --rcfile=.pylintrc --reports=n c4r/*.py examples/*.py test/*.py

test:
	python -m unittest discover test

ci: pep8 lint test

.PHONY: init pep8 lint test ci
