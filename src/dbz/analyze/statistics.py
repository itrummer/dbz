'''
Created on Nov 27, 2022

@author: immanueltrummer
'''
import argparse
import json
import os.path


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
    generated_chars = sum(len(c['completion']) for c in s_calls)
    generated_lines = sum(c['completion'].count('\n') for c in s_calls)
    processed_chars = sum(len(c['prompt']) for c in s_calls) + generated_chars
    stats['generated_chars'] = generated_chars
    stats['generated_lines'] = generated_lines
    stats['processed_chars'] = processed_chars
    
    print(f'--- {args.engine_dir} ---')
    for k, v in stats.items():
        print(f'{k}\t:{v}')