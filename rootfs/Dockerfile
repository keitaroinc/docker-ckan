FROM keitaro/base:0.1

MAINTAINER Keitaro Inc <info@keitaro.info>

ENV APP_DIR=/srv/app
ENV GIT_URL=https://github.com/ckan/ckan.git
ENV GIT_BRANCH=release-v2.5.2
ENV CKAN_SITE_URL=http://localhost
ENV CKAN__PLUGINS image_view text_view recline_view datastore datapusher envvars

WORKDIR ${APP_DIR}

# Install necessary packages to run CKAN
RUN apk add --no-cache git \
    gettext \
    python \
    py-pip \
    py-gunicorn 

# Temporary packages to build CKAN requirements
RUN apk add --no-cache --virtual .build-deps \
    postgresql-client \
    postgresql-dev \
    gcc \
    musl-dev \
    python-dev

# Fetch CKAN and install
RUN mkdir ${APP_DIR}/src && cd ${APP_DIR}/src && \
    git clone -b ${GIT_BRANCH} --depth=1 --single-branch ${GIT_URL} ckan && \
    cd ckan && \
    cp who.ini ${APP_DIR} && \
    python setup.py install && \
    pip install --no-cache-dir testrepository && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    pip install --no-cache-dir html5lib==0.9999999

# Remove temporary packages and files
RUN apk del .build-deps && \
    rm -rf ${APP_DIR}/src

# Default Extensions
RUN pip install --no-cache-dir git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars

# Create and update CKAN config
RUN paster --plugin=ckan make-config ckan ${APP_DIR}/production.ini
RUN paster --plugin=ckan config-tool ${APP_DIR}/production.ini "ckan.plugins = ${CKAN__PLUGINS}"

EXPOSE 8000

CMD ["gunicorn", "--paste", "production.ini"]
