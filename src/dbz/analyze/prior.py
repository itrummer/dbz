'''
Created on Nov 25, 2022

@author: immanueltrummer
'''
import argparse
import os
import time


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('script', type=str, help='Script for executing query')
    parser.add_argument('queries', type=str, help='Path to file with queries')
    parser.add_argument('timeout', type=str, help='Per-query timeout in seconds')
    args = parser.parse_args()

    with open(args.queries) as file:
        queries = file.read()
        queries = queries.split(';')
        print(queries)
    
    query_times = []
    for query in queries:
        command = f'timeout {args.timeout} ' + args.script + f' "{query}"'
        print(command)
        start_s = time.time()
        os.system(command)
        total_s = time.time() - start_s
        query_times += [total_s]
        print(f'Total Seconds: {total_s}')
    
    print('\n'.join([str(t) for t in query_times]))