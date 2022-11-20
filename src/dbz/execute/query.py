'''
Created on Mar 11, 2022

@author: immanueltrummer
'''
import datetime
import re
import sqlglot.expressions


class Rewriter():
    """ Rewrites queries for better performance. """
    
    def rewrite(self, query):
        """ Rewrite input query.
        
        Args:
            query: an SQL query
        
        Returns:
            rewritten query
        """
        parsed = sqlglot.parse_one(query)
        where = parsed.args.get('where', None)
        if where is not None:
            where_pred = where.args['this']
            disjuncts = self._disjuncts(where_pred)
            if len(disjuncts) > 1:
                common = set(self._conjuncts(disjuncts[0]))
                for disjunct in disjuncts[1:]:
                    conjuncts = set(self._conjuncts(disjunct))
                    common = common.intersection(conjuncts)
                
                where_items = list(common) + [where_pred]
                new_where = self._conjunction(where_items)
                parsed.args['where'].args['this'] = new_where
        
        query = parsed.sql()
        query = self._fix_dates(query)
        query = self._strip_trailing_zeros(query)
        return query
    
    def _binary_operands(self, expression):
        """ Decompose binary expression into operands.
        
        Args:
            expression: binary expression
        
        Returns:
            list of operand expressions
        """
        return [expression.args['this']] + [expression.args['expression']]
    
    def _conjunction(self, predicates):
        """ Create conjunction of multiple predicates. 
        
        Args:
            predicates: a list of predicates
        
        Returns:
            a conjunction of input predicates
        """
        nr_predicates = len(predicates)
        if nr_predicates == 0:
            return sqlglot.parse_one('True')
        else:
            conjunction_sql = ' and '.join([f'({p.sql()})' for p in predicates])
            return sqlglot.parse_one(conjunction_sql)
    
    def _conjuncts(self, predicate):
        """ Extracts conjuncts from predicate.
        
        Args:
            predicate: parsed predicate
        
        Returns:
            list of conjuncts
        """
        if isinstance(predicate, sqlglot.expressions.And):
            operands = self._binary_operands(predicate)
            return [c for op in operands for c in self._conjuncts(op)]
        elif isinstance(predicate, sqlglot.expressions.Paren):
            operand = predicate.args['this']
            return self._conjuncts(operand)
        else:
            return [predicate.copy()]
    
    def _disjuncts(self, predicate):
        """ Extracts disjuncts from predicate.
        
        Args:
            predicate: parsed predicate
        
        Returns:
            list of disjuncts
        """
        if isinstance(predicate, sqlglot.expressions.Or):
            operands = self._binary_operands(predicate)
            return [d for op in operands for d in self._disjuncts(op)]
        elif isinstance(predicate, sqlglot.expressions.Paren):
            operand = predicate.args['this']
            return self._disjuncts(operand)
        else:
            return [predicate.copy()]
    
    def _fix_dates(self, query):
        """ Fix representation of dates for Java-based planner. 
        
        Args:
            query: SQL string generated by SqlGlot library
        
        Returns:
            SQL query without casts of constants to dates
        """
        dates = re.findall("CAST\('([\d-]*)' AS DATE\)", query)
        for date in dates:
            to_replace = f"CAST('{date}' AS DATE)"
            replace_by = f"date '{date}'"
            query = query.replace(to_replace, replace_by)

        return query
    
    def _strip_trailing_zeros(self, query):
        """ Remove trailing zeros from float constants. 
        
        Args:
            query: SQL query as string
        
        Returns:
            SQL query without trailing zeros in float constants
        """
        floats = re.findall('(\d*\.\d*)0*', query)
        for to_replace in floats:
            replace_by = to_replace
            while replace_by.endswith('0'):
                replace_by = replace_by[:-1]
            
            query = query.replace(to_replace, replace_by)
        return query


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
        for op in re.findall('avg\((.*)\)', s)]
    for avg_op in avg_ops:
        old_avg = f'avg({avg_op})'
        new_avg = f'avg(cast ({avg_op} as float))'
        query = query.replace(old_avg, new_avg)
    
    # TODO: move all simplifications into rewriter
    rewriter = Rewriter()
    rewritten = rewriter.rewrite(query)
    print(f'Rewritten Query: {rewritten}')
    return rewritten


if __name__ == '__main__':
    rewriter = Rewriter()
    query = "select sum(l_extendedprice* (1 - l_discount)) as revenue from lineitem, part where ( p_partkey = l_partkey and p_brand = 'Brand#12' and p_container in ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG') and l_quantity >= 1 and l_quantity <= 1 + 10 and p_size between 1 and 5 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON' ) or ( p_partkey = l_partkey and p_brand = 'Brand#23' and p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK') and l_quantity >= 10 and l_quantity <= 10 + 10 and p_size between 1 and 10 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON' ) or ( p_partkey = l_partkey and p_brand = 'Brand#34' and p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG') and l_quantity >= 20 and l_quantity <= 20 + 10 and p_size between 1 and 15 and l_shipmode in ('AIR', 'AIR REG') and l_shipinstruct = 'DELIVER IN PERSON' )"
    rewritten = rewriter.rewrite(query)
    print(rewritten)