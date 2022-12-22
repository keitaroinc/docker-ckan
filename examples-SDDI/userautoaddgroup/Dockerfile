###################
### Extensions ####
###################
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as extbuild

ARG CKAN_EXT_USRADDGROUP_VERSION=master
ENV CKAN_EXT_USRADDGROUP_VERSION=${CKAN_EXT_USRADDGROUP_VERSION}

# Switch to the root user
USER root

# Install any system packages necessary to build extensions
#

RUN pip wheel --wheel-dir=/wheels git+https://github.com/tum-gis/ckanext-userautoaddgroup-sddi.git@${CKAN_EXT_USRADDGROUP_VERSION}#egg=ckanext-userautoaddgroup


############
### MAIN ###
############
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as runtime

# List all extensions here
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher userautoaddgroup

# Switch to the root user
USER root

# Copy python wheels from build stage
COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions, remove wheels
RUN set -ex && \
  pip install --no-index --find-links=/srv/app/ext_wheels ckanext-userautoaddgroup && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
  chown -R ckan:ckan /srv/app && \
  rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
