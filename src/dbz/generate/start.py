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
        self.start_s = time.time()
        self.timeout_s = timeout_s
        signatures_path = os.path.join(config_dir, 'signatures.json')
        synthesis_path = os.path.join(config_dir, 'synthesis.json')
        customization_dir = os.path.join(engine_dir, 'customization')
        customization_path = os.path.join(
            customization_dir, 'customization.json')
        
        self.code_cache_path = os.path.join(engine_dir, 'code_cache.json')
        self.history_path = os.path.join(engine_dir, 'history.json')
        self.sys_code_dir = os.path.join(engine_dir, 'system')
        self.sql_engine_path = os.path.join(self.sys_code_dir, 'sql_engine.py')
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
            synthesis, self.operators, self.tasks, custom_code)
        self.debugger = dbz.generate.debug.Debugger(self.composer)
        self.defaults = dbz.generate.default.DefaultOperators(
            signatures_path, default_dir, engine_dir)
    
    def generate(self):
        """ Generate SQL execution engine. """
        self._init_operators()
        self._iterate()
        self._write_history()
    
    def _debug(self):
        """ Try debugging by replacing operator implementations.
        
        Returns:
            True if debugging was successful
        """
        comp = self.composer.composition
        redo_ids_weighted = self.debugger.to_redo()
        redo_ids = [t for t, _ in redo_ids_weighted]
        redo_ids = [t for t in redo_ids if self.operators.uses_default(comp, t)]
        assert redo_ids, 'Failed check involves only default operators!'
        
        for redo_id in redo_ids[:3]:
            # Does using default implementation fix the problem?
            if self._use_default_implementations(redo_id, 'test'):
                # Try synthesizing a new operator in that case
                for i in range(2):
                    if self._timeout():
                        return False
                
                    self.logger.info(f'Redoing {redo_id} from {redo_ids} ({i})')
                    task = self.tasks.id2task[redo_id]
                    code_id = self.miner.mine(task, comp)
                    self.logger.info(f'Mined code ID: {code_id}.')
                
                    if code_id is not None:
                        success = self.composer.update({redo_id:code_id}, 'optional')
                        self.logger.info(f'Composer update successful: {success}.')
                        if success:
                            return True
            
                # Fix problem by using default operator implementations
                success = self._use_default_implementations([redo_id], 'optional')
                self.logger.info(f'Default for {redo_id} - success: {success}.')
                if success:
                    return True
            
        # Last try: replace operator most likely to be faulty by default code
        self.logger.info(f'Giving up: replacing {redo_ids[0]} ...')
        success = self._use_default_implementations(redo_ids[:1], 'force')
        assert success, 'Forced update should always succeed!'
        return success
    
    def _init_operators(self):
        """ Create first implementation for each operator. """
        composition = {}
        for gen_task in self.tasks.gen_tasks:
            self.miner.mine(gen_task, composition)
            task_id = gen_task['task_id']
            composition[task_id] = 0
        
        first_task = self.tasks.gen_tasks[0]
        first_task_id = first_task['task_id']
        self.composer.update({first_task_id:0}, 'optional')
        
    def _iterate(self):
        """ Iteratively debug operator implementations. """
        round_ctr = 0
        success = True
        while success and not self.composer.finished() and not self._timeout():
            round_ctr += 1
            self.logger.info(f'Starting Debugging Round {round_ctr} ...')
    
            with open(self.code_cache_path, 'w') as file:
                json.dump(self.miner.code_cache, file)

            success = self._debug()

            sql_engine = self.composer.all_code()
            with open(self.sql_engine_path, 'w') as file:
                file.write(sql_engine)

    def _load_referenced_code(self, code_dir, file_name):
        """ Load code referenced via given key, removes last newline.
        
        Args:
            code_dir: path of code directory
            file_name: name of code file (or empty)
        
        Returns:
            empty string for empty path or file content without last newline
        """
        if not file_name:
            return ''
        else:
            code_path = os.path.join(code_dir, file_name)
            with open(code_path) as file:
                return file.read()[:-1]
    
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

    def _use_default_implementations(self, task_ids, mode):
        """ Replace operators with default implementations and try update.
        
        Args:
            task_ids: replace implementations for those operators
            mode: composer update mode ("force", "optional", "test")
        
        Returns:
            True iff the update was successful
        """
        self.logger.info(f'Using default for: {task_ids} (mode: {mode}).')
        updates = {}
        for task_id in task_ids:
            self.logger.info(f'Generating default operator for {task_id} ...')
            try:
                default_code = self.defaults.generate_default(task_id)
                code_id = self.operators.add_op(task_id, default_code)
                if code_id is None:
                    code_id = self.operators.get_code_id(default_code)
                
                self.operators.mark_default(task_id, code_id)
                self.logger.info(f'Default for {task_id}: code ID {code_id}.')
                updates[task_id] = code_id
            except:
                self.logger.info('Generation of default operator failed.')
        
        success = self.composer.update(updates, mode)
        self.logger.info(f'Composer update successful: {success}.')
        return success

    def _write_history(self):
        """ Append history of calls to various sub-functions to file. """
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
        
        prior_history = collections.defaultdict(lambda:[])
        if os.path.exists(self.history_path):
            with open (self.history_path) as file:
                prior_history = json.load(file)
        for component, calls in history.items():
            history[component] = prior_history[component] + calls
        
        with open(self.history_path, 'w') as file:
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
    generator.generate()

    print('Process complete.')