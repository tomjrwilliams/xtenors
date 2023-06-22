
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

    FIELD: str = "COUNT"

    current = get_convention

    # day count:
    # 30_360_bond
    # 30_e_360 (| _isda)
    # 30_e_plus_360
    # act_act_isda
    # act_act_isma
    # act_365f
    # act_360
    # act_365l
    # simple

COUNT = _COUNT()

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
