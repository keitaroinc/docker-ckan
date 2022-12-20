###################
### Extensions ####
###################
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as extbuild

# Switch to the root user
USER root

###############################################################################################################
# Hierarchy
###############################################################################################################
ENV CKAN_EXT_HIERARCHY_VERSION=master

# Install any system packages necessary to build extensions
RUN set -ex && \
  apk add --no-cache --virtual .build-deps \
    python3-dev && \
    pip install --upgrade pip \
    pip install -r https://raw.githubusercontent.com/ckan/ckanext-hierarchy/${CKAN_EXT_HIERARCHY_VERSION}/dev-requirements.txt

RUN set -ex && \
  mkdir -p /wheels && \
  pip wheel --wheel-dir=/wheels git+https://github.com/davidread/ckanext-hierarchy.git@${CKAN_EXT_HIERARCHY_VERSION}#egg=ckanext-hierarchy && \
  pip wheel --wheel-dir=/wheels -r https://raw.githubusercontent.com/ckan/ckanext-hierarchy/${CKAN_EXT_HIERARCHY_VERSION}/requirements.txt && \
  curl -o /wheels/ckanext-hierarchy.txt https://raw.githubusercontent.com/ckan/ckanext-hierarchy/${CKAN_EXT_HIERARCHY_VERSION}/requirements.txt && \
  ls -lah /wheels
  
###############################################################################################################
# TUM-GIS Scheming
###############################################################################################################
ENV CKAN_EXT_TUMGIS_SCHEMING_VERSION=master

RUN pip wheel --wheel-dir=/wheels git+https://github.com/tum-gis/ckanext-scheming-sddi@${CKAN_EXT_TUMGIS_SCHEMING_VERSION}#egg=ckanext-scheming
RUN pip wheel --wheel-dir=/wheels -r https://raw.githubusercontent.com/tum-gis/ckanext-scheming-sddi/${CKAN_EXT_TUMGIS_SCHEMING_VERSION}/requirements.txt
RUN curl -o /wheels/tumgis-scheming.txt https://raw.githubusercontent.com/tum-gis/ckanext-scheming-sddi/${CKAN_EXT_TUMGIS_SCHEMING_VERSION}/requirements.txt






############
### MAIN ###
############
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as runtime

LABEL maintainer="Keitaro Inc <info@keitaro.com>"


# List CKAN extensions
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher

# Switch to the root user
USER root

# Copy python wheels from build stage
COPY --from=extbuild /wheels /srv/app/ext_wheels


# Install and enable the custom extensions, remove wheels
RUN set -ex && \

###############################################################################################################
# Hierarchy
###############################################################################################################
pip install --no-index --find-links=/srv/app/ext_wheels ckanext-hierarchy && \
pip install --no-index --find-links=/srv/app/ext_wheels -r /srv/app/ext_wheels/ckanext-hierarchy.txt && \

###############################################################################################################
# TUM-GIS Scheming
###############################################################################################################
  pip install --no-index --find-links=/srv/app/ext_wheels ckanext-scheming && \
  pip install --no-index --find-links=/srv/app/ext_wheels -r /srv/app/ext_wheels/tumgis-scheming.txt && \
###############################################################################################################
  
######
  # Finalize extensions
###############################################################################################################  
  
# Configure plugins
  chown -R ckan:ckan /srv/app
  
# Remove wheels
RUN rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
