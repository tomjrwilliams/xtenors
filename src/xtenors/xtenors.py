

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
    D: typing.Optional[int] = 0

# ---------------------------------------------------------------
