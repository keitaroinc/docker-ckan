# Dockerized CKAN ![Docker Pulls](https://img.shields.io/docker/pulls/keitaro/ckan.svg)
This repository contains base docker images, examples and docker-compose used to build and run CKAN. 

We build and publish docker images built using this repository to Dockerhub:
- [CKAN docker images](https://hub.docker.com/r/keitaro/ckan). 
- [Datapusher docker images](https://hub.docker.com/r/keitaro/ckan-datapusher)

Looking to run CKAN on Kubernetes? Check out our [CKAN Helm Chart](https://github.com/keitaroinc/ckan-helm)!

## Overview
All images are based on [Alpine Linux](https://alpinelinux.org/) and include only required extensions to start a CKAN instance. The docker images are built using a multi-stage docker approach in order to produce slim production grade docker images with the right libraries and configuration. This multi-stage approach allows us to build python binary wheels in the build stages that later on we install in the main stage.

Directory layout:
- [compose](./compose) - contains a docker-compose setup allowing users to spin up a CKAN setup easily using [docker-compose](https://docs.docker.com/compose/)
- [images](./images) - includes docker contexts for building all supported CKAN versions and datapusher
- [examples](./examples) - includes examples on how to extend the CKAN docker images and how to run them

## Running CKAN using docker-compose
To start CKAN using docker-compose, simply change into the *compose* directory and run
```sh
cd compose
docker-compose build
docker-compose up
```
Check if CKAN was succesfuly started on http://localhost:5000. 

### Configuration
In order to configure CKAN within docker-compose we use both build/up time variables loaded via the [.env](./compose/.env) file, and runtime variables loaded via the [.ckan-env](./compose/.ckan-env) file. 

Variables in the [.env](./compose/.env) file are loaded when running `docker-compose build` and `docker-compose up`, while variables in [.ckan-env](./compose/.ckan-env) file are used withing the CKAN container at runtime to configure CKAN and CKAN extensions using [ckanext-envvars](https://github.com/okfn/ckanext-envvars).

## Extending CKAN docker images
Check some examples of extending CKAN docker images in the [examples](./examples) directory.

We recommend to use a multi-stage approach to extend the docker images that we provide here. To extend the images the following Dockerfile structure is recommended:
```docker
###################
### Extensions ####
###################
FROM keitaro/ckan:2.9.0 as extbuild

# Switch to the root user
USER root

# Install any system packages necessary to build extensions
RUN apk add --no-cache python3-dev

# Fetch and build the custom CKAN extensions
RUN pip wheel --wheel-dir=/wheels git+https://github.com/acmecorp/ckanext-acme@0.0.1#egg=ckanext-acme

############
### MAIN ###
############
FROM keitaro/ckan:2.9.0

# Add the custom extensions to the plugins list
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher acme

# Switch to the root user
USER root

COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions
RUN pip install --no-index --find-links=/srv/app/ext_wheels ckanext-acme && \
    ckan -c ${APP_DIR}/production.ini config-tool "ckan.plugins = ${CKAN__PLUGINS}" && \
    chown -R ckan:ckan /srv/app

# Remove wheels
RUN rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
```

### Adding prerun scripts
You can add scripts to CKAN custom images and copy them to the *docker-entrypoint.d* directory. Any *.sh or *.py file in that directory will be executed after the main initialization script (prerun.py) is executed.

## Build
To build a CKAN image run:
```sh 
docker build --tag keitaro/ckan:2.9.0 images/ckan/2.9 
``` 
The –-tag keitaro/ckan:2.9.0 flag sets the image name to ketiaro/ckan:2.9.0 and 'images/ckan/2.9'  at the end tells docker build to use the context into the specified directory where the Dockerfile and related contents are.

## Upload to DockerHub
>*It's recommended to upload built images to DockerHub* 

To upload the image to DockerHub run:

```sh 
docker push [options] <docker-hub-namespace>/ckan:<image-tag> 
```
