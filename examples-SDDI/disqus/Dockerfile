###################
### Extensions ####
###################
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as extbuild

ARG CKAN_EXT_DISQUS_VERSION=master
ENV CKAN_EXT_DISQUS_VERSION=${CKAN_EXT_DISQUS_VERSION}

# Switch to the root user
USER root


# Install any system packages necessary to build extensions
# RUN apk add --no-cache &&\
# 	pip install --upgrade pip


RUN set -ex && \
pip wheel --wheel-dir=/wheels git+https://github.com/BWibo/ckanext-disqus@${CKAN_EXT_DISQUS_VERSION}#egg=ckanext-disqus
  
############
### MAIN ###
############
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as runtime

# List all extensions here
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher disqus

# Switch to the root user
USER root

# Copy python wheels from build stage
COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions, remove wheels
RUN set -ex && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
  ckan config-tool "${APP_DIR}/production.ini" "disqus.name = 129-187-38-46" && \
  chown -R ckan:ckan /srv/app && \
  rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
