'''
Created on Nov 18, 2022

@author: immanueltrummer
'''
import argparse
import dbz.execute.engine
import dbz.util
import json
import os.path


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('benchmark', type=str, help='Path to benchmark file')
    parser.add_argument('engine', type=str, help='Path to operators')
    args = parser.parse_args()
    
    with open(args.benchmark) as file:
        benchmark = json.load(file)
    with open(args.engine) as file:
        operators = file.read()
        
    # sql_ref_info = benchmark['sql_ref']
    # pg_db = sql_ref_info['pg_db']
    # pg_user = sql_ref_info['pg_user']
    # pg_pwd = sql_ref_info['pg_pwd']
    # pg_host = sql_ref_info['host']
    # sql_ref = dbz.execute.engine.PgEngine(
        # pg_db, pg_user, pg_pwd, pg_host)
        
    test_access = benchmark['test_access']
    data_dir = test_access['data_dir']
    paths = dbz.util.DbzPaths(data_dir)
    python_path = test_access['python']
    engine = dbz.execute.engine.DbzEngine(
        paths, operators, python_path, True)
        
    queries = benchmark['queries']
    nr_queries = len(queries)
    
    for q_idx, query in enumerate(queries, 1):
        print(f'Executing Query {q_idx}/{nr_queries}: {query}')
        out_path = os.path.join(paths.tmp_dir, f'out{q_idx}')
        success = engine.execute(query, out_path)
        print(f'Execution Successful: {success}')

    results = {"benchmark":benchmark, "results":engine.stats}
    with open('benchmark_results.json', 'w') as file:
        json.dump(results, file)
    
    print('plan_s\ttotal_s\tsuccess')
    for stats in engine.stats:
        plan_s = stats['planning_s']
        total_s = stats['total_s']
        success = stats['success']
        print(f'{plan_s}\t{total_s}\t{success}')