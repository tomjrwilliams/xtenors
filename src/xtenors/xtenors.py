
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

from contextlib import contextmanager

import datetime
import pandas
import holidays
import pandas_market_calendars

import collections

from . import conventions

# ---------------------------------------------------------------

def _date_iter(d, step, n = None, max_iter = 10 ** 6):
    i = 0
    done = False
    while not done:
        if n is not None and i == n:
            return
        yield d
        d += datetime.timedelta(days=step)
        i += 1
        assert i < max_iter

# ---------------------------------------------------------------

_calendar_cache = collections.deque(maxlen=1)

def _get_calendar_cache():
    global _calendar_cache
    maxlen = conventions.get_convention("MARKET_CALENDARS")
    if maxlen == _calendar_cache.maxlen:
        return _calendar_cache
    _calendar_cache = collections.deque(
        _calendar_cache, maxlen=maxlen
    )
    return _calendar_cache

_country_cache = collections.deque(maxlen=1)

def _get_country_cache():
    global _country_cache
    maxlen = conventions.get_convention("COUNTRY_CALENDARS")
    if maxlen == _country_cache.maxlen:
        return _country_cache
    _country_cache = collections.deque(
        _country_cache, maxlen=maxlen
    )
    return _country_cache

# ---------------------------------------------------------------


@xtuples.nTuple.enum
class AllIterator(typing.NamedTuple):

    def get_offset(self, d):
        return d.toordinal()

    def get(self, i, d):
        return d

@xtuples.nTuple.enum
class AllSchedule(typing.NamedTuple):

    iterator: AllIterator

    def get_offset(self, d):
        return d.toordinal()

# ---------------------------------------------------------------


@xtuples.nTuple.enum
class WeekdaysIterator(typing.NamedTuple):

    def get(self, i, d):
        return d if d.weekday() < 5 else None

@xtuples.nTuple.enum
class WeekdaysSchedule(typing.NamedTuple):

    iterator: WeekdaysIterator

    def get_offset(self, d):
        return d.toordinal()

# ---------------------------------------------------------------

@xtuples.nTuple.decorate
class CountryIterator(typing.NamedTuple):

    holidays: holidays.holiday_base.HolidayBase

    def get(self, i, d):
        if d.weekday() >= 5:
            return None
        return None if d in self.holidays else d

@xtuples.nTuple.decorate
class CountrySchedule(typing.NamedTuple):

    calendar: str

    iterator: CountryIterator

    def get_offset(self, d):
        return d.toordinal()

def _get_country_schedule(calendar):

    cache = _get_country_cache()

    match = False

    for i, obj in enumerate(cache):

        if obj.calendar == calendar:
            if d1 >= obj.d1 and d2 <= obj.d2:
                return obj

            match = True
            break

    if match:
        return obj
    else:
        obj = CountrySchedule(
            calendar, 
            CountryIterator(
                holidays.utils.country_holidays(calendar)
            )
        )
        cache.appendleft(obj)
    return obj

# ---------------------------------------------------------------

def get_offset(schedule, d):
    return (d - schedule.d1).days

    
update_schedule = xtuples.nTuple.replace(
    "d1", "d2", "iterator"
)

@xtuples.nTuple.decorate
class MarketIterator(typing.NamedTuple):

    acc: collections.deque

    def get(self, i, d):
        return self.acc[i]

@xtuples.nTuple.decorate
class MarketSchedule(typing.NamedTuple):

    calendar: str

    d1: datetime.date
    d2: datetime.date

    iterator: MarketIterator

    update = update_schedule
    get_offset = get_offset

# ---------------------------------------------------------------


def _calendar_date_range(calendar, d1, d2):
    ds = set([
        d.to_pydatetime().date() for d 
        in calendar.valid_days(
            start_date=d1,
            end_date=d2,
        )
    ])
    acc = []
    for d in _date_iter(d1, 1):
        acc.append(d if d in ds else None)
        if d == d2:
            return acc

