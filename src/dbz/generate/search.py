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

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('config', type=str, help='Path to synthesis')
    parser.add_argument('ai_key', type=str, help='Access key to OpenAI')
    parser.add_argument('table_nl', type=str, help='Table representation')
    parser.add_argument('column_nl', type=str, help='Column representation')
    parser.add_argument('tbl_post_nl', type=str, help='Table post-processing')
    parser.add_argument('null_nl', type=str, help='Representing NULL values')
    parser.add_argument('log_level', type=str, help='Set logging level')
    args = parser.parse_args()
    
    openai.api_key = args.ai_key
    with open(args.config) as file:
        config = json.load(file)
    logging.basicConfig(level=int(args.log_level))
    logger = logging.getLogger('all')
    logger.setLevel(int(args.log_level))

    tasks = dbz.generate.task.Tasks(config)
    operators = dbz.generate.operator.Operators()
    substitutions = {
        '<Table>':args.table_nl, 
        '<Column>':args.column_nl, 
        '<TablePost>':args.tbl_post_nl,
        '<Null>':args.null_nl
    }
    synthesizer = dbz.generate.synthesize.Synthesizer(operators, substitutions)
    miner = dbz.generate.mine.CodeMiner(operators, synthesizer)
    composer = dbz.generate.compose.Composer(config, operators, tasks)
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
        redo_tasks = debugger.to_redo()
        comp = composer.composition
        for task_id, _ in redo_tasks:
            logger.info(f'Redoing task {task_id}; context: {comp}')
            task = tasks.id2task[task_id]
            code_id = miner.mine(task, comp)
            logger.info(f'Mined code ID: {code_id}')
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