
# import sys
# import importlib.util

# import xtuples

# spec = importlib.util.spec_from_file_location(
#     "xtuples", "c:/hc/xtuples/src/xtuples/__init__.py"
# )
# xtuples = importlib.util.module_from_spec(spec)
# sys.modules["xtuples"] = xtuples
# spec.loader.exec_module(xtuples)

# # ---------------------------------------------------------------

# import typing

# from contextlib import contextmanager

# import calendar as pycalendar
# import datetime
# import pandas
# import holidays
# import pandas_market_calendars

# import functools

# import collections

# from . import conventions

# # ---------------------------------------------------------------

# # TODO: move the iteration and calendar stuff to a separate module

# def _date_iter(d, step, d2 = None, n = None, max_iter = 10 ** 6):
#     i = 0
#     done = False
#     while not done:
#         if n is not None and i == n:
#             return
#         yield d
#         d += datetime.timedelta(days=step)
#         if d2 is not None and d == d2:
#             return
#         i += 1
#         assert i < max_iter

# # ---------------------------------------------------------------

# _calendar_cache = collections.deque(maxlen=1)

# def _get_calendar_cache():
#     global _calendar_cache
#     maxlen = conventions.get_convention("MARKET_CALENDARS")
#     if maxlen == _calendar_cache.maxlen:
#         return _calendar_cache
#     _calendar_cache = collections.deque(
#         _calendar_cache, maxlen=maxlen
#     )
#     return _calendar_cache

# _country_cache = collections.deque(maxlen=1)

# def _get_country_cache():
#     global _country_cache
#     maxlen = conventions.get_convention("COUNTRY_CALENDARS")
#     if maxlen == _country_cache.maxlen:
#         return _country_cache
#     _country_cache = collections.deque(
#         _country_cache, maxlen=maxlen
#     )
#     return _country_cache

# # ---------------------------------------------------------------


# @xtuples.nTuple.enum
# class AllIterator(typing.NamedTuple):

#     def get_offset(self, d):
#         return d.toordinal()

#     def get(self, i, d):
#         return d

# @xtuples.nTuple.enum
# class AllSchedule(typing.NamedTuple):

#     iterator: AllIterator

#     def get_offset(self, d):
#         return d.toordinal()

# # ---------------------------------------------------------------


# @xtuples.nTuple.enum
# class WeekdaysIterator(typing.NamedTuple):

#     def get(self, i, d):
#         return d if d.weekday() < 5 else None

# @xtuples.nTuple.enum
# class WeekdaysSchedule(typing.NamedTuple):

#     iterator: WeekdaysIterator

#     def get_offset(self, d):
#         return d.toordinal()

# # ---------------------------------------------------------------

# @xtuples.nTuple.decorate
# class CountryIterator(typing.NamedTuple):

#     holidays: holidays.holiday_base.HolidayBase

#     def get(self, i, d):
#         if d.weekday() >= 5:
#             return None
#         return None if d in self.holidays else d

# @xtuples.nTuple.decorate
# class CountrySchedule(typing.NamedTuple):

#     calendar: str

#     iterator: CountryIterator

#     def get_offset(self, d):
#         return d.toordinal()

# def _get_country_schedule(calendar):

#     cache = _get_country_cache()

#     match = False

#     for i, obj in enumerate(cache):

#         if obj.calendar == calendar:
#             if d1 >= obj.d1 and d2 <= obj.d2:
#                 return obj

#             match = True
#             break

#     if match:
#         return obj
#     else:
#         obj = CountrySchedule(
#             calendar, 
#             CountryIterator(
#                 holidays.utils.country_holidays(calendar)
#             )
#         )
#         cache.appendleft(obj)
#     return obj

# # ---------------------------------------------------------------

# def get_offset(schedule, d):
#     return (d - schedule.d1).days

    
# update_schedule = xtuples.nTuple.update(
#     "d1", "d2", "iterator"
# )

# @xtuples.nTuple.decorate
# class MarketIterator(typing.NamedTuple):

#     acc: collections.deque

#     def get(self, i, d):
#         return self.acc[i]

