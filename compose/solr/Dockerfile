ARG SOLR_VERSION

FROM solr:${SOLR_VERSION:-9}

EXPOSE 8983

ARG CKAN_BRANCH
RUN echo ${CKAN_BRANCH} | sed 's/\-xloader//g' > /tmp/version

ENV SOLR_CONFIG_DIR="/opt/solr/server/solr/configsets"
ENV SOLR_SCHEMA_FILE="$SOLR_CONFIG_DIR/ckan/conf/managed-schema"

USER root

# Create a CKAN configset by copying the default one
RUN cp -R $SOLR_CONFIG_DIR/_default $SOLR_CONFIG_DIR/ckan

# Update the schema
RUN apt install curl -y
RUN curl https://raw.githubusercontent.com/ckan/ckan/`cat /tmp/version`/ckan/config/solr/schema.xml -o $SOLR_SCHEMA_FILE
RUN chmod 644 $SOLR_SCHEMA_FILE 

USER solr

CMD ["sh", "-c", "solr-precreate ckan $SOLR_CONFIG_DIR/ckan"]