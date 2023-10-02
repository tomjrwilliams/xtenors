


from __future__ import annotations

import abc
import typing

import operator
import itertools
import functools
import datetime
import calendar

import cython

import xtuples as xt

from .dates import *
from .units import *

from . import conventions
from . import iterators
from . import calendars
from . import arithmetic
from . import adjustments


# ---------------------------------------------------------------

yymmdd = dict(
    y1=cython.int,
    y2=cython.int,
    m1=cython.int,
    m2=cython.int,
    d1=cython.int,
    d2=cython.int,
)

# ---------------------------------------------------------------


@functools.lru_cache(maxsize=100)
def _ndays_february(y):
    return calendar.monthrange(y, 2)[1]

@functools.lru_cache(maxsize=100)
def _is_leap_year(y):
    return _ndays_february(y) == 29

@cython.cfunc
@cython.returns(cython.int)
@cython.locals(**yymmdd)
def pack_30_360(y1, m1, d1, y2, m2, d2):
    return (
        (d2 - d1)
        + (360 * (y2 - y1))
        + (30 * (m2 - m1))
    )

# ---------------------------------------------------------------

def day_count_simple(ddt1, ddt2):
    return (ddt2 - ddt1).days

def day_count_n_actual(ddt1, ddt2):
    return (ddt2 - ddt1).days

# ----------------

@cython.cfunc
@cython.returns(cython.int)
@cython.locals(**yymmdd)
def day_count_n_30_360_bond_C(y1, m1, d1, y2, m2, d2):

    d1 = min((d1, 30))
    if d1 == 30:
        d2 = min((d2, 30))

    return pack_30_360(y1, m1, d1, y2, m2, d2)

def day_count_n_30_360_bond(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)
    
    d1 = min((d1, 30))
    if d1 > 29:
        d2 = min((d2, 30))

    return pack_30_360(y1, m1, d1, y2, m2, d2)

# ----------------

@cython.cfunc
@cython.returns(cython.int)
@cython.locals(**yymmdd, feb1 = cython.int, feb2=cython.int)
def day_count_n_30_360_US_C(
    y1, m1, d1, y2, m2, d2, feb1, feb2
):
    if d1 == feb1 and d2 == feb2:
        d2 = 30
    
    if d1 == feb1:
        d1 = 30

    if d2 > 30 and d1 > 29:
        d2 = 30
    
    d1 = min((31, 30))
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)

def day_count_n_30_360_US(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)
    
    d1_eo_feb = d1 == _ndays_february(y1)
    d2_eo_feb = d2 == _ndays_february(y2)

    if d1_eo_feb and d2_eo_feb:
        d2 = 30
    
    if d1_eo_feb:
        d1 = 30

    if d2 > 30 and d1 > 29:
        d2 = 30
    
    d1 = min((31, 30))
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)

# ----------------


@cython.cfunc
@cython.returns(cython.int)
@cython.locals(**yymmdd)
def day_count_n_30E_360_C(
    y1, m1, d1, y2, m2, d2,
):

    d1 = min((d1, 30))
    d2 = min((d2, 30))
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)
    

def day_count_n_30E_360(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)

    d1 = min((d1, 30))
    d2 = min((d2, 30))
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)

# ----------------


@cython.cfunc
@cython.returns(cython.int)
@cython.locals(**yymmdd, feb1 = cython.int, feb2 = cython.int)
def day_count_n_30E_360_ISDA_C(
    y1, m1, d1, y2, m2, d2, feb1, feb2
):

    d1 = min((d1, 30))
    d2 = min((d2, 30))

    if m1 == 2 and d1 == feb1:
        d1 = 30

    # if d2 is not maturity date?
    if m2 == 2 and d2 == feb2:
        d2 = 30
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)

def day_count_n_30E_360_ISDA(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)

    d1 = min((d1, 30))
    d2 = min((d2, 30))

    if m1 == 2 and d1 == _ndays_february(y1):
        d1 = 30

    # if d2 is not maturity date?
    if m2 == 2 and d2 == _ndays_february(y2):
        d2 = 30
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)

# ----------------


@cython.cfunc
@cython.returns(cython.int)
@cython.locals(**yymmdd)
def day_count_n_30E_plus_360_C(
    y1, m1, d1, y2, m2, d2,
):

    d1 = min((d1, 30))
    if d2 == 31:
        m2 += 1
        d2 = 1
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)

def day_count_n_30E_plus_360(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)

    d1 = min((d1, 30))
    if d2 == 31:
        m2 += 1
        d2 = 1
    
    return pack_30_360(y1, m1, d1, y2, m2, d2)

def day_count_n_1_1(ddt1, ddt2):
    raise NotImplementedError

# ---------------------------------------------------------------