# @xtuples.nTuple.decorate
# class MarketSchedule(typing.NamedTuple):

#     calendar: str

#     d1: datetime.date
#     d2: datetime.date

#     iterator: MarketIterator

#     update = update_schedule
#     get_offset = get_offset

# # ---------------------------------------------------------------


# def _calendar_date_range(calendar, d1, d2):
#     ds = set([
#         d.to_pydatetime().date() for d 
#         in calendar.valid_days(
#             start_date=d1,
#             end_date=d2,
#         )
#     ])
#     acc = []
#     for d in _date_iter(d1, 1):
#         acc.append(d if d in ds else None)
#         if d == d2:
#             return acc

# def _new_schedule(cal, d1, d2):
#     calendar = pandas_market_calendars.get_calendar(cal)
#     return MarketSchedule(
#         cal,
#         d1,
#         d2,
#         MarketIterator(_calendar_date_range(calendar, d1, d2))
#     )

# def _extend_schedule(obj, d1, d2):
#     calendar = pandas_market_calendars.get_calendar(obj.calendar)
#     iterator = obj.iterator
#     if d1 < obj.d1:
#         iterator.acc.extendleft(_calendar_date_range(
#             calendar, d1, obj.d1 + datetime.timedelta(days=-1)
#         ))
#     if d2 > obj.d2:
#         iterator.acc.extend(_calendar_date_range(
#             calendar, obj.d2 + datetime.timedelta(days=1), d2
#         ))
#     return


# CALENDARS_MARKET = xtuples.iTuple(
#     pandas_market_calendars.get_calendar_names()
# )
# CALENDARS_COUNTRY = xtuples.iTuple(
#     holidays.utils.list_supported_countries()
# )

# def _get_schedule(
#     calendar=None,
#     country=None,
#     market=None,
#     starting=None,
#     ending=None,
#     n = None
# ):

#     if country is not None:
#         assert country in CALENDARS_COUNTRY, country
#         return _get_country_schedule(country)

#     elif market is not None:
#         pass

#     else:
#         if calendar == conventions.CALENDAR.ALL:
#             return AllSchedule(AllIterator())

#         elif calendar == conventions.CALENDAR.WEEKDAYS:
#             return WeekdaysSchedule(WeekdaysIterator())

#         elif calendar in CALENDARS_MARKET:
#             pass

#         else:
#             assert calendar in CALENDARS_COUNTRY, calendar
#             return _get_country_schedule(calendar)

#     cache = _get_calendar_cache()

#     n = 365 if n is None else max([365, n])

#     if starting is None and ending is None:
#         d_mid = datetime.date.today()
#         d1 = d_mid + datetime.timedelta(days=-n)
#         d2 = d_mid + datetime.timedelta(days=n)
#     elif ending is None:
#         d1 = starting
#         d2 = d1 + datetime.timedelta(days=n)
#     elif starting is None:
#         d2 = ending
#         d1 = d2 + datetime.timedelta(days=-n)
#     else:
#         d1 = starting
#         d2 = ending
    
#     update = False

#     for i, obj in enumerate(cache):

#         if obj.calendar == calendar:
#             if d1 >= obj.d1 and d2 <= obj.d2:
#                 return obj

#             update = True
#             break

#     if update:
#         _extend_schedule(obj, d1, d2)
#     else:
#         obj = _new_schedule(calendar, d1, d2)
#         cache.appendleft(obj)
#     return obj

