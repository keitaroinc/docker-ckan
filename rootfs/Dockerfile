FROM keitaro/base:0.1

MAINTAINER Keitaro Inc <info@keitaro.info>

ENV APP_DIR=/srv/app
ENV SRC_DIR=/srv/app/src
ENV GIT_URL=https://github.com/ckan/ckan.git
ENV GIT_BRANCH=ckan-2.6.0
ENV CKAN_SITE_URL=http://localhost:5000
ENV CKAN__PLUGINS image_view text_view recline_view datastore datapusher envvars

WORKDIR ${APP_DIR}

# Install necessary packages to run CKAN
RUN apk add --no-cache git \
        gettext \
        postgresql-client \
        python \
        py-pip \
        py-gevent \
        py-gunicorn && \
    # Temporary packages to build CKAN requirements
    apk add --no-cache --virtual .build-deps \
        postgresql-dev \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
	libtool \
        musl-dev \
        python-dev && \
    # Build and install libgeos to support geospatial
    git clone -b 3.6.0 --depth=1 --single-branch https://git.osgeo.org/gogs/geos/geos.git ${SRC_DIR}/geos && \
    cd ${SRC_DIR}/geos && \
    ./autogen.sh && \
    ./configure --prefix /usr && \
    make -j2 && \
    make install && \
    # Fetch CKAN and install
    git clone -b ${GIT_BRANCH} --depth=1 --single-branch ${GIT_URL} ${SRC_DIR}/ckan && \
    cd ${SRC_DIR}/ckan && \
    cp who.ini ${APP_DIR} && \
    python setup.py install && \
    pip install --no-cache-dir testrepository && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    pip install --no-cache-dir gevent && \
    # Remove temporary packages and files
    apk del .build-deps && \
    rm -rf ${SRC_DIR}

# CKAN plugins to enable
ENV CKAN__PLUGINS image_view text_view recline_view datastore datapusher envvars

# Default Extensions
RUN pip install --no-cache-dir git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars && \
    # Create and update CKAN config
    paster --plugin=ckan make-config ckan ${APP_DIR}/production.ini && \
    paster --plugin=ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}"

COPY setup ${APP_DIR}

EXPOSE 5000

CMD ["/srv/app/start_ckan.sh"]
