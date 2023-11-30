leads_api
=========

Development
-----------

- Create a Python virtual environment, if not already created.

    python3 -m venv env

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e .

- Setup a local postgres database

  TODO: complete section

- Run your project.

    env/bin/pserve development.ini


Running tests
-------------

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run all tests.

    env/bin/pytest
