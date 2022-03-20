'''
Created on Mar 12, 2022

@author: immanueltrummer
'''
import argparse
import os
import pandas as pd

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('in_dir', type=str, help='Input directory with raw data')
    parser.add_argument('out_dir', type=str, help='Output directory')
    args = parser.parse_args()
    
    file_names = os.listdir(args.in_dir)
    for file_name in file_names:
        in_path = f'{args.in_dir}/{file_name}'
        if file_name.endswith('.tbl'):
            print(f'Processing file {file_name} ...')
            df = pd.read_csv(in_path, sep='|', header=None)
            df = df.iloc[:,:-1]
            out_path = f'{args.out_dir}/{file_name[:-3]}csv'
            df.to_csv(out_path, index=None, header=None)