# def calendar_iterator(
#     calendar=None,
#     country=None,
#     market=None,
#     starting=None,
#     ending=None,
#     n = None,
#     #
# ):
#     """
#     >>> xtuples.iTuple(calendar_iterator(ending=datetime.date(2023, 1, 1), n = 5))
#     iTuple(datetime.date(2023, 1, 1), datetime.date(2022, 12, 31), datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
#     >>> xtuples.iTuple(calendar_iterator(calendar="ALL", ending=datetime.date(2023, 1, 1), n = 5))
#     iTuple(datetime.date(2023, 1, 1), datetime.date(2022, 12, 31), datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
#     >>> xtuples.iTuple(calendar_iterator(calendar="WEEKDAYS", ending=datetime.date(2023, 1, 1), n = 5))
#     iTuple(None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
#     >>> xtuples.iTuple(calendar_iterator(calendar="US", ending=datetime.date(2023, 1, 1), n = 5))
#     iTuple(None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
#     >>> xtuples.iTuple(calendar_iterator("NYSE", ending=datetime.date(2023, 1, 1), n = 5))
#     iTuple(None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
#     >>> xtuples.iTuple(calendar_iterator("NYSE", starting=datetime.date(2023, 1, 1), n = 5))
#     iTuple(None, None, datetime.date(2023, 1, 3), datetime.date(2023, 1, 4), datetime.date(2023, 1, 5))
#     >>> xtuples.iTuple(calendar_iterator("NYSE", starting=datetime.date(2022, 12, 28), ending=datetime.date(2023, 1, 5)))
#     iTuple(datetime.date(2022, 12, 28), datetime.date(2022, 12, 29), datetime.date(2022, 12, 30), None, None, None, datetime.date(2023, 1, 3), datetime.date(2023, 1, 4), datetime.date(2023, 1, 5))
#     >>> xtuples.iTuple(calendar_iterator("NYSE", ending=datetime.date(2022, 12, 28), starting=datetime.date(2023, 1, 5)))
#     iTuple(datetime.date(2023, 1, 5), datetime.date(2023, 1, 4), datetime.date(2023, 1, 3), None, None, None, datetime.date(2022, 12, 30), datetime.date(2022, 12, 29), datetime.date(2022, 12, 28))
#     """
#     assert len([k for k in [
#         calendar,
#         country,
#         market,
#     ] if k is not None]) <= 1, dict(
#         calendar=calendar,
#         country=country,
#         market=market,
#     )
#     if (
#         calendar is None
#         and market is None
#         and country is None
#     ):
#         calendar = conventions.get_convention(
#             conventions.CALENDAR.FIELD
#         )
        
#     schedule = _get_schedule(
#         calendar=calendar,
#         country=country,
#         market=market,
#         starting=starting,
#         ending=ending,
#         n=n,
#     )
#     iterator = schedule.iterator

#     assert starting is not None or ending is not None

#     if starting is not None and ending is not None:
#         if starting < ending:
#             for _i, d in zip(range(
#                 schedule.get_offset(starting),
#                 schedule.get_offset(ending) + 1
#                 #
#             ), _date_iter(starting, step = 1)):
#                 yield iterator.get(_i, d)
#         elif ending < starting:
#             for _i , d in zip(reversed(range(
#                 schedule.get_offset(ending),
#                 schedule.get_offset(starting) + 1
#                 #
#             )), _date_iter(starting, step=-1)):
#                 yield iterator.get(_i, d)
#         elif starting == ending:
#             yield iterator.get(
#                 schedule.get_offset(starting), starting
#             )
#         else:
#             assert False, dict(
#                 calendar=calendar,
#                 country=country,
#                 market=market,
#                 starting=starting,
#                 ending=ending,
#                 n=n
#             )

#     elif starting is not None:
#         offset = schedule.get_offset(starting)
#         for i, d in enumerate(
#             _date_iter(starting, step = 1, n = n), offset
#         ):
#             if i > len(iterator):
#                 schedule = _get_schedule(
#                     calendar,
#                     starting=d
#                     #
#                 )
#                 iterator = schedule.iterator
#             yield iterator.get(i, d)

#     else:
#         # ending is not none
#         i = schedule.get_offset(ending)
#         for d in _date_iter(ending, step = -1, n = n):
#             if i < 0:
#                 schedule = _get_schedule(
#                     calendar=calendar,
#                     country=country,
#                     market=market,
#                     ending=d
#                     #
#                 )
#                 iterator = schedule.iterator
#                 i = schedule.get_offset(d)
#             yield iterator.get(i, d)
#             i -= 1

# def next_valid_date(**kwargs):

#     itr = calendar_iterator(**kwargs)

#     while (dt_roll := next(itr, None)) is None:
#         pass

#     return dt_roll

