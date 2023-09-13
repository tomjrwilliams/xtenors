
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

from . import iteration

# ---------------------------------------------------------------

class Calendar(typing.Protocol):

    @abc.abstractmethod
    def valid(self: Calendar, current: DDT) -> bool:
        ...

    @abc.abstractmethod
    def iterator(
        self: Calendar, 
        start: DDT,
        step: datetime.timedelta,
        **kwargs
    ) -> iteration.Iterator:
        ...

# ---------------------------------------------------------------

@xt.nTuple.decorate()
class Weekday(typing.NamedTuple):

    val: typing.Union[
        bool,
        int,
        xt.iTuple,
    ]

    @functools.lru_cache(maxsize=1)
    def f(self):
        val = self.val
        if isinstance(val, bool):
            f = (
                lambda current: current.weekday() < 5
                if val
                else lambda current: not current.weekday() < 5
            )
        elif isinstance(val, int):
            f = lambda current: current.weekday() == val
        elif isinstance(val, xt.iTuple):
            val = frozenset(val)
            f = lambda current: current.weekday() in val
        else:
            assert False, val
        return f

    def valid(self: Calendar, current: DDT) -> bool:
        """
        >>> calendar = Weekday(True)
        >>> _, gen = iteration.Iterator(year(2020, d=3), days(1)).gen()
        >>> xt.iTuple.from_where(gen(), lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v)
        iTuple(datetime.date(2020, 1, 3), datetime.date(2020, 1, 6))
        >>> calendar = Weekday(1)
        >>> _, gen = iteration.Iterator(year(2020, d=3), days(1)).gen()
        >>> xt.iTuple.from_where(gen(), lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v.weekday())
        iTuple(1, 1)
        >>> calendar = Weekday([0, 1])
        >>> _, gen = iteration.Iterator(year(2020, d=3), days(1)).gen()
        >>> xt.iTuple.from_where(gen(), lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v.weekday())
        iTuple(0, 1)
        """
        return self.f()(current)

    def iterator(
        self, 
        start: DDT,
        step: datetime.timedelta,
        **kwargs
    ):
        if "accept" in kwargs:
            f = kwargs.pop("accept")
            accept = lambda ddt: self.valid(ddt) and f(ddt)
        else:
            accept = self.valid
        return iteration.Iterator(
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
        state: typing.Any
    ) -> bool:
        ...

    @abc.abstractmethod
    def update(
        self: Manager, 
        calendar: Stateful,
        state: typing.Any,
        current: DDT,
    ) -> bool:
        ...

# ---------------------------------------------------------------

@xt.nTuple.decorate()
class Stateful(typing.NamedTuple):

    manager: Manager

    def gen(self):
        def f(state = None):
            itr, gen = self.itr.gen()
            i = 0
            done = False
            current = None
            while not done:
                if i == 0:
                    state = self.manager.update(
                        self, state, current,
                    )
                elif not self.manager.in_scope(self, state):
                    state = self.manager.update(
                        self, state, current,
                    )
                try:
                    current = next(gen)
                    given: typing.Optional[int] = yield current
                    if given is not None:
                        yield gen.send(given)
                except StopIteration:
                    done = True
                i += 1
        return self, f

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

INCLUDES: dict[str, typing.FrozenSet] = {}
EXCLUDES: dict[str, typing.FrozenSet] = {}

# ---------------------------------------------------------------

def extend_includes(k: str, vals: typing.Iterable):
    INCLUDES[k] = INCLUDES[k].union(vals)
    return INCLUDES[k]

def extend_excludes(k: str, vals: typing.Iterable):
    EXCLUDES[k] = EXCLUDES[k].union(vals)
    return EXCLUDES[k]

# ---------------------------------------------------------------

# package specific implementations, where above is appropriate

# ---------------------------------------------------------------