def day_factor_n_30_360(ddt1, ddt2):
    dc = day_count_n_actual(ddt1, ddt2)
    return dc / 360

def day_factor_actual_365_f(ddt1, ddt2):
    dc = day_count_n_actual(ddt1, ddt2)
    return dc / 365

def day_factor_actual_360(ddt1, ddt2):
    dc = day_count_n_actual(ddt1, ddt2)
    return dc / 360

def day_factor_actual_364(ddt1, ddt2):
    dc = day_count_n_actual(ddt1, ddt2)
    return dc / 364

def day_factor_actual_actual_icma(
    day_count_n_actual,
    ddt1,
    ddt2,
    ddt3,
    freq,
):
    dc1 = day_count_n_actual(ddt1, ddt2)
    dc2 = day_count_n_actual(ddt1, ddt3)
    return dc1 / (freq * dc2)

def day_factor_actual_365_l(ddt1, ddt2, freq):

    dc = day_count_n_actual(ddt1, ddt2)

    min_ddt = min((ddt1, ddt2))
    max_ddt = max((ddt1, ddt2))

    if freq != 1 and _is_leap_year(ddt2.year):
        div = 366
    elif freq == 1 and any((
        _is_leap_year(y)
        for y in range(min_ddt.year, max_ddt.year + 1)
    )):
        div = 366
    else:
        div = 365
    
    return dc / div

def day_factor_actual_actual_isda(ddt1, ddt2):

    dc = day_count_n_actual(ddt1, ddt2)

    min_ddt = min((ddt1, ddt2))
    max_ddt = max((ddt1, ddt2))

    if ddt1.year == ddt2.year:
        return dc / (
            366 if _is_leap_year(ddt1.year) else 365
        )
    
    sign = 1 if ddt1 < ddt2 else -1

    left_stub = day_count_n_actual(min_ddt, datetime.date(
        min_ddt.year + 1, 1, 1
    ))
    right_stub = day_count_n_actual(datetime.date(
        max_ddt.year - 1, 12, 31
    ), max_ddt)

    y_delta = max_ddt.year - min_ddt.year

    return sign * sum(
        y_delta - 1,
        left_stub / (
            366 if _is_leap_year(min_ddt.year) else 365
        ),
        right_stub / (
            366 if _is_leap_year(max_ddt.year) else 365
        ),
    )

# TODO: check should adjust
def day_factor_actual_actual_afb(
    day_count_n_actual,
    ddt1,
    ddt2,
    iterator,
    flags,
):

    dc = day_count_n_actual(ddt1, ddt2)

    min_ddt = min((ddt1, ddt2))
    max_ddt = max((ddt1, ddt2))

    sign = 1 if ddt1 < ddt2 else -1
    n_years = max_ddt.year - min_ddt.year

    # adjustment needs an iterator
    ddt_adj = adjustments.adjust(
        arithmetic.add(
            max_ddt,
            years=n_years,
            iterator=iterator,
            flags=flags,
        ),
        iterator,
        flags=flags,
    )

    dc_adj = day_count_n_actual(ddt1, ddt_adj)

    return sign * sum((
        n_years,
        dc_adj / (
            366 if _is_leap_year(ddt1) else 365
        )
    ))

def day_factor_n_1_1(ddt1, ddt2):
    raise NotImplementedError

# ---------------------------------------------------------------

