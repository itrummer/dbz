'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.util
import psycopg2

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('pg_user', type=str, help='Postgres DBMS user')
    parser.add_argument('pg_pwd', type=str, help='Postgres password')
    parser.add_argument('pg_db', type=str, help='Postgres database name')
    parser.add_argument('data_dir', type=str, help='Directory containing data')
    parser.add_argument('workload', type=str, help='Path to workload file')
    args = parser.parse_args()
    
    queries = dbz.util.load_queries(args.workload)
    