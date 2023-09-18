
from __future__ import annotations

import typing

import itertools
import functools
import datetime

import xtuples as xt

import cython

# ---------------------------------------------------------------

DDT = typing.Union[datetime.date, datetime.datetime]

# ---------------------------------------------------------------

def is_date_strict(v):
    if isinstance(v, datetime.datetime):
        return False
    return isinstance(v, datetime.date)

# ---------------------------------------------------------------

def year(y, m = 1, d = 1):
    return datetime.date(y, m, d)

def month(y, m, d = 1):
    return datetime.date(y, m, d)

# ---------------------------------------------------------------

def unpack(ddt):
    if is_date_strict(ddt):
        d = ddt
        return d.year, d.month, d.day
    dt = ddt
    return (
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
    )
    
def unpack_date(ddt):
    return ddt.year, ddt.month, ddt.day

def unpack_time(ddt):
    assert not is_date_strict(ddt), ddt
    dt = ddt
    return (
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
        #
    )

# ---------------------------------------------------------------
