

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

# TODO: rename iteration as iterators for consistency

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

    # TODO: worth trying to compile this with cypy / similar
    # as this will presumably be a fair amount of run time cost    

    @classmethod
    def parse(cls, s: str) -> Tenor:
        unit = s[-1]
        val = int(s[:-1])
        if unit == "Y":
            return cls(Y=val)
        elif unit == "M":
            return cls(M=val)
        elif unit == "W":
            return cls(W=val)
        elif unit == "D":
            return cls(D=val)
        else:
            assert False, s

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

def add(
    left: typing.Union[DDT, Tenor],
    right: Tenor,
    iterator: typing.Optional[iteration.Iterator] = None,
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