def _new_schedule(cal, d1, d2):
    calendar = pandas_market_calendars.get_calendar(cal)
    return MarketSchedule(
        cal,
        d1,
        d2,
        MarketIterator(_calendar_date_range(calendar, d1, d2))
    )

def _extend_schedule(obj, d1, d2):
    calendar = pandas_market_calendars.get_calendar(obj.calendar)
    iterator = obj.iterator
    if d1 < obj.d1:
        iterator.acc.extendleft(_calendar_date_range(
            calendar, d1, obj.d1 + datetime.timedelta(days=-1)
        ))
    if d2 > obj.d2:
        iterator.acc.extend(_calendar_date_range(
            calendar, obj.d2 + datetime.timedelta(days=1), d2
        ))
    return


CALENDARS_MARKET = xtuples.iTuple(
    pandas_market_calendars.get_calendar_names()
)
CALENDARS_COUNTRY = xtuples.iTuple(
    holidays.utils.list_supported_countries()
)

def _get_schedule(
    calendar=None,
    country=None,
    market=None,
    starting=None,
    ending=None,
    n = None
):

    if country is not None:
        assert country in CALENDARS_COUNTRY, country
        return _get_country_schedule(country)

    elif market is not None:
        pass

    else:
        if calendar == conventions.CALENDAR.ALL:
            return AllSchedule(AllIterator())

        elif calendar == conventions.CALENDAR.WEEKDAYS:
            return WeekdaysSchedule(WeekdaysIterator())

        elif calendar in CALENDARS_MARKET:
            pass

        else:
            assert calendar in CALENDARS_COUNTRY, calendar
            return _get_country_schedule(calendar)

    cache = _get_calendar_cache()

    n = 365 if n is None else max([365, n])

    if starting is None and ending is None:
        d_mid = datetime.date.today()
        d1 = d_mid + datetime.timedelta(days=-n)
        d2 = d_mid + datetime.timedelta(days=n)
    elif ending is None:
        d1 = starting
        d2 = d1 + datetime.timedelta(days=n)
    elif starting is None:
        d2 = ending
        d1 = d2 + datetime.timedelta(days=-n)
    else:
        d1 = starting
        d2 = ending
    
    update = False

    for i, obj in enumerate(cache):

        if obj.calendar == calendar:
            if d1 >= obj.d1 and d2 <= obj.d2:
                return obj

            update = True
            break

    if update:
        _extend_schedule(obj, d1, d2)
    else:
        obj = _new_schedule(calendar, d1, d2)
        cache.appendleft(obj)
    return obj

