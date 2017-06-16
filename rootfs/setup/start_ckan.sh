#!/bin/bash
python prerun.py
if [ $? -eq 0 ]
then
  if [ "$HTTPS_REDIRECT" -eq "1" ]
  then
    cp -a /srv/app/nginx.conf /etc/nginx/nginx.conf
    nginx
    gunicorn --log-file=- -k gevent -w 4 -b 127.0.0.1:4000 --paste production.ini
  else
    gunicorn --log-file=- -k gevent -w 4 -b 0.0.0.0:5000 --paste production.ini
  fi
else
  echo "[prerun] failed...not starting CKAN."
fi
