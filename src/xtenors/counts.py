


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


@functools.lru_cache(maxsize=100)
def _ndays_february(y):
    return calendar.monthrange(y, 2)[1]

@functools.lru_cache(maxsize=100)
def _is_leap_year(y):
    return _ndays_february(y) == 29

def pack_30_360(y1, y2, m1, m2, d1, d2):
    return sum((
        360 * (y2 - y1),
        30 * (m2 - m1),
        d2 - d1
    ))

# ---------------------------------------------------------------

def day_count_simple(ddt1, ddt2):
    return (ddt2 - ddt1).days

def day_count_n_actual(ddt1, ddt2):
    return (ddt2 - ddt1).days

def day_count_n_30_360_bond(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)
    
    d1 = min((d1, 30))
    if d1 > 29:
        d2 = min((d2, 30))

    return pack_30_360(y1, y2, m1, m2, d1, d2)

def day_count_n_30_360_US(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)
    
    d1_eo_feb = d1 == _ndays_february(y2)
    d2_eo_feb = d2 == _ndays_february(y2)

    if d1_eo_feb and d2_eo_feb:
        d2 = 30
    
    if d1_eo_feb:
        d1 = 30

    if d2 > 30 and d1 > 29:
        d2 = 30
    
    d1 = min((31, 30))
    
    return pack_30_360(y1, y2, m1, m2, d1, d2)

def day_count_n_30E_360(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)

    d1 = min((d1, 30))
    d2 = min((d2, 30))
    
    return pack_30_360(y1, y2, m1, m2, d1, d2)

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
    
    return pack_30_360(y1, y2, m1, m2, d1, d2)

def day_count_n_30E_plus_360(ddt1, ddt2):
    y1, m1, d1 = unpack_date(ddt1)
    y2, m2, d2 = unpack_date(ddt2)

    d1 = min((d1, 30))
    if d2 == 31:
        m2 += 1
        d2 = 1
    
    return pack_30_360(y1, y2, m1, m2, d1, d2)

def day_count_n_1_1(ddt1, ddt2):
    raise NotImplementedError

# ---------------------------------------------------------------

day_count_funcs = xt.iTuple([
    day_count_simple,
    day_count_n_actual,
    day_count_n_30_360_bond,
    day_count_n_30_360_US,
    day_count_n_30E_360,
    day_count_n_30E_360_ISDA,
    day_count_n_30E_plus_360,
    day_count_n_1_1,
])

assert (
    xt.iTuple(conventions.Day_Count.__members__.items())
    .zip(
        day_count_funcs.map(lambda f: f.__name__),
        xt.iTuple.range(day_count_funcs.len()),
    )
    .all(lambda kv, f_name, i: (
        f_name.lower() == "day_count_{}".format(kv[0].lower()) 
        and i == kv[1].value -1
    ), star = True)
), dict(
    keys=xt.iTuple(conventions.Day_Count.__members__.keys()),
    values=xt.iTuple(conventions.Day_Count.__members__.values()),
    irange=xt.iTuple.range(day_count_funcs.len()),
    funcs=day_count_funcs.map(lambda f: f.__name__),
)

# ---------------------------------------------------------------

def day_count(ddt1, ddt2, flags = None):
    """
    
    """
    if flags is None:
        flags = conventions
    count = flags.get(conventions.Day_Count)
    return day_count_funcs[count.value - 1](ddt1, ddt2)

# ---------------------------------------------------------------

def day_factor_n_360(f_count, ddt1, ddt2):
    dc = f_count(ddt1, ddt2)
    return dc / 360

def day_factor_actual_365_f(f_count, ddt1, ddt2):
    dc = f_count(ddt1, ddt2)
    return dc / 365

def day_factor_actual_360(f_count, ddt1, ddt2):
    dc = f_count(ddt1, ddt2)
    return dc / 360

def day_factor_actual_364(f_count, ddt1, ddt2):
    dc = f_count(ddt1, ddt2)
    return dc / 364

