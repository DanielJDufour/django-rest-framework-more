#!/bin/sh -e

pipenv install -e .
pipenv run python3 ./test/psql/manage.py makemigrations
pipenv run python3 ./test/psql/manage.py migrate
DEBUG_DRF_MORE=True pipenv run python3 ./test/psql/manage.py runserver
