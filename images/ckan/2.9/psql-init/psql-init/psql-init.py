"""
Copyright (c) 2020 Keitaro AB

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

import os
import sys
import subprocess
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extensions import AsIs
from sqlalchemy.engine.url import make_url


ckan_conn_str = os.environ.get('CKAN_SQLALCHEMY_URL', '')
datastorerw_conn_str = os.environ.get('CKAN_DATASTORE_WRITE_URL', '')
datastorero_conn_str = os.environ.get('CKAN_DATASTORE_READ_URL', '')

master_user = os.environ.get('PSQL_MASTER', '')
master_passwd = os.environ.get('PSQL_PASSWD', '')
master_database = os.environ.get('PSQL_DB', '')


class DB_Params:
    def __init__(self, conn_str):
        self.db_user = make_url(conn_str).username
        self.db_passwd = make_url(conn_str).password
        self.db_host = make_url(conn_str).host
        self.db_name = make_url(conn_str).database


def check_db_connection(db_params, retry=None):

    print('Checking whether database is up...')

    if retry is None:
        retry = 20
    elif retry == 0:
        print('Giving up...')
        sys.exit(1)

    try:
        con = psycopg2.connect(user=master_user,
                               host=db_params.db_host,
                               password=master_passwd,
                               database=master_database)

    except psycopg2.Error as e:
        print((str(e)))
        print('Unable to connect to the database...try again in a while.')
        import time
        time.sleep(30)
        check_db_connection(db_params, retry=retry - 1)
    else:
        con.close()


def create_user(db_params):
    con = None
    try:
        con = psycopg2.connect(user=master_user,
                               host=db_params.db_host,
                               password=master_passwd,
                               database=master_database)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        print("Creating user " + db_params.db_user.split("@")[0])
        cur.execute('CREATE ROLE "%s" ' +
                    'WITH ' +
                    'LOGIN NOSUPERUSER INHERIT ' +
                    'CREATEDB NOCREATEROLE NOREPLICATION ' +
                    'PASSWORD %s',
                    (AsIs(db_params.db_user.split("@")[0]),
                     db_params.db_passwd,))
    except(Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        cur.close()
        con.close()


def create_db(db_params):
    con = None
    try:
        con = psycopg2.connect(user=master_user,
                               host=db_params.db_host,
                               password=master_passwd,
                               database=master_database)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute('GRANT "' + db_params.db_user.split("@")
                    [0] + '" TO "' + master_user.split("@")[0] + '"')
        print("Creating database " + db_params.db_name + " with owner " +
              db_params.db_user.split("@")[0])
        cur.execute('CREATE DATABASE ' + db_params.db_name + ' OWNER "' +
                    db_params.db_user.split("@")[0] + '"')
        cur.execute('GRANT ALL PRIVILEGES ON DATABASE ' +
                    db_params.db_name + ' TO "' +
                    db_params.db_user.split("@")[0] + '"')
        if is_pg_buffercache_enabled(db_params) >= 1:
            # FIXME: This is a known issue with pg_buffercache access
            # For more info check this thread:
            # https://www.postgresql.org/message-id/21009351582737086%40iva6-22e79380f52c.qloud-c.yandex.net
            print("Granting privileges on pg_monitor to " +
                  db_params.db_user.split("@")[0])
            cur.execute('GRANT "pg_monitor" TO "' + db_params.db_user.split("@")[0] + '"')
    except(Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        cur.close()
        con.close()


def is_pg_buffercache_enabled(db_params):
    con = None
    result = None
    try:
        con = psycopg2.connect(user=master_user,
                               host=db_params.db_host,
                               password=master_passwd,
                               database=db_params.db_name)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute("SELECT count(*) FROM pg_extension " +
                    "WHERE extname = 'pg_buffercache'")
        result = cur.fetchone()
    except(Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        cur.close()
        con.close()
    return result[0]


def set_datastore_permissions(datastore_rw_params, datastore_ro_params, sql):
    con = None
    try:
        con = psycopg2.connect(user=master_user,
                               host=datastore_rw_params.db_host,
                               password=master_passwd,
                               database=datastore_rw_params.db_name)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute('GRANT CONNECT ON DATABASE ' +
                    datastore_rw_params.db_name +
                    ' TO ' + datastore_ro_params.db_user.split("@")[0])
        if is_pg_buffercache_enabled(datastore_rw_params) >= 1:
            print("Granting privileges on pg_monitor to " +
                  datastore_ro_params.db_user.split("@")[0])
            cur.execute('GRANT ALL PRIVILEGES ON TABLE pg_monitor TO ' +
                        datastore_ro_params.db_user.split("@")[0])
        print("Setting datastore permissions\n")
        print(sql)
        cur.execute(sql)
        print("Datastore permissions applied.")
    except Exception as error:
        print("ERROR DB: ", error)
    finally:
        cur.close()
        con.close()


if master_user == '' or master_passwd == '' or master_database == '':
    print("No master postgresql user provided.")
    print("Cannot initialize default CKAN db resources. Exiting!")
    sys.exit(1)

print("Master DB: " + master_database + " Master User: " + master_user)

ckan_db = DB_Params(ckan_conn_str)
datastorerw_db = DB_Params(datastorerw_conn_str)
datastorero_db = DB_Params(datastorero_conn_str)


# Check to see whether we can connect to the database, exit after 10 mins
check_db_connection(ckan_db)

try:
    create_user(ckan_db)
except(Exception, psycopg2.DatabaseError) as error:
    print("ERROR DB: ", error)

try:
    create_user(datastorerw_db)
except(Exception, psycopg2.DatabaseError) as error:
    print("ERROR DB: ", error)

try:
    create_user(datastorero_db)
except(Exception, psycopg2.DatabaseError) as error:
    print("ERROR DB: ", error)

try:
    create_db(ckan_db)
except(Exception, psycopg2.DatabaseError) as error:
    print("ERROR DB: ", error)

try:
    create_db(datastorerw_db)
except(Exception, psycopg2.DatabaseError) as error:
    print("ERROR DB: ", error)


def execute_sql_script(ckan_dbp, datastorero_dbp, datastorerw_dbp, script_path):
    # Connect to the database
    conn = psycopg2.connect(
        user=master_user,
        host=datastorerw_dbp.db_host,
        password=master_passwd,
        database=datastorerw_dbp.db_name
    )

    try:
        # Create a cursor
        cur = conn.cursor()

        # Execute the SQL script
        with open(script_path, 'r') as f:
            sql_script = f.read()

        # Replace placeholders with actual values
        
        sql_script = sql_script.replace('{datastoredb}', datastorerw_dbp.db_name)
        sql_script = sql_script.replace('{readuser}', datastorero_dbp.db_user)
        sql_script = sql_script.replace('{writeuser}', datastorerw_dbp.db_user)
        sql_script = sql_script.replace('{mainuser}', ckan_dbp.db_user)
        sql_script = sql_script.replace('{maindb}', ckan_dbp.db_name)

        print("CKAN DB User:", ckan_dbp.db_user)

        # Execute the SQL script
        cur.execute(sql_script)

        # Commit the changes
        conn.commit()

        print("SQL script executed successfully.")

        print("CKAN DB User:", ckan_dbp.db_user)
        print("read/write DB User:", datastorerw_dbp.db_user)
        print("read/write DB name:", datastorerw_dbp.db_name)
        print("read/write host:", datastorerw_dbp.db_host)
        print("read DB user:", datastorero_dbp.db_user)
        print("read DB name:", datastorero_dbp.db_name)

    except psycopg2.Error as e:
        print(f"Error executing SQL script: {str(e)}")

    finally:
        # Close the cursor and the connection
        cur.close()
        conn.close()

set_permissions = './set_permissions.sql'

# Print the current working directory
print("Current working directory:", os.getcwd())

# Check if the file exists
if os.path.isfile(set_permissions):
    print("File exists.")
    # Call the execute_sql_script function with the appropriate arguments
    execute_sql_script(ckan_db, datastorero_db, datastorerw_db, set_permissions)
else:
    print("File not found.")
