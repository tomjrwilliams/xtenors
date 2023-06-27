
import sys
import importlib.util

spec = importlib.util.spec_from_file_location(
    "xtuples", "../xtuples/src/xtuples/__init__.py"
)
xtuples = importlib.util.module_from_spec(spec)
sys.modules["xtuples"] = xtuples
spec.loader.exec_module(xtuples)

# ---------------------------------------------------------------

import typing

import enum
import datetime

from contextlib import contextmanager

# ---------------------------------------------------------------

update_history = xtuples.nTuple.replace("history")

@xtuples.nTuple.decorate
class IntConvention(typing.NamedTuple):
    default: int = None
    history: xtuples.iTuple = xtuples.iTuple()

    update_history = update_history

@xtuples.nTuple.decorate
class StrConvention(typing.NamedTuple):
    default: str = None
    history: xtuples.iTuple = xtuples.iTuple()

    update_history = update_history

    # NOTE: update_default is deliberately not provided
    # but should be assigned at init

# ---------------------------------------------------------------

def get_convention(k):
    if xtuples.nTuple.is_instance(k):
        k = k.FIELD
    con = CONVENTIONS.get(k, StrConvention())
    return (
        con.default 
        if not con.history.len() 
        else con.history.last()
    )

def get_conventions(*ks):
    return {
        k: get_convention(k)
        for k in ks
    }

# TODO: set defaults (to be called once at init)
# enforce only called once

@contextmanager
def set_conventions(**conventions):
    """
    >>> with set_conventions(test="A"):
    ...     convs = get_conventions("test", "test2")
    >>> convs
    {'test': 'A', 'test2': None}
    """
    try:
        for k, v in conventions.items():
            con = CONVENTIONS.get(k, StrConvention())
            CONVENTIONS[k] = con.update_history(
                con.history.append(v)
            )
        yield conventions
    finally:
        for k in conventions.keys():
            CONVENTIONS[k] = con.pipe(
                update_history, 
                con.history.pop_last()
            )

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _LIBRARY(typing.NamedTuple):
    PYTHON: str = "PYTHON"
    # separate types for deafult to date or datetime?

    PANDAS: str = "PANDAS"
    NUMPY: str = "NUMPY"

    # separate types for 64 / 32?

    FIELD: str = "LIBRARY"

    current = get_convention

LIBRARY = _LIBRARY()

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _COUNT(typing.NamedTuple):

    SIMPLE: str = "SIMPLE"

    ACTUAL_ACTUAL_ISDA: str = "ACTUAL_ACTUAL_ISDA"
    ACTUAL_ACTUAL_ICMA: str = "ACTUAL_ACTUAL_ICMA"
    ACTUAL_ACTUAL_AFB: str = "ACTUAL_ACTUAL_AFB"

    ACTUAL_365_F: str = "ACTUAL_365_F"
    ACTUAL_365_L: str = "ACTUAL_365_L"
    ACTUAL_360: str = "ACTUAL_360"
    ACTUAL_364: str = "ACTUAL_364"

    N_30_360_BOND: str = "N_30_360_BOND"
    N_30_360_US: str = "N_30_360_US"

    N_30E_360: str = "N_30E_360"
    N_30E_360_ISDA: str = "N_30E_360_ISDA"
    N_30E_PLUS_360: str = "N_30E_PLUS_360"

    N_1_1: str = "N_1_1"

    FIELD: str = "COUNT"

    current = get_convention

    # day count:

COUNT = _COUNT()

COUNT_360 = {
    COUNT.N_30_360_BOND,
    COUNT.N_30_360_US,
    COUNT.N_30E_360,
    COUNT.N_30E_360_ISDA,
    COUNT.N_30E_PLUS_360,
}

COUNT_ACTUAL = {
    COUNT.ACTUAL_ACTUAL_ISDA,
    COUNT.ACTUAL_ACTUAL_ICMA,
    COUNT.ACTUAL_ACTUAL_AFB,
    COUNT.ACTUAL_365_F,
    COUNT.ACTUAL_365_L,
    COUNT.ACTUAL_360,
    COUNT.ACTUAL_364,
}

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _OVERFLOW(typing.NamedTuple):

    ERROR: str = "ERROR"
    PREV: str = "PREV"
    NEXT: str = "NEXT"

    FIELD: str = "OVERFLOW"

    current = get_convention

OVERFLOW = _OVERFLOW()

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _ROLL(typing.NamedTuple):

    ACTUAL: str = "ACTUAL"

    FOLLOWING: str = "FOLLOWING"
    PRECEDING: str = "PRECEDING"

    FOLLOWING_MODIFIED: str = "FOLLOWING_MODIFIED"
    PRECEDING_MODIFIED: str = "PRECEDING_MODIFIED"

    FIELD: str = "ROLL"

    current = get_convention

ROLL = _ROLL()

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _ITERATION(typing.NamedTuple):

    WITH_CALENDAR: str = "WITH_CALENDAR"
    WITHOUT_CALENDAR: str = "WITHOUT_CALENDAR"

    FIELD: str = "ITERATION"

    current = get_convention

ITERATION = _ITERATION()

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _ROUND(typing.NamedTuple):

    UP: str = "UP"
    DOWN: str = "DOWN"

    FIELD: str = "ROUND"

    current = get_convention

ROUND = _ROUND()

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _CALENDAR(typing.NamedTuple):

    ALL: str = "ALL"
    WEEKDAYS: str = "WEEKDAYS"

    FIELD: str = "CALENDAR"

    current = get_convention

CALENDAR = _CALENDAR()

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class _FORMAT(typing.NamedTuple):

    ISO: str = "ISO"

    FIELD: str = "FORMAT"

    current = get_convention

FORMAT = _FORMAT()

# ---------------------------------------------------------------

# NOTE: needs to be mutable, so dict not NamedTuple

CONVENTIONS = dict(
    LIBRARY=StrConvention(
        default = LIBRARY.PYTHON,
        #
    ),
    CALENDAR = StrConvention(
        default=CALENDAR.ALL,
    ),
    MARKET_CALENDARS = IntConvention(
        default=1,
    ),
    COUNTRY_CALENDARS = IntConvention(
        default=1,
    ),
    COUNT=StrConvention(
        default=COUNT.SIMPLE,
        # NOTE: simple is count all days
    ),
    ITERATION = StrConvention(
        default=ITERATION.WITHOUT_CALENDAR,
    ),
    ROUND = StrConvention(
        default=ROUND.UP,
    ),
    OVERFLOW = StrConvention(
        default=OVERFLOW.PREV,
    ),
    ROLL=StrConvention(
        default=ROLL.ACTUAL,
        # NOTE: actual is no roll
        # ie. do not skip weekends / holidays
        # to skip, have to specify HOW to skip
    ),
    FORMAT=StrConvention(
        default=FORMAT.ISO,
        #
    ),
    # tenor_between rounding conventions
    # tenor_between default unit?
)

# ---------------------------------------------------------------