def calendar_iterator(
    calendar=None,
    country=None,
    market=None,
    starting=None,
    ending=None,
    n = None,
    #
):
    """
    >>> xtuples.iTuple(calendar_iterator(ending=datetime.date(2023, 1, 1), n = 5))
    iTuple(datetime.date(2023, 1, 1), datetime.date(2022, 12, 31), datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
    >>> xtuples.iTuple(calendar_iterator(calendar="ALL", ending=datetime.date(2023, 1, 1), n = 5))
    iTuple(datetime.date(2023, 1, 1), datetime.date(2022, 12, 31), datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
    >>> xtuples.iTuple(calendar_iterator(calendar="WEEKDAYS", ending=datetime.date(2023, 1, 1), n = 5))
    iTuple(None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
    >>> xtuples.iTuple(calendar_iterator(calendar="US", ending=datetime.date(2023, 1, 1), n = 5))
    iTuple(None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
    >>> xtuples.iTuple(calendar_iterator("NYSE", ending=datetime.date(2023, 1, 1), n = 5))
    iTuple(None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
    >>> xtuples.iTuple(calendar_iterator("NYSE", starting=datetime.date(2023, 1, 1), n = 5))
    iTuple(None, None, datetime.date(2023, 1, 3), datetime.date(2023, 1, 4), datetime.date(2023, 1, 5))
    >>> xtuples.iTuple(calendar_iterator("NYSE", starting=datetime.date(2022, 12, 28), ending=datetime.date(2023, 1, 5)))
    iTuple(datetime.date(2022, 12, 28), datetime.date(2022, 12, 29), datetime.date(2022, 12, 30), None, None, None, datetime.date(2023, 1, 3), datetime.date(2023, 1, 4), datetime.date(2023, 1, 5))
    >>> xtuples.iTuple(calendar_iterator("NYSE", ending=datetime.date(2022, 12, 28), starting=datetime.date(2023, 1, 5)))
    iTuple(datetime.date(2023, 1, 5), datetime.date(2023, 1, 4), datetime.date(2023, 1, 3), None, None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
    """
    assert len([k for k in [
        calendar,
        country,
        market,
    ] if k is not None]) <= 1, dict(
        calendar=calendar,
        country=country,
        market=market,
    )
    if (
        calendar is None
        and market is None
        and country is None
    ):
        calendar = conventions.get_convention(
            conventions.CALENDAR.FIELD
        )
    schedule = _get_schedule(
        calendar=calendar,
        country=country,
        market=market,
        starting=starting,
        ending=ending,
        n=n,
    )
    iterator = schedule.iterator

    assert starting is not None or ending is not None

    if starting is not None and ending is not None:
        if starting < ending:
            for _i, d in zip(range(
                schedule.get_offset(starting),
                schedule.get_offset(ending) + 1
                #
            ), _date_iter(starting, step = 1)):
                yield iterator.get(_i, d)
        elif ending < starting:
            for _i , d in zip(reversed(range(
                schedule.get_offset(ending),
                schedule.get_offset(starting) + 1
                #
            )), _date_iter(starting, step=-1)):
                yield iterator.get(_i, d)
        elif starting == ending:
            yield iterator.get(
                schedule.get_offset(starting), starting
            )
        else:
            assert False, dict(
                calendar=calendar,
                country=country,
                market=market,
                starting=starting,
                ending=ending,
                n=n
            )

    elif starting is not None:
        offset = schedule.get_offset(starting)
        for i, d in enumerate(
            _date_iter(starting, step = 1, n = n), offset
        ):
            if i > len(iterator):
                schedule = _get_schedule(
                    calendar,
                    starting=d
                    #
                )
                iterator = schedule.iterator
            yield iterator.get(i, d)

    else:
        # ending is not none
        i = schedule.get_offset(ending)
        for d in _date_iter(ending, step = -1, n = n):
            if i < 0:
                schedule = _get_schedule(
                    calendar=calendar,
                    country=country,
                    market=market,
                    ending=d
                    #
                )
                iterator = schedule.iterator
                i = schedule.get_offset(d)
            yield iterator.get(i, d)
            i -= 1

# ---------------------------------------------------------------

def date_validate(dt):
    assert isinstance(dt, (
        datetime.date,
        pandas.Timestamp
    )), dt

def unit_validate(unit):
    assert unit in UNIT, unit

@xtuples.nTuple.enum
class _UNIT(typing.NamedTuple):
    D: str = "D"
    W: str = "W"
    M: str = "M"
    Y: str = "Y"
    
UNIT = _UNIT()

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

    library_enum = conventions.LIBRARY
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
    
    library_enum = conventions.LIBRARY
    library = library_enum.current()

    roll_enum = conventions.ROLL
    roll = roll_enum.current()

    if roll == roll_enum.ACTUAL:
        if tenor.unit == "D":
            if library == library_enum.PYTHON:
                return datetime.timedelta(days=tenor.n)
            elif library == library_enum.PANDAS:
                return pandas.Timedelta(days=tenor.n)


    # TODO: need a calendar if we're going to roll
    # WEEKDAYS implies just skip weekends
    # if roll is not actual

    # following = next busday

    # following modified = next busday if same month, else prev

    # preceding = prev busday

    # preceding modified = prev busday if same month, else next

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
    TypeError: unsupported operand type(s) for tenor_sub: <class 'xtenors.xtenors.Tenor'> and <class 'datetime.date'>
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

    roll_enum = conventions.ROLL
    roll = roll_enum.current()

    count_enum = conventions.COUNT
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
