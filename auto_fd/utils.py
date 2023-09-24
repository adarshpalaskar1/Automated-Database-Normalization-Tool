import sys
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm

# Establish connection to MySQL-database
def establish_db_connection(host, database, user, password):
    try:
        connection = mysql.connector.connect(
            host = host,
            database = database,
            user = user,
            password = password,
            auth_plugin = 'mysql_native_password')
        if connection.is_connected():
            # Successfully connected to database. Return connection
            return connection

    except Error as err:
        # Couldn't connect to database. Print error message with more details
        sys.exit(f'Failed to connect to database:\n{err}')


def get_table_desc(db_connection, table_name):
    cursor = db_connection.cursor(dictionary=True)
    cursor.execute(f'DESCRIBE {table_name}')
    result = cursor.fetchall()

    if not result:
        raise Error(f'Table {table_name} couldn\'t be found.')

    fields = []
    primary_keys = []

    for row in result:
        field = row['Field']
        fields.append(field)
        
        if row['Key'] == 'PRI': # Check if field is primary key in table
            primary_keys.append(field)
    
    return {'fields': fields, 'primary_keys': primary_keys}
