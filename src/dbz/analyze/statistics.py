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
    total_s = sum(call['total_s'] for call in history['genesis'])
    
    print(f'--- {args.engine_dir} ---')
    print(f'Nr. calls: {nr_calls}')
    print(f'Time: {total_s} seconds')