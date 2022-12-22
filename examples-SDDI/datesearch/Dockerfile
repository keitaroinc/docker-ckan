###################
### Extensions ####
###################
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as extbuild

ARG CKAN_EXT_DATESEARCH_VERSION=master
ENV CKAN_EXT_DATESEARCH_VERSION=${CKAN_EXT_DATESEARCH_VERSION}

# Switch to the root user
USER root

# Install any system packages necessary to build extensions


RUN set -ex && \
  mkdir -p /wheels && \
  pip wheel --wheel-dir=/wheels git+https://github.com/MarijaKnezevic/ckanext-datesearch.git@${CKAN_EXT_DATESEARCH_VERSION}#egg=ckanext-datesearch && \
  ls -lah /wheels

############
### MAIN ###
############
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as runtime

# List all extensions here
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher datesearch

# Switch to the root user
USER root

# Copy python wheels from build stage
COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions, remove wheels
RUN set -ex && \
  pip install --no-index --find-links=/srv/app/ext_wheels ckanext-datesearch && \
#  pip install --no-index --find-links=/srv/app/ext_wheels -r /srv/app/ext_wheels/ckanext-datesearch.txt && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
  chown -R ckan:ckan /srv/app && \
  rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
