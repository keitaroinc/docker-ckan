import os
import sys
import subprocess
import psycopg2
import urllib2


ckan_ini = os.environ.get('CKAN_INI', '/srv/app/production.ini')

RETRY = 5

def check_db_connection(retry=None):

    if retry is None:
        retry = RETRY
    elif retry == 0:
        print '[prerun] Giving up after 5 tries...'
        sys.exit(1)

    conn_str = os.environ.get('CKAN_SQLALCHEMY_URL', '')
    try:
        connection = psycopg2.connect(conn_str)

    except psycopg2.Error as e:
        print str(e)
        print '[prerun] Unable to connect to the database...try again in a while.'
        import time
        time.sleep(10)
        check_db_connection(retry = retry - 1)
    else:
        connection.close()

def check_solr_connection(retry=None):

    if retry is None:
        retry = RETRY
    elif retry == 0:
        print '[prerun] Giving up after 5 tries...'
        sys.exit(1)

    url = os.environ.get('CKAN_SOLR_URL', '')
    search_url = '{url}/select/?q=*&wt=json'.format(url=url)

    try:
        connection = urllib2.urlopen(search_url)
    except urllib2.URLError as e:
        print str(e)
        print '[prerun] Unable to connect to solr...try again in a while.'
        import time
        time.sleep(10)
        check_solr_connection(retry = retry - 1)
    else:
        eval(connection.read())


def init_db():

    db_command = ['paster', '--plugin=ckan', 'db',
                  'init', '-c', ckan_ini]
    print '[prerun] Initializing or upgrading db - start'
    try:
        subprocess.check_output(db_command, stderr=subprocess.STDOUT)
        print '[prerun] Initializing or upgrading db - end'
    except subprocess.CalledProcessError, e:
        if 'OperationalError' in e.output:
            print e.output
            print '[prerun] Database not ready, waiting a bit before exit...'
            import time
            time.sleep(5)
            sys.exit(1)
        else:
            print e.output
            raise e


def create_sysadmin():

    name = os.environ.get('CKAN_SYSADMIN_NAME')
    password = os.environ.get('CKAN_SYSADMIN_PASSWORD')
    email = os.environ.get('CKAN_SYSADMIN_EMAIL')

    if name and password and email:

        # Check if user exists
        command = ['paster', '--plugin=ckan', 'user', name, '-c', ckan_ini]

        out = subprocess.check_output(command)
        if 'User: \nNone\n' not in out:
            print '[prerun] Sysadmin user exists, skipping creation'
            return

        # Create user
        command = ['paster', '--plugin=ckan', 'user', 'add',
                   name,
                   'password=' + password,
                   'email=' + email,
                   '-c', ckan_ini]

        subprocess.call(command)
        print '[prerun] Created user {0}'.format(name)

        # Make it sysadmin
        command = ['paster', '--plugin=ckan', 'sysadmin', 'add',
                   name,
                   '-c', ckan_ini]

        subprocess.call(command)
        print '[prerun] Made user {0} a sysadmin'.format(name)


if __name__ == '__main__':

    maintenance = os.environ.get('MAINTENANCE_MODE', '').lower() == 'true'

    if maintenance:
        print '[prerun] Maintenance mode, skipping setup...'
    else:
        check_db_connection()
        check_solr_connection()
        init_db()
        create_sysadmin()
