# Docker ckan image  ![Docker Pulls](https://img.shields.io/docker/pulls/keitaro/ckan.svg)

## Overview

This repository contains base docker image used to build CKAN instances. It's based on [Alpine Linux](https://alpinelinux.org/) and includes only required extensions to start CKAN instance.

## Build

To create new image run:

```sh 
docker build --tag ckan-2.8.2 . 
``` 
The –-tag ckan-2.8.2 flag sets the image name to ckan-2.8.2 and the dot ( “.” ) at the end tells docker build to look into the current directory for Dockerfile and related contents.

## List

Check if the image shows up in the list of images:
```sh
 docker images
```

## Run

To start and test newly created image run:
```sh
 docker run ckan-2.8.2
```
Check if CKAN was succesfuly started on http://localhost:5000. The ckan site url is configured in ENV CKAN_SITE_URL.


## Upload to DockerHub

>*It's recommended to upload built images to DockerHub* 

To upload the image to DockerHub run:

```sh 
docker push [options] <docker-hub>/ckan:<image-tag> 
```

## Upgrade 
To upgrade the Docker file to use new CKAN version, in the Dockerfile you should change:

>ENV GIT_BRANCH={ckan_release} 

Check [CKAN repository](https://github.com/ckan/ckan/releases) for the latest releases. 
If there are new libraries used by the new version requirements, those needs to be included too.

## Extensions

Default extensions used in the Dockerfile  are kept in:

>ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher

## Add new scripts

You can add scripts to CKAN custom images and copy them to the *docker-entrypoint.d* directory. Any *.sh or *.py file in that directory will be executed after the main initialization script (prerun.py) is executed.
