'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import argparse
import dbz.engine
import json

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('plan', type=str, help='Path to test plan')
    args = parser.parse_args()
    
    with open(args.plan) as file:
        plan = json.load(file)
        print(plan)
    
    engine = dbz.engine.Engine('', '/tmp', 'data')
    engine.execute(plan)