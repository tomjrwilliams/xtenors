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

from contextlib import contextmanager

import datetime
import pandas

from . import conventions

# ---------------------------------------------------------------

def date_validate(dt):
    assert isinstance(dt, (
        datetime.date,
        pandas.Timestamp
    )), dt

def unit_validate(unit):
    assert unit in UNIT(), unit

@xtuples.nTuple.enum
class UNIT(typing.NamedTuple):
    D: str = "D"
    W: str = "W"
    M: str = "M"
    Y: str = "Y"
    
def tenor_validate(tenor):
    unit_validate(tenor.unit)
    assert isinstance(tenor.n, int)
    return tenor

# ---------------------------------------------------------------

# TODO: cast_date and cast_datetime and convention?
# so default time convention needed if convention is datetime
# eg. open close midday etc.

def cast_date(dt):
    """
    >>> dt = datetime.date(2023, 1, 1)
    >>> cast_date(dt)
    datetime.date(2023, 1, 1)
    >>> cast_date(pandas.Timestamp(dt))
    datetime.date(2023, 1, 1)
    >>> with conventions.set_conventions(LIBRARY="PANDAS"):
    ...     cast_date(dt)
    Timestamp('2023-01-01 00:00:00')
    >>> with conventions.set_conventions(LIBRARY="PANDAS"):
    ...     cast_date(pandas.Timestamp(dt))
    Timestamp('2023-01-01 00:00:00')
    """
    # validate dt?

    library_enum = conventions.LIBRARY()
    library = library_enum.current()

    if library == library_enum.PYTHON:
        if isinstance(dt, pandas.Timestamp):
            return dt.to_pydatetime().date()
        elif isinstance(dt, datetime.date):
            return dt

    elif library == library_enum.PANDAS:
        if isinstance(dt, pandas.Timestamp):
            return dt
        elif isinstance(dt, datetime.date):
            return pandas.Timestamp(dt)

    assert False, dict(
        library=library,
        tenor=tenor,
        #
    )

# ---------------------------------------------------------------

def tenor_timedelta(tenor):
    """
    >>> Tenor("D", 1).timedelta
    <bound method tenor_timedelta of Tenor(unit='D', n=1)>
    >>> Tenor("D", 1).timedelta()
    datetime.timedelta(days=1)
    """
    tenor.validate()
    
    library_enum = conventions.LIBRARY()
    library = library_enum.current()

    roll_enum = conventions.ROLL()
    roll = roll_enum.current()

    # TODO: need a calendar if we're going to roll
    # GREGORIAN implies just skip weekends
    # if roll is not actual

    if roll == roll_enum.ACTUAL:
        if tenor.unit == "D":
            if library == library_enum.PYTHON:
                return datetime.timedelta(days=tenor.n)
            elif library == library_enum.PANDAS:
                return pandas.Timedelta(days=tenor.n)

    assert False, dict(
        roll=roll,
        library=library,
        tenor=tenor,
        #
    )

# ---------------------------------------------------------------

def tenor_add(tenor, dt):
    """
    >>> Tenor("D", 1) + datetime.date(2023, 1, 1)
    datetime.date(2023, 1, 2)
    >>> datetime.date(2023, 1, 1) + Tenor("D", 1)
    datetime.date(2023, 1, 2)
    >>> Tenor("D", 1) + Tenor("D", 2)
    Tenor(unit='D', n=3)
    """
    tenor.validate()
    
    if isinstance(dt, Tenor):
        assert tenor.unit == dt.unit, dict(tenor=tenor, dt = dt)
        return tenor.update_n(tenor.n + dt.n)

    res = dt + tenor_timedelta(tenor)
    return cast_date(res)

# ---------------------------------------------------------------

def tenor_rsub(tenor, dt):
    """
    >>> Tenor("D", 1) - Tenor("D", 2)
    Tenor(unit='D', n=-1)
    >>> Tenor("D", 1) - datetime.date(2023, 1, 1)
    Traceback (most recent call last):
        ...
    TypeError: unsupported operand type(s) for tenor_sub: <class '__local__.tenors.Tenor'> and <class 'datetime.date'>
    >>> datetime.date(2023, 1, 1) - Tenor("D", 1)
    datetime.date(2022, 12, 31)
    """
    tenor.validate()
    date_validate(dt)
    return tenor.update_n(tenor.n * -1) + dt

def tenor_sub(t1, t2):
    """
    >>> Tenor("D", 1) - Tenor("D", 2)
    Tenor(unit='D', n=-1)
    """
    if not (
        isinstance(t1, Tenor)
        and isinstance(t2, Tenor)
    ):
        raise TypeError(
            "unsupported operand type(s) for tenor_sub: "
            + "{} and {}".format(type(t1), type(t2))
            #
        )

    t1.validate()
    t2.validate()

    assert t1.unit == t2.unit, dict(t1=t1, t2 = t2)
    return t1.update_n(t1.n - t2.n)

# ---------------------------------------------------------------

def tenor_between(dt_l, dt_r, unit = "D"):
    """
    >>> dt = datetime.date(2023, 1, 1)
    >>> Tenor.between(dt, dt + Tenor("D", 1))
    Tenor(unit='D', n=1)
    >>> Tenor.between(dt, dt - Tenor("D", 1))
    Tenor(unit='D', n=-1)
    """
    unit_validate(unit)

    roll_enum = conventions.ROLL()
    roll = roll_enum.current()

    count_enum = conventions.COUNT()
    count = count_enum.current()

    if count == count_enum.SIMPLE and roll == roll_enum.ACTUAL:
        if unit == "D":
            return Tenor(unit=unit, n=(dt_r - dt_l).days)

    assert False, dict(
        dt_l=dt_l,
        dt_r=dt_r,
        unit=unit,
        roll=roll,
        count=count,
    )

# ---------------------------------------------------------------

# NOTE: remove for now as roll convention would mean conversion is date local and haven't decided whether that makes sense or not
# def convert(tenor, unit):
#     """
#     >>> Tenor(unit='D', n=1).convert("F")
#     Traceback (most recent call last):
#         ...
#     AssertionError: F
#     >>> Tenor(unit='D', n=1).convert("W")
#     """
#     tenor.validate()
#     unit_validate(unit)

#     # to include roll convention need a date?
#     # so how to contextualise that?

#     return

# ---------------------------------------------------------------

update_unit = xtuples.nTuple.replace("unit")
update_n = xtuples.nTuple.replace("n")

@xtuples.nTuple.decorate
class Tenor(typing.NamedTuple):
    
    unit: str
    n: int

    validate = tenor_validate

    update_unit = update_unit
    update_n = update_n

    # convert = convert

    __add__ = tenor_add
    __radd__ = tenor_add
    add = tenor_add

    __sub__ = tenor_sub
    sub = tenor_sub

    __rsub__ = tenor_rsub
    rsub = tenor_rsub

    timedelta = tenor_timedelta

    between = staticmethod(tenor_between)

# ---------------------------------------------------------------
