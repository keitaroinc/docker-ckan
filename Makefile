VERSION := $(shell git describe --tags --exact-match 2>/dev/null || echo latest)
DOCKERHUB_NAMESPACE ?= keitaro
IMAGE := ${DOCKERHUB_NAMESPACE}/ckan:${VERSION}

# Set target CKAN directory to build
CKAN_DIR=2.9
ifeq ($(findstring v2.8, ${VERSION}), v2.8)
	CKAN_DIR=2.8
else ifeq ($(findstring v2.7, ${VERSION}), v2.7)
	CKAN_DIR=2.7
endif

build:
	docker build -t ${IMAGE} images/ckan/${CKAN_DIR}

build-alt:
	docker build -t ${IMAGE}-focal -f images/ckan/${CKAN_DIR}/Dockerfile.focal images/ckan/${CKAN_DIR}

push: build
	docker push ${IMAGE}

push-alt: build-alt
	docker push ${IMAGE}-focal

