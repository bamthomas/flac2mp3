VIRTUALENV := venv/
PWD := `pwd`
CURRENT_VERSION ?= `python setup.py --version`

clean:
		find . -name "*.pyc" -exec rm -rf {} \;
		rm -rf dist *.egg-info __pycache__

install: install-virtualenv install-pip

dist:
		python setup.py sdist

install-virtualenv:
		# Check if venv folder is already created and create it
		if [ ! -d venv ]; then virtualenv $(VIRTUALENV) --python=python3 --no-site-package --distribute; fi

install-pip:
		. $(VIRTUALENV)bin/activate; pip install -e ".[dev]"

minor:
		. $(VIRTUALENV)bin/activate; bumpversion --commit --tag --current-version ${CURRENT_VERSION} minor setup.py

major:
		. $(VIRTUALENV)bin/activate; bumpversion --commit --tag --current-version ${CURRENT_VERSION} major setup.py

patch:
		. $(VIRTUALENV)bin/activate; bumpversion --commit --tag --current-version ${CURRENT_VERSION} patch setup.py

deploy:
		. $(VIRTUALENV)bin/activate; python setup.py sdist bdist_egg upload
