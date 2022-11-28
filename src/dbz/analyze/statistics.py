'''
Created on Nov 27, 2022

@author: immanueltrummer
'''
import argparse
import collections
import json
import os.path
import statistics


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('engine_dir', type=str, help='Path to engine directory')
    args = parser.parse_args()
    
    history_path = os.path.join(args.engine_dir, 'history.json')
    with open(history_path) as file:
        history = json.load(file)
    
    nr_calls = len(history['genesis'])
    nr_interventions = nr_calls-1
    
    stats = {}
    # Analyzing breakdown by component
    for component, calls in history.items():
        nr_calls = len(calls)
        nr_calls_key = f'nr_calls_{component}'
        stats[nr_calls_key] = nr_calls
        
        total_s = sum(call['total_s'] for call in calls)
        total_s_key = f'total_s_{component}'
        stats[total_s_key] = total_s
    
    # Analyzing synthesized code
    s_calls = history['synthesizer']
    nr_generated_chars = sum(len(c['completion']) for c in s_calls)
    nr_processed_chars = sum(len(c['prompt']) for c in s_calls) + nr_generated_chars
    generated_lines = [l for c in s_calls for l in c['completion'].split('\n')]
    nr_generated_lines = len(l for l in generated_lines if l)
    stats['nr_generated_chars'] = nr_generated_chars
    stats['nr_processed_chars'] = nr_processed_chars
    stats['nr_generated_lines'] = generated_lines
    
    # More code generation analysis
    stats['embedding_chars'] = sum(c['nr_chars'] for c in stats['tasks'])
    temperatures = [c['temperature'] for c in history['miner']]
    stats['temperature'] = statistics.mean(temperatures)
    
    # Analyzing final code
    def code_size(code_path):
        """ Analyzes code path.
        
        Args:
            code_path: path to file containing code
        
        Returns:
            tuple: number of characters, number of lines
        """
        with open(code_path) as file:
            code = file.read()
            nr_chars = len(code)
            lines = [l for l in code.split('\n') if l]
            nr_lines = len(lines)
            return nr_chars, nr_lines
    
    engine_path = os.path.join(args.engine_dir, 'system', 'sql_engine.py')
    include_dir = os.path.join('src', 'dbz', 'include', 'run')
    function_path = os.path.join(include_dir, 'functions.py')
    imports_path = os.path.join(include_dir, 'imports.py')
    
    engine_chars, engine_lines = code_size(engine_path)
    function_chars, function_lines = code_size(function_path)
    imports_chars, imports_lines = code_size(imports_path)
    
    stats['final_chars'] = engine_chars - function_chars - imports_chars
    stats['final_lines'] = engine_lines - function_lines - imports_lines
    
    print(f'--- {args.engine_dir} ---')
    stats_items = list(stats.items())
    stats_items.sort(key=lambda i:i[0])
    for k, v in stats_items:
        print(f'{k}\t:{v}')