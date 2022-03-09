'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import argparse
import dbz.engine
import dbz.plan
import sys

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=str, help='Path to data directory')
    parser.add_argument('work_path', type=str, help='File containing queries')
    args = parser.parse_args()

    tmp_dir = f'{args.data_dir}/tmp'
    planner_jar = f'{args.data_dir}/Planner.jar'
    planner = dbz.plan.Planner(tmp_dir, planner_jar)
    engine = dbz.engine.Engine('', args.data_dir, tmp_dir)
    
    with open(args.work_path) as file:
        workload = file.read()
    queries = workload.split(';')
    def clean(query):
        query = query.replace('\n', ' ')
        query = query.replace('\t', '')
        if 'select' in query:
            trim_before = query.index('select')
            return query[trim_before:]
        else:
            return ''
    queries = [clean(q) for q in queries]
    queries = [q for q in queries if q]
    
    for idx, query in enumerate(queries, 1):
        print(f'Query index: {idx}')
        try:
            plan = planner.plan(query)
            code = engine.execute(plan)
            #print(code)
        except Exception as e:
            print(f'Exception: {e}', file=sys.stderr)