# Base docker ckan image 

## Overview

This repository contains base docker image used to build CKAN instance images. 

## Build
To create the image 

```sh 
docker build -t ckan-2.8.2 . 
``` 

## Upload to DockerHub

>*It's recommended to upload built images to DockerHub* 

To upload the image to DockerHub

```sh 
docker push [options] ehealthafrica/ckan:<image-tag> 
```
