

from __future__ import annotations

import abc
import typing

import operator
import itertools
import functools
import datetime
import calendar

import cython

import xtuples as xt

from .dates import *
from .units import *

from . import conventions
from . import iterators
from . import calendars

# ---------------------------------------------------------------

ymd = dict(
    y=cython.int, 
    m=cython.int, 
    d=cython.int,
)
ym = dict(y=cython.int, m=cython.int)

# ---------------------------------------------------------------

@cython.cfunc
@cython.returns(tuple[cython.int, cython.int])
@cython.locals(
    **ym, years=cython.int, months=cython.int, _y=cython.int
)
def add_y_m_C(y, m, years, months):
    _y, m = divmod(m + months - 1, 12)
    return y + years + _y, m + 1
    
# ---------------------------------------------------------------

@cython.cfunc
@cython.returns(tuple[cython.int, cython.int, cython.int])
@cython.locals(
    **ymd, d_max=cython.int
)
def overflow_prev_C(y, m, d, d_max):

    if d > d_max:
        d = d_max

    return y, m, d

@cython.cfunc
@cython.returns(tuple[cython.int, cython.int, cython.int])
@cython.locals(
    **ymd, years=cython.int, d_max=cython.int
)
def overflow_next_C(y, m, d, d_max):

    if d > d_max:
        years, m = divmod(m + 1 - 1, 12)
        return y + years, m + 1, 1

    return y, m, d

# ---------------------------------------------------------------

def overflow_prev_py(y, m, d):
    d_max = calendar.monthrange(y, m)[1]
    return datetime.date(y, m, d_max)

def overflow_next_py(y, m, d):
    m += 1
    ys, m = divmod(m - 1, 12)
    m += 1
    y += ys
    return datetime.date(y, m, 1)

# ---------------------------------------------------------------

def add_time(
    ddt: DDT,
    hours=0,
    minutes=0,
    seconds=0,
    milliseconds=0,
    microseconds=0,
):
    if (
        seconds != 0
        or microseconds != 0
        or milliseconds != 0
        or minutes != 0
        or hours != 0
    ):
        assert not is_date_strict(ddt), ddt
        ddt = ddt + datetime.timedelta(
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
        )
    return ddt

def add_days(
    ddt,
    days,
    iterator=None,
):
    if days != 0 and iterator is None:
        ddt = ddt + datetime.timedelta(days=days)
        return unpack_date(ddt)

    elif days != 0:
        iterator, gen = iterator.update(
            start=(
                ddt
                if not isinstance(ddt, datetime.datetime)
                else ddt.date()
            ),
            step=days(1 if days > 0 else -1)
        )
        end = xt.iTuple.n_from(gen, days)[-1]
        return unpack_date(end)

    else:
        return unpack_date(ddt)

# ---------------------------------------------------------------

def is_error_day_range(e: Exception):
    return "day is out of range for month" in str(e)

# ---------------------------------------------------------------

def add_py(
    ddt: DDT,
    years=0,
    months=0,
    weeks=0,
    days=0,
    hours=0,
    minutes=0,
    seconds=0,
    milliseconds=0,
    microseconds=0,
    iterator: typing.Optional[iterators. Iterator] = None,
    overflow=None,
):
    """
    >>> ddt = datetime.date(2020, 1, 31)
    >>> add_py(ddt, months=1)
    Traceback (most recent call last):
     ...
    ValueError: day is out of range for month
    >>> add_py(ddt, months=1, overflow=conventions.Overflow.PREV)
    datetime.date(2020, 2, 29)
    >>> add_py(ddt, months=1, overflow=conventions.Overflow.NEXT)
    datetime.date(2020, 3, 1)
    """
    ddt = add_time(
        ddt,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds,
        microseconds=microseconds,
    )

    days += weeks * 7

    y, m, d = add_days(ddt, days, iterator=iterator)
    
    y += years
    m += months

    years, m = divmod(m - 1, 12)

    m += 1
    y += years

    try:
        return datetime.date(y, m, d)
    except Exception as e:
        if not is_error_day_range(e):
            raise e
        elif overflow is conventions.Overflow.NEXT:
            dt = datetime.date(*overflow_next_py(y, m, d))
        elif overflow is conventions.Overflow.PREV:
            dt = datetime.date(*overflow_prev_py(y, m, d))
        else:
            raise e

    if is_date_strict(ddt):
        return dt

    return datetime.datetime(
        *unpack_date(dt),
        *unpack_time(ddt),
    )

def add_C(
    ddt: DDT,
    years=0,
    months=0,
    weeks=0,
    days=0,
    hours=0,
    minutes=0,
    seconds=0,
    milliseconds=0,
    microseconds=0,
    iterator: typing.Optional[iterators. Iterator] = None,
    overflow=None,
):
    """
    >>> ddt = datetime.date(2020, 1, 31)
    >>> add_C(ddt, months=1)
    Traceback (most recent call last):
     ...
    ValueError: day is out of range for month
    >>> add_C(ddt, months=1, overflow=conventions.Overflow.PREV)
    datetime.date(2020, 2, 29)
    >>> add_C(ddt, months=1, overflow=conventions.Overflow.NEXT)
    datetime.date(2020, 3, 1)
    """
    ddt = add_time(
        ddt,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds,
        microseconds=microseconds,
    )

    days += weeks * 7

    y, m, d = add_days(ddt, days, iterator=iterator)

    y, m = add_y_m_C(y, m, years, months)

    try:
        return datetime.date(y, m, d)
    except Exception as e:
        if not is_error_day_range(e):
            raise e
        elif overflow is conventions.Overflow.NEXT:
            dt = datetime.date(*overflow_next_C(y, m, d))
        elif overflow is conventions.Overflow.PREV:
            d_max = calendar.monthrange(y, m)[1]
            dt = datetime.date(*overflow_prev_C(y, m, d, d_max))
        else:
            raise e

    if is_date_strict(ddt):
        return dt

    return datetime.datetime(
        *unpack_date(dt),
        *unpack_time(ddt),
    )

# ---------------------------------------------------------------

# add = add_C
add = add_py

# ---------------------------------------------------------------
