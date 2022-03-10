'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import argparse
import dbz.engine
import dbz.plan
import dbz.util
import sys

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=str, help='Path to data directory')
    args = parser.parse_args()

    paths = dbz.util.DbzPaths(args.data_dir)
    planner = dbz.plan.Planner(paths.tmp_dir, paths.planner)
    engine = dbz.engine.Engine('', args.data_dir, paths.tmp_dir)
    
    queries = dbz.util.load_queries(args.work_path)
    
    for idx, query in enumerate(queries, 1):
        print(f'Query index: {idx}')
        try:
            plan = planner.plan(query)
            code = engine.execute(plan)
            #print(code)
        except Exception as e:
            print(f'Exception: {e}', file=sys.stderr)