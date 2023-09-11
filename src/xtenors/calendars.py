
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

def stateless_iterator_function(
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
    ):
        i = 0
        current = start
        f = stateless_iterator_function(
            current,
            step,
            self.f_f_accept,
            f_f_done=self.f_f_done,
        )
        itr = iteration.iterate(start, step, f)
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
        >>> xt.iTuple.range(2).zip(itr).mapstar(lambda i, d: d)
        iTuple(datetime.date(2020, 1, 3), datetime.date(2020, 1, 6))
        >>> calendar = Stateless.is_weekday(1)
        >>> itr = calendar.iterate(year(2020, d=3), days(1))
        >>> xt.iTuple.range(2).zip(itr).mapstar(lambda i, d: d.weekday())
        iTuple(1, 1)
        >>> calendar = Stateless.is_weekday([0, 1])
        >>> itr = calendar.iterate(year(2020, d=3), days(1))
        >>> xt.iTuple.range(2).zip(itr).mapstar(lambda i, d: d.weekday())
        iTuple(0, 1)
        """
        if isinstance(val, bool):
            if val:
                f_accept = lambda current: current.weekday() < 5
            else:
                f_accept = lambda current: not current.weekday() < 5
        elif isinstance(val, int):
            f_accept = lambda current: current.weekday() == val
        else:
            try:
                iter(val)
                val = frozenset(val)
                f_accept = lambda current: current.weekday() in val
            except:
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

def stateful_iterator_function(
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
        state=None,
    ):
        i = 0
        includes = INCLUDES[self.key]
        current = start
        itr = iteration.iterate(start, step)
        done = False
        while not done:
            if i == 0 or not self.f_scope(current, step, state):
                includes = extend_includes(
                    self.f_extend(current, step, state, includes)
                )
                state = self.f_state(current, step, state, includes)
                f = stateful_iterator_function(
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
        state=None,
    ):
        i = 0
        excludes = EXCLUDES[self.key]
        current = start
        itr = iteration.iterate(start, step)
        done = False
        while not done:
            if i == 0 or self.f_scope(current, step, state):
                excludes = extend_includes(
                    self.f_extend(current, step, state, excludes)
                )
                state = self.f_state(current, step, state), excludes
                f = stateful_iterator_function(
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

# how to chain together several stateful calendars?

# ie. calendar intersection / union

# joint iter, take where in both / any

# where should itself return a generator in the same form
# so can combine upwards

# ---------------------------------------------------------------

# union:

# loop iters, call next

# for lowest, yield, iter source gen, (loop)

def try_next(itr):
    try:
        return False, next(itr)
    except StopIteration:
        return True, None

def union(
    itrs,
    op,
    # gt = ascending order of result
    # lt = descending
):
    """
    >>> itr0 = Stateless.is_weekday(0).iterate(year(2020, d=3), days(1))
    >>> itr1 = Stateless.is_weekday(1).iterate(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1]), operator.gt)
    >>> xt.iTuple.range(4).zip(itr).mapstar(lambda i, d: d.weekday())
    iTuple(0, 1, 0, 1)
    """
    assert itrs.len() > 1, itrs.len()
    vs = itrs.enumerate().mapstar(lambda i, itr: (i, try_next(itr)))
    done = (
        vs.filterstar(lambda i, res: res[0])
        .mapstar(lambda i, res: i)
    )
    vs = (
        vs.filterstar(lambda i, res: not res[0])
        .mapstar(lambda i, res: (i, res[1]))
    )
    order = vs.sortstar(lambda i, v: v)
    while done.len() < itrs.len() - 1:
        itr_i, v = order[0]
        order = order[1:]
        yield v
        is_done, v = try_next(itrs[itr_i])
        next_i, next_v = order[0]
        order = order[1:]
        while not is_done and not op(v, next_v):
            yield v
            is_done, v = try_next(itrs[itr_i])
        if is_done:
            done = done.append(itr_i)
        else:
            insert_at = order.first_where(
                lambda i, _v: op(_v, v),
                star=True,
            )
            if insert_at is None:
                order = order.append((itr_i, v,))
            else:
                order = order.insert(
                    i=insert_at[0],
                    v=(itr_i, v,),
                )
        order = order.prepend((next_i, next_v))
    itr_i, v = order[0]
    while not is_done:
        yield v
        is_done, v = try_next(itrs[itr_i])


# ---------------------------------------------------------------

# intersection:

# loop iters, call next

# for lowest, if not equal to all
# iter source gen, (loop)

# if equal, yield (loop)

def intersection(
    itrs,
    op,
    # gt = ascending order of result
    # lt = descending
):
    """
    >>> itr0 = Stateless.is_weekday([0, 1]).iterate(year(2020, d=3), days(1))
    >>> itr1 = Stateless.is_weekday([1, 2]).iterate(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1]), operator.gt)
    >>> xt.iTuple.range(4).zip(itr).mapstar(lambda i, d: d.weekday())
    iTuple(1, 1, 1, 1)
    """
    assert itrs.len() > 1, itrs.len()
    vs = itrs.enumerate().mapstar(lambda i, itr: (i, try_next(itr)))
    done = (
        vs.filterstar(lambda i, res: res[0])
        .mapstar(lambda i, res: i)
    )
    vs = (
        vs.filterstar(lambda i, res: not res[0])
        .mapstar(lambda i, res: (i, res[1]))
    )
    order = vs.sortstar(lambda i, v: v)
    while not done.len():
        itr_i, v = order[0]
        if order.allstar(lambda i, _v: _v == v):
            yield v
            vs = itrs.enumerate().mapstar(lambda i, itr: (i, try_next(itr)))
            done = (
                vs.filterstar(lambda i, res: res[0])
                .mapstar(lambda i, res: i)
            )
            vs = (
                vs.filterstar(lambda i, res: not res[0])
                .mapstar(lambda i, res: (i, res[1]))
            )
            order = vs.sortstar(lambda i, v: v)
        else:
            order = order[1:]
            is_done, v = try_next(itrs[itr_i])
            next_i, next_v = order[0]
            order = order[1:]
            while not is_done and not (v == next_v or op(v, next_v)):
                is_done, v = try_next(itrs[itr_i])
            if is_done:
                done = done.append(itr_i)
            else:
                insert_at = order.first_where(
                    lambda i, _v: op(_v, v),
                    star=True,
                )
                if insert_at is None:
                    order = order.append((itr_i, v,))
                else:
                    order = order.insert(
                        i=insert_at[0],
                        v=(itr_i, v,),
                    )
            order = order.prepend((next_i, next_v))

# ---------------------------------------------------------------
