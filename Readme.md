# Dockerized CKAN 

[![build-status](https://github.com/keitaroinc/docker-ckan/workflows/Docker%20Image%20Build/badge.svg?branch=master)](https://github.com/keitaroinc/docker-ckan/actions) [![License][]][1] [![Docker Pulls][]][2] [![Chat on Gitter][]][3]
    
This repository contains base docker images, examples and docker-compose used to build and run CKAN. 

We build and publish docker images built using this repository to Dockerhub:
- [CKAN docker images](https://hub.docker.com/r/keitaro/ckan). 
- [Datapusher docker images](https://hub.docker.com/r/keitaro/ckan-datapusher)

and Github Container Registry:
- [CKAN docker images on GHCR](https://github.com/orgs/keitaroinc/packages/container/package/ckan)
- [Datapusher docker images on GHCR](https://github.com/orgs/keitaroinc/packages/container/package/datapusher)

Looking to run CKAN on Kubernetes? Check out our [CKAN Helm Chart](https://github.com/keitaroinc/ckan-helm)!

## Overview
Images are provided in two flavors:
- [Alpine Linux](https://alpinelinux.org/) based images
- [Ubuntu Focal](https://ubuntu.com/) based images are the ones ending with `-focal` in the tag name

The Docker containers include only the required extensions to start a CKAN instance. The docker images are built using a multi-stage docker approach in order to produce slim production grade docker images with the right libraries and configuration. This multi-stage approach allows us to build python binary wheels in the build stages that later on we install in the main stage.

Directory layout:
- [compose](./compose) - contains a docker-compose setup allowing users to spin up a CKAN setup easily using [docker-compose](https://docs.docker.com/compose/)
- [images](./images) - includes docker contexts for building all supported CKAN versions and datapusher
- [examples](./examples) - includes examples on how to extend the CKAN docker images and how to run them

## Running CKAN using docker-compose
To start CKAN using docker-compose, simply change into the *compose* directory and run
```sh
cd compose/2.9
docker-compose build
docker-compose up
```
Check if CKAN was succesfuly started on http://localhost:5000. 

### Configuration
In order to configure CKAN within docker-compose we use both build/up time variables loaded via the [.env](./compose/2.9/.env) file, and runtime variables loaded via the [.ckan-env](./compose/2.9/.ckan-env) file. 

Variables in the [.env](./compose/2.9/.env) file are loaded when running `docker-compose build` and `docker-compose up`, while variables in [.ckan-env](./compose/2.9/.ckan-env) file are used withing the CKAN container at runtime to configure CKAN and CKAN extensions using [ckanext-envvars](https://github.com/okfn/ckanext-envvars).

## Extending CKAN docker images
Check some examples of extending CKAN docker images in the [examples](./examples) directory.

We recommend to use a multi-stage approach to extend the docker images that we provide here. To extend the images the following Dockerfile structure is recommended:
```docker
###################
### Extensions ####
###################
FROM ghcr.io/keitaroinc/ckan:2.9.9 as extbuild

# Switch to the root user
USER root

# Install any system packages necessary to build extensions
# Make sure we install python 3.8, cause CKAN is not compatible with 3.9
RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/v3.13/main \
        python3-dev=3.8.10-r0 

# Fetch and build the custom CKAN extensions
RUN pip wheel --wheel-dir=/wheels git+https://github.com/acmecorp/ckanext-acme@0.0.1#egg=ckanext-acme

############
### MAIN ###
############
FROM ghcr.io/keitaroinc/ckan:2.9.9

# Add the custom extensions to the plugins list
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher acme

# Switch to the root user
USER root

COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions
RUN pip install --no-index --find-links=/srv/app/ext_wheels ckanext-acme && \
    ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}" && \
    chown -R ckan:ckan /srv/app

# Remove wheels
RUN rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
```

### Adding init and afterinit scripts
You can add scripts to CKAN custom images and copy them to the *docker-entrypoint.d* directory. Any *.sh or *.py file in that directory will be executed before the main initialization script (prerun.py) is executed.

You can add scripts to CKAN custom images and copy them to the *docker-afterinit.d* directory. Any *.sh or *.py file in that directory will be executed after the main initialization script (prerun.py) is executed.

## Build
To build a CKAN image run:
```sh 
docker build --tag ghcr.io/keitaroinc/ckan:2.9.9 images/ckan/2.9
``` 
The –-tag ghcr.io/keitaroinc/ckan:2.9.9 flag sets the image name to ghcr.io/keitaroinc/ckan:2.9.9 and 'images/ckan/2.9'  at the end tells docker build to use the context into the specified directory where the Dockerfile and related contents are.

## Upload to DockerHub
>*It's recommended to upload built images to DockerHub* 

To upload the image to DockerHub run:

```sh 
docker push [options] <docker-hub-namespace>/ckan:<image-tag> 
```

  [License]: https://img.shields.io/badge/license-Apache--2.0-blue.svg?style=flat
  [1]: https://opensource.org/licenses/Apache-2.0
  [Docker Pulls]: https://img.shields.io/docker/pulls/keitaro/ckan.svg?style=flat
  [2]: https://hub.docker.com/r/keitaro/ckan
  [Chat on Gitter]: https://badges.gitter.im/gitterHQ/gitter.svg
  [3]: https://gitter.im/keitaroinc/docker-ckan
