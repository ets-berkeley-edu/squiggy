# Squiggy

Providing the Asset Library and Engagement Index LTI tools for bCourses sites.

![Squiggy says hello](src/assets/hello.jpg)

## Installation

* Install Python 3.7
* Create your virtual environment (venv)
* Install dependencies

```
pip3 install -r requirements.txt [--upgrade]
```

If you get errors installing psycopg2 into a virtual env on OSX, try a tip from https://stackoverflow.com/questions/9678408/cant-install-psycopg2-with-pip-in-virtualenv-on-mac-os-x-10-7

```
brew install openssl
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
```

and retry the install.

libmagic is used to determine content type on file assets.

```
brew install libmagic
```

### Front-end dependencies

```
npm install
```

### Create Postgres user and databases

```
createuser squiggy --no-createdb --no-superuser --no-createrole --pwprompt
createdb squiggy --owner=squiggy
createdb squiggy_test --owner=squiggy

# Load schema
export FLASK_APP=application.py
flask initdb
```

### Create local configurations

If you plan to use any resources outside localhost, put your configurations in a separately encrypted area:

```
mkdir /Volumes/XYZ/squiggy_config
export SQUIGGY_LOCAL_CONFIGS=/Volumes/XYZ/squiggy_config
```

## Run the app locally

Start the back end:
`python application.py`

Start the front end:
`npm run serve-vue`

## Run tests, lint the code

We use [Tox](https://tox.readthedocs.io) for continuous integration. Under the hood, you'll find [PyTest](https://docs.pytest.org), [Flake8](http://flake8.pycqa.org) and [ESLint](https://eslint.org/). Please install NPM dependencies (see above) before running tests.
```
# Run all tests and linters
tox

# Pytest
tox -e test

# Run specific test(s)
tox -e test -- tests/test_models/test_foo.py
tox -e test -- tests/test_externals/

# Linters, à la carte
tox -e lint-py
tox -e lint-vue

# Auto-fix linting errors in Vue code
tox -e lint-vue-fix

# Lint specific file(s)
tox -e lint-py -- scripts/foo.py
```
