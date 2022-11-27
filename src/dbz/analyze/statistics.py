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
    
    comp2time = {}
    for component, calls in history.items():
        total_s = sum(call['total_s'] for call in calls)
        comp2time[component] = total_s
    
    print(f'--- {args.engine_dir} ---')
    print(f'Nr. calls: {nr_calls}')
    print(f'Nr. interventions: {nr_interventions}')
    print(f'Time by Component: {comp2time}')