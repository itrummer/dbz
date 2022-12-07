'''
Created on Dec 6, 2022

@author: immanueltrummer
'''
import argparse
import json
import os.path


def read_input(data_path, p_type):
    """ Read operator input from file.
    
    Args:
        data_path: path to file on disk
        p_type: type of parameter
    
    Returns:
        input data from disk
    """
    assert p_type in [
        'table', 'column', 'list:int', 
        'list:string', 'value:int', 
        'value:string']
    if p_type == 'table':
        table = load_from_csv(data_path)
        return table
    elif p_type == 'column':
        table = load_from_csv(data_path)
        column = get_column(table, 0) 
        return column
    else:
        with open(data_path) as file:
            data = file.readlines()
        if 'int' in p_type:
            data = [int(i) for i in data]
        if 'value' in p_type:
            data = data[0]
        return data


def write_output(data, data_type, data_path):
    """ Writes output to file.
    
    Args:
        data: write this data to disk
        data_type: data type
        data_path: write data to this path
    """
    assert data_type in ['table', 'column']
    if data_type == 'column':
        data = create_table([data])
    write_to_csv(data, data_path)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('signatures', type=str, help='Path to signatures')
    parser.add_argument('task_id', type=str, help='Operator generation task')
    args = parser.parse_args()
    
    with open(args.signatures) as file:
        signatures = json.load(file)
    signature = signatures[args.task_id]
    
    inputs_data = []
    for p_idx, parameter in enumerate(signature['inputs']):
        in_path = f'p{p_idx}.csv'
        p_type = parameter['type']
        input_data = read_input(in_path, p_type)
        inputs_data += [input_data]
    
    function_name = signature['function_name']
    command = f'result = {function_name}(*inputs_data)'
    exec(command)
    
    outputs = signature['outputs']
    if outputs:
        result_type = outputs[0]['type']
        out_path = 'result.csv'
        write_output(result, result_type, out_path)