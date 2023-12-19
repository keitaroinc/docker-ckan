#!/bin/bash
# Run any startup scripts provided by images extending this one
if [[ -d "${APP_DIR}/docker-entrypoint.d" ]]
then
    for f in ${APP_DIR}/docker-entrypoint.d/*; do
        case "$f" in
            *.sh)     echo "$0: Running init file $f"; . "$f" ;;
            *.py)     echo "$0: Running init file $f"; python "$f"; echo ;;
            *)        echo "$0: Ignoring $f (not an sh or py file)" ;;
        esac
        echo
    done
fi

# Add session secret from chart
if [[ -z $BEAKER_SESSION_SECRET || -v $BEAKER_SESSION_SECRET || -z $JWT_ENCODE_SECRET || -v $JWT_ENCODE_SECRET || -z $JWT_DECODE_SECRET || -v $JWT_DECODE_SECRET ]];then
  echo "Not all environment variables are set. Generating sessions..."
else
  echo "Setting session secrets from environment variables"
  ckan config-tool $APP_DIR/production.ini "beaker.session.secret=$BEAKER_SESSION_SECRET"
  ckan config-tool $APP_DIR/production.ini "api_token.jwt.encode.secret=$JWT_ENCODE_SECRET"
  ckan config-tool $APP_DIR/production.ini "api_token.jwt.decode.secret=$JWT_DECODE_SECRET"
fi

if grep -E "beaker.session.secret ?= ?$" $APP_DIR/production.ini
then
    echo "Setting secrets in ini file"
    ckan config-tool $APP_DIR/production.ini "beaker.session.secret=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')"
    ckan config-tool $APP_DIR/production.ini "WTF_CSRF_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe())')"
    JWT_SECRET=$(python3 -c 'import secrets; print("string:" + secrets.token_urlsafe())')
    ckan config-tool $APP_DIR/production.ini "api_token.jwt.encode.secret=$JWT_SECRET"
    ckan config-tool $APP_DIR/production.ini "api_token.jwt.decode.secret=$JWT_SECRET"
fi

# Run the prerun script to init CKAN and create the default admin user
python prerun.py || { echo '[CKAN prerun] FAILED. Exiting...' ; exit 1; }

# Check if we are in maintenance mode and if yes serve the maintenance pages
if [ "$MAINTENANCE_MODE" = true ]; then PYTHONUNBUFFERED=1 python maintenance/serve.py; fi

# Run any after prerun/init scripts provided by images extending this one
if [[ -d "${APP_DIR}/docker-afterinit.d" ]]
then
    for f in ${APP_DIR}/docker-afterinit.d/*; do
        case "$f" in
            *.sh)     echo "$0: Running after prerun init file $f"; . "$f" ;;
            *.py)     echo "$0: Running after prerun init file $f"; python "$f"; echo ;;
            *)        echo "$0: Ignoring $f (not an sh or py file)" ;;
        esac
        echo
    done
fi

# Check whether http basic auth password protection is enabled and enable basicauth routing on uwsgi respecfully
if [ $? -eq 0 ]
then
  if [ "$PASSWORD_PROTECT" = true ]
  then
    if [ "$HTPASSWD_USER" ] || [ "$HTPASSWD_PASSWORD" ]
    then
      # Generate htpasswd file for basicauth
      htpasswd -d -b -c /srv/app/.htpasswd $HTPASSWD_USER $HTPASSWD_PASSWORD
      # Start uwsgi with basicauth
      uwsgi --ini /srv/app/basic-auth-uwsgi.conf -p ${UWSGI_PROC_NO:-2} --pcre-jit 
    else
      echo "Missing HTPASSWD_USER or HTPASSWD_PASSWORD environment variables. Exiting..."
      exit 1
    fi
  else
    # Start uwsgi
    echo "Starting UWSGI with '${UWSGI_PROC_NO:-2}' workers"
    uwsgi --ini /srv/app/uwsgi.conf -p ${UWSGI_PROC_NO:-2}
  fi
else
  echo "[prerun] failed...not starting CKAN."
fi