# # ---------------------------------------------------------------

# def date_validate(dt):
#     assert isinstance(dt, (
#         datetime.date,
#         pandas.Timestamp
#     )), dt

# def unit_validate(unit):
#     assert unit in UNIT, unit

# @xtuples.nTuple.enum
# class _UNIT(typing.NamedTuple):
#     D: str = "D"
#     W: str = "W"
#     M: str = "M"
#     Y: str = "Y"
    
# UNIT = _UNIT()

# def tenor_validate(tenor):
#     unit_validate(tenor.unit)
#     assert isinstance(tenor.n, int)
#     return tenor

# # ---------------------------------------------------------------

# # TODO: cast_date and cast_datetime and convention?
# # so default time convention needed if convention is datetime
# # eg. open close midday etc.


# def cast_date(dt):
#     """
#     >>> dt = datetime.date(2023, 1, 1)
#     >>> cast_date(dt)
#     datetime.date(2023, 1, 1)
#     >>> cast_date(pandas.Timestamp(dt))
#     datetime.date(2023, 1, 1)
#     >>> with conventions.set_conventions(LIBRARY="PANDAS"):
#     ...     cast_date(dt)
#     Timestamp('2023-01-01 00:00:00')
#     >>> with conventions.set_conventions(LIBRARY="PANDAS"):
#     ...     cast_date(pandas.Timestamp(dt))
#     Timestamp('2023-01-01 00:00:00')
#     """
#     # validate dt?

#     library_enum = conventions.LIBRARY
#     library = library_enum.current()

#     if library == library_enum.PYTHON:
#         if isinstance(dt, pandas.Timestamp):
#             return dt.to_pydatetime().date()
#         elif isinstance(dt, datetime.date):
#             return dt

#     elif library == library_enum.PANDAS:
#         if isinstance(dt, pandas.Timestamp):
#             return dt
#         elif isinstance(dt, datetime.date):
#             return pandas.Timestamp(dt)

#     assert False, dict(
#         library=library,
#         library_enum=library_enum,
#         #
#     )

# # ---------------------------------------------------------------

# def unpack_date(dt, library=None):
#     return dt.year, dt.month, dt.day

# def day_delta(n, library):
    
#     if library == conventions.LIBRARY.PYTHON:
#         return datetime.timedelta(days=n)
#     elif library == conventions.LIBRARY.PANDAS:
#         return pandas.Timedelta(days=n)

#     assert False, n

# def overflow_date(y, m, d, calendar = None, roll = None):
#     """
#     >>> overflow_date(2023, 1, 32)
#     datetime.date(2023, 1, 31)
#     """
#     try:
#         dt = datetime.date(y, m, d)
#     except:
#         overflow_enum = conventions.OVERFLOW
#         overflow = overflow_enum.current()

#         d_max = pycalendar.monthrange(y, m)[1]
#         assert d > d_max, dict(y=y, m=m, d=d)
        
#         if overflow == overflow_enum.PREV:
#             dt = datetime.date(y, m, d_max)

#         elif overflow == overflow_enum.NEXT:
#             dt = datetime.date(y, m, d_max) + datetime.timedelta(days=delta)

#         elif overflow == overflow_enum.ERROR:
#             assert False

#         else:
#             assert False, dict(overflow=overflow, enum=overflow_enum)
    
#     return cast_date(dt)

# def adjust_date_forward(dt):

#     dt_roll = next_valid_date(starting=dt)
    
#     if dt_roll.month == dt.month:
#         return dt_roll

#     elif (
#         dt_roll.month > dt.month 
#         and roll == roll_enum.FOLLOWING_MODIFIED
#     ):
#         return next_valid_date(ending=dt)

#     else:
#         assert False, dict(dt_roll=dt_roll, roll=roll)

# def adjust_date_backward(dt):

#     dt_roll = next_valid_date(ending=dt)
    
#     if dt_roll.month == dt.month:
#         return dt_roll
        
#     elif (
#         dt_roll.month > dt.month 
#         and roll == roll_enum.FOLLOWING_MODIFIED
#     ):
#         return next_valid_date(starting=dt)

