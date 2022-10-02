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
    parser.add_argument('log_level', type=str, help='Set logging level')
    args = parser.parse_args()
    
    openai.api_key = args.ai_key
    with open(args.config) as file:
        config = json.load(file)
    logging.basicConfig(level=args.log_level)

    tasks = dbz.generate.task.Tasks(config)
    operators = dbz.generate.operator.Operators()
    synthesizer = dbz.generate.synthesize.Synthesizer(
        operators, args.table_nl, args.column_nl, args.tbl_post_nl)
    miner = dbz.generate.mine.CodeMiner(operators, synthesizer)
    composer = dbz.generate.compose.Composer(config, operators, tasks)
    debugger = dbz.generate.debug.Debugger(composer)
    
    for gen_task in tasks.gen_tasks:
        miner.mine(gen_task)
    first_task = tasks.gen_tasks[0]
    first_task_id = first_task['task_id']
    composer.update(first_task_id, 0)
    
    while not composer.finished():
        task_id = debugger.to_redo()
        logging.info(f'Redoing task {task_id}')
        task = tasks.id2task[task_id]
        code_id = miner.mine(task)
        logging.info(f'Mined code ID: {code_id}')
        composer.update(task_id, code_id)
        logging.info('Composer update completed.')
    
    print('Process complete.')
    sql_engine = composer.final_code()
    with open('sql_engine.py', 'w') as file:
        file.write(sql_engine)