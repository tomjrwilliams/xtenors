

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
    s = cython.p_char,
    unit = cython.char,
    v = cython.int,
)
def parse_C(s):
    unit = s[-1]
    v = int(s[:-1])
    if unit == 'Y':
    # if unit == 89:
        return (v, 0, 0, 0)
    elif unit == 'M':
    # elif unit == 77:
        return (0, v, 0, 0)
    elif unit == 'W':
    # elif unit == 87:
        return (0, 0, v, 0)
    elif unit == 'D':
    # elif unit == 68:
        return (0, 0, 0, v)
    else:
        assert False, (unit, v)

@xt.nTuple.decorate()
class Tenor(typing.NamedTuple):

    # deliberately no __add__
    # as what about iterator / overflow - forces one to be explicit
    
    Y: typing.Optional[int] = 0
    M: typing.Optional[int] = 0
    W: typing.Optional[int] = 0
    D: typing.Optional[int] = 0

    overflow: typing.Optional[conventions.Overflow] = None

    # h / m / s / ms / ... ?

    # adjust

    @classmethod
    def parse(cls, s: str, overflow = None) -> Tenor:
        """
        >>> Tenor.parse("1D")
        Tenor(Y=0, M=0, W=0, D=1, overflow=None)
        >>> Tenor.parse("1W")
        Tenor(Y=0, M=0, W=1, D=0, overflow=None)
        >>> Tenor.parse("1M")
        Tenor(Y=0, M=1, W=0, D=0, overflow=None)
        >>> Tenor.parse("1Y")
        Tenor(Y=1, M=0, W=0, D=0, overflow=None)
        """
        return cls(*parse_C(s), overflow = overflow)
        # return cls(
        #     *parse_C(s.encode("UTF-8")), overflow = overflow
        # )

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
