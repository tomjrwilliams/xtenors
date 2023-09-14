

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

    # deliberately no __add__
    # as what about iterator - force one to be explicit
    
    Y: typing.Optional[int] = 0
    M: typing.Optional[int] = 0
    W: typing.Optional[int] = 0
    D: typing.Optional[int] = 0

    # h / m / s / ms / ... ?

    # adjust

    def add(
        self: Tenor,
        ddt: typing.Union[DDT, Tenor],
        iterator: typing.Optional[iteration.Iterator] = None,
        adjust: bool = False,
        flags=None,
    ):
        return add(
            ddt,
            self,
            iterator=iterator,
            adjust=adjust,
            flags=flags,
        )

# ---------------------------------------------------------------

# add tenor and tenor?

def add(
    left: typing.Union[DDT, Tenor],
    right: Tenor,
    iterator: typing.Optional[iteration.Iterator ]= None,
    adjust: bool = False,
    flags=None,
):
    if not isinstance(left, Tenor):
        ddt = left
        tenor = right
        res = arithmetic.add(
            ddt,
            years=tenor.Y,
            months=tenor.M,
            weeks=tenor.W,
            days=tenor.D,
            iterator=iterator,
            flags=flags,
        )
        return res if not adjust else adjustments.adjust(
            res, flags=flags
        )
    return Tenor(
        Y=left.Y+right.Y,
        M=left.M+right.M,
        W=left.W+right.W,
        D=left.D+right.D,
        #
    )

# ---------------------------------------------------------------
