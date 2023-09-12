
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

def try_next(itr):
    try:
        y, v = next(itr)
        return False, y, v
    except StopIteration as e:
        return True, None, None

def zip_next(itrs):
    return itrs.map(try_next).zip().map(xt.iTuple)

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
            if val:
                f_accept = lambda current: current.weekday() < 5
            else:
                f_accept = lambda current: not current.weekday() < 5
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

def joint_iter(
    itrs,
    op,
    f_done,
    f_accept,
):
    assert itrs.len() > 1, itrs.len()
    i_range = xt.iTuple.range(itrs.len())
    
    v_done, v_accept, vs = zip_next(itrs)
    order = i_range.sort(lambda i: (not v_done[i], vs[i]))

    acc_done = xt.iTuple()
    acc_accept = xt.iTuple()
    acc_vs = xt.iTuple()
    
    while not (
        (acc_done.len() == itrs.len() and acc_done.all())   
        or f_done(acc_done, acc_accept, acc_vs)
    ):

        if acc_accept.len() == itrs.len() - 1:

            yield f_accept(
                acc_done, 
                acc_accept.append(v_accept[order[-1]]), 
                acc_vs.append(vs[order[-1]]),
            ), acc_vs[-1]
            
            v_done, v_accept, vs = zip_next(itrs)
            order = i_range.sort(lambda i: (not v_done[i], vs[i]))
            
            acc_accept = acc_accept.clear()
            acc_vs = acc_vs.clear()
            continue
            
        i_min, i_next = order[:2]
        order = order[2:]

        min_done = v_done[i_min]

        if min_done:
            acc_done = acc_done.append(i_min)
            order = order.prepend(i_next)
            continue

        v_min = vs[i_min]
        v_next = vs[i_next]

        if v_min == v_next:
            acc_accept = acc_accept.append(v_accept[i_min])
            acc_vs = acc_vs.append(v_min)
            
            order = order.prepend(i_next)
            continue

        # if any to the right are non equal
        # have to step to the left up
        # we include current, as that's what was equal to the left

        if len(acc_vs):
            yield f_accept(acc_done, acc_accept, acc_vs), acc_vs[-1]
            offset = acc_vs.len() + 1

            _v_done, _v_accept, _vs = zip_next(itrs[:offset])

            v_done = _v_done + v_done[offset:]
            v_accept = _v_accept + v_accept[offset:]
            vs = _vs + vs[offset:]

            order = i_range.sort(lambda i: (not v_done[i], vs[i]))
            
            acc_accept = acc_accept.clear()
            acc_vs = acc_vs.clear()
            continue

        min_done = False
        min_accept = v_accept[i_min]

        # if we get here, we've cleared any equal to the left
        # in the above
        # so we're definitely dealing with the (left) min

        while not min_done and not (v_min == v_next or op(v_min, v_next)):
            yield f_accept(acc_done, acc_accept, acc_vs), v_min
            min_done, min_accept, v_min = try_next(itrs[i_min])

        if min_done:
            acc_done = acc_done.append(i_min)
            order = order.prepend(i_next)
            continue

        if v_min == v_next:
            order = order.pretend((i_min, i_next))
            continue
        
        insert_at = order.first_where(lambda i: op(vs[i], v_min))
        if insert_at is None:
            order = order.append(i_min)
        else:
            order = order.insert(i=insert_at[0], v = i_min)

        order = order.prepend(i_next)
        
# ---------------------------------------------------------------

def union(
    itrs,
    op,
    # gt = ascending order of result
    # lt = descending
):
    """
    >>> cal0 = Stateless.is_weekday(0)
    >>> cal1 = Stateless.is_weekday(1)
    >>> cal2 = Stateless.is_weekday(2)
    >>> itr0 = cal0.iterate(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterate(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1]), operator.gt)
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(0, 1, 0, 1)
    >>> _ = itr0.send(year(2020, d=3))
    >>> _ = itr1.send(year(2020, d=3))
    >>> itr2 = cal2.iterate(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1, itr2]), operator.gt)
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(0, 1, 2, 0)
    """
    yield from joint_iter(
        itrs,
        op,
        # account for none in accept
        lambda done, accept, vs: done.len() == itrs.len(),
        lambda done, accept, vs: accept.len() and accept.any(),
    )

# ---------------------------------------------------------------

def intersection(
    itrs,
    op,
    # gt = ascending order of result
    # lt = descending,
):
    """
    >>> cal0 = Stateless.is_weekday([0, 1])
    >>> cal1 = Stateless.is_weekday([1, 2])
    >>> cal2 = Stateless.is_weekday([2, 3])
    >>> itr0 = cal0.iterate(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterate(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1]), operator.gt)
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(1, 1, 1, 1)
    >>> _ = itr0.send(year(2020, d=3))
    >>> _ = itr1.send(year(2020, d=3))
    >>> itr2 = cal2.iterate(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1, itr2]), operator.gt)
    >>> xt.iTuple.n_from(itr, 8).any(lambda y, v: y, star = True)
    False
    >>> cal2 = Stateless.is_weekday([1, 2, 3])
    >>> _ = itr0.send(year(2020, d=3))
    >>> _ = itr1.send(year(2020, d=3))
    >>> itr2 = cal2.iterate(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1, itr2]), operator.gt)
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(1, 1, 1, 1)
    """
    yield from joint_iter(
        itrs,
        op,
        lambda done, accept, vs: done.len(),
        lambda done, accept, vs: not done.len() and (
            accept.len() == itrs.len()
            and accept.all()
        )
    )

# ---------------------------------------------------------------
