'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.engine
import dbz.synthesize
import dbz.util
import openai

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('pg_user', type=str, help='Postgres DBMS user')
    parser.add_argument('pg_pwd', type=str, help='Postgres password')
    parser.add_argument('pg_db', type=str, help='Postgres database name')
    parser.add_argument('data_dir', type=str, help='Directory containing data')
    parser.add_argument('workload', type=str, help='Path to workload file')
    parser.add_argument('data_nl', type=str, help='Description of data')
    parser.add_argument('operator_nl', type=str, help='Description of operators')
    parser.add_argument('ai_key', type=str, help='Access key to OpenAI')
    parser.add_argument('python', type=str, help='Python command')
    args = parser.parse_args()
    
    openai.api_key = args.ai_key
    paths = dbz.util.DbzPaths(args.data_dir, args.python)
    queries = dbz.util.load_queries(args.workload)
    # synthesizer = dbz.synthesize.Synthesizer(
        # paths.config, args.data_nl, args.operator_nl)
    # library = synthesizer.synthesize()
    # print(library)
    # engine = dbz.engine.DbzEngine(paths, library)
    engine = dbz.engine.DbzEngine(paths, '')
    for idx, query in enumerate(queries, 1):
        engine.execute(query, f'result_{idx}')