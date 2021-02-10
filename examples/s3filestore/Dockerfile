###################
### Extensions ####
###################
FROM ghcr.io/keitaroinc/ckan:2.8.7 as extbuild

# Locations and tags, please use specific tags or revisions
ENV S3FILESTORE_GIT_URL=https://github.com/keitaroinc/ckanext-s3filestore
ENV S3FILESTORE_GIT_BRANCH=master

# Switch to the root user
USER root

# Fetch and build the custom CKAN extensions
RUN pip wheel --wheel-dir=/wheels git+${S3FILESTORE_GIT_URL}@${S3FILESTORE_GIT_BRANCH}#egg=ckanext-s3filestore
RUN pip wheel --wheel-dir=/wheels -r https://raw.githubusercontent.com/keitaroinc/ckanext-s3filestore/${S3FILESTORE_GIT_BRANCH}/requirements.txt
RUN curl -o /wheels/s3filestore.txt https://raw.githubusercontent.com/keitaroinc/ckanext-s3filestore/${S3FILESTORE_GIT_BRANCH}/requirements.txt

USER ckan

############
### MAIN ###
############
FROM ghcr.io/keitaroinc/ckan:2.8.7

LABEL maintainer="Keitaro Inc <info@keitaro.com>"

ENV CKAN__PLUGINS envvars s3filestore image_view text_view recline_view datastore datapusher

# Switch to the root user
USER root

COPY --from=extbuild /wheels /srv/app/ext_wheels

# Install and enable the custom extensions
RUN pip install --no-index --find-links=/srv/app/ext_wheels ckanext-s3filestore && \
    pip install --no-index --find-links=/srv/app/ext_wheels -r /srv/app/ext_wheels/s3filestore.txt && \
    paster --plugin=ckan config-tool "${APP_DIR}/production.ini" "ckan.plugins = ${CKAN__PLUGINS}" && \
    chown -R ckan:ckan /srv/app

# Remove wheels
RUN rm -rf /srv/app/ext_wheels

USER ckan
