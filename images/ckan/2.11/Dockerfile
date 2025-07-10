# Set a default docker base image to pass to all stages
ARG BASE_IMAGE=python:3.10.18-alpine

##################
### Build CKAN ###
##################
# hadolint ignore=DL3006
FROM ${BASE_IMAGE} AS ckanbuild

# Used by Github Actions to tag the image with
ENV IMAGE_TAG="2.11.3"

# Set CKAN version to build
ENV GIT_URL="https://github.com/ckan/ckan.git"
ENV GIT_BRANCH="ckan-${IMAGE_TAG}"

# Set src dirs
ENV SRC_DIR="/app/src"

# Set uv config
ENV XDG_BIN_HOME="/usr/local/bin"
ENV XDG_CACHE_HOME="/app/cache"
ENV UV_COMPILE_BYTECODE="1"
ENV UV_LINK_MODE="copy"
ENV UV_PYTHON_DOWNLOADS="0"

# Set default shell to ash and enable pipefail
# This is nececary when using pipes in docker so it wont silent fail
SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# System packages to build CKAN requirements and plugins
RUN apk add --no-cache \
        git=2.49.1-r0 \
        curl=8.14.1-r1 \
        postgresql17-dev=17.5-r0

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR ${SRC_DIR}/ckan

# Fetch CKAN from github and remove git history
RUN git clone --depth=1 --branch ${GIT_BRANCH} ${GIT_URL} . && \
    rm -rf ${SRC_DIR}/.git

# Build wheels for CKAN requirements
RUN uv pip install --system -r requirements.txt


###################
### Build uWSGI ###
###################
# hadolint ignore=DL3006
FROM ${BASE_IMAGE} AS uwsgibuild

# Set uWSGI version to build
ENV UWSGI_VERSION=2.0.28

# Set uv config
ENV XDG_BIN_HOME="/usr/local/bin"
ENV XDG_CACHE_HOME="/app/cache"
ENV UV_COMPILE_BYTECODE="1"
ENV UV_LINK_MODE="copy"
ENV UV_PYTHON_DOWNLOADS="0"

# Set default shell to ash and enable pipefail
# This is nececary when using pipes in docker so it wont silent fail
SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# System packages to build CKAN requirements and plugins
RUN apk add --no-cache \
        curl=8.14.1-r1 \
        linux-headers=6.14.2-r0 \
        musl-dev=1.2.5-r10 \
        gcc=14.2.0-r6

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Compile uWSGI
RUN uv pip install --system uwsgi==${UWSGI_VERSION}


############
### MAIN ###
############
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

LABEL maintainer="Keitaro Inc <info@keitaro.com>"
LABEL org.opencontainers.image.source="https://github.com/keitaroinc/docker-ckan"

# Default CKAN Extensions
ENV ENVVARS_GIT_URL="https://github.com/okfn/ckanext-envvars"
ENV ENVVARS_GIT_VERSION="v0.0.6"
ENV XLOADER_GIT_URL="https://github.com/ckan/ckanext-xloader.git"
ENV XLOADER_GIT_VERSION="2.0.1"
ENV XLOADER_REQUIREMENTS_URL="https://raw.githubusercontent.com/ckan/ckanext-xloader/refs/tags/${XLOADER_GIT_VERSION}/requirements.txt"

# CKAN env
ENV APP_DIR="/app"
ENV SRC_DIR="/app/src"
ENV CKAN_DIR="${SRC_DIR}/ckan"
ENV DATA_DIR="/app/data"
ENV CKAN_SITE_URL="http://localhost:5000"
ENV CKAN__PLUGINS="envvars activity image_view text_view datatables_view datastore xloader"

# Set uv config
ENV XDG_BIN_HOME="/usr/local/bin"
ENV XDG_CACHE_HOME="/app/cache"
ENV UV_PYTHON_DOWNLOADS="0"

# Set default shell to ash and enable pipefail
# This is nececary when using pipes in docker so it wont silent fail
SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# Install necessary packages to run CKAN
RUN apk add --no-cache \
        bash=5.2.37-r0 \
        git=2.49.1-r0 \
        curl=8.14.1-r1 \
        # Required for CKAN
        libmagic=5.46-r2 \
        postgresql17-client=17.5-r0

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR ${APP_DIR}

# Create a local user and group to run the app
RUN addgroup -g 92 -S ckan && \
    adduser -u 92 -h /app -H -D -S -G ckan ckan && \
    chown -R ckan:ckan /app

# Get artifacts from build stages
COPY --from=uwsgibuild /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=ckanbuild --chown=ckan:ckan /app/cache /app/cache
COPY --from=ckanbuild --chown=ckan:ckan /app/src/ckan ${CKAN_DIR}

WORKDIR ${CKAN_DIR}

# Install CKAN
RUN uv pip sync --system requirements.txt && \
    uv pip install --system -e ${CKAN_DIR} && \
    # Install necessary CKAN extensions
    uv pip install --system git+${ENVVARS_GIT_URL}@${ENVVARS_GIT_VERSION} && \
    uv pip install --system git+${XLOADER_GIT_URL}@${XLOADER_GIT_VERSION} && \
    uv pip install --system -r ${XLOADER_REQUIREMENTS_URL} && \
    uv pip install --system -U requests[security] && \
    # Create and update CKAN config
    echo "UTC" >  /etc/timezone && \
    # Generate CKAN config
    ckan generate config ${APP_DIR}/production.ini && \
    ckan config-tool ${APP_DIR}/production.ini "beaker.session.secret = " && \
    # Configure plugins
    ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}" && \
    # Create the data directory
    mkdir ${DATA_DIR} && \
    # Webassets can't be loaded from env variables at runtime, it needs to be in the config so that it is created
    ckan config-tool ${APP_DIR}/production.ini "ckan.webassets.path = ${DATA_DIR}/webassets" && \
    # Set the default level for extensions to INFO
    ckan config-tool ${APP_DIR}/production.ini -s logger_ckanext -e level=INFO && \
    chown -R ckan:ckan ${APP_DIR} && \
    # Remove uv cache
    rm -rf ${XDG_CACHE_HOME}

# Copy necessary scripts
COPY --chown=ckan:ckan setup/app ${APP_DIR}

WORKDIR ${APP_DIR}

# Create entrypoint directory for children image scripts
ONBUILD RUN mkdir docker-entrypoint.d

# Create afterinit directory for children image scripts
ONBUILD RUN mkdir docker-afterinit.d

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1

USER ckan

# Startup options for uwsgi, set UWSGI_OPTS env variable on runtime to override
ENV UWSGI_PROC_NU="2"
ENV UWSGI_OPTS="--socket /tmp/uwsgi.sock --uid ckan --gid ckan --http :5000 --master --enable-threads --wsgi-file $APP_DIR/wsgi.py --module wsgi:application --lazy-apps -p ${UWSGI_PROC_NU} -L --vacuum --harakiri 50 --callable application"

CMD ["/app/start_ckan.sh"]
