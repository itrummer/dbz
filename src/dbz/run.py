'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import argparse
import dbz.engine
import dbz.util
import os
import prompt_toolkit

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=str, help='Path to data directory')
    parser.add_argument('lib_path', type=str, help='Path to library')
    parser.add_argument('python', type=str, help='Command for Python invocation')
    args = parser.parse_args()

    paths = dbz.util.DbzPaths(args.data_dir)
    engine = dbz.engine.DbzEngine(paths, args.lib_path, args.python)
    
    terminated = False
    while not terminated:
        user_input = prompt_toolkit.prompt('0>')
        print(f'Input: {user_input}')
        if user_input == 'quit':
            terminated = True
        else:
            try:
                engine.execute(user_input, 'query_result.csv')
                os.system('cat query_result.csv')
            except Exception as e:
                print(f'Exception: {e}')