def day_count_not_n_30_360(ddt1, ddt2, count):
    
    if count is conventions.Day_Count.ACTUAL_365_F:
        return day_count_n_actual(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_360:
        return day_count_n_actual(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_364:
        return day_count_n_actual(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_ACTUAL_ICMA:
        return day_count_n_actual(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_365_L:
        return day_count_n_actual(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_ACTUAL_ISDA:
        return day_count_n_actual(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_ACTUAL_AFB:
        return day_count_n_actual(ddt1, ddt2)

    assert False, count

def day_count_C(ddt1, ddt2, count=None):
    """
    
    """
    if count is conventions.Day_Count.N_30_360_BOND:
        return day_count_n_30_360_bond_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
        )

    elif count is conventions.Day_Count.N_30_360_US:
        return day_count_n_30_360_US_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        )

    elif count is conventions.Day_Count.N_30E_360:
        return day_count_n_30E_360_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
        )

    elif count is conventions.Day_Count.N_30E_360_ISDA:
        return day_count_n_30E_360_ISDA_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        )

    elif count is conventions.Day_Count.N_30E_PLUS_360:
        return day_count_n_30E_plus_360_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
        )
    
    return day_count_not_n_30_360(ddt1, ddt2, count)
    
def day_count_py(ddt1, ddt2, count=None):
    """
    
    """
    if count is conventions.Day_Count.N_30_360_BOND:
        return day_count_n_30_360_bond(
            ddt1,
            ddt2,
        )
    elif count is conventions.Day_Count.N_30_360_US:
        return day_count_n_30_360_US(
            ddt1,
            ddt2,
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        )
    elif count is conventions.Day_Count.N_30E_360:
        return day_count_n_30E_360(
            ddt1,
            ddt2,
        )
    elif count is conventions.Day_Count.N_30E_360_ISDA:
        return day_count_n_30E_360_ISDA(
            ddt1,
            ddt2,
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        )
    elif count is conventions.Day_Count.N_30E_PLUS_360:
        return day_count_n_30E_plus_360(
            ddt1,
            ddt2,
        )
    
    return day_count_not_n_30_360(ddt1, ddt2, count)

# ---------------------------------------------------------------

# ddt1 = starting date for accrual (last coupon date before ddt2)
# ddt2 = date through which interest accured. for bonds=settlement
# ddt3 = next coupon date, maturity date if no more interim payments, for regular coupon periods ddt2 == ddt3

def day_factor_not_n_30_360(
    ddt1,
    ddt2,
    ddt3 = None,
    freq = None,
    # flags = None,
    count=None,
    iterator: typing.Optional[iterators. Iterator] = None,
):
    if count is conventions.Day_Count.ACTUAL_365_F:
        return day_factor_actual_365_f(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_360:
        return day_factor_actual_360(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_364:
        return day_factor_actual_364(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_ACTUAL_ICMA:
        assert ddt3 is not None, ddt3
        assert freq is not None, freq
        return day_factor_actual_actual_icma(ddt1, ddt2, ddt3, freq)

    elif count is conventions.Day_Count.ACTUAL_365_L:
        assert freq is not None, freq
        return day_factor_actual_365_l(ddt1, ddt2, freq)

    elif count is conventions.Day_Count.ACTUAL_ACTUAL_ISDA:
        return day_factor_actual_actual_isda(ddt1, ddt2)

    elif count is conventions.Day_Count.ACTUAL_ACTUAL_AFB:
        assert iterator is not None, iterator
        return day_factor_actual_actual_afb(ddt1, ddt2, iterator)

    else:
        assert False, count

def day_factor_C(
    ddt1,
    ddt2,
    ddt3 = None,
    freq = None,
    count=None,
    iterator: typing.Optional[iterators. Iterator] = None,
):
    if count is conventions.Day_Count.N_30_360_BOND:
        return day_count_n_30_360_bond_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
        ) / 360

    elif count is conventions.Day_Count.N_30_360_US:
        return day_count_n_30_360_US_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        ) / 360

    elif count is conventions.Day_Count.N_30E_360:
        return day_count_n_30E_360_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
        ) / 360

    elif count is conventions.Day_Count.N_30E_360_ISDA:
        return day_count_n_30E_360_ISDA_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        ) / 360

    elif count is conventions.Day_Count.N_30E_PLUS_360:
        return day_count_n_30E_plus_360_C(
            *unpack_date(ddt1),
            *unpack_date(ddt2),
        ) / 360

    return day_factor_not_n_30_360(
        ddt1,
        ddt2,
        ddt3=ddt3,
        freq=freq,
        count=count,
        iterator=iterator,
    )

def day_factor_py(
    ddt1,
    ddt2,
    ddt3 = None,
    freq = None,
    count=None,
    iterator: typing.Optional[iterators. Iterator] = None,
):
    """
    >>> ddt1 = datetime.date(2020, 2, 1)
    >>> ddt2 = datetime.date(2020, 4, 1)
    >>> ddt3 = datetime.date(2020, 3, 1)
    >>> freq = 1
    """
    if count is conventions.Day_Count.N_30_360_BOND:
        return day_count_n_30_360_bond(
            ddt1,
            ddt2,
        ) / 360

    elif count is conventions.Day_Count.N_30_360_US:
        return day_count_n_30_360_US(
            ddt1,
            ddt2,
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        ) / 360

    elif count is conventions.Day_Count.N_30E_360:
        return day_count_n_30E_360(
            ddt1,
            ddt2,
        ) / 360

    elif count is conventions.Day_Count.N_30E_360_ISDA:
        return day_count_n_30E_360_ISDA(
            ddt1,
            ddt2,
            _ndays_february(ddt1.year),
            _ndays_february(ddt2.year),
        ) / 360

    elif count is conventions.Day_Count.N_30E_PLUS_360:
        return day_count_n_30E_plus_360(
            ddt1,
            ddt2,
        ) / 360

    return day_factor_not_n_30_360(
        ddt1,
        ddt2,
        ddt3=ddt3,
        freq=freq,
        count=count,
        iterator=iterator,
    )

# ---------------------------------------------------------------

day_count = day_count_C
day_factor = day_factor_C

# interest = principal * coupon_rate * day_factor

# ---------------------------------------------------------------
