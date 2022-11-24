'''
Created on Mar 11, 2022

@author: immanueltrummer
'''
import datetime
import re
import sqlglot.expressions
import sqlglot.optimizer

from sqlglot.optimizer.annotate_types import annotate_types
from sqlglot.optimizer.canonicalize import canonicalize
from sqlglot.optimizer.eliminate_ctes import eliminate_ctes
from sqlglot.optimizer.eliminate_joins import eliminate_joins
from sqlglot.optimizer.eliminate_subqueries import eliminate_subqueries
from sqlglot.optimizer.expand_multi_table_selects import expand_multi_table_selects
from sqlglot.optimizer.isolate_table_selects import isolate_table_selects
from sqlglot.optimizer.merge_subqueries import merge_subqueries
from sqlglot.optimizer.normalize import normalize
from sqlglot.optimizer.optimize_joins import optimize_joins
from sqlglot.optimizer.pushdown_predicates import pushdown_predicates
from sqlglot.optimizer.pushdown_projections import pushdown_projections
from sqlglot.optimizer.qualify_columns import qualify_columns
from sqlglot.optimizer.qualify_tables import qualify_tables
from sqlglot.optimizer.quote_identities import quote_identities
from sqlglot.optimizer.unnest_subqueries import unnest_subqueries


class Rewriter():
    """ Rewrites queries for better performance. """
    
    def __init__(self, schema_path):
        """ Initialize query rewriter for given schema.
        
        Args:
            schema_path: path to file containing DDL commands
        """
        self.schema = self._read_schema(schema_path)
        print(self.schema)
    
    def rewrite(self, query):
        """ Rewrite input query.
        
        Args:
            query: an SQL query
        
        Returns:
            rewritten query
        """
        query = self._simplify_dates(query)
        ast = sqlglot.parse_one(query)
        
        rules = (
            qualify_tables,
            isolate_table_selects,
            qualify_columns,
            pushdown_projections,
            normalize,
            unnest_subqueries,
            expand_multi_table_selects,
            pushdown_predicates,
            optimize_joins,
            eliminate_subqueries,
            merge_subqueries,
            eliminate_joins,
            eliminate_ctes,
            annotate_types,
            canonicalize,
            quote_identities,
        )        
        ast = sqlglot.optimizer.optimize(ast, schema=self.schema, rules=rules)
        
        ast = ast.transform(self._rewrite_select)
        ast = ast.transform(self._rewrite_avg)
        ast = ast.transform(self._rewrite_sum)
        
        query = ast.sql()
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
        dates = re.findall("CAST\(\\'([\d-]*)\\' AS DATE\)", query)
        for date in dates:
            to_replace = f"CAST('{date}' AS DATE)"
            replace_by = f"date '{date}'"
            query = query.replace(to_replace, replace_by)

        return query
    
    def _plus_or_minus(self, operand1, operator, operand2):
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
    
    def _read_schema(self, schema_path):
        """ Parse database schema definition from file.
        
        Args:
            schema_path: path to database schema definition
        
        Returns:
            a dictionary mapping table names to column definitions
        """
        with open(schema_path) as file:
            ddl = file.read()
            ddl_statements = ddl.split(';')
        
        schema_dict = {}
        for sql in ddl_statements:
            parsed = sqlglot.parse_one(sql)
            if isinstance(parsed, sqlglot.expressions.Create):
                schema = parsed.args['this']
                if isinstance(schema, sqlglot.expressions.Schema):
                    table_name, cols = self._read_table_schema(schema)
                    schema_dict[table_name] = cols
        
        return schema_dict
    
    def _read_table_schema(self, schema):
        """ Parses DDL instructions creating a table.
        
        Args:
            schema: DDL statement creating table
        
        Returns:
            a tuple: table name, dictionary mapping column names to types
        """
        column_dict = {}
        schema_items = schema.args['expressions']
        for schema_item in schema_items:
            if isinstance(
                schema_item, sqlglot.expressions.ColumnDef):
                column_name = schema_item.args['this'].sql()
                data_type = schema_item.args['kind'].sql()
                column_dict[column_name] = data_type

        table_name = schema.args['this'].sql()
        return table_name, column_dict
    
    def _resolve_date(self, year, month, day, op, delta, unit):
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
            year = self._plus_or_minus(year, op, delta)
        elif unit == 'month':
            year_delta = delta // 12
            month_delta = delta - 12 * year_delta
            year = self._plus_or_minus(year, op, year_delta)
            month = self._plus_or_minus(month, op, month_delta)
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
    
    def _rewrite_avg(self, avg):
        """ Rewrite average aggregate (leaves others unchanged). 
        
        Args:
            avg: an average aggregate as tree
        
        Returns:
            rewritten average aggregate or input node
        """
        if isinstance(avg, sqlglot.expressions.Avg):
            avg_op = avg.args['this']
            casted_sql = f'avg(cast ({avg_op} as float))'
            return sqlglot.parse_one(casted_sql)
        
        return avg
    
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
    
    def _rewrite_sum(self, sum_):
        """ Rewrite sum aggregate by casting operand to float, if required.
        
        Due to scaling decimals, sum operands with multiple products caused
        an integer overflow.
        
        Args:
            sum_: possible sum aggregate as tree
        
        Returns:
            rewritten sum aggregate or input node
        """
        if isinstance(sum_, sqlglot.expressions.Sum):
            sum_operand = sum_.args['this']
            products = sum_operand.find_all(sqlglot.expressions.Mul)
            nr_products = len(list(products))
            if nr_products > 1:
                operand_sql = sum_operand.sql()
                casted_op_sum = f'sum(cast({operand_sql} as float))'
                return sqlglot.parse_one(casted_op_sum)
        
        return sum_
    
    def _simplify_dates(self, query):
        """ Replace relative by absolute dates in query.
        
        Args:
            query: replace relative dates in this query
        
        Returns:
            query with relative dates replaced
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
            new_date = self._resolve_date(
                year, month, day, op, delta, unit)
            query = query.replace(m.group(0), new_date)

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


if __name__ == '__main__':
    rewriter = Rewriter('data/schema/ddl.sql')
    #query = "select l_returnflag, l_linestatus, sum(l_quantity) as sum_qty, sum(l_extendedprice) as sum_base_price, sum(l_extendedprice * (1 - l_discount)) as sum_disc_price, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, avg(l_quantity) as avg_qty, avg(l_extendedprice) as avg_price, avg(l_discount) as avg_disc, count(*) as count_order from lineitem where l_shipdate <= date '1998-12-01' - interval '90' day group by l_returnflag, l_linestatus order by l_returnflag, l_linestatus"
    #query = "select supp_nation, cust_nation, l_year, sum(volume) as revenue from ( select n1.n_name as supp_nation, n2.n_name as cust_nation, extract(year from l_shipdate) as l_year, l_extendedprice * (1 - l_discount) as volume from supplier, lineitem, orders, customer, nation n1, nation n2 where s_suppkey = l_suppkey and o_orderkey = l_orderkey and c_custkey = o_custkey and s_nationkey = n1.n_nationkey and c_nationkey = n2.n_nationkey and ( (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY') or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE') ) and l_shipdate between date '1995-01-01' and date '1996-12-31' ) as shipping group by supp_nation, cust_nation, l_year order by supp_nation, cust_nation, l_year"
    query = "select nation, o_year, sum(amount) as sum_profit from ( select n_name as nation, extract(year from o_orderdate) as o_year, l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount from part, supplier, lineitem, partsupp, orders, nation where s_suppkey = l_suppkey and ps_suppkey = l_suppkey and ps_partkey = l_partkey and p_partkey = l_partkey and o_orderkey = l_orderkey and s_nationkey = n_nationkey and p_name like '%green%' ) as profit group by nation, o_year order by nation, o_year desc"
    #query = "SELECT n_name AS nation, EXTRACT(year FROM o_orderdate) AS o_year, l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity AS amount FROM part, supplier, lineitem, partsupp, orders, nation WHERE s_suppkey = l_suppkey AND ps_suppkey = l_suppkey AND ps_partkey = l_partkey AND p_partkey = l_partkey AND o_orderkey = l_orderkey AND s_nationkey = n_nationkey AND p_name LIKE '%green%'"
    #query = "select ps_partkey, sum(ps_supplycost * ps_availqty) as value_ from partsupp, supplier, nation where ps_suppkey = s_suppkey and s_nationkey = n_nationkey and n_name = 'GERMANY' group by ps_partkey having sum(ps_supplycost * ps_availqty) > ( select sum(ps_supplycost * ps_availqty) * 0.0001000000 from partsupp, supplier, nation where ps_suppkey = s_suppkey and s_nationkey = n_nationkey and n_name = 'GERMANY' ) order by value_ desc"
    rewritten = rewriter.rewrite(query)
    print(rewritten)
    # simplified = simplify(query)
    # print(simplified)