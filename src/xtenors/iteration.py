
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
    end: typing.Optional[
        typing.Union[datetime.date, datetime.datetime]
    ] = None,
):
    """
    >>> itr = iterate(year(2020), days(1))
    >>> xt.iTuple.n_from(itr, 2).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 1), datetime.date(2020, 1, 2))
    >>> itr.send(year(2020))
    (False, datetime.date(2019, 12, 31))
    >>> xt.iTuple.n_from(itr, 2).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 1), datetime.date(2020, 1, 2))
    >>> itr.send(days(-1))
    (False, datetime.date(2020, 1, 3))
    >>> xt.iTuple.n_from(itr, 2).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 2), datetime.date(2020, 1, 1))
    >>> itr.send(1)
    (False, datetime.date(2019, 12, 31))
    >>> next(itr)
    (True, datetime.date(2019, 12, 30))
    >>> itr.send(2)
    (False, datetime.date(2019, 12, 28))
    >>> next(itr)
    (True, datetime.date(2019, 12, 27))
    >>> itr.send(-5)
    (False, datetime.date(2020, 1, 1))
    >>> itr.send(lambda d: d.year != 2020)
    (False, datetime.date(2020, 1, 2))
    >>> next(itr)
    (False, datetime.date(2020, 1, 1))
    >>> itr.send(lambda d: (True, True))
    (False, datetime.date(2020, 1, 2))
    >>> list(itr)
    []
    """
    # NOTE: when sent a value, we step back one iter
    # so next(gen) is where we were when sent the value
    current = start
    if f is None:
        f = lambda dt: True
    done = False
    accept = True
    mask = False
    while not done:
        if not mask:
            f_current = f(current)
            if isinstance(f_current, bool):
                accept = f_current
                done = False
            else:
                accept, done = f_current
        if done:
            continue
        given: typing.Union[
            datetime.datetime,
            datetime.date,
            datetime.timedelta,
            typing.Callable,
        ] = yield accept, current
        if end is not None:
            done = end == current
        if given is None:
            current += step
            mask = False
            continue
        if given == 0:
            current -= step
        elif isinstance(given, int):
            current += step * given 
        elif isinstance(
            given, (datetime.datetime, datetime.date)
        ):
            current = given
            current -= step
        elif isinstance(given, datetime.timedelta):
            step = given
            current -= step
        elif isinstance(given, typing.Callable):
            f = given
            current -= step
        else:
            assert False, given
        mask = True
        accept = False

# ---------------------------------------------------------------

def direction(gen):
    """
    >>> itr = iterate(year(2020), days(1))
    >>> direction(itr)
    1
    >>> next(itr)
    (True, datetime.date(2020, 1, 1))
    >>> itr = iterate(year(2020), days(-1))
    >>> direction(itr)
    -1
    >>> next(itr)
    (True, datetime.date(2020, 1, 1))
    """
    # NOTE: be careful, needs to be at least len(2) before done
    _, v_r = next(gen)
    _ = gen.send(-2)
    _, v_l = next(gen)
    return 1 if v_r > v_l else -1

# ---------------------------------------------------------------

def between(
    start: typing.Union[datetime.date, datetime.datetime],
    end: typing.Union[datetime.date, datetime.datetime],
    step: datetime.timedelta,
    f: typing.Optional[typing.Callable] = None,
):
    """
    >>> xt.iTuple(between(year(2020), year(2020, d=3), days(1))).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 1), datetime.date(2020, 1, 2), datetime.date(2020, 1, 3))
    """

    if start < end:
        # assert timedelta sign is appropriate?
        f_accept = lambda current: current <= end
        f_done = lambda current: current > end
    else:
        # assert timedelta sign is appropriate?
        f_accept = lambda current: current >= end
        f_done = lambda current: current < end
    
    def f_wrapped(current):
        if f is None:
            accept = True
            done = False
        else:
            accept, done = f(current)
        return (
            accept and f_accept(current),
            done or f_done(current),
        )

    return iterate(start, step, f=f_wrapped)

# ---------------------------------------------------------------