#     else:
#         assert False, dict(dt_roll=dt_roll, roll=roll)

# def adjust_date(dt):

#     roll_enum = conventions.ROLL
#     roll = roll_enum.current()

#     if (
#         roll == roll_enum.FOLLOWING
#         or roll == roll_enum.FOLLOWING_MODIFIED
#     ):
#         return adjust_date_forward(dt, roll)

#     elif (
#         roll == roll_enum.PRECEDING
#         or roll == roll_enum.PRECEDING_MODIFIED
#     ):
#         return adjust_date_backward(dt, roll)

#     else:
#         assert False, dict(roll=roll, roll_enum=roll_enum)

# def tenor_add(tenor, dt):
#     """
#     >>> Tenor("D", 1) + datetime.date(2023, 1, 1)
#     datetime.date(2023, 1, 2)
#     >>> datetime.date(2023, 1, 1) + Tenor("D", 1)
#     datetime.date(2023, 1, 2)
#     >>> Tenor("D", 1) + Tenor("D", 2)
#     Tenor(unit='D', n=3)
#     """
#     tenor.validate()
    
#     if isinstance(dt, Tenor):
#         assert tenor.unit == dt.unit, dict(tenor=tenor, dt = dt)
#         return tenor.update_n(tenor.n + dt.n)

#     calendar = conventions.CALENDAR.current()
#     library = conventions.LIBRARY.current()

#     iteration_enum = conventions.ITERATION
#     iteration = iteration_enum.current()

#     if tenor.unit == UNIT.D:
#         if iteration == iteration_enum.WITH_CALENDAR:
#             if n >= 0:
#                 itr = calendar_iterator(starting=dt)
#             else:
#                 itr = calendar_iterator(ending=dt)
#             i = 0
#             while i < abs(tenor.n):
#                 dt = next(itr, None)
#                 if dt is not None:
#                     i += 1
#         elif iteration == iteration_enum.WITHOUT_CALENDAR:
#             dt = dt + day_delta(tenor.n, library=library)
#         else:
#             assert False, dict(iteration=iteration, enum=iteration_enum)
        
#     elif tenor.unit == UNIT.W:
#         dt = dt + day_delta(tenor.n * 7, library=library)
#     else:
#         y, m, d = unpack_date(dt, library=library)

#         if tenor.unit == UNIT.M:
#             y_incr, m_incr = divmod(tenor.n, 12)
#             y += y_incr
#             y_incr, m = divmod(m + m_incr, 12)
#             y += y_incr
#         elif tenor.unit == UNIT.Y:
#             y += tenor.y
#         else:
#             assert False, dict(tenor=tenor, dt = dt)

#         dt = overflow_date(y, m, d)

#     if calendar == conventions.CALENDAR.ALL:
#         return cast_date(dt)

#     return cast_date(adjust_date(dt))

# # ---------------------------------------------------------------

# def tenor_rsub(tenor, dt):
#     """
#     >>> Tenor("D", 1) - Tenor("D", 2)
#     Tenor(unit='D', n=-1)
#     >>> Tenor("D", 1) - datetime.date(2023, 1, 1)
#     Traceback (most recent call last):
#         ...
#     TypeError: unsupported operand type(s) for tenor_sub: <class 'xtenors.xtenors.Tenor'> and <class 'datetime.date'>
#     >>> datetime.date(2023, 1, 1) - Tenor("D", 1)
#     datetime.date(2022, 12, 31)
#     """
#     tenor.validate()
#     date_validate(dt)
#     return tenor.update_n(tenor.n * -1) + dt

# def tenor_sub(t1, t2):
#     """
#     >>> Tenor("D", 1) - Tenor("D", 2)
#     Tenor(unit='D', n=-1)
#     """
#     if not (
#         isinstance(t1, Tenor)
#         and isinstance(t2, Tenor)
#     ):
#         raise TypeError(
#             "unsupported operand type(s) for tenor_sub: "
#             + "{} and {}".format(type(t1), type(t2))
#             #
#         )

#     t1.validate()
#     t2.validate()

