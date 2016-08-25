import os
import sys
import subprocess


ckan_ini = os.environ.get('CKAN_INI', '/srv/app/production.ini')


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
        init_db()
        create_sysadmin()
