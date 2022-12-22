###################
### Extensions ####
###################
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as extbuild

ARG CKAN_EXT_GEOVIEW_VERSION=master
ENV CKAN_EXT_GEOVIEW_VERSION=${CKAN_EXT_GEOVIEW_VERSION}

# Switch to the root user
USER root

# Install any system packages necessary to build extensions
RUN pip install -r https://raw.githubusercontent.com/ckan/ckanext-geoview/${CKAN_EXT_GEOVIEW_VERSION}/dev-requirements.txt

RUN pip wheel --wheel-dir=/wheels git+https://github.com/ckan/ckanext-geoview.git@${CKAN_EXT_GEOVIEW_VERSION}#egg=ckanext-geoview

############
### MAIN ###
############
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as runtime

# List all extensions here
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher resource_proxy geo_view geojson_view wmts_view shp_view


# Switch to the root user
USER root

# Copy python wheels from build stage
COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions, remove wheels
RUN set -ex && \
  pip install --no-index --find-links=/srv/app/ext_wheels ckanext-geoview && \
#  pip install --no-index --find-links=/srv/app/ext_wheels -r /srv/app/ext_wheels/ckanext-geoview.txt && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.views.default_views = geo_view geojson_view wmts_view shp_view" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckanext.geoview.ol_viewer.formats = wms kml" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckanext.geoview.shp_viewer.srid = 4326" && \
  ckan config-tool "${APP_DIR}/production.ini" "ckanext.geoview.shp_viewer.encoding = UTF-8" && \
  chown -R ckan:ckan /srv/app && \
  rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
