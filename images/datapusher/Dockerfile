#############
### Build ###
#############
FROM alpine:3.14.2 as build

# Used by Github Actions to tag the image with
ENV IMAGE_TAG=0.0.17

# Set datapusher version to build
ENV GIT_URL https://github.com/keitaroinc/datapusher.git
ENV GIT_BRANCH master
ENV REQUIREMENTS_URL https://raw.githubusercontent.com/keitaroinc/datapusher/${GIT_BRANCH}/requirements.txt

# Set src dirs
ENV SRC_DIR=/srv/app/src
ENV PIP_SRC=${SRC_DIR}

WORKDIR ${SRC_DIR}

# Packages to build datapusher
# Make sure we install python 3.8, cause some dependencies are not compatible with 3.9
RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/v3.13/main \
        python3=3.8.10-r0 \
        python3-dev=3.8.10-r0 && \
    apk add --no-cache \
        curl \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
        libtool \
        git \
        musl-dev \
        libffi-dev \
        openssl-dev \
        libxml2-dev \
        libxslt-dev \
        rust \
        cargo

# Create the src directory
RUN mkdir -p ${SRC_DIR}

# Install pip
RUN curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python3 ${SRC_DIR}/get-pip.py

# Fetch and build datapusher and requirements
RUN pip wheel --wheel-dir=/wheels git+${GIT_URL}@${GIT_BRANCH}#egg=datapusher
RUN pip wheel --wheel-dir=/wheels -r ${REQUIREMENTS_URL} 
RUN curl -o /wheels/requirements.txt ${REQUIREMENTS_URL}

# Get uwsgi and gevent from pip
RUN pip wheel --wheel-dir=/wheels uwsgi==2.0.19.1 gevent==20.6.2 greenlet==0.4.16


############
### MAIN ###
############
FROM alpine:3.14.2

LABEL maintainer="Keitaro Inc <info@keitaro.com>"
LABEL org.opencontainers.image.source https://github.com/keitaroinc/docker-ckan

ENV APP_DIR=/srv/app
ENV JOB_CONFIG ${APP_DIR}/datapusher_settings.py

WORKDIR ${APP_DIR}

# Make sure we install python 3.8, cause some dependencies are not compatible with 3.9
RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/v3.13/main \
        python3=3.8.10-r0 \
    apk add --no-cache \
        curl \
        libmagic \
        libxslt

# Install pip
RUN curl -o /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python3 /tmp/get-pip.py

# Get artifacts from build stages
COPY --from=build /wheels /srv/app/wheels

# Install uwsgi and gevent
RUN pip install --no-index --find-links=/srv/app/wheels uwsgi==2.0.19.1 gevent==20.6.2

# Create a local user and group to run the app
RUN addgroup -g 92 -S ckan && \
    adduser -u 92 -h /srv/app -H -D -S -G ckan ckan

# Install datapusher
RUN pip install --no-index --find-links=/srv/app/wheels datapusher && \
    pip install --no-index --find-links=/srv/app/wheels -r /srv/app/wheels/requirements.txt && \
    # Set timezone
    echo "UTC" >  /etc/timezone && \
    # Change ownership to app user
    chown -R ckan:ckan /srv/app

# Remove wheels
RUN rm -rf /srv/app/wheels

COPY setup ${APP_DIR}

EXPOSE 8000

USER ckan

CMD ["uwsgi", "--socket=/tmp/uwsgi.sock", "--uid=92", "--gid=92", "--http=:8000", "--master", "--enable-threads", "--gevent=2000", "-p 2", "-L", "--wsgi-file=wsgi.py"]
