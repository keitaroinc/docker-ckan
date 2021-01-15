FROM solr:6.6.6

# Enviroment
ENV SOLR_CORE ckan
ENV SOLR_VERSION 6.6.6

# Build Arguments
ARG CKAN_VERSION

# Create Directories
RUN mkdir -p /opt/solr/server/solr/$SOLR_CORE/conf
RUN mkdir -p /opt/solr/server/solr/$SOLR_CORE/data

# Adding Files
COPY ./solr/solrconfig-$CKAN_VERSION.xml /opt/solr/server/solr/$SOLR_CORE/conf/
ADD https://raw.githubusercontent.com/ckan/ckan/ckan-$CKAN_VERSION/ckan/config/solr/schema.xml \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/$SOLR_VERSION/solr/server/solr/configsets/basic_configs/conf/currency.xml \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/$SOLR_VERSION/solr/server/solr/configsets/basic_configs/conf/synonyms.txt \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/$SOLR_VERSION/solr/server/solr/configsets/basic_configs/conf/stopwords.txt \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/$SOLR_VERSION/solr/server/solr/configsets/basic_configs/conf/protwords.txt \
https://raw.githubusercontent.com/apache/lucene-solr/releases/lucene-solr/$SOLR_VERSION/solr/server/solr/configsets/data_driven_schema_configs/conf/elevate.xml \
/opt/solr/server/solr/$SOLR_CORE/conf/

# Create Core.properties
RUN mv /opt/solr/server/solr/$SOLR_CORE/conf/solrconfig-$CKAN_VERSION.xml /opt/solr/server/solr/$SOLR_CORE/conf/solrconfig.xml && \
    echo name=$SOLR_CORE > /opt/solr/server/solr/$SOLR_CORE/core.properties

# Giving ownership to Solr

USER root

RUN chown -R "$SOLR_USER:$SOLR_USER" /opt/solr/server/solr/$SOLR_CORE

# User
USER $SOLR_USER:$SOLR_USER
