#!/bin/bash
python prerun.py
gunicorn --log-file=- --paste production.ini
