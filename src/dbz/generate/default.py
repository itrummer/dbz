'''
Created on Dec 6, 2022

@author: immanueltrummer
'''
import argparse
import json
import os.path


class DefaultOperators():
    """ Methods for generating default operator implementations. """
    
    def __init__(self, signatures_path, default_dir, target_dir):
        """ Initialize default operator implementations.
        
        Args:
            signatures_path: path to operator signatures
            default_dir: base operators on engine in this directory
            target_dir: create default operators in this directory
        """
        self.signatures_path = signatures_path
        with open(signatures_path) as file:
            self.signatures = json.load(file)
        self.operator_path = os.path.join(
            target_dir, 'system', 'default_operator.py')
        self._enable_defaults(default_dir, self.operator_path)
    
    def generate_default(self, task_id):
        """ Generate code of default operator implementation.
        
        Args:
            task_id: ID of operator generation task
        
        Returns:
            code invoking default operator
        """
        parts = []
        parts += ['import pandas as pd']
        parts += ['import os']
        signature = self.signatures[task_id]
        parts += [self._header(signature)]
        parts += [self._write_inputs(signature)]
        parts += [self._default_call(task_id)]
        parts += [self._return_outputs(signature)]
        return '\n'.join(parts)

    def _default_call(self, task_id):
        """ Generates code to call default operator implementation.
        
        Args:
            task_id: ID of operator generation task
        
        Returns:
            Code calling default operator implementation
        """
        parts = []
        parts += ['os.system("']
        parts += [self.operator_path]
        parts += [' ']
        parts += [self.signatures_path]
        parts += [' ']
        parts += [task_id]
        parts += ['")']
        return '\t' + ''.join(parts)

    def _enable_defaults(self, default_dir, operator_path):
        """ Create default operator implementation.
        
        Args:
            default_dir: directory containing default engine (a Python engine)
            operator_path: create default operator implementation here
        """
        sql_path = os.path.join(
            default_dir, 'system', 'sql_engine.py')
        wrapper_path = os.path.join(
            'src', 'dbz', 'include', 'default', 'wrapper.py')
        part_paths = [sql_path, wrapper_path]
        
        parts = []
        for part_path in part_paths:
            with open(part_path) as file:
                part = file.read()
                parts += [part]
        
        code = '\n'.join(parts)
        with open(operator_path, 'w') as file:
            file.write(code)
    
    def _header(self, signature):
        """ Generates header of function implementing default operator. 
        
        Args:
            signature: dictionary describing operator signature
        
        Returns:
            Header code of operator function
        """
        parts = []
        parts += ['def ']
        parts += [signature['function_name']]
        parts += ['(']
        parameters = [i['name'] for i in signature['inputs']]
        parts += ', '.join(parameters)
        parts += ['):']
        return ''.join(parts)
    
    def _return_outputs(self, signature):
        """ Read and return outputs of standard operator implementation.
        
        Args:
            signature: dictionary describing operator signature
        
        Returns:
            code for reading output, if any, from disk and returning it
        """
        parts = []
        outputs = signature['outputs']
        if outputs:
            if len(outputs) > 1:
                raise NotImplementedError(
                    f'Unsupported output signature: {outputs}')
            
            output = outputs[0]
            o_type = output['type']
            parts += [f'result = load_from_csv("result.csv")']
            if o_type == 'table':
                pass
            elif o_type == 'column':
                parts += ['result = get_column(result, 0)']
            else:
                raise NotImplementedError(f'Unknown output type: {o_type}')
            
            parts += ['return result']
        
        parts = [f'\t{p}' for p in parts]
        return '\n'.join(parts)
    
    def _write_inputs(self, signature):
        """ Generates code for writing operator input to disk.
        
        Args:
            signature: describes operator signature
        
        Returns:
            code writing operator inputs to disk
        """
        parts = []
        for p_idx, parameter in enumerate(signature['inputs']):
            p_name = parameter['name']
            p_type = parameter['type']
            file_name = f'p{p_idx}.csv'
            if p_type == 'table':
                parts += [f'write_to_csv({p_name}, "{file_name}")']
            elif p_type == 'column':
                parts += [f'table = create_table([{p_name}])']
                parts += [f'write_to_csv(table, "{file_name}")']
            elif p_type in [
                'list:int', 'list:string', 'value:int', 'value:string']:
                if 'value' in p_type:
                    parts += [f'{p_name} = [{p_name}]']
                parts += [
                    f'pd.Series({p_name}).to_csv("{file_name}", ' +\
                    'header=False, index=None)']
            else:
                raise NotImplementedError(f'No serialization for {p_type}')
        
        parts = [f'\t{p}' for p in parts]
        return '\n'.join(parts)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('signatures_path', type=str, help='Path to signatures')
    parser.add_argument('default_dir', type=str, help='Default engine directory')
    parser.add_argument('target_dir', type=str, help='Target engine directory')
    args = parser.parse_args()
    
    defaults = DefaultOperators(
        args.signatures_path, args.default_dir, 
        args.target_dir)
    code = defaults.generate_default('left_join')
    print(code)