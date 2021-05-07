#!/bin/sh -e

pipenv install -e .
pipenv run python3 ./test/mysite/manage.py migrate
pipenv run python3 ./test/mysite/manage.py runserver
