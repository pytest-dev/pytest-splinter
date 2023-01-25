# create virtual environment
PATH := .env/bin:$(PATH)

.env:
	virtualenv .env

# install all needed for development
develop: .env
	pip install -e . -r requirements-testing.txt tox coveralls
	npm install selenium-standalone@6.15.0
	node_modules/.bin/selenium-standalone install

coverage: develop
	coverage run --source=pytest_splinter .env/bin/py.test tests
	coverage report -m

test: develop
	tox

coveralls: coverage
	coveralls

# clean the development environment
clean:
	-rm -rf .env
