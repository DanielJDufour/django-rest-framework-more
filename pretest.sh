#!/bin/sh -e

pipenv install -e .
pipenv run python3 ./test/mysite/manage.py migrate
DEBUG_DRF_MORE=True pipenv run python3 ./test/mysite/manage.py runserver
