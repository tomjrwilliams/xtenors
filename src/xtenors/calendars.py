
from __future__ import annotations

import abc
import typing

import operator
import itertools
import functools
import datetime

import xtuples as xt

from .dates import *
from .units import *

from . import iterators

# ---------------------------------------------------------------

class Calendar(typing.Protocol):

    @abc.abstractmethod
    def valid(self: Calendar) -> typing.Callable[[DDT], bool]:
        ...

    @abc.abstractmethod
    def iterator(
        self: Calendar, 
        start: DDT,
        step: datetime.timedelta,
        **kwargs
    ) -> iterators. Iterator:
        ...

# ---------------------------------------------------------------

@xt.nTuple.decorate()
class Weekday(typing.NamedTuple):

    val: typing.Union[
        bool,
        int,
        typing.Iterable[int],
    ]

    def valid(self: Weekday) -> typing.Callable[[DDT], bool]:
        """
        >>> _, gen = Weekday(True).iterator(year(2020, d=3), days(1)).gen()
        >>> xt.iTuple.from_where(gen, lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v)
        iTuple(datetime.date(2020, 1, 3), datetime.date(2020, 1, 6))
        >>> _, gen = Weekday(1).iterator(year(2020, d=3), days(1)).gen()
        >>> xt.iTuple.from_where(gen, lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v.weekday())
        iTuple(1, 1)
        >>> _, gen = Weekday([0, 1]).iterator(year(2020, d=3), days(1)).gen()
        >>> xt.iTuple.from_where(gen, lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v.weekday())
        iTuple(0, 1)
        """
        val = self.val
        if isinstance(val, bool):
            f = (
                lambda current: current.weekday() < 5
                if val
                else lambda current: not current.weekday() < 5
            )
        elif isinstance(val, int):
            f = lambda current: current.weekday() == val
        elif isinstance(val, typing.Iterable):
            v_set = frozenset(val)
            f = lambda current: current.weekday() in v_set
        else:
            assert False, val
        return f

    def iterator(
        self, 
        start: DDT,
        step: datetime.timedelta,
        **kwargs
    ):
        f = kwargs.pop("accept", None)
        valid = self.valid()
        accept = (
            valid
            if f is None
            else lambda ddt: valid(ddt) and f(ddt)
        )
        return iterators. Iterator(
            start,
            step,
            **kwargs, 
            accept=accept
        )

# ---------------------------------------------------------------

class Manager(typing.Protocol):

    @abc.abstractmethod
    def in_scope(
        self: Manager, 
        calendar: Stateful,
        state: typing.Any,
        current: DDT,
    ) -> bool:
        ...

    @abc.abstractmethod
    def update(
        self: Manager, 
        calendar: Stateful,
        state: typing.Any,
        current: DDT,
    ) -> tuple:
        ...

    @abc.abstractmethod
    def valid(
        self: Manager,
        calendar: Stateful,
    ) -> typing.Callable[[DDT], bool]:
        ...

class Manager_With_K(Manager, typing.Protocol):

    @property
    def k(self) -> str: ...

class Manager_With_Window(Manager, typing.Protocol):

    @property
    def k(self) -> str: ...

    @property
    def window(self) -> datetime.timedelta: ...

# ---------------------------------------------------------------

@xt.nTuple.decorate()
class Stateful(typing.NamedTuple):

    manager: Manager

    def valid(
        self: Stateful,
    ) -> typing.Callable[[DDT], bool]:
        return self.manager.valid(self)

    def iterator(
        self, 
        start: DDT,
        step: datetime.timedelta,
        **kwargs
    ):
        f = kwargs.pop("accept", None)
        valid = self.valid()
        accept = (
            valid
            if f is None
            else lambda ddt: valid(ddt) and f(ddt)
        )
        return iterators.Iterator(
            start,
            step,
            **kwargs, 
            accept=accept
        )

    @classmethod
    def pandas_market_calendar(
        cls, k, window, closed = False
    ):
        return cls(Manager_Pandas_Market_Calendar(
            k, window, closed=closed
        ))

    @classmethod
    def holidays_country(
        cls, k, window, subdiv = None, exclude = True
    ):
        return cls(Manager_Holidays_Country(
            k, window, subdiv = subdiv, exclude=exclude
        ))

    @classmethod
    def holidays_financial(
        cls, k, window, exclude = True
    ):
        return cls(Manager_Holidays_Financial(
            k, window, exclude=exclude
        ))

