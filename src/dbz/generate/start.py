'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import collections
import dbz.generate.compose
import dbz.generate.debug
import dbz.generate.default
import dbz.generate.mine
import dbz.generate.operator
import dbz.generate.synthesize
import dbz.generate.task
import json
import logging
import openai
import os.path
import time
        

class Generator():
    """ Generates SQL processing engines via code synthesis. """
    
    def __init__(
            self, config_dir, engine_dir, 
            log_level, timeout_s, default_dir):
        """ Initialize generation of SQL processing engines. 
        
        Args:
            config_dir: directory containing configuration files
            engine_dir: generate engine in this directory
            log_level: level for logging during engine generation
            timeout_s: timeout for generation in seconds (or -1)
            default_dir: directory with default operator implementations
        """
        self.timeout_s = timeout_s        
        signatures_path = os.path.join(config_dir, 'signatures.json')
        synthesis_path = os.path.join(config_dir, 'synthesis.json')
        customization_dir = os.path.join(engine_dir, 'customization')
        customization_path = os.path.join(
            customization_dir, 
            'customization.json')
        
        self.code_cache_path = os.path.join(engine_dir, 'code_cache.json')
        self.history_path = os.path.join(engine_dir, 'history.json')
        self.sys_code_dir = os.path.join(engine_dir, 'system')
        user_code_dir = os.path.join(engine_dir, 'user')
        
        with open(synthesis_path) as file:
            synthesis = json.load(file)
        with open(customization_path) as file:
            custom = json.load(file)
    
        prompt_prefix = self._load_referenced_code(
            customization_dir, custom['prompt_prefix_path'])
        prompt_suffix = self._load_referenced_code(
            customization_dir, custom['prompt_suffix_path'])
        custom_code = self._load_referenced_code(
            customization_dir, custom['custom_code_path'])
        pre_code = prompt_prefix + '\n\n' + custom_code
        must_contain = custom['must_contain']
        
        logging.basicConfig(level=int(log_level))
        self.logger = logging.getLogger('all')
        self.logger.setLevel(int(log_level))
        
        if os.path.exists(self.code_cache_path):
            with open(self.code_cache_path) as file:
                code_cache = json.load(file)
        else:
            code_cache = {}

        self.operators = dbz.generate.operator.Operators()
        substitutions = custom['substitutions']
        self.tasks = dbz.generate.task.Tasks(synthesis, substitutions)
        self.synthesizer = dbz.generate.synthesize.Synthesizer(
            self.operators, substitutions, prompt_prefix, prompt_suffix)
        self.miner = dbz.generate.mine.CodeMiner(
            self.operators, user_code_dir, self.synthesizer, 
            code_cache, must_contain=must_contain)
        self.composer = dbz.generate.compose.Composer(
            synthesis, self.operators, self.tasks, pre_code)
        self.debugger = dbz.generate.debug.Debugger(self.composer)
        self.defaults = dbz.generate.default.DefaultOperators(
            signatures_path, default_dir, engine_dir)
    
    def start(self):
        self.start_s = time.time()
        self._init_operators()
        self._iterate()
        self._finalize()
    
    def _debug(self):
        """ """
        comp = self.composer.composition
        redo_ids_weighted = self.debugger.to_redo()
        redo_ids = [t for t, _ in redo_ids_weighted]
        
        for redo_id in redo_ids:
            for i in range(2):
                if self._timeout():
                    return False
                
                self.logger.info(f'Redoing {redo_id} from {redo_ids} ({i})')
                task = self.tasks.id2task[redo_id]
                code_id = self.miner.mine(task, comp)
                self.logger.info(f'Mined code ID: {code_id}')
            
                if code_id is not None:
                    success = self.composer.update(redo_id, code_id)
                    self.logger.info(f'Composer update successful: {success}.')
                    if success:
                        return True
            
            try:
                default_code = self.defaults.generate_default(redo_id)
                code_id = self.operators.add_op(redo_id, default_code)
                if code_id is not None:
                    success = self.composer.update(redo_id, code_id)
                    self.logger.info(f'Default update successful: {success}.')
                    if success:
                        return True
            except:
                self.logger.info(f'Failed generating default for {redo_id}.')
            
            self.logger.info(f'Added default operator for {redo_id}.')
            
            
        self.logger.info(f'Trying all default operators: {redo_ids}')
        updates = {}
        for redo_id in redo_ids:
            self.logger.info(f'Generating default operator for {redo_id} ...')
            try:
                default_code = self.defaults.generate_default(redo_id)
                code_id = self.operators.add_op(redo_id, default_code)
                assert code_id is not None
                updates[redo_id] = code_id
                self.logger.info(f'Added default operator for {redo_id}.')
            except:
                self.logger.info('Generation of default operator failed.')
        
        success = self.composer.multi_update(updates)
        self.logger.info(f'Composer multi-update successful: {success}.')
        
        if not success:
            print('Giving up - please add operator code in "user" directory!')
            print(f'Operators ranked by likelihood of mistake: {redo_ids}')

    
    def _init_operators(self):
        """ Create first versions of operator implementations. """
        composition = {}
        for gen_task in self.tasks.gen_tasks:
            self.miner.mine(gen_task, composition)
            task_id = gen_task['task_id']
            composition[task_id] = 0
        
        first_task = self.tasks.gen_tasks[0]
        first_task_id = first_task['task_id']
        self.composer.update(first_task_id, 0)
        
    def _iterate(self):
        """ Iteratively debug operator implementations. """
        round_ctr = 0
        success = True
        while success and not self.composer.finished():
            round_ctr += 1
            self.logger.info(f'Starting Debugging Round {round_ctr} ...')
    
            with open(self.code_cache_path, 'w') as file:
                json.dump(self.miner.code_cache, file)
            
            if self._timeout():
                break
            
            success = self._debug()
                
            sql_engine = self.composer.all_code()
            sql_engine_path = os.path.join(self.sys_code_dir, 'sql_engine.py')
            with open(sql_engine_path, 'w') as file:
                file.write(sql_engine)
        
    def _finalize(self):
        total_s = time.time() - self.start_s
        g_call = {"start_s":self.start_s, "total_s":total_s}
        history = {
            "genesis":[g_call],
            **self.tasks.call_history(),
            **self.composer.call_history(), 
            **self.miner.call_history(),
            **self.synthesizer.call_history(), 
            **self.debugger.call_history(),
            **self.defaults.call_history()
            }
        self._write_history(history, self.history_path)
    
    def _load_referenced_code(self, code_dir, file_name):
        """ Load code referenced via given key. 
        
        Args:
            code_dir: path of code directory
            file_name: name of code file (or empty)
        
        Returns:
            empty string for empty path, file content otherwise
        """
        if not file_name:
            return ''
        else:
            code_path = os.path.join(code_dir, file_name)
            with open(code_path) as file:
                return file.read()
    
    def _timeout(self):
        """ Check for timeout. 
        
        Returns:
            True iff a timeout occurred
        """
        total_s = time.time() - self.start_s
        if self.timeout_s > 0 and total_s > self.timeout_s:
            print('Reached Timeout!')
            return True
        else:
            return False

    def _write_history(self, history, history_path):
        """ Append history to file at given path.
        
        Args:
            history: append this history
            history_path: append to this file
        """
        prior_history = collections.defaultdict(lambda:[])
        if os.path.exists(history_path):
            with open (history_path) as file:
                prior_history = json.load(file)
        
        for component, calls in history.items():
            history[component] = prior_history[component] + calls
        
        with open(history_path, 'w') as file:
            json.dump(history, file)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('config_dir', type=str, help='Configuration directory')
    parser.add_argument('ai_key', type=str, help='Access key to OpenAI')
    parser.add_argument('engine_dir', type=str, help='Directory of new engine')
    parser.add_argument('log_level', type=str, help='Set logging level')
    parser.add_argument('timeout_s', type=int, help='Timeout in seconds or -1')
    parser.add_argument('default_dir', type=str, help='Default engine path')
    args = parser.parse_args()
    
    print(f'Using timeout {args.timeout_s} seconds!')
    
    openai.api_key = args.ai_key
    generator = Generator(
        args.config_dir, args.engine_dir, 
        args.log_level, args.timeout_s, 
        args.default_dir)
    generator.start()

    print('Process complete.')