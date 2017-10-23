# create virtual environment
PATH := .env/bin:$(PATH)

.env:
	virtualenv .env

# install all needed for development
develop: .env
	pip install -e . -U -r requirements-testing.txt tox coveralls
	npm install selenium-standalone
	node_modules/.bin/selenium-standalone install

coverage: develop
	coverage run --source=pytest_splinter .env/bin/py.test tests
	coverage report -m

test: develop
	tox

coveralls: coverage
	coveralls

# clean the development envrironment
clean:
	-rm -rf .env
