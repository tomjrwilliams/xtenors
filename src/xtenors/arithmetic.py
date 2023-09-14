

from __future__ import annotations

import abc
import typing

import operator
import itertools
import functools
import datetime
import calendar

import xtuples as xt

from .dates import *
from .units import *

from . import conventions
from . import iteration
from . import calendars


# ---------------------------------------------------------------

def overflow_date(y, m, d, flags = None):

    if flags is None:
        flags = conventions

    overflow = flags.get(conventions.Overflow)

    if overflow is None or overflow is conventions.Overflow.ERROR:
        return datetime.date(y, m, d)

    elif overflow is conventions.Overflow.NEXT:
        m += 1
        ys, m = divmod(m - 1, 12)
        m += 1
        y += ys
        return datetime.date(y, m, 1)

    elif overflow is conventions.Overflow.PREV:
        d_max = calendar.monthrange(y, m)[1]
        return datetime.date(y, m, d_max)

    assert False, overflow

def pack_date(y, m, d, flags = None):
    try:
        return datetime.date(y, m, d)
    except ValueError as e:
        if not "day is out of range for month" in str(e):
            raise e
        return overflow_date(y, m, d, flags = flags)

# ---------------------------------------------------------------

def add(
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
    iterator: typing.Optional[iteration.Iterator] = None,
    flags=None,
):
    """
    >>> ddt = datetime.date(2020, 1, 31)
    >>> add(ddt, months=1)
    Traceback (most recent call last):
     ...
    ValueError: day is out of range for month
    >>> _ = conventions.set(conventions.Overflow.PREV)
    >>> add(ddt, months=1)
    datetime.date(2020, 2, 29)
    >>> _ = conventions.set(conventions.Overflow.NEXT)
    >>> add(ddt, months=1)
    datetime.date(2020, 3, 1)
    """
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
            weeks=weeks,
        )

    days += weeks * 7

    if days != 0 and iterator is None:
        ddt = ddt + datetime.timedelta(days=days)
        y, m, d = unpack_date(ddt)

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
        y, m, d = unpack_date(end)

    else:
        y, m, d = unpack_date(ddt)

    y += years
    m += months

    years, m = divmod(m - 1, 12)

    m += 1
    y += years

    if is_date_strict(ddt):
        return pack_date(y, m, d, flags = flags)

    return datetime.datetime(
        *unpack_date(pack_date(y, m, d, flags = flags)),
        *unpack_time(ddt),
    )

# ---------------------------------------------------------------
