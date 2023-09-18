

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

@cython.cfunc
@cython.returns(tuple[
    cython.int, cython.int, cython.int, cython.int
])
@cython.locals(
    s = cython.p_char, unit = cython.p_char, v = cython.int
)
def parse_C(s):
    unit = s[-1]
    v = int(s[:-1])
    if unit == "Y":
        return (v, 0, 0, 0)
    elif unit == "M":
        return (0, v, 0, 0)
    elif unit == "W":
        return (0, 0, v, 0)
    elif unit == "D":
        return (0, 0, 0, v)
    else:
        assert False, s

@xt.nTuple.decorate()
class Tenor(typing.NamedTuple):

    # deliberately no __add__
    # as what about iterator - force one to be explicit
    
    Y: typing.Optional[int] = 0
    M: typing.Optional[int] = 0
    W: typing.Optional[int] = 0
    D: typing.Optional[int] = 0

    overflow: typing.Optional[conventions.Overflow] = None

    # h / m / s / ms / ... ?

    # adjust  
    
    # @classmethod
    # def parse(cls, s: str) -> Tenor:
    #     unit = s[-1]
    #     val = int(s[:-1])
    #     if unit == "Y":
    #         return cls(Y=val)
    #     elif unit == "M":
    #         return cls(M=val)
    #     elif unit == "W":
    #         return cls(W=val)
    #     elif unit == "D":
    #         return cls(D=val)
    #     else:
    #         assert False, s

    @classmethod
    def parse(cls, s: str, overflow = None) -> Tenor:
        return cls(*parse_C(s), overflow = overflow)

    def add(
        self: Tenor,
        ddt: typing.Union[DDT, Tenor],
        iterator: typing.Optional[iteration.Iterator] = None,
        adjust: bool = False,
        overflow=None,
    ):
        return add(
            ddt,
            self,
            iterator=iterator,
            adjust=adjust,
            overflow=(
                overflow if overflow is None else self.overflow
            )
        )

# ---------------------------------------------------------------

def add(
    left: typing.Union[DDT, Tenor],
    right: Tenor,
    iterator: typing.Optional[iteration.Iterator] = None,
    adjust: bool = False,
    overflow=None,
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
            overflow=(
                overflow if overflow is not None else tenor.overflow
            )
        )
        return res if not adjust else adjustments.adjust(
            res, overflow=overflow
        )
    return Tenor(
        Y=left.Y+right.Y,
        M=left.M+right.M,
        W=left.W+right.W,
        D=left.D+right.D,
        overflow=(
            overflow if overflow is not None else left.overflow
        )
        #
    )

# ---------------------------------------------------------------
