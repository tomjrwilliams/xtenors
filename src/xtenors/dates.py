
from __future__ import annotations

import typing

import itertools
import functools
import datetime

import xtuples as xt

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
