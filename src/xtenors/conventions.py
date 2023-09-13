
from __future__ import annotations

import enum
import contextlib

import typing

import operator
import itertools
import functools
import datetime

import xtuples as xt

from .dates import *
from .units import *


# ---------------------------------------------------------------

manager = xt.Flags()

def get(*enum_types):
    """
    >>> get(Overflow)
    >>> set(Overflow.NEXT)
    <Overflow.NEXT: 1>
    >>> get(Overflow)
    <Overflow.NEXT: 1>
    >>> with context(Overflow.PREV) as overflow:
    ...     print(overflow)
    ...     print(get(Overflow))
    Overflow.PREV
    Overflow.PREV
    >>> get(Overflow)
    <Overflow.NEXT: 1>
    >>> get(Overflow, Format)
    iTuple(<Overflow.NEXT: 1>, None)
    >>> set(Format.ISO)
    <Format.ISO: 0>
    >>> get(Overflow, Format)
    iTuple(<Overflow.NEXT: 1>, <Format.ISO: 0>)
    """
    return manager.get(*enum_types)

def set(*enum_instances):
    return manager.set(*enum_instances)

def context(*enum_instances):
    return manager.context(*enum_instances)

# ---------------------------------------------------------------

class Overflow(enum.Enum):
    ERROR = 0
    PREV = -1
    NEXT = 1

class Roll(enum.Enum):
    ERROR = 0
    PRECEDING = -1
    FOLLOWING = 1

class Modified(enum.Enum):
    UNMODIFIED = 0
    MODIFIED = 1

class Format(enum.Enum):
    ISO = 0

# ---------------------------------------------------------------

