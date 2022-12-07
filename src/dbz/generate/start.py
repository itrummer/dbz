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
        

def load_referenced_code(code_dir, file_name):
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


def timeout(start_s, timeout_s):
    """ Check for timeout, given start time and limit. 
    
    Args:
        start_s: start time in epoch seconds
        timeout_s: number of seconds until timeout
    
    Returns:
        True iff a timeout occurred
    """
    total_s = time.time() - start_s
    if timeout_s > 0 and total_s > timeout_s:
        print('Reached Timeout!')
        return True
    else:
        return False


def write_history(history, history_path):
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
    
    start_s = time.time()
    openai.api_key = args.ai_key

    signatures_path = os.path.join(args.config_dir, 'signatures.json')
    synthesis_path = os.path.join(args.config_dir, 'synthesis.json')
    customization_dir = os.path.join(args.engine_dir, 'customization')
    customization_path = os.path.join(customization_dir, 'customization.json')
    code_cache_path = os.path.join(args.engine_dir, 'code_cache.json')
    history_path = os.path.join(args.engine_dir, 'history.json')
    sys_code_dir = os.path.join(args.engine_dir, 'system')
    user_code_dir = os.path.join(args.engine_dir, 'user')
    
    with open(synthesis_path) as file:
        synthesis = json.load(file)
    with open(customization_path) as file:
        custom = json.load(file)

    prompt_prefix = load_referenced_code(
        customization_dir, custom['prompt_prefix_path'])
    prompt_suffix = load_referenced_code(
        customization_dir, custom['prompt_suffix_path'])
    custom_code = load_referenced_code(
        customization_dir, custom['custom_code_path'])
    pre_code = prompt_prefix + '\n\n' + custom_code
    
    logging.basicConfig(level=int(args.log_level))
    logger = logging.getLogger('all')
    logger.setLevel(int(args.log_level))
    
    if os.path.exists(code_cache_path):
        with open(code_cache_path) as file:
            code_cache = json.load(file)
    else:
        code_cache = {}

    operators = dbz.generate.operator.Operators()
    # Substitutions: <Table>, <Column>, <TablePost>, <Null>, 
    # <BooleanField>, <IntegerField>, <FloatField>, <StringField> 
    substitutions = custom['substitutions']
    tasks = dbz.generate.task.Tasks(synthesis, substitutions)
    synthesizer = dbz.generate.synthesize.Synthesizer(
        operators, substitutions, prompt_prefix, prompt_suffix)
    miner = dbz.generate.mine.CodeMiner(
        operators, user_code_dir, synthesizer, code_cache)
    composer = dbz.generate.compose.Composer(
        synthesis, operators, tasks, pre_code)
    debugger = dbz.generate.debug.Debugger(composer)
    defaults = dbz.generate.default.DefaultOperators(
        signatures_path, args.default_dir, sys_code_dir)
    
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
    success = True
    while success and not composer.finished():
        round_ctr += 1
        logger.info(f'Starting Debugging Round {round_ctr} ...')

        with open(code_cache_path, 'w') as file:
            json.dump(miner.code_cache, file)
        
        if timeout(start_s, args.timeout_s):
            break
        
        comp = composer.composition
        redo_tasks_weighted = debugger.to_redo()
        redo_tasks = [t for t, _ in redo_tasks_weighted]
        redo_iters = [(t_id, i) for t_id in redo_tasks for i in range(5)]
        
        for task_id, i in redo_iters:
            if timeout(start_s, args.timeout_s):
                break

            logger.info(f'Redoing {task_id} from {redo_tasks} ({i})')
            task = tasks.id2task[task_id]
            code_id = miner.mine(task, comp)
            logger.info(f'Mined code ID: {code_id}')
            
            if code_id is not None:
                success = composer.update(task_id, code_id)
                logger.info(f'Composer update successful: {success}.')
                if success:
                    break
        
        if not success:
            logger.info(f'Trying to generate default operators: {redo_tasks}')
            for redo_task in redo_tasks:
                logger.info(f'Generating default operator for {redo_task} ...')
                try:
                    default_code = defaults.generate_default(redo_task)
                    code_id = operators.add_op(redo_task, default_code)
                    assert code_id is not None
                    success = composer.update(redo_task, code_id)
                    logger.info(f'Composer update successful: {success}.')
                    if success:
                        break
                except:
                    logger.info('Generation of default operator failed.')
            
        if not success:
            print('Giving up - please add operator code in "user" directory!')
            print(f'Operators ranked by likelihood of mistake: {redo_tasks}')
            
        sql_engine = composer.all_code()
        sql_engine_path = os.path.join(sys_code_dir, 'sql_engine.py')
        with open(sql_engine_path, 'w') as file:
            file.write(sql_engine)

    total_s = time.time() - start_s
    g_call = {"start_s":start_s, "total_s":total_s}
    history = {
        "genesis":[g_call],
        **tasks.call_history(),
        **composer.call_history(), 
        **miner.call_history(),
        **synthesizer.call_history(), 
        **debugger.call_history()
        }
    write_history(history, history_path)
    print('Process complete.')