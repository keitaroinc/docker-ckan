# Dockerized CKAN 

[![build-status](https://github.com/keitaroinc/docker-ckan/workflows/Docker%20Image%20Build/badge.svg?branch=master)](https://github.com/keitaroinc/docker-ckan/actions) [![License][]][1] [![Docker Pulls][]][2] [![Chat on Gitter][]][3]
 
This repository contains base docker images and docker-compose used to build and run CKAN. 

We build and publish docker images built using this repository to Dockerhub:
- [CKAN docker images](https://hub.docker.com/r/keitaro/ckan). 
- [Datapusher docker images](https://hub.docker.com/r/keitaro/ckan-datapusher)

and Github Container Registry:
- [CKAN docker images on GHCR](https://github.com/orgs/keitaroinc/packages/container/package/ckan)
- [Datapusher docker images on GHCR](https://github.com/orgs/keitaroinc/packages/container/package/datapusher)

Looking to run CKAN on Kubernetes? Check out our [CKAN Helm Chart](https://github.com/keitaroinc/ckan-helm)!

## Overview
CKAN Docker images for CKAN supported releases based on [Alpine Linux](https://alpinelinux.org/).

The Docker base images provided here contain base CKAN and the extensions: [ckanext-envvars](https://github.com/ckan/ckanext-envvars) and [ckanext-xloader](https://github.com/ckan/ckanext-xloader). The docker images are built using a multi-stage docker approach in order to produce slim production grade docker images with the right libraries and configuration. 

Directory layout:
- [compose](./compose) - contains a docker-compose setup allowing users to spin up a CKAN setup easily using [docker-compose](https://docs.docker.com/compose/)
- [images](./images) - includes docker contexts for building all supported CKAN versions

## Running CKAN using docker-compose
To start CKAN using docker-compose, simply change into the *compose* directory and run
```sh
docker compose build
docker compose up -d
```

Check if CKAN was succesfuly started on http://localhost:5000. 

## Extending CKAN docker images
The docker images contain `uv` and we recommend using when extending the images with additional CKAN and python packages. Example:
```docker
############
### MAIN ###
############
FROM ghcr.io/keitaroinc/ckan:2.11.2

# CKAN extension source code URLs
ENV ACME_GIT_URL="https://github.com/myghorg/ckanext-acme.git"
ENV ACME_GIT_VERSION="0.4.2"
ENV ACME_REQUIREMENTS_URL="https://raw.githubusercontent.com/myghorg/ckanext-acme/refs/tags/${ACME_GIT_VERSION}/requirements.txt"

# Add the custom extensions to the plugins list
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher acme

# Switch to the root user
USER root

# Install and enable the custom extensions
    # Install necessary system packages with apk 
RUN apk add --no-cache libffi-dev && \
    # Install the CKAN extension and any requirements using uv
    uv pip install --system git+${ACME_GIT_URL}@${ACME_GIT_VERSION} && \
    uv pip install --system git+${ACME_GIT_URL}@${ACME_GIT_VERSION} && \
    uv pip install --system -r ${ACME_REQUIREMENTS_URL} && \
    # Install any other required python packages
    uv pip install --system requests && \
    # Update plugin configuration
    ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}" && \
    chown -R ckan:ckan /srv/app && \
    # Remove uv cache
    rm -rf /app/cache

# Switch to the ckan user
USER ckan
```

### Adding init and afterinit scripts
You can add scripts to CKAN custom images and copy them to the *docker-entrypoint.d* directory. Any *.sh or *.py file in that directory will be executed before the main initialization script (prerun.py) is executed.

You can add scripts to CKAN custom images and copy them to the *docker-afterinit.d* directory. Any *.sh or *.py file in that directory will be executed after the main initialization script (prerun.py) is executed.

## Build
To build a CKAN image run:
```sh 
docker build --tag ghcr.io/keitaroinc/ckan:2.11.2 images/ckan/2.11
``` 
The –-tag ghcr.io/keitaroinc/ckan:2.11.2 flag sets the image name to ghcr.io/keitaroinc/ckan:2.11.2 and 'images/ckan/2.11'  at the end tells docker build to use the context into the specified directory where the Dockerfile and related contents are.

  [License]: https://img.shields.io/badge/license-Apache--2.0-blue.svg?style=flat
  [1]: https://opensource.org/licenses/Apache-2.0
  [Docker Pulls]: https://img.shields.io/docker/pulls/keitaro/ckan.svg?style=flat
  [2]: https://hub.docker.com/r/keitaro/ckan
  [Chat on Gitter]: https://badges.gitter.im/gitterHQ/gitter.svg
  [3]: https://gitter.im/keitaroinc/docker-ckan
