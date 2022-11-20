'''
Created on Nov 18, 2022

@author: immanueltrummer
'''
import argparse
import dbz.execute.check
import dbz.execute.engine
import dbz.util
import json


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('benchmark', type=str, help='Path to benchmark file')
    parser.add_argument('engine', type=str, help='Path to operators')
    args = parser.parse_args()
    
    with open(args.benchmark) as file:
        benchmark = json.load(file)
    with open(args.engine) as file:
        operators = file.read()
        
    sql_ref_info = benchmark['sql_ref']
    pg_db = sql_ref_info['pg_db']
    pg_user = sql_ref_info['pg_user']
    pg_pwd = sql_ref_info['pg_pwd']
    pg_host = sql_ref_info['host']
    sql_ref = dbz.execute.engine.PgEngine(
        pg_db, pg_user, pg_pwd, pg_host, True)
        
    test_access = benchmark['test_access']
    data_dir = test_access['data_dir']
    paths = dbz.util.DbzPaths(data_dir)
    python_path = test_access['python']
    engine_to_benchmark = dbz.execute.engine.DbzEngine(
        paths, operators, python_path, True)

    validator = dbz.execute.check.Validator(paths, sql_ref)        
    queries = benchmark['queries']
    nr_queries = len(queries)
    
    for q_idx, query in enumerate(queries, 1):
        print(f'Executing Query {q_idx}/{nr_queries}: {query}')
        check = {'type':'sql', 'query':query}
        valid = validator.validate(engine_to_benchmark, check)
        if not valid:
            raise Exception('Validation not successful!')

    results = {
        "benchmark":benchmark, 
        "test_results":engine_to_benchmark.stats,
        "ref_results":sql_ref.stats}
    with open('benchmark_results.json', 'w') as file:
        json.dump(results, file)
    
    print('Results for test engine:')
    engine_to_benchmark.print_stats()
    print('---')
    print('Results for reference engine:')
    sql_ref.print_stats()