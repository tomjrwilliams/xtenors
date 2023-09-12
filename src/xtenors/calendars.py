
from __future__ import annotations

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

def f_stateless_iterator(
    current,
    step,
    f_f_accept,
    # current, step -> current -> bool
    f_f_done = None,
    # current, step -> current -> bool
):
    f_accept = f_f_accept(current, step)
    if f_f_done is not None:
        f_done = f_f_done(current, step)
    else:
        f_done = lambda current: False
    f = lambda current: (f_accept(current), f_done(current))
    return f

@xt.nTuple.decorate()
class Stateless(typing.NamedTuple):

    f_f_accept: typing.Callable
    f_f_done: typing.Optional[typing.Callable] = None

    # returns a generator
    def iterate(
        self,
        start,
        step,
        state=None,
        end=None,
    ):
        i = 0
        current = start
        f = f_stateless_iterator(
            current,
            step,
            self.f_f_accept,
            f_f_done=self.f_f_done,
        )
        itr = iteration.iterate(start, step, f, end = end)
        done = False
        while not done:
            try:
                current = next(itr)
                given = yield current
                if given is None:
                    pass
                else:
                    yield itr.send(given)
            except StopIteration:
                done = True
            
            i += 1

    @classmethod
    def is_weekday(cls, val):
        """
        >>> calendar = Stateless.is_weekday(True)
        >>> itr = calendar.iterate(year(2020, d=3), days(1))
        >>> xt.iTuple.from_where(itr, lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v)
        iTuple(datetime.date(2020, 1, 3), datetime.date(2020, 1, 6))
        >>> calendar = Stateless.is_weekday(1)
        >>> itr = calendar.iterate(year(2020, d=3), days(1))
        >>> xt.iTuple.from_where(itr, lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v.weekday())
        iTuple(1, 1)
        >>> calendar = Stateless.is_weekday([0, 1])
        >>> itr = calendar.iterate(year(2020, d=3), days(1))
        >>> xt.iTuple.from_where(itr, lambda y, v: y, n=2, star=True).mapstar(lambda y, v: v.weekday())
        iTuple(0, 1)
        """
        if isinstance(val, bool):
            f_accept = (
                lambda current: current.weekday() < 5
                if val
                else lambda current: not current.weekday() < 5
            )
        elif isinstance(val, int):
            f_accept = lambda current: current.weekday() == val
        elif isinstance(val, typing.Iterable):
            val = frozenset(val)
            f_accept = lambda current: current.weekday() in val
        else:
            assert False, val
        return cls(lambda _, step: f_accept)

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

def f_stateful_iterator(
    current,
    step,
    state,
    state_global,
    f_f_accept,
    # current, step, state, stateglobal -> current -> bool
    f_f_done = None,
    # current, step, state, stateglobal -> current -> bool
):
    f_accept = f_f_accept(current, step, state, state_global)
    if f_f_done is not None:
        f_done = f_f_done(current, step, state, state_global)
    else:
        f_done = lambda current: False
    f = lambda current: (f_accept(current), f_done(current))
    return f

# ---------------------------------------------------------------

# TODO:

# stateful, not incl / excl
# so state replace not extend


# NOTE: rather than assume if included, f_accept = true
# pass a func, so can combine tests

@xt.nTuple.decorate()
class Inclusion(typing.NamedTuple):
    key: str

    f_scope: typing.Callable
    f_extend: typing.Callable
    f_state: typing.Callable
    f_f_accept: typing.Callable
    f_f_done: typing.Optional[typing.Callable] = None

    # returns a generator
    def iterate(
        self,
        start,
        step,
        end=None,
        state=None,
    ):
        i = 0
        includes = INCLUDES[self.key]
        current = start
        itr = iteration.iterate(start, step, end = end)
        done = False
        while not done:
            if i == 0 or not self.f_scope(current, step, state):
                includes = extend_includes(
                    self.f_extend(current, step, state, includes)
                )
                state = self.f_state(current, step, state, includes)
                f = f_stateful_iterator(
                    current,
                    step,
                    state,
                    includes,
                    f_f_accept=self.f_f_accept,
                    f_f_done=self.f_f_done,
                )
                _ = itr.send(f)
            try:
                current = next(itr)
                given = yield current
                if given is None:
                    pass
                else:
                    yield itr.send(given)
            except StopIteration:
                done = True
            
            i += 1

@xt.nTuple.decorate()
class Exclusion(typing.NamedTuple):
    key: str

    f_scope: typing.Callable
    f_extend: typing.Callable
    f_state: typing.Callable
    f_f_accept: typing.Callable
    f_f_done: typing.Optional[typing.Callable] = None

    # returns a generator
    def iterate(
        self,
        start,
        step,
        end=None,
        state=None,
    ):
        i = 0
        excludes = EXCLUDES[self.key]
        current = start
        itr = iteration.iterate(start, step, end = end)
        done = False
        while not done:
            if i == 0 or self.f_scope(current, step, state):
                excludes = extend_includes(
                    self.f_extend(current, step, state, excludes)
                )
                state = self.f_state(current, step, state), excludes
                f = f_stateful_iterator(
                    current,
                    step,
                    state,
                    excludes,
                    f_f_accept=self.f_f_accept,
                    f_f_done=self.f_f_done,
                )
                _ = itr.send(f)
            try:
                current = next(itr)
                given = yield current
                if given is None:
                    pass
                else:
                    yield itr.send(given)
            except StopIteration:
                done = True
            
            i += 1

# ---------------------------------------------------------------
