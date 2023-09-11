
from __future__ import annotations

import typing

import itertools
import functools
import datetime

import xtuples as xt

from .dates import *
from .units import *

# ---------------------------------------------------------------

def iterate(
    start: typing.Union[datetime.date, datetime.datetime],
    step: datetime.timedelta,
    f: typing.Optional[typing.Callable] = None,
    i_max = 10 ** 3
    # NOTE: f should tuple: (done, accept)
):
    """
    >>> itr = iterate(year(2020), days(1))
    >>> list(zip(itr, range(2)))
    [(datetime.date(2020, 1, 1), 0), (datetime.date(2020, 1, 2), 1)]
    >>> itr.send(year(2020))
    datetime.date(2020, 1, 1)
    >>> list(zip(itr, range(2)))
    [(datetime.date(2020, 1, 2), 0), (datetime.date(2020, 1, 3), 1)]
    >>> itr.send(days(-1))
    datetime.date(2020, 1, 3)
    >>> list(zip(itr, range(2)))
    [(datetime.date(2020, 1, 2), 0), (datetime.date(2020, 1, 1), 1)]
    >>> itr.send(lambda d: (d.year != 2019, False))
    datetime.date(2020, 1, 1)
    >>> next(itr)
    datetime.date(2018, 12, 31)
    >>> itr.send(lambda d: (True, True))
    Traceback (most recent call last):
     ...
    StopIteration
    >>> list(itr)
    []
    """
    current = start
    if f is not None:
        accept, done = f(current)
        it = 0
        while not accept and not done:
            current += step
            accept, done = f(current)
            it += 1
            assert it < i_max
    prev = None
    while not done:
        given: typing.Union[
            datetime.datetime,
            datetime.date,
            datetime.timedelta,
            typing.Callable,
        ] = yield current
        if given is None:
            current += step
        elif isinstance(
            given, (datetime.datetime, datetime.date)
        ):
            current = given - step
        elif isinstance(given, datetime.timedelta):
            # current -= step
            step = given
        elif isinstance(given, typing.Callable):
            current -= step
            f = given
        else:
            assert False, given
        if f is not None:
            accept, done = f(current)
            it = 0
            while not accept and not done:
                current += step
                accept, done = f(current)
                it += 1
                assert it < i_max
        prev = current
# ---------------------------------------------------------------

def between(
    start: typing.Union[datetime.date, datetime.datetime],
    end: typing.Union[datetime.date, datetime.datetime],
    step: datetime.timedelta,
):
    """
    >>> list(between(year(2020), year(2020, d=3), days(1)))
    [datetime.date(2020, 1, 1), datetime.date(2020, 1, 2), datetime.date(2020, 1, 3)]
    """
    if start < end:
        # assert timedelta sign is appropriate?
        f = lambda current: (current <= end, current > end)
    else:
        # assert timedelta sign is appropriate?
        f = lambda current: (current >= end, current < end)
    return iterate(start, step, f=f)

# ---------------------------------------------------------------
