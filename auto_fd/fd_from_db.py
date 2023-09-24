import sys
from mysql.connector import Error
from tqdm import tqdm
from .utils import establish_db_connection, get_table_desc



def find_func_depend_in_table(db_connection, table_name):
    table_description = get_table_desc(db_connection, table_name)
    fields = table_description['fields']
    cursor = db_connection.cursor(buffered=True)

    tqdm.write(f'\nNow analyzing table \'{table_name}\'...')

    FDs = {}
    for i in tqdm(range(0, len(fields)), desc=f'Current table ({table_name})'):
        for j in tqdm(range(0, len(fields)), desc=f'Current field'):
            if (i == j):
                continue

            field_1 = fields[i]
            field_2 = fields[j]
            
            cursor.execute(f'SELECT {field_1}, COUNT(DISTINCT {field_2}) c FROM {table_name} GROUP BY {field_1} HAVING c > 1')

            # Functional dependency found: it's not the case that there's more than one value (field_2)
            # associated with field_1
            if (cursor.rowcount == 0):
                if field_1 in FDs:
                    FDs[field_1].append(field_2)
                else:
                    FDs[field_1] = [field_2]
    
    # Print results
    tqdm.write(f'\n### Results for \'{table_name}\' ###')
    tqdm.write('Primary key(s) in table: ' + ', '.join(map(str, table_description['primary_keys'])))
    if FDs:
        tqdm.write('Following functional dependencies found:')
        for g, d in FDs:
            tqdm.write(f'{g} -> {"".join(d)}')
    else:
        tqdm.write('No functional dependencies found.')
    
    return FDs


def find_fd_from_db(host, database, user, passwd, table_name):
    db_connection = establish_db_connection(host, database, user, str(passwd))
    try:
        fd = find_func_depend_in_table(db_connection, table_name)
        return fd
    except Error as err:
        sys.exit(f'An error occurred:\n{err}\nExiting...')

    finally:
        db_connection.close()
