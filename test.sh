#!/bin/sh -e

DEBUG_DRF_MORE=true pipenv run python3 test/mysite/manage.py test myapp.tests
