


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
from . import iterators
from . import calendars

# ---------------------------------------------------------------

# TODO: check signs

# TODO: check unmodified and m != m(valid) is error?

# ---------------------------------------------------------------

def adjust_date_forward(d, first_valid, iterator, modified = None):

    if d.month == first_valid.month:
        return first_valid
    
    elif (
        first_valid.month > d.month 
        and modified is conventions.Modified.MODIFIED
    ):
        _, gen = iterator.update(start=d, step = days(-1))
        _, prev_valid = next(gen)
        return prev_valid

    else:
        assert False, dict(
            d=d,
            first_valid=first_valid,
            modified=modified,
        )

def adjust_date_backward(d, first_valid, iterator, modified = None):

    if d.month == first_valid.month:
        return first_valid
    
    elif (
        first_valid.month < d.month 
        and modified is conventions.Modified.MODIFIED
    ):
        _, gen = iterator.update(start=d, step = days(1))
        _, next_valid = next(gen)
        return next_valid

    else:
        assert False, dict(
            d=d,
            first_valid=first_valid,
            modified=modified,
        )

# ---------------------------------------------------------------

def adjust(
    ddt,
    iterator,
    roll=None,
    modified = None,
):

    d = (
        ddt if not isinstance(ddt, datetime.datetime)
        else ddt.date()
    )

    _, gen = iterator.update(start=d, step = days(
        1 if roll is conventions.Roll.FOLLOWING
        else -1 if roll is conventions.Roll.PRECEDING
        else 0
    ))

    accept, first_valid = next(gen)

    if roll is None or roll is conventions.Roll.ERROR:
        assert accept and first_valid == d, dict(
            accept=accept,
            first_valid=first_valid,
            d=d,
        )
        res = d

    elif roll is conventions.Roll.PRECEDING:
        res = adjust_date_backward(
            d, first_valid, iterator, modified=modified
            #
        )

    elif roll is conventions.Roll.FOLLOWING:
        res = adjust_date_forward(
            d, first_valid, iterator, modified=modified
            #
        )

    else:
        assert False, roll

    if isinstance(ddt, datetime.datetime):
        return datetime.datetime.combine(res, ddt.time())

    return res

# ---------------------------------------------------------------

@xt.nTuple.decorate()
class Adjustment(typing.NamedTuple):

    iterator: iterators.Iterator
    overflow: typing.Optional[conventions.Overflow] = None
    roll: typing.Optional[conventions.Roll] = None
    modified: typing.Optional[conventions.Modified] = None

# ---------------------------------------------------------------
