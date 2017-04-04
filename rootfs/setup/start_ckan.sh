#!/bin/bash
python prerun.py
if [ $? -eq 0 ]
then
  gunicorn --log-file=- -k gevent -w 4 --paste production.ini
else
  echo "[prerun] failed...not starting CKAN."
fi
