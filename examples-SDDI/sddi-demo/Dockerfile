###################
### Extensions ####
###################
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as extbuild

# Switch to the root user
USER root

###############################################
### ckanext-geoview
###############################################

ARG CKAN_EXT_GEOVIEW_VERSION=master
ENV CKAN_EXT_GEOVIEW_VERSION=${CKAN_EXT_GEOVIEW_VERSION}

# Install any system packages necessary to build extensions
RUN pip install -r https://raw.githubusercontent.com/ckan/ckanext-geoview/${CKAN_EXT_GEOVIEW_VERSION}/dev-requirements.txt

RUN pip wheel --wheel-dir=/wheels git+https://github.com/ckan/ckanext-geoview.git@${CKAN_EXT_GEOVIEW_VERSION}#egg=ckanext-geoview


###############################################
### ckanext-hierarchy 
###############################################
ARG CKAN_EXT_HIERARCHY_VERSION=master
ENV CKAN_EXT_HIERARCHY_VERSION=${CKAN_EXT_HIERARCHY_VERSION}

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


############
### MAIN ###
############
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as runtime

# List all extensions here
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher resource_proxy geo_view geojson_view wmts_view shp_view hierarchy_display hierarchy_form hierarchy_group_form


# Switch to the root user
USER root

# Copy python wheels from build stage
COPY --from=extbuild /wheels /srv/app/ext_wheels

###############################################
### ckanext-geoview
###############################################
# Install and enable the custom extensions, remove wheels
RUN set -ex && \
  pip install --no-index --find-links=/srv/app/ext_wheels ckanext-geoview && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.views.default_views = geo_view geojson_view wmts_view shp_view" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckanext.geoview.ol_viewer.formats = wms kml" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckanext.geoview.shp_viewer.srid = 4326" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckanext.geoview.shp_viewer.encoding = UTF-8" && \
  
  
###############################################
### ckanext-hierarchy
###############################################  
# Install and enable the custom extensions, remove wheels
  pip install --no-index --find-links=/srv/app/ext_wheels ckanext-hierarchy && \
  pip install --no-index --find-links=/srv/app/ext_wheels -r /srv/app/ext_wheels/ckanext-hierarchy.txt && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
  
  
  chown -R ckan:ckan /srv/app && \
  rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
