FROM keitaro/base:0.1

MAINTAINER Keitaro Inc <info@keitaro.info>

ENV APP_DIR=/srv/app
ENV SRC_DIR=/srv/app/src
ENV PIP_SRC=${SRC_DIR}
ENV GIT_URL=https://github.com/ckan/ckan.git
ENV GIT_BRANCH=ckan-2.6.2
ENV CKAN_SITE_URL=http://localhost:5000
ENV CKAN__PLUGINS image_view text_view recline_view datastore datapusher envvars

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
        apache2-utils && \
    # Packages to build CKAN requirements and plugins
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
    # Create SRC_DIR
    mkdir -p ${SRC_DIR} && \
    # Create nginx run dir
    mkdir -p /run/nginx && \
    # Install pip and gunicorn
    curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python ${SRC_DIR}/get-pip.py && \
    pip install gunicorn gevent && \
    rm -rf ${SRC_DIR}/get-pip.py

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
    # Create and update CKAN config
    paster --plugin=ckan make-config ckan ${APP_DIR}/production.ini && \
    paster --plugin=ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}"

COPY setup ${APP_DIR}

EXPOSE 5000

CMD ["/srv/app/start_ckan.sh"]
