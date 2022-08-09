'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.synthesize
import json
import openai

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str, help='Path to synthesis')
    parser.add_argument('ai_key', type=str, help='Access key to OpenAI')
    parser.add_argument('table_nl', type=str, help='Table representation')
    parser.add_argument('column_nl', type=str, help='Column representation')
    args = parser.parse_args()
    
    openai.api_key = args.ai_key
    synthesizer = dbz.synthesize.Synthesizer(
        args.config, args.table_nl, args.column_nl)
    library, stats = synthesizer.synthesize()
    print('*** GENERATED LIBRARY ***')
    print(library)
    print('*** SYNTHESIS STATISTICS ***')
    print(stats)
    
    with open('library.py', 'w') as file:
        file.write(library)
    with open('synthesis_stats.json', 'w') as file:
        json.dump(stats, file)