#     assert t1.unit == t2.unit, dict(t1=t1, t2 = t2)
#     return t1.update_n(t1.n - t2.n)

# # ---------------------------------------------------------------

# # TODO: split cases to separate functions?
# # so that have separate doctests and easier to read?

# def day_count_factor(dt1, dt2, dt3 = None, freq = None):
#     """

#     """
#     count_enum = conventions.COUNT
#     count = count_enum.current()

#     dc1 = day_count(dt1, dt2)

#     min_d = min((dt1, dt2))
#     max_d = max((dt1, dt2))

#     if dt3 is not None:
#         dc2 = day_count(dt1, dt3)

#     if count in conventions.COUNT_360:
#         return dc1 / 360
    
#     elif count == count_enum.ACTUAL_365_F:
#         return dc1 / 365
    
#     elif count == count_enum.ACTUAL_360:
#         return dc1 / 360
    
#     elif count == count_enum.ACTUAL_364:
#         return dc1 / 364
    
#     elif count == count_enum.ACTUAL_ACTUAL_ICMA:
#         return dc1 / (freq * dc2)
    
#     elif count == count_enum.ACTUAL_365_L:
#         if freq != 1 and _is_leap_year(dt2.year):
#             div = 366
#         elif freq == 1 and any((
#             _is_leap_year(y)
#             for y in range(min_d.year, max_d.year + 1)
#         )):
#             div = 366
#         else:
#             div = 365
        
#         return dc1 / div

#     elif count == count_enum.ACTUAL_ACTUAL_ISDA:
#         if dt1.year == dt.year:
#             return dc1 / (
#                 366 if _is_leap_year(dt1.year) else 365
#             )
        
#         sign = 1 if dt1 < dt2 else -1

#         left_stub = day_count(min_d, datetime.date(
#             min_d.year + 1, 1, 1
#         ))
#         right_stub = day_count(datetime.date(
#             max_d.year - 1, 12, 31
#         ), max_d)

#         y_delta = max_d.year - min_d.year

#         return sign * sum(
#             y_delta - 1,
#             left_stub / (
#                 366 if _is_leap_year(min_d.year) else 365
#             ),
#             right_stub / (
#                 366 if _is_leap_year(max_d.year) else 365
#             ),
#         )

#     elif count == count_enum.ACTUAL_ACTUAL_AFB:

#         sign = 1 if dt1 < dt2 else -1
#         n_years = max_d.year - min_d.year

#         dt_adj = max_d + Tenor(
#             unit=UNIT.Y, n = n_years
#         )

#         dc_adj = day_count(dt1, dt_adj)

#         return sign * sum((
#             n_years,
#             dc_adj / (
#                 366 if _is_leap_year(dt1) else 365
#             )
#         ))

#     elif count == count_enum.N_1_1:
#         assert False, dict(count=count, enum=count_enum)
#     else:
#         assert False, dict(count=count, enum=count_enum)

# @functools.lru_cache(maxsize=100)
# def _ndays_february(y):
#     return pycalendar.monthrange(y, 2)[1]

# @functools.lru_cache(maxsize=100)
# def _is_leap_year(y):
#     return _ndays_february(y) == 29

# # TODO: split cases to separate functions?
# # so that have separate doctests and easier to read?

# def day_count(dt1, dt2):
#     """
    
#     """
#     count_enum = conventions.COUNT
#     count = count_enum.current()

#     y1, m1, d1 = unpack_date(dt1)
#     y2, m2, d2 = unpack_date(dt2)

#     if (
#         count == count_enum.SIMPLE
#         or count in conventions.COUNT_ACTUAL
#     ):
#         return (dt2 - dt1).days

#     elif count in conventions.COUNT_360:

#         if count == count_enum.N_30_360_BOND:

#             d1 = min((d1, 30))
#             if d1 > 29:
#                 d2 = min((d2, 30))

#         elif count == count_enum.N_30_360_US:

#             # first two conditions, only iF interest end of month?

#             d1_eo_feb = d1 == _ndays_february(y2)
#             d2_eo_feb = d2 == _ndays_february(y2)

