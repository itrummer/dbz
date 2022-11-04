'''
Created on Mar 11, 2022

@author: immanueltrummer
'''
import datetime
import re


def clean(query):
    """ Cleans up query representation.
    
    Args:
        query: raw SQL query
    
    Returns:
        SQL query after trimming
    """
    query = query.replace('\n', ' ')
    query = query.replace('\t', '')
    if 'select' in query:
        trim_before = query.index('select')
        return query[trim_before:]
    else:
        return ''

def load_queries(query_path):
    """ Load queries from a given file.
    
    Args:
        query_path: path to file containing queries
    
    Returns:
        cleaned-up queries
    """
    with open(query_path) as file:
        workload = file.read()
    workload = workload.replace('\n', ' ')
    queries = workload.split(';')
    queries = [clean(q) for q in queries]
    return [q for q in queries if q]

def plus_or_minus(operand1, operator, operand2):
    """ Auxiliary function for addition or subtraction.
    
    Args:
        operand1: first operand
        operator: either + or - (as string)
        operand2: second operand
    
    Returns:
        result of addition or subtraction
    """
    if operator == '+':
        return operand1 + operand2
    elif operator == '-':
        return operand1 - operand2
    else:
        raise ValueError(f'Unknown operator: {operator}')

def resolve_date(year, month, day, op, delta, unit):
    """ Resolve date expression into new date.
    
    Args:
        year: start year
        month: start month
        day: start day
        op: whether to add or subtract interval
        delta: how many units to add or subtract
        unit: what unit to subtract (e.g., days or months)
    
    Returns:
        new date obtained by resolving date expression
    """
    if unit == 'year':
        year = plus_or_minus(year, op, delta)
    elif unit == 'month':
        year_delta = delta // 12
        month_delta = delta - 12 * year_delta
        year = plus_or_minus(year, op, year_delta)
        month = plus_or_minus(month, op, month_delta)
        if month > 12:
            year += 1
            month -= 12
        elif month < 1:
            year -= 1
            month += 12
    elif unit == 'day':
        old_date = datetime.datetime(year, month, day)
        interval = datetime.timedelta(days=delta)
        if op == '+':
            new_date = old_date + interval
        elif op == '-':
            new_date = old_date - interval
        else:
            raise ValueError(f'Unknown operator: {op}')
        year = new_date.year
        month = new_date.month
        day = new_date.day
    else:
        raise ValueError(f'Unknown interval unit: {unit}')
    return f"date '{year}-{month}-{day}'"

def simplify(query):
    """ Simplify SQL query (e.g., eliminating constant expressions). 
    
    Args:
       query: an SQL query
    
    Returns:
        SQL query after simplification
    """
    matches = re.finditer(
        "date '(\d{4,4})-(\d{1,2})-(\d{1,2})' ([-+]) " +\
        "interval '(\d*)' (day|month|year)", query)
    for m in matches:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        op = m.group(4)
        delta = int(m.group(5))
        unit = m.group(6)
        new_date = resolve_date(year, month, day, op, delta, unit)
        query = query.replace(m.group(0), new_date)
    
    # TODO: this is a hack - use query parser instead
    avg_ops = [
        op for s in re.split(',|from', query) 
        for op in re.findall('avg\((.[^,(from)]*)\)', s)]
    for avg_op in avg_ops:
        old_avg = f'avg({avg_op})'
        new_avg = f'avg(cast ({avg_op} as float))'
        query = query.replace(old_avg, new_avg)
    
    return query