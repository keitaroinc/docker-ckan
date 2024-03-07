"""
Copyright (c) 2016 Keitaro AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from multiprocessing import connection

import os
import sys
import subprocess
import psycopg2
from sqlalchemy.engine.url import make_url
import urllib.request, urllib.error, urllib.parse, base64
import re
import json
import time

ckan_ini = os.environ.get('CKAN_INI', '/srv/app/production.ini')

RETRY = 5

def check_db_connection(retry=None):

    print('[prerun] Start check_db_connection...')

    if retry is None:
        retry = RETRY
    elif retry == 0:
        print('[prerun] Giving up after 5 tries...')
        sys.exit(1)

    conn_str = os.environ.get('CKAN_SQLALCHEMY_URL', '')
    try:
        db_user = make_url(conn_str).username
        db_passwd = make_url(conn_str).password
        db_host = make_url(conn_str).host
        db_name = make_url(conn_str).database
        connection = psycopg2.connect(user=db_user,
                               host=db_host,
                               password=db_passwd,
                               database=db_name)

    except psycopg2.Error as e:
        print((str(e)))
        print('[prerun] Unable to connect to the database...try again in a while.')
        import time
        time.sleep(10)
        check_db_connection(retry = retry - 1)
    else:
        connection.close()

def check_solr_connection(retry=None):

    print('[prerun] Start check_solr_connection...')

    if retry is None:
        retry = RETRY
    elif retry == 0:
        print('[prerun] Giving up after 5 tries...')
        sys.exit(1)

    url = os.environ.get('CKAN_SOLR_URL', '')
    username = os.environ.get('CKAN_SOLR_USER', '')
    password = os.environ.get('CKAN_SOLR_PASSWORD', '')
    search_url = '{url}/schema/name?wt=json'.format(url=url)

    try:
        if not username:
            connection = urllib.request.urlopen(search_url)
        else:
            request = urllib.request.Request(search_url)
            base64string = base64.b64encode(bytes('%s:%s' % (username, password),'ascii'))
            request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))
            connection = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        print('[prerun] Unable to connect to solr...try again in a while.')
        import time
        time.sleep(10)
        check_solr_connection(retry = retry - 1)
    else:
        import re
        conn_info = connection.read()
        schema_name = json.loads(conn_info)
        if 'ckan' in schema_name['name']:
            print('[prerun] Succesfully connected to solr and CKAN schema loaded')
        else:
            print('[prerun] Succesfully connected to solr, but CKAN schema not found')
            sys.exit(1)
           
def init_db():

    print('[prerun] Start init_db...')

    db_command = ['ckan', '-c', ckan_ini, 'db', 'init']

    print('[prerun] Initializing or upgrading db - start using ckan db init')
    try:
        # run init scripts
        subprocess.check_output(db_command, stderr=subprocess.STDOUT)

        print('[prerun] Initializing or upgrading db - end')
    except subprocess.CalledProcessError as e:
        if 'OperationalError' in str(e.output):
            print(e.output.decode('utf-8'))
            print('[prerun] Database not ready, waiting a bit before exit...')
            import time
            time.sleep(5)
            sys.exit(1)
        else:
            print(e.output.decode('utf-8'))
            raise e
    print('[prerun] Initializing or upgrading db - finish')


def init_datastore():

    conn_str = os.environ.get('CKAN_DATASTORE_WRITE_URL')
    if not conn_str:
        print('[prerun] Skipping datastore initialization')
        return

    datastore_perms_command = ['ckan', '-c', ckan_ini, 'datastore',
                               'set-permissions']

    db_user = make_url(conn_str).username
    db_passwd = make_url(conn_str).password
    db_host = make_url(conn_str).host
    db_name = make_url(conn_str).database
    connection = psycopg2.connect(user=db_user,
                            host=db_host,
                            password=db_passwd,
                            database=db_name)
    cursor = connection.cursor()

    print('[prerun] Initializing datastore db - start')
    try:
        datastore_perms = subprocess.Popen(
            datastore_perms_command,
            stdout=subprocess.PIPE)

        perms_sql = datastore_perms.stdout.read()
        perms_sql = perms_sql.decode('utf-8')
        perms_sql = perms_sql.replace("@"+db_host, "")
        # Remove internal pg command as psycopg2 does not like it
        perms_sql = re.sub('\\\\connect \"(.*)\"', '', perms_sql)
        cursor.execute(perms_sql)
        for notice in connection.notices:
            print(notice)

        connection.commit()

        print('[prerun] Initializing datastore db - end')
        print((datastore_perms.stdout.read()))
    except psycopg2.Error as e:
        print('[prerun] Could not initialize datastore')
        print(e.decode('utf-8'))

    except subprocess.CalledProcessError as e:
        if 'OperationalError' in str(e.output):
            print(e.output.decode('utf-8'))
            print('[prerun] Database not ready, waiting a bit before exit...')
            time.sleep(5)
            sys.exit(1)
        else:
            print(e.output.decode('utf-8'))
            raise e
    finally:
        cursor.close()
        connection.close()


def create_sysadmin():

    print('[prerun] Start create_sysadmin...')

    name = os.environ.get('CKAN_SYSADMIN_NAME')
    password = os.environ.get('CKAN_SYSADMIN_PASSWORD')
    email = os.environ.get('CKAN_SYSADMIN_EMAIL')

    if name and password and email:

        # Check if user exists
        command = ['ckan', '-c', ckan_ini, 'user', 'show', name]

        out = subprocess.check_output(command)
        if 'User:None' not in re.sub(r'\s', '', out.decode('utf-8')):
            print('[prerun] Sysadmin user exists, skipping creation')
            return

        # Create user
        command = ['ckan', '-c', ckan_ini, 'user', 'add',
                   name,
                   'password=' + password,
                   'email=' + email]

        subprocess.call(command)
        print(('[prerun] Created user {0}'.format(name)))

        # Make it sysadmin
        command = ['ckan', '-c', ckan_ini, 'sysadmin', 'add',
                   name]

        subprocess.call(command)
        print(('[prerun] Made user {0} a sysadmin'.format(name)))

if __name__ == '__main__':

    maintenance = os.environ.get('MAINTENANCE_MODE', '').lower() == 'true'

    if maintenance:
        print('[prerun] Maintenance mode, skipping setup...')
    else:
        check_db_connection()
        check_solr_connection()
        init_db()
        if os.environ.get('CKAN_DATASTORE_WRITE_URL'):
            init_datastore()
        create_sysadmin()
