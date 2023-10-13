

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
from . import iterators
from . import calendars
from . import arithmetic
from . import adjustments

# ---------------------------------------------------------------


# @cython.cfunc
# @cython.returns(tuple[
#     cython.int, cython.int, cython.int, cython.int
# ])
# @cython.locals(
#     s = cython.p_char,
#     unit = cython.char,
#     v = cython.int,
# )
# def parse_C(s):
#     unit = s[-1]
#     v = int(s[:-1])
#     if unit == 'Y':
#     # if unit == 89:
#         return (v, 0, 0, 0)
#     elif unit == 'M':
#     # elif unit == 77:
#         return (0, v, 0, 0)
#     elif unit == 'D':
#     # elif unit == 68:
#         return (0, 0, 0, v)
#     elif unit == 'W':
#     # elif unit == 87:
#         return (0, 0, v, 0)
#     else:
#         assert False, (unit, v)
    

@xt.nTuple.decorate()
class Tenor(typing.NamedTuple):

    s: typing.Optional[str] = None

    # deliberately no __add__
    # as what about iterator / adjustment - forces one to be explicit
    
    Y: typing.Optional[int] = None
    M: typing.Optional[int] = None
    W: typing.Optional[int] = None
    D: typing.Optional[int] = None

    adjustment: typing.Optional[adjustments.Adjustment] = None

    # h / m / s / ms / ... ?

    # adjust

    @classmethod
    def parse(cls, s: str, adjustment = None) -> Tenor:
        """
        >>> Tenor.parse("1D")
        Tenor(s=None, Y=0, M=0, W=0, D=1, adjustment=None)
        >>> Tenor.parse("1W")
        Tenor(s=None, Y=0, M=0, W=1, D=0, adjustment=None)
        >>> Tenor.parse("1M")
        Tenor(s=None, Y=0, M=1, W=0, D=0, adjustment=None)
        >>> Tenor.parse("1Y")
        Tenor(s=None, Y=1, M=0, W=0, D=0, adjustment=None)
        """
        unit = s[-1]
        v = int(s[:-1])
        if unit == 'Y':
            return Tenor(None, v, 0, 0, 0, adjustment)
        elif unit == 'M':
            return Tenor(None, 0, v, 0, 0, adjustment)
        elif unit == 'D':
            return Tenor(None, 0, 0, 0, v, adjustment)
        elif unit == 'W':
            return Tenor(None, 0, 0, v, 0, adjustment)
        else:
            assert False, (unit, v)

    # @classmethod
    # def parse_C(cls, s: str, adjustment = None) -> Tenor:
    #     """
    #     >>> Tenor.parse("1D")
    #     Tenor(s=None, Y=0, M=0, W=0, D=1, adjustment=None)
    #     >>> Tenor.parse("1W")
    #     Tenor(s=None, Y=0, M=0, W=1, D=0, adjustment=None)
    #     >>> Tenor.parse("1M")
    #     Tenor(s=None, Y=0, M=1, W=0, D=0, adjustment=None)
    #     >>> Tenor.parse("1Y")
    #     Tenor(s=None, Y=1, M=0, W=0, D=0, adjustment=None)
    #     """
    #     return Tenor(None, *parse_C(s), adjustment = adjustment)

    @typing.overload
    def init(
        self: Tenor,
        *,
        unpack: typing.Literal[True]
    ) -> tuple[
        Tenor, int, int, int, int
    ]: ...
    
    @typing.overload
    def init(
        self: Tenor,
        *,
        unpack: typing.Literal[False] = False,
    ) -> Tenor: ...

    def init(self, *, unpack = False):
        if self.s is not None:
            self = self.parse(self.s, adjustment=self.adjustment)
        if unpack:
            return self, self.Y, self.M, self.W, self.D
        return self

    def add(
        self: Tenor,
        ddt: typing.Union[DDT, Tenor],
        iterator: typing.Optional[iterators. Iterator] = None,
        adjust: bool = False,
        adjustment=None,
    ):
        """
        >>> Tenor("1D").add(datetime.date(2021, 1, 1))
        datetime.date(2021, 1, 2)
        """
        return add(
            ddt,
            self,
            iterator=iterator,
            adjust=adjust,
            adjustment=(
                adjustment
                if adjustment is None
                else self.adjustment
            )
        )

# ---------------------------------------------------------------

def add(
    left: typing.Union[DDT, Tenor],
    right: Tenor,
    iterator: typing.Optional[iterators. Iterator] = None,
    adjust: bool = False,
    adjustment=None,
):
    if isinstance(left, Tenor) and isinstance(right, Tenor):

        assert isinstance(left, Tenor)
        left, lY, lM, lW, lD = left.init(unpack=True)

        assert isinstance(right, Tenor)
        right, rY, rM, rW, rD = left.init(unpack=True)

        return Tenor(
            Y=lY+rY,
            M=lM+rM,
            W=lW+rW,
            D=lD+rD,
            adjustment=(
                adjustment
                if adjustment is not None
                else left.adjustment
            )
            #
        )
    elif (
        isinstance(left, (datetime.datetime, datetime.date))
        and isinstance(right, Tenor)
    ):
        ddt = left
        tenor = right.init()
    elif  (
        isinstance(right, (datetime.datetime, datetime.date))
        and isinstance(left, Tenor)
    ):
        ddt = right
        tenor = left.init()
    else:
        assert False, dict(left=left, right=right)

    res = arithmetic.add(
        ddt,
        years=tenor.Y,
        months=tenor.M,
        weeks=tenor.W,
        days=tenor.D,
        iterator=iterator,
        overflow=(
            adjustment.overflow
            if adjustment is not None
            else None if tenor.adjustment is None
            else tenor.adjustment.overflow
        )
    )

    return res if not adjust else adjustments.adjust(
        res,
        iterator=adjustment.iterator,
        roll=adjustment.roll,
        modified=adjustment.modified,
    )

# ---------------------------------------------------------------