def day_factor_actual_actual_icma(
    f_count,
    ddt1,
    ddt2,
    ddt3,
    freq,
):
    dc1 = f_count(ddt1, ddt2)
    dc2 = f_count(ddt1, ddt3)
    return dc1 / (freq * dc2)

def day_factor_actual_365_l(f_count, ddt1, ddt2, freq):

    dc = f_count(ddt1, ddt2)

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

def day_factor_actual_actual_isda(f_count, ddt1, ddt2):

    dc = f_count(ddt1, ddt2)

    min_ddt = min((ddt1, ddt2))
    max_ddt = max((ddt1, ddt2))

    if ddt1.year == ddt2.year:
        return dc / (
            366 if _is_leap_year(ddt1.year) else 365
        )
    
    sign = 1 if ddt1 < ddt2 else -1

    left_stub = day_count(min_ddt, datetime.date(
        min_ddt.year + 1, 1, 1
    ))
    right_stub = day_count(datetime.date(
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
    f_count,
    ddt1,
    ddt2,
    iterator,
    flags,
):

    dc = f_count(ddt1, ddt2)

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

    dc_adj = day_count(ddt1, ddt_adj)

    return sign * sum((
        n_years,
        dc_adj / (
            366 if _is_leap_year(ddt1) else 365
        )
    ))

def day_factor_n_1_1(f_count, ddt1, ddt2):
    raise NotImplementedError


# ---------------------------------------------------------------

day_factor_funcs = xt.iTuple([
    day_factor_n_360,
    day_factor_actual_365_f,
    day_factor_actual_360,
    day_factor_actual_364,
    day_factor_actual_actual_icma,
    day_factor_actual_365_l,
    day_factor_actual_actual_isda,
    day_factor_actual_actual_afb,
    day_factor_n_1_1,
])

assert (
    xt.iTuple(conventions.Day_Count_Factor.__members__.items())
    .zip(
        day_factor_funcs.map(lambda f: f.__name__),
        xt.iTuple.range(day_factor_funcs.len()),
    )
    .all(lambda kv, f_name, i: (
        f_name.lower() == "day_factor_{}".format(kv[0].lower()) 
        and i == kv[1].value -1
    ), star = True)
), dict(
    keys=xt.iTuple(conventions.Day_Count_Factor.__members__.keys()),
    values=xt.iTuple(conventions.Day_Count_Factor.__members__.values()),
    irange=xt.iTuple.range(day_factor_funcs.len()),
    funcs=day_factor_funcs.map(lambda f: f.__name__),
)

# ---------------------------------------------------------------

# ddt1 = starting date for accrual (last coupon date before ddt2)
# ddt2 = date through which interest accured. for bonds=settlement
# ddt3 = next coupon date, maturity date if no more interim payments, for regular coupon periods ddt2 == ddt3

def day_factor(
    ddt1,
    ddt2,
    ddt3 = None,
    freq = None,
    flags = None,
    iterator: typing.Optional[iteration.Iterator] = None,
):
    """
    >>> ddt1 = datetime.date(2020, 2, 1)
    >>> ddt2 = datetime.date(2020, 4, 1)
    >>> ddt3 = datetime.date(2020, 3, 1)
    >>> freq = 1
    """
    if flags is None:
        flags = conventions

    count = flags.get(conventions.Day_Count)
    factor = flags.get(conventions.Day_Count_Factor)

    f_count = day_count_funcs[count.value - 1]
    f_factor = day_factor_funcs[factor.value - 1]

    if factor is conventions.Day_Count_Factor.ACTUAL_ACTUAL_ICMA:
        assert ddt3 is not None, ddt3
        assert freq is not None, freq
        args = (ddt3, freq,)

    elif factor is conventions.Day_Count_Factor.ACTUAL_365_L:
        assert freq is not None, freq
        args = (freq,)

    elif factor is conventions.Day_Count_Factor.ACTUAL_ACTUAL_AFB:
        assert iterator is not None, iterator
        args = (iterator, flags,)
    else:
        args = ()

    return f_factor(f_count, ddt1, ddt2, *args)

# ---------------------------------------------------------------

# interest = principal * coupon_rate * day_factor

# ---------------------------------------------------------------