# ---------------------------------------------------------------

# NOTE: we have a global inclusion / exclusion list
# per calendar (some make more sense for one vs other)

# where that list is built up incrementally, once we hit a value
# outside of scope (as decided by f_scope)
# where it's then extended with f_extend
# presumably with some margin so we're not constantly extending
# and the scope updated to reflect the new check bounds

# as we're only storing those included / excluded
# we need to know the range of values we've checked
# and that won't be given necessarily by the list in question
# as we only keep the truthy / falsey values respectively

# ---------------------------------------------------------------

global INCLUDES
global EXCLUDES

INCLUDES: dict[typing.Type, dict[str, typing.FrozenSet]] = {}
EXCLUDES: dict[typing.Type, dict[str, typing.FrozenSet]] = {}

# ---------------------------------------------------------------

def extend_includes(t, k: str, vals: typing.Iterable):
    if t not in INCLUDES:
        INCLUDES[t] = {k: frozenset(vals)}
    elif k not in INCLUDES[t]:
        INCLUDES[t][k] = frozenset(vals)
    else:
        INCLUDES[t][k] = INCLUDES[t][k].union(vals)
    return INCLUDES[t][k]

def extend_excludes(t, k: str, vals: typing.Iterable):
    if t not in EXCLUDES:
        EXCLUDES[t] = {k: frozenset(vals)}
    elif k not in EXCLUDES[t]:
        EXCLUDES[t][k] = frozenset(vals)
    else:
        EXCLUDES[t][k] = EXCLUDES[t][k].union(vals)
    return EXCLUDES[t][k]

# ---------------------------------------------------------------

# package specific implementations

# ---------------------------------------------------------------

def date_exclusion_valid(
    self: Manager_With_K,
    calendar: Stateful,
    val: bool
) -> typing.Callable[[DDT], bool]:
    t = type(self)
    state = None
    excl = EXCLUDES[t][self.k]
    def f(current: DDT) -> bool:
        nonlocal state
        nonlocal excl
        if not self.in_scope(calendar, state, current):
            state = self.update(calendar, state, current)
            excl = EXCLUDES[t][self.k]
        if isinstance(current, datetime.datetime):
            res = current.date() not in excl
        else:
            res = current not in excl
        return res if val else not res
    return f

def date_inclusion_valid(
    self: Manager_With_K,
    calendar: Stateful,
    val: bool
) -> typing.Callable[[DDT], bool]:
    t = type(self)
    state = None
    incl = INCLUDES[t][self.k]
    def f(current: DDT) -> bool:
        nonlocal state
        nonlocal incl
        if not self.in_scope(calendar, state, current):
            state = self.update(calendar, state, current)
            incl = INCLUDES[t][self.k]
        if isinstance(current, datetime.datetime):
            res = current.date() in incl
        else:
            res = current in incl
        return res if val else not res
    return f

# ---------------------------------------------------------------

def date_exclusion_in_scope(
    self: Manager, 
    calendar: Stateful,
    state: typing.Optional[tuple[DDT, DDT]],
    current: DDT,
) -> bool:
    if state is None:
        return False
    return current >= state[0] and current <= state[1]

date_inclusion_in_scope = date_exclusion_in_scope

# ---------------------------------------------------------------

def date_exclusion_update(
    self: Manager_With_Window, 
    calendar: Stateful,
    state: typing.Optional[tuple[DDT, DDT]],
    current: DDT,
    f_excludes,
    f_extend=extend_excludes,
) -> tuple[DDT, DDT]:

    if isinstance(current, datetime.datetime):
        current = current.date()

    if state is None:
        start = current - self.window
        end = current + self.window
        state = (start, end,)

    elif current < state[0]:
        start = current - self.window
        end = state[0]
        state = (start, state[1],)

    elif current > state[1]:
        start = state[1]
        end = current + self.window
        state = (state[0], end,)

    else:
        return state

    f_extend(
        type(self), self.k, f_excludes(start, end)
    )
    return state

date_inclusion_update = functools.partial(
    date_exclusion_update, f_extend=extend_includes
)

