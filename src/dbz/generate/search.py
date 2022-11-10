'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.generate.compose
import dbz.generate.debug
import dbz.generate.mine
import dbz.generate.operator
import dbz.generate.synthesize
import dbz.generate.task
import json
import logging
import openai
import os.path

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str, help='Path to synthesis')
    parser.add_argument('ai_key', type=str, help='Access key to OpenAI')
    parser.add_argument('custom', type=str, help='Path to customization file')
    parser.add_argument('log_level', type=str, help='Set logging level')
    parser.add_argument('code_cache', type=str, help='Path to code cache')
    args = parser.parse_args()
    
    openai.api_key = args.ai_key
    with open(args.config) as file:
        config = json.load(file)
    with open(args.custom) as file:
        custom = json.load(file)
    
    def load_referenced_code(code_path):
        """ Load code referenced via given key. 
        
        Args:
            code_path: path to code file (or empty)
        
        Returns:
            empty string for empty path, file content otherwise
        """
        if not code_path:
            return ''
        else:
            with open(code_path) as file:
                return file.read()

    prompt_code = load_referenced_code(custom['prompt_code_path'])
    custom_code = load_referenced_code(custom['custom_code_path'])
    
    logging.basicConfig(level=int(args.log_level))
    logger = logging.getLogger('all')
    logger.setLevel(int(args.log_level))
    
    if os.path.exists(args.code_cache):
        with open(args.code_cache) as file:
            code_cache = json.load(file)
    else:
        code_cache = {}

    tasks = dbz.generate.task.Tasks(config)
    operators = dbz.generate.operator.Operators()
    # Substitutions: <Table>, <Column>, <TablePost>, <Null>, 
    # <BooleanField>, <IntegerField>, <FloatField>, <StringField> 
    substitutions = custom['substitutions']
    synthesizer = dbz.generate.synthesize.Synthesizer(
        operators, substitutions, prompt_code)
    miner = dbz.generate.mine.CodeMiner(
        operators, synthesizer, code_cache)
    pre_code = prompt_code + '\n\n' + custom_code
    composer = dbz.generate.compose.Composer(
        config, operators, tasks, pre_code)
    debugger = dbz.generate.debug.Debugger(composer)
    
    composition = {}
    for gen_task in tasks.gen_tasks:
        miner.mine(gen_task, composition)
        task_id = gen_task['task_id']
        composition[task_id] = 0
    
    # TODO: Need to update this if ordering in composer
    first_task = tasks.gen_tasks[0]
    first_task_id = first_task['task_id']
    composer.update(first_task_id, 0)
    
    round_ctr = 0
    while not composer.finished():
        round_ctr += 1
        logger.info(f'Starting Debugging Round {round_ctr} ...')

        with open(args.code_cache, 'w') as file:
            json.dump(miner.code_cache, file)
        
        redo_tasks = debugger.to_redo()
        comp = composer.composition
        for task_id, _ in redo_tasks:
            logger.info(
                f'Redoing task {task_id} from {redo_tasks}; context: {comp}')
            task = tasks.id2task[task_id]
            code_id = miner.mine(task, comp)
            logger.info(f'Mined code ID: {code_id}')
            
            if code_id is not None:
                success = composer.update(task_id, code_id)
                logger.info(f'Composer update successful: {success}.')
                if success:
                    break
            
        if round_ctr % 10 == 0:
            code = composer.final_code()
            logger.info(f'Current Library:\n{code}')
    
    print('Process complete.')
    sql_engine = composer.final_code()
    with open('sql_engine.py', 'w') as file:
        file.write(sql_engine)