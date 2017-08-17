FROM keitaro/base:0.1

MAINTAINER Keitaro Inc <info@keitaro.info>

ENV APP_DIR=/srv/app
ENV SRC_DIR=/srv/app/src
ENV PIP_SRC=${SRC_DIR}
ENV GIT_BRANCH=ckan-2.7.0
ENV GIT_URL=https://github.com/ckan/ckan.git
ENV CKAN_SITE_URL=http://localhost:5000
# These plugins should always be added to cloud instances
# (you can add more needed by your instance)
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher sentry s3filestore repo_info harvest ckan_harvester
WORKDIR ${APP_DIR}

#########################
### Base docker layer ###
#########################
# Install necessary packages to run CKAN
RUN apk add --no-cache git \
        gettext \
        postgresql-client \
        python \
        nginx \
        apache2-utils \
        libxml2 \
        libmagic \
        libxslt && \
    # Packages to build CKAN requirements and plugins
    apk add --no-cache --virtual .build-deps \
        postgresql-dev \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
	libtool \
        python-dev \
        libxml2-dev \
        libxslt-dev && \

    apk add --no-cache --virtual .build-deps-testing \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        gdal-dev \
        geos-dev && \

    # Create SRC_DIR
    mkdir -p ${SRC_DIR} && \
    # Create nginx run dir
    mkdir -p /run/nginx && \
    # Install pip and gunicorn
    curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python ${SRC_DIR}/get-pip.py && \
    pip install gunicorn gevent && \
    pip install supervisor && \
    mkdir /etc/supervisord.d && \
    rm -rf ${SRC_DIR}/get-pip.py && \
    pip install pygdal==2.1.3.3


COPY setup/supervisord.conf /etc

RUN mkdir -p /var/log && \
    mkdir -m 0644 -p /var/spool/cron/crontabs && \
    touch /var/log/cron.log && \
    mkdir -m 0644 -p /etc/cron.d

############################
### libgeos docker layer ###
############################
# Build and install libgeos to support geospatial
RUN git clone -b 3.6.0 --depth=1 --single-branch https://git.osgeo.org/gogs/geos/geos.git ${SRC_DIR}/geos && \
    cd ${SRC_DIR}/geos && \
    ./autogen.sh && \
    ./configure --prefix /usr && \
    make -j2 && \
    make install && \
    rm -rf ${SRC_DIR}/geos


###########################
### redis docker layers ###
###########################
# Compile and install redis needed for harvest and CKAN 2.7
ENV REDIS_VERSION=3.2.9
ENV CKAN__HARVEST__MQ__TYPE=redis
ENV CKAN__HARVEST__MQ__HOSTNAME=localhost
ENV CKAN__HARVEST__MQ__PORT=6379
RUN apk add --no-cache linux-headers && \
    cd ${SRC_DIR} && \
    wget http://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz && \
    tar xzf redis-${REDIS_VERSION}.tar.gz && \
    rm -f redis-${REDIS_VERSION}.tar.gz && \
    cd redis-${REDIS_VERSION} && \
    make && \
    cp src/redis-server /bin/redis-server && \
    rm -rf ${SRC_DIR}/redis-${REDIS_VERSION}


#########################
### CKAN docker layer ###
#########################
# Install CKAN
RUN pip install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan && \
    cd ${SRC_DIR}/ckan && \
    cp who.ini ${APP_DIR} && \
    pip install -r requirements.txt && \
    # Install CKAN envvars to support loading config from environment variables
    pip install -e git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars && \
    pip install -e git+https://github.com/ckan/ckanext-harvest.git@v1.0.0#egg=ckanext-harvest && \
    pip install -r https://raw.githubusercontent.com/ckan/ckanext-harvest/v1.0.0/pip-requirements.txt && \
    # Create and update CKAN config
    paster --plugin=ckan make-config ckan ${APP_DIR}/production.ini && \
    paster --plugin=ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}"

#########################
### Celery docker layer ###
#########################
# Install Celery
RUN pip install kombu==3.0.30 && \
    pip install celery==3.1.0

# Install additional extensions here
RUN pip install -e git+https://github.com/ckan/ckanext-googleanalytics.git@v0.0.2#egg=ckanext-googleanalytics && \
    pip install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages && \
    pip install -e git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars && \
    pip install -e git+https://github.com/okfn/ckanext-sentry.git#egg=ckanext-sentry && \
    pip install -r ${APP_DIR}/src/ckanext-sentry/requirements.txt && \
    pip install --no-cache-dir git+https://github.com/keitaroinc/ckanext-s3filestore.git@v0.0.6-minio#egg=ckanext-s3filestore &&  \
    pip install --no-cache-dir -r https://raw.githubusercontent.com/keitaroinc/ckanext-s3filestore/minio-to-s3/requirements.txt && \
    pip install -e git+https://github.com/ckan/ckanext-repo.git#egg=ckanext-repo

RUN touch crontab.tmp \
    && echo '*/2 * * * * paster --plugin=ckanext-harvest harvester run -c /srv/app/production.ini >> /var/log/cron.log 2>&1' > crontab.tmp \
    && crontab crontab.tmp \
    && rm -rf crontab.tmp

CMD [/usr/sbin/crond, -f, -d, 0]

COPY setup/cron.conf /etc/supervisord.d/cron.conf

COPY setup ${APP_DIR}
COPY setup/harvest.conf /etc/supervisord.d/harvest.conf
COPY setup/prerun_harvest.py ${APP_DIR}/prerun_harvest.py
COPY setup/redis.conf /etc/supervisord.d/redis.conf
COPY setup/celery.conf /etc/supervisord.d/celery.conf

# Dirty fix for https://github.com/ckan/ckan/issues/3539
RUN sed -i "s/i18n.set_lang(lang, config=fake_config, class_=Translations)/i18n.set_lang(lang, pylons_config=fake_config, class_=Translations)/g" /srv/app/src/ckan/ckan/lib/i18n.py


# Load envvars plugin on ini file
RUN paster --plugin=ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}"

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1

CMD ["/srv/app/start_ckan.sh"]

# For the indexing to create correct resource URLs, the site url
# must be in the ini file
ENV CKAN_SITE_URL http://beta.ckan.org
RUN paster --plugin=ckan config-tool ${APP_DIR}/production.ini "ckan.site_url = ${CKAN_SITE_URL}"