#             if d1_eo_feb and d2_eo_feb:
#                 d2 = 30
            
#             if d1_eo_feb:
#                 d1 = 30

#             if d2 > 30 and d1 > 29:
#                 d2 = 30
            
#             d1 = min((31, 30))

#         elif count == count_enum.N_30E_360:

#             d1 = min((d1, 30))
#             d2 = min((d2, 30))

#         elif count == count_enum.N_30E_360_ISDA:

#             d1 = min((d1, 30))
#             d2 = min((d2, 30))

#             if m1 == 2 and d1 == _ndays_february(y1):
#                 d1 = 30

#             # if d2 is not maturity date?
#             if m2 == 2 and d2 == _ndays_february(y2):
#                 d2 = 30

#         elif count == count_enum.N_30E_PLUS_360:

#             d1 = min((d1, 30))
#             if d2 == 31:
#                 m2 += 1
#                 d2 = 1
        
#         else:
#             assert False, dict(count=count, enum=count_enum)

#         return sum((
#             360 * (y2 - y1),
#             30 * (m2 - m1),
#             d2 - d1
#         ))
    
#     elif count == count_enum.N_1_1:
#         assert False
#     else:
#         assert False, dict(count=count, enum=count_enum)
    
# def tenor_day_count(d1, t):
#     """

#     """
#     return day_count(d1, d1 + t)

# # ---------------------------------------------------------------

# # TODO: split cases to separate functions?
# # so that have separate doctests and easier to read?

# def tenor_between(dt_l, dt_r, unit = UNIT.D):
#     """
#     >>> dt = datetime.date(2023, 1, 1)
#     >>> Tenor.between(dt, dt + Tenor("D", 1))
#     Tenor(unit='D', n=1)
#     >>> Tenor.between(dt, dt - Tenor("D", 1))
#     Tenor(unit='D', n=-1)
#     """
#     unit_validate(unit)

#     iteration_enum = conventions.ITERATION
#     iteration = iteration_enum.current()
    
#     if iteration == iteration_enum.WITHOUT_CALENDAR:
#         sign = 1 if dt_l <= dt_r else -1
#         itr = _date_iter(dt_l, d2=dt_r, step = sign)

#     elif iteration == iteration_enum.WITH_CALENDAR:
#         itr = calendar_iterator(starting=dt_l, ending=dt_r)

#     else:
#         assert False, dict(iteration=iteration, enum=iteration_enum)

#     if unit == UNIT.D:
#         n = len(list(
#             d for d in itr if d is not None
#         ))
#         return Tenor(unit=unit, n=n * sign)

#     round_enum == conventions.ROUND
#     _round = round_enum.current()

#     # TODO: faster to do this, or to iter Tenor(n=1) steps?

#     if unit == UNIT.W:
#         n = len(list(set(
#             d.isocalendar().week for d in itr if d is not None
#         )))
#     elif unit == UNIT.M:
#         n = len(list(set(
#             d.month for d in itr if d is not None
#         )))
#     elif unit == UNIT.Y:
#         n = len(list(set(
#             d.year for d in itr if d is not None
#         )))
#     else:
#         assert False, dict(unit=unit, enum=unit_enum)

#     if _round == round_enum.UP:
#         pass
#     elif _round == round_enum.DOWN:
#         n -= 1
#     else:
#         assert False, dict(round=_round, enum=round_enum)

#     return Tenor(unit=unit, n = n * sign)

# # ---------------------------------------------------------------

# update_unit = xtuples.nTuple.update("unit")
# update_n = xtuples.nTuple.update("n")

# @xtuples.nTuple.decorate
# class Tenor(typing.NamedTuple):
    
#     unit: str
#     n: int

#     validate = tenor_validate

#     update_unit = update_unit
#     update_n = update_n

#     # convert = convert

#     __add__ = tenor_add
#     __radd__ = tenor_add
#     add = tenor_add

#     __sub__ = tenor_sub
#     sub = tenor_sub

#     __rsub__ = tenor_rsub
#     rsub = tenor_rsub

#     between = staticmethod(tenor_between)

# # ---------------------------------------------------------------
