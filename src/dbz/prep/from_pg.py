'''
Created on Mar 19, 2022

@author: immanueltrummer
'''
import argparse
import psycopg2


def get_tables(connection):
    """ Returns tables found via given connection.
    
    Args:
        connection: connection to database
    
    Returns:
        list of table names
    """
    cursor = connection.cursor()
    cursor.execute(
        'select table_name from information_schema.tables ' +\
        'where table_schema = \'public\'')
    return [row[0] for row in cursor]


def get_cols_types(connection, table):
    """ Returns columns with types for given table.
    
    Args:
        connection: connection to Postgres database
        table: retrieve columns for this table
    
    Returns:
        list of tuples (column name, type, and numeric scale)
    """
    cursor = connection.cursor()
    cursor.execute(
        'select column_name, data_type, numeric_scale ' +\
        'from information_schema.columns ' +\
        f'where table_schema = \'public\' and table_name = \'{table}\' ' +\
        'order by ordinal_position')
    return [row for row in cursor]


def extract(connection, table, to_dir):
    """ Extract data from table and write normalized data to disk.
    
    Args:
        connection: connection to Postgres database
        table: extract data from this table
        to_dir: extract data to this directory
    """
    col_types = get_cols_types(connection, table)
    selects = []
    for col_name, col_type, scale in col_types:
        if col_type == 'date':
            selects += [f'{col_name} - date \'1970-01-01\'']
        elif scale is not None and scale > 0:
            selects += [f'round({col_name} * 1' + '0'*scale + ')']
        else:
            selects += [col_name]
    retrieval_query = f'select ' + ', '.join(selects) + ' from ' + table
    
    to_path = f'{to_dir}/{table}.csv'
    copy_query = f'COPY ({retrieval_query}) to STDOUT csv'
    cursor = connection.cursor()
    with open(to_path, 'w') as file:
        cursor.copy_expert(copy_query, file)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('db', type=str, help='Postgres database name')
    parser.add_argument('user', type=str, help='Postgres database user')
    parser.add_argument('pwd', type=str, help='Password for database')
    parser.add_argument('host', type=str, help='Host for Postgres database')
    parser.add_argument('to_dir', type=str, help='Target directory')
    args = parser.parse_args()
    
    with psycopg2.connect(
        database=args.db, user=args.user, 
        password=args.pwd, host=args.host) as connection:
        tables = get_tables(connection)
        for table in tables:
            extract(connection, table, args.to_dir)