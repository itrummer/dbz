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
        parsed = parsed.transform(self._rewrite_select)
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
    
    def _common_preds(self, where):
        """ Extract common unary predicates from disjunctive where clause. 
        
        Args:
            where: where clause in tree representation
        
        Returns:
            list of predicates that appear in all disjuncts
        """
        disjuncts = self._disjuncts(where)
        if len(disjuncts) > 1:
            common = set(self._conjuncts(disjuncts[0]))
            for disjunct in disjuncts[1:]:
                conjuncts = set(self._conjuncts(disjunct))
                common = common.intersection(conjuncts)
            
            return list(common)
        else:
            return []
    
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
    
    def _rewrite_select(self, select):
        """ Rewrite select expression (leave others unchanged).
        
        Args:
            select: possible select expression as tree
        
        Returns:
            rewritten select expression or input node
        """
        if isinstance(select, sqlglot.expressions.Select):
            # select = select.copy()
            where = select.args.get('where', None)
            if where is not None:
                where_pred = where.args['this']
                common_preds = self._common_preds(where_pred)
                trans_preds = self._transitive_preds(where_pred)
                where_items = common_preds + trans_preds + [where_pred]
                new_where = self._conjunction(where_items)
                select.args['where'].args['this'] = new_where
        
        return select
    
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
    
    def _transitive_preds(self, where):
        """ Extracts transitive binary predicates.
        
        Args:
            where: where clause in tree representation
        
        Returns:
            list of transitive equality predicates
        """
        conjuncts = self._conjuncts(where)
        equalities = [
            c for c in conjuncts if isinstance(c,sqlglot.expressions.EQ)]
        # equalities = list(where.find_all(sqlglot.expressions.EQ))
        eq_ops_pairs = [set(self._binary_operands(eq)) for eq in equalities]
        all_ops = [op for eq in equalities for op in self._binary_operands(eq)]
        op2class = {op:set([op]) for op in all_ops}
        
        changed = True
        while changed:
            changed = False
            for eq in equalities:
                ops = self._binary_operands(eq)
                classes = [op2class[op] for op in ops]
                if ops[0] not in classes[1] or ops[1] not in classes[0]:
                    new_class = classes[0].union(classes[1])
                    for op in new_class:
                        op2class[op] = new_class
                    changed = True
        
        trans_preds = set()
        for eq_class in op2class.values():
            if len(eq_class) > 2:
                for op_1 in eq_class:
                    op_1_sql = op_1.sql()
                    for op_2 in eq_class:
                        op_2_sql = op_2.sql()
                        ops = set([op_1, op_2])
                        if not (op_1 == op_2) and \
                            op_1_sql < op_2_sql and \
                            not ops in eq_ops_pairs:
                            p = sqlglot.parse_one(f'{op_1_sql} = {op_2_sql}')
                            trans_preds.add(p)
        
        return list(trans_preds)
                            

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
    
    # Sum over products can exceed integer range due to scaling - fix:
    sum_ops = [
        op for s in re.split(',|from', query)
        for op in re.findall('sum\((.*\*.*\*.*)\)', s)]
    for sum_op in sum_ops:
        old_sum = f'sum({sum_op})'
        new_sum = f'sum(cast ({sum_op} as float))'
        query = query.replace(old_sum, new_sum)
    
    # TODO: move all simplifications into rewriter
    rewriter = Rewriter()
    rewritten = rewriter.rewrite(query)
    print(f'Rewritten Query: {rewritten}')
    return rewritten


if __name__ == '__main__':
    rewriter = Rewriter()
    #query = "select supp_nation, cust_nation, l_year, sum(volume) as revenue from ( select n1.n_name as supp_nation, n2.n_name as cust_nation, extract(year from l_shipdate) as l_year, l_extendedprice * (1 - l_discount) as volume from supplier, lineitem, orders, customer, nation n1, nation n2 where s_suppkey = l_suppkey and o_orderkey = l_orderkey and c_custkey = o_custkey and s_nationkey = n1.n_nationkey and c_nationkey = n2.n_nationkey and ( (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY') or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE') ) and l_shipdate between date '1995-01-01' and date '1996-12-31' ) as shipping group by supp_nation, cust_nation, l_year order by supp_nation, cust_nation, l_year"
    query = "select nation, o_year, sum(amount) as sum_profit from ( select n_name as nation, extract(year from o_orderdate) as o_year, l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount from part, supplier, lineitem, partsupp, orders, nation where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey and p_partkey = l_partkey and o_orderkey = l_orderkey and s_nationkey = n_nationkey and p_name like '%green%' ) as profit group by nation, o_year order by nation, o_year desc"
    rewritten = rewriter.rewrite(query)
    print(rewritten)