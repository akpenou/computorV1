#from .parser import parse
from typing import List, Any, Optional, Tuple, Union, Set
import itertools
import sys
import os
import re

Term = Tuple[float, int]

def exists(item: Any) -> Any:
    """ Filter condition for true object.

    Args:
        item: item to test

    Returns:
        The item
    """
    return item


def input_error(message: str = 'Input equation error'):
    """ Exit the program wit error message.

    Args:
        message: error message to print
    """
    print(message)
    sys.exit(os.EX_DATAERR)


def find_op(string: str, op: str) -> Optional[List[int]]:
    """ Find all the occurences of op.

    Args:
        string: the string to evaluate
        op: the string to find

    Return:
        List of occurences index.
    """
    res = list()
    index = 0
    while op in string[index:]:
        index = string.index(op, index) 
        res.append(index)
        index += 1
    return res


def format_term(term: str) -> List[str]:
    """ Split the '=' of a term if exists.

    Args:
        term: term to evaluate

    Returns:
        List of '=' and term
    """
    res = list()
    if term.startswith('='):
        res.append('=')
        term = term[1:].strip()
    res.append(term)
    return res


def parse_term(term: str) -> Term:
    """ Parse term.

    Args:
        term: term to parse

    Returns:
        Tuple(Value, Power)
    """
    # Initialize attr if not exists
    if not hasattr(parse_term, 'sign'):
        parse_term.sign = 1
    if term == '=':
        parse_term.sign = -1
        return None

    term = term.replace(' ', '')
    if not re.fullmatch('[+-]?[0-9]+(?:\.[0-9]+)?(?:\*X(?:\^[0-9]+)?)?', term):
        input_error('bad term: ' + ' '.join(list(term)))
    value, power = term.split('*') if '*' in term else [term, 'X^0']
    value = float(value) * parse_term.sign 
    power = 1 if power == 'X' else int(power[2:])
    return (value, power)


def sort_power(terms: List[Term]) -> List[Term]:
    """ Group and sort terms by power.

    Args:
        terms: raw terms of the equation

    Returns:
        Sorted non zero coeficients.
    """
    res = dict()
    for value, power in terms:
        res[power] = value if not power in res else res[power] + value
    return sorted([ (v, k) for k, v in res.items() if v ], key = lambda x: x[1])


def parse(equation: str) -> List[Term]:
    """ Parse the equation.

    Args:
        equation: the equation to parse

    Returns:
        List of term
    """
    ops = filter(exists, map(lambda x: find_op(equation, x), ['+', '-', '=']))
    splitted = list()
    previous_index = 0
    for index in sorted(itertools.chain(*ops)):
        term = equation[previous_index:index].strip()
        previous_index = index
        splitted += format_term(term)
    splitted += format_term(equation[previous_index:])
    if sum([ 1 for item in splitted if item == '=' ]) != 1:
        input_error('missing equality')
    return sort_power(filter(exists, map(parse_term, filter(exists, splitted))))


def str_terms(terms: List[Term]) -> str:
    """ Make reduce form of terms equation.

    Args:
        terms: terms of the equation

    Returns:
        The reduce form string
    """
    res = list()
    for value, power in terms:
        res.append('{:+2.2f} * X ^ {:d}'.format(value, power))
    res += '=0'
    return ' '.join(res)


def get_coef(terms: List[Term]):
    """ Get coeficient.

    Args:
        terms: terms of the equation

    Returns:
        a coeficent array [c, b, a]
    """
    res = [0, 0, 0]
    for value, degree in terms:
        res[degree] = value
    return res


def second_degree(a: float, b: float, c: float)\
    -> Tuple[float, Union[Tuple[float, float], Set[float]]]:
    """ Solve 2nd degree equation.

    a * X ^ 2 + b * X + c = 0

    Args:
        a: coef of the equation
        b: coef of the equation
        c: coef of the equation

    Returns:
        delta, the result
    """
    delta = b ** 2 - 4 * a * c
    print('The delta is:', delta)
    if delta < 0:
        return delta, (-b / (2 * a), (-delta) ** .5 / (2 * a))
    return delta, ({(-b + delta ** .5) / (2 * a), (-b - delta ** .5) / (2 * a)})


def solve(terms: List[Term]):
    """ Solve the equation.

    Args:
        terms: terms of the equation
    """
    if not terms:
        print('Reduced form: 0 = 0')
        print('There is an infinity of solution')
        return
    print('Reduced form:', str_terms(terms))
    _, degree = max(terms, key = lambda x: x[1])
    print('Polynomial degree:', degree)
    if degree > 2:
        input_error()
    c, b, a = get_coef(terms)
    if degree == 2:
        delta, res = second_degree(a, b, c)
        if delta > 0:
            print('The solutions are:', res)
        elif not delta:
            print('The solution is:', res)
        else:
            print('The solution are:', res[0], u"\u00B1", res[1])
    elif degree == 1:
        print('The solution is:', -c / b if b else 'undifined')
    elif degree == 0:
        print('No solution')


if __name__ == '__main__':
    if len(sys.argv) not in [2]:
        print('usage: python3 {:s} equation'.format(sys.argv[0]))
        sys.exit(os.EX_USAGE)
    equation = sys.argv[1]
    solve(parse(equation))
