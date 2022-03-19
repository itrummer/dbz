'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.synthesize
import openai

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str, help='Path to synthesis')
    parser.add_argument('ai_key', type=str, help='Access key to OpenAI')
    parser.add_argument('data_nl', type=str, help='Description of data')
    parser.add_argument('operator_nl', type=str, help='Description of operators')
    args = parser.parse_args()
    
    openai.api_key = args.ai_key
    synthesizer = dbz.synthesize.Synthesizer(
        args.config, args.data_nl, 
        args.operator_nl)
    library = synthesizer.synthesize()
    print(library)
    
    with open('library.py', 'w') as file:
        file.write(library)