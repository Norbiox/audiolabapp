#!/usr/bin/env bash

pip install -r requirements.txt

py.test --cov=. --cov-report term-missing -v app/tests
