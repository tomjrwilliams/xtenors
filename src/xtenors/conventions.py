import typing

import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    "xtuples", "../src/xtuples/__init__.py"
)
xtuples = importlib.util.module_from_spec(spec)
sys.modules["xtuples"] = xtuples
spec.loader.exec_module(xtuples)

# ---------------------------------------------------------------

import enum
import datetime

from contextlib import contextmanager

# ---------------------------------------------------------------

update_history = xtuples.nTuple.replace("history")

@xtuples.nTuple.decorate
class Convention(typing.NamedTuple):
    default: str = None
    history: xtuples.iTuple = xtuples.iTuple()

    update_history = update_history

    # NOTE: update_default is deliberately not provided
    # but should be assigned at init

# ---------------------------------------------------------------

def get_convention(k):
    if xtuples.nTuple.is_instance(k):
        k = k.FIELD
    con = CONVENTIONS.get(k, Convention())
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
            con = CONVENTIONS.get(k, Convention())
            CONVENTIONS[k] = con.update_history(
                con.history.append(v)
            )
        yield conventions
    finally:
        for k in conventions.keys():
            CONVENTIONS[k] = con.pipe(
                Convention.update_history, 
                con.history.pop_last()
            )

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class LIBRARY(typing.NamedTuple):
    PYTHON: str = "PYTHON"
    # separate types for deafult to date or datetime?

    PANDAS: str = "PANDAS"
    NUMPY: str = "NUMPY"

    # separate types for 64 / 32?

    FIELD: str = "LIBRARY"

    current = get_convention

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class COUNT(typing.NamedTuple):

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

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class ROLL(typing.NamedTuple):

    ACTUAL: str = "ACTUAL"

    FOLLOWING: str = "FOLLOWING"
    PRECEDING: str = "PRECEDING"

    FOLLOWING_MODIFIED: str = "FOLLOWING_MODIFIED"
    PRECEDING_MODIFIED: str = "PRECEDING_MODIFIED"

    FIELD: str = "ROLL"

    current = get_convention

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class CALENDAR(typing.NamedTuple):

    GREGORIAN: str = "GREGORIAN"
    # NOTE: no holidays other than weekends
    # else, any valid value of pandas_market_calendars
    # or python.calendars (?)

    FIELD: str = "CALENDAR"

    current = get_convention

# ---------------------------------------------------------------

@xtuples.nTuple.enum
class FORMAT(typing.NamedTuple):

    ISO: str = "ISO"

    FIELD: str = "FORMAT"

    current = get_convention

# ---------------------------------------------------------------

# NOTE: needs to be mutable, so dict not NamedTuple

CONVENTIONS = dict(
    LIBRARY=Convention(
        default = LIBRARY().PYTHON,
        #
    ),
    CALENDAR = Convention(
        # any valid value of pandas_market_calendars
    ),
    COUNT=Convention(
        default=COUNT().SIMPLE,
        # NOTE: simple is count all days
    ),
    ROLL=Convention(
        default=ROLL().ACTUAL,
        # NOTE: actual is no roll
        # ie. do not skip weekends / holidays
        # to skip, have to specify HOW to skip
    ),
    FORMAT=Convention(
        default=FORMAT().ISO,
        #
    ),
    # tenor_between rounding conventions
    # tenor_between default unit?
)

# ---------------------------------------------------------------
