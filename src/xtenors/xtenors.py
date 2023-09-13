

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
from . import arithmetic
from . import adjustments

# ---------------------------------------------------------------

@xt.nTuple.decorate()
class Tenor(typing.NamedTuple):
    
    Y: typing.Optional[int] = 0
    M: typing.Optional[int] = 0
    W: typing.Optional[int] = 0
    D: typing.Optional[int] = 0

    # h / m / s / ms / ... ?

    # adjust

    def add(self, ddt: DDT, iterator = None, adjust = False):
        return

    # deliberately no __add__
    # as what about iterator - force one to be explicit

# ---------------------------------------------------------------

# add tenor and tenor?

def add(ddt: DDT, tenor: Tenor, iterator=None, adjust=False):
    return tenor.add(ddt, iterator=iterator, adjust=adjust)

# ---------------------------------------------------------------
