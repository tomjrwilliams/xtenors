
from __future__ import annotations

import typing

import itertools
import functools
import datetime

import xtuples as xt

# ---------------------------------------------------------------

def microseconds(n):
    return datetime.timedelta(microseconds=n)
    
def milliseconds(n):
    return datetime.timedelta(milliseconds=n)
    
def seconds(n):
    return datetime.timedelta(seconds=n)

def minutes(n):
    return datetime.timedelta(minutes=n)

def hours(n):
    return datetime.timedelta(hours=n)

def days(n):
    return datetime.timedelta(days=n)
    
def weeks(n):
    return datetime.timedelta(weeks=n)

# ---------------------------------------------------------------