# ---------------------------------------------------------------

import pandas_market_calendars

@xt.nTuple.decorate()
class Manager_Pandas_Market_Calendar(typing.NamedTuple):

    k: str
    window: datetime.timedelta

    closed: bool = False

    def f_excludes(self, start, end):
        cal = pandas_market_calendars.get_calendar(self.k)
        valid = frozenset([
            d.to_pydatetime().date() for d in cal.valid_days(
                start_date=start,
                end_date=end,
            )
        ])
        _, gen = iterators. Iterator(
            start,
            days(1),
            end=end,
            accept=lambda d: d not in valid,
        ).gen()
        return xt.iTuple(gen)

    def valid(
        self: Manager_Pandas_Market_Calendar,
        calendar: Stateful,
    ) -> typing.Callable[[DDT], bool]:
        return date_exclusion_valid(
            self, calendar, not self.closed
        )

    def in_scope(
        self: Manager_Pandas_Market_Calendar, 
        calendar: Stateful,
        state: typing.Optional[tuple[DDT, DDT]],
        current: DDT,
    ) -> bool:
        return date_exclusion_in_scope(
            self,
            calendar,
            state,
            current,
        )

    def update(
        self: Manager_Pandas_Market_Calendar, 
        calendar: Stateful,
        state: typing.Optional[tuple[DDT, DDT]],
        current: DDT,
    ) -> tuple[DDT, DDT]:
        return date_exclusion_update(
            self,
            calendar,
            state,
            current,
            self.f_excludes,
        )

# ---------------------------------------------------------------

import holidays

@xt.nTuple.decorate()
class Manager_Holidays_Country(typing.NamedTuple):

    k: str
    window: datetime.timedelta
    subdiv: typing.Optional[str] = None

    exclude: bool = True

    def f_excludes(self, start, end):
        hols = holidays.country_holidays(
            self.k, subdiv=self.subdiv
        )
        _, gen = iterators. Iterator(
            start,
            days(1),
            end=end,
            accept=lambda d: d in hols,
        ).gen()
        return xt.iTuple(gen)

    def valid(
        self: Manager_Holidays_Country,
        calendar: Stateful,
    ) -> typing.Callable[[DDT], bool]:
        return date_exclusion_valid(
            self, calendar, self.exclude
        )

    def in_scope(
        self: Manager_Holidays_Country, 
        calendar: Stateful,
        state: typing.Optional[tuple[DDT, DDT]],
        current: DDT,
    ) -> bool:
        return date_exclusion_in_scope(
            self,
            calendar,
            state,
            current,
        )

    def update(
        self: Manager_Holidays_Country, 
        calendar: Stateful,
        state: typing.Optional[tuple[DDT, DDT]],
        current: DDT,
    ) -> tuple[DDT, DDT]:
        return date_exclusion_update(
            self,
            calendar,
            state,
            current,
            self.f_excludes,
        )

# ---------------------------------------------------------------

@xt.nTuple.decorate()
class Manager_Holidays_Financial(typing.NamedTuple):

    k: str
    window: datetime.timedelta

    exclude: bool = True

    def f_excludes(self, start, end):
        hols = holidays.financial_holidays(self.k)
        _, gen = iterators. Iterator(
            start,
            days(1),
            end=end,
            accept=lambda d: d in hols,
        ).gen()
        return xt.iTuple(gen)

    def valid(
        self: Manager_Holidays_Financial,
        calendar: Stateful,
    ) -> typing.Callable[[DDT], bool]:
        return date_exclusion_valid(
            self, calendar, self.exclude
        )

    def in_scope(
        self: Manager_Holidays_Financial, 
        calendar: Stateful,
        state: typing.Optional[tuple[DDT, DDT]],
        current: DDT,
    ) -> bool:
        return date_exclusion_in_scope(
            self,
            calendar,
            state,
            current,
        )

    def update(
        self: Manager_Holidays_Financial, 
        calendar: Stateful,
        state: typing.Optional[tuple[DDT, DDT]],
        current: DDT,
    ) -> tuple[DDT, DDT]:
        return date_exclusion_update(
            self,
            calendar,
            state,
            current,
            self.f_excludes,
        )

# ---------------------------------------------------------------