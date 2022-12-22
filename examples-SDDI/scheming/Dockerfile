###################
### Extensions ####
###################
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as extbuild

ARG CKAN_EXT_SCHEMING_VERSION=0.3-(without_composite_und_repeating)
ENV CKAN_EXT_SCHEMING_VERSION=${CKAN_EXT_SCHEMING_VERSION}

# Switch to the root user
USER root

# Install any system packages necessary to build extensions


RUN pip wheel --wheel-dir=/wheels git+https://github.com/MarijaKnezevic/ckanext-scheming.git@${CKAN_EXT_SCHEMING_VERSION}#egg=ckanext-scheming
RUN pip wheel --wheel-dir=/wheels -r https://raw.githubusercontent.com/MarijaKnezevic/ckanext-scheming/${CKAN_EXT_SCHEMING_VERSION}/test-requirements.txt
RUN curl -o /wheels/ckanext-scheming.txt https://raw.githubusercontent.com/MarijaKnezevic/ckanext-scheming/${CKAN_EXT_SCHEMING_VERSION}/test-requirements.txt
RUN pip wheel --wheel-dir=/wheels -r https://raw.githubusercontent.com/MarijaKnezevic/ckanext-scheming/${CKAN_EXT_SCHEMING_VERSION}/test-requirements-py2.txt
RUN curl -o /wheels/ckanext-scheming.txt https://raw.githubusercontent.com/MarijaKnezevic/ckanext-scheming/${CKAN_EXT_SCHEMING_VERSION}/test-requirements-py2.txt

############
### MAIN ###
############
ARG CKAN_VERSION=2.9.5
FROM ghcr.io/keitaroinc/ckan:${CKAN_VERSION} as runtime

# List all extensions here
ENV CKAN__PLUGINS envvars image_view text_view recline_view datastore datapusher scheming_datasets

# Switch to the root user
USER root

# Copy python wheels from build stage
COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions, remove wheels
RUN set -ex && \
  pip install --no-index --find-links=/srv/app/ext_wheels ckanext-scheming && \
  pip install --no-index --find-links=/srv/app/ext_wheels -r /srv/app/ext_wheels/ckanext-scheming.txt && \
  ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
  ckan config-tool "${APP_DIR}/production.ini" "scheming.dataset_schemas = ckanext.scheming:ckan_dataset.yaml" && \
  ckan config-tool "${APP_DIR}/production.ini" "scheming.presets = ckanext.scheming:presets.json" && \
  ckan config-tool "${APP_DIR}/production.ini" "scheming.dataset_fallback = false" && \
  chown -R ckan:ckan /srv/app && \
  rm -rf /srv/app/ext_wheels

# Switch to the ckan user
USER ckan
