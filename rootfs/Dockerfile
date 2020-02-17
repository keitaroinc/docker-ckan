##################
### Build CKAN ###
##################
FROM alpine:3.11 as ckanbuild

# Set CKAN version to build
ENV GIT_URL=https://github.com/ckan/ckan.git
ENV GIT_BRANCH=master

# Set src dirs
ENV SRC_DIR=/srv/app/src
ENV PIP_SRC=${SRC_DIR}

WORKDIR ${SRC_DIR}

# Packages to build CKAN requirements and plugins
RUN apk add --no-cache \
        git \
        curl \
        python3 \
        postgresql-dev \
        linux-headers \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
        libtool \
        musl-dev \
        pcre-dev \
        pcre \
        python3-dev \
        libxml2-dev \
        libxslt-dev

# Link python to python3
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create the src directory
RUN mkdir -p ${SRC_DIR}

# Install pip
RUN curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python ${SRC_DIR}/get-pip.py

# Fetch and build CKAN and requirements
RUN pip install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan
RUN rm -rf /srv/app/src/ckan/.git
RUN pip wheel --wheel-dir=/wheels -r ckan/requirements.txt
RUN pip wheel --wheel-dir=/wheels uwsgi gevent

############
### MAIN ###
############
FROM alpine:3.11

MAINTAINER Keitaro Inc <info@keitaro.com>

ENV APP_DIR=/srv/app
ENV SRC_DIR=/srv/app/src
ENV PIP_SRC=${SRC_DIR}
ENV CKAN_SITE_URL=http://localhost:5000
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher

WORKDIR ${APP_DIR}

# Install necessary packages to run CKAN
RUN apk add --no-cache git \
        bash \
        gettext \
        curl \
        postgresql-client \
        python3 \
        libmagic \
        pcre \
        libxslt \
        libxml2 \
        tzdata \
        apache2-utils && \
    # Create SRC_DIR
    mkdir -p ${SRC_DIR} && \
    # Link python to python3
    ln -s /usr/bin/python3 /usr/bin/python

# Install pip
RUN curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python ${SRC_DIR}/get-pip.py

# Get artifacts from build stages
COPY --from=ckanbuild /wheels /srv/app/wheels
COPY --from=ckanbuild /srv/app/src/ckan /srv/app/src/ckan

# Additional install steps for build stages artifacts
RUN pip install --no-index --find-links=/srv/app/wheels uwsgi gevent

# Create a local user and group to run the app
RUN addgroup -g 92 -S ckan && \
    adduser -u 92 -h /srv/app -H -D -S -G ckan ckan

# Install CKAN
RUN pip install -e /srv/app/src/ckan && \
    cd ${SRC_DIR}/ckan && \
    cp who.ini ${APP_DIR} && \
    pip install --no-index --find-links=/srv/app/wheels -r requirements.txt && \
    # Install CKAN envvars to support loading config from environment variables
    pip install -e git+https://github.com/okfn/ckanext-envvars.git@0.0.1#egg=ckanext-envvars && \
    # Create and update CKAN config
    # ckan generate config requires cookiecutter which is in the dev-requirements, temp workaround
    pip install cookiecutter==1.6.0 && \
    # Set timezone
    echo "Europe/Stockholm" >  /etc/timezone && \
    ckan generate config ${APP_DIR}/production.ini && \
    # Not working atm since ckan config tool tries to load config before executing config-tool, workaround
    #ckan -c ${APP_DIR}/production.ini config-tool "ckan.plugins = ${CKAN__PLUGINS}" && \
    sed -i "/ckan.plugins = stats/c ckan.plugins = ${CKAN__PLUGINS}" ${APP_DIR}/production.ini && \
    # Change ownership to app user
    chown -R ckan:ckan /srv/app

# Remove wheels
RUN rm -rf /srv/app/wheels

# Copy necessary scripts
COPY setup/app ${APP_DIR}

# Create entrypoint directory for children image scripts
ONBUILD RUN mkdir docker-entrypoint.d

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1

USER ckan

CMD ["/srv/app/start_ckan.sh"]
