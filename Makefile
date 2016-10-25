build: init style lint test

init:
	pip install --upgrade -r requirements.txt

style:
	pep8 --show-source --config=.pep8_setup.cfg --show-pep8 .

lint:
	pylint --rcfile=.pylintrc --reports=n cloud4rpi/*.py examples/*.py test/*.py

test:
	python -m unittest discover test

ci: style lint test

.PHONY: init style lint test ci
