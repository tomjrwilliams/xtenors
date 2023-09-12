
from __future__ import annotations

import typing

import operator
import itertools
import functools
import datetime

import xtuples as xt

from .dates import *
from .units import *

# ---------------------------------------------------------------

def iterate(
    start: typing.Union[datetime.date, datetime.datetime],
    step: datetime.timedelta,
    f: typing.Optional[typing.Callable] = None,
    end: typing.Optional[
        typing.Union[datetime.date, datetime.datetime]
    ] = None,
):
    """
    >>> itr = iterate(year(2020), days(1))
    >>> xt.iTuple.n_from(itr, 2).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 1), datetime.date(2020, 1, 2))
    >>> itr.send(year(2020))
    (False, datetime.date(2019, 12, 31))
    >>> xt.iTuple.n_from(itr, 2).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 1), datetime.date(2020, 1, 2))
    >>> itr.send(days(-1))
    (False, datetime.date(2020, 1, 3))
    >>> xt.iTuple.n_from(itr, 2).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 2), datetime.date(2020, 1, 1))
    >>> itr.send(1)
    (False, datetime.date(2019, 12, 31))
    >>> next(itr)
    (True, datetime.date(2019, 12, 30))
    >>> itr.send(2)
    (False, datetime.date(2019, 12, 28))
    >>> next(itr)
    (True, datetime.date(2019, 12, 27))
    >>> itr.send(-5)
    (False, datetime.date(2020, 1, 1))
    >>> itr.send(lambda d: d.year != 2020)
    (False, datetime.date(2020, 1, 2))
    >>> next(itr)
    (False, datetime.date(2020, 1, 1))
    >>> itr.send(lambda d: (True, True))
    (False, datetime.date(2020, 1, 2))
    >>> list(itr)
    []
    """
    # NOTE: when sent a value, we step back one iter
    # so next(gen) is where we were when sent the value
    current = start
    if f is None:
        f = lambda dt: True
    done = False
    accept = True
    mask = False
    while not done:
        if not mask:
            f_current = f(current)
            if isinstance(f_current, bool):
                accept = f_current
                done = False
            else:
                accept, done = f_current
        if done:
            continue
        given: typing.Union[
            datetime.datetime,
            datetime.date,
            datetime.timedelta,
            typing.Callable,
        ] = yield accept, current
        if end is not None:
            done = end == current
        if given is None:
            current += step
            mask = False
            continue
        if given == 0:
            current -= step
        elif isinstance(given, int):
            current += step * given 
        elif isinstance(
            given, (datetime.datetime, datetime.date)
        ):
            current = given
            current -= step
        elif isinstance(given, datetime.timedelta):
            step = given
            current -= step
        elif isinstance(given, typing.Callable):
            f = given
            current -= step
        else:
            assert False, given
        mask = True
        accept = False

# ---------------------------------------------------------------

def direction(gen):
    """
    >>> itr = iterate(year(2020), days(1))
    >>> direction(itr)
    1
    >>> next(itr)
    (True, datetime.date(2020, 1, 1))
    >>> itr = iterate(year(2020), days(-1))
    >>> direction(itr)
    -1
    >>> next(itr)
    (True, datetime.date(2020, 1, 1))
    """
    # NOTE: be careful, needs to be at least len(2) before done
    _, v_r = next(gen)
    _ = gen.send(-2)
    _, v_l = next(gen)
    return 1 if v_r > v_l else -1

# ---------------------------------------------------------------

def between(
    start: typing.Union[datetime.date, datetime.datetime],
    end: typing.Union[datetime.date, datetime.datetime],
    step: datetime.timedelta,
    f: typing.Optional[typing.Callable] = None,
):
    """
    >>> xt.iTuple(between(year(2020), year(2020, d=3), days(1))).mapstar(lambda y, v: v)
    iTuple(datetime.date(2020, 1, 1), datetime.date(2020, 1, 2), datetime.date(2020, 1, 3))
    """

    if start < end:
        # assert timedelta sign is appropriate?
        f_accept = lambda current: current <= end
        f_done = lambda current: current > end
    else:
        # assert timedelta sign is appropriate?
        f_accept = lambda current: current >= end
        f_done = lambda current: current < end
    
    def f_wrapped(current):
        if f is None:
            accept = True
            done = False
        else:
            accept, done = f(current)
        return (
            accept and f_accept(current),
            done or f_done(current),
        )

    return iterate(start, step, f=f_wrapped)

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

def joint(
    itrs,
    f_done,
    f_accept,
):
    assert itrs.len() > 1, itrs.len()

    dirs = itrs.map(direction)
    assert dirs.all(lambda d: d == dirs[0]), dirs

    op = operator.gt if dirs[0] == 1 else operator.lt

    i_range = xt.iTuple.range(itrs.len())
    
    v_done, v_accept, vs = zip_next(itrs)
    order = i_range.sort(lambda i: (not v_done[i], vs[i]))

    acc_i = xt.iTuple()
    acc_done = xt.iTuple()
    acc_accept = xt.iTuple()
    acc_vs = xt.iTuple()
    
    while not (
        acc_done.len() == itrs.len() 
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
            acc_i = acc_i.clear()
            continue
            
        i_min = order[0]

        if order.len() > 1:
            i_next = order[1]
            v_next = vs[i_next]
            order = order[2:]
        else:
            i_next = None
            v_next = None

        min_done = v_done[i_min]

        if min_done:
            acc_done = acc_done.append(i_min)
            order = order.prepend(i_next)
            continue

        v_min = vs[i_min]

        if v_min == v_next:
            acc_i = acc_i.append(i_min)
            acc_accept = acc_accept.append(v_accept[i_min])
            acc_vs = acc_vs.append(v_min)
            
            order = order.prepend(i_next)
            continue

        # if any to the right are non equal
        # have to step to the left up
        # we include current, as that's what was equal to the left

        min_accept = v_accept[i_min]

        if len(acc_vs):
            yield f_accept(
                acc_done,
                acc_accept.append(min_accept),
                acc_vs.append(v_min),
            ), v_min

            offset = acc_vs.len() + 1

            inds = acc_i.append(i_min).append(i_next).extend(order)
            inds_order = inds.argsort()

            itrs_order = inds[:offset].map(lambda i: itrs[i])

            order_ = order.prepend(i_next)
            tail_done = order_.map(lambda i: v_done[i])
            tail_accept = order_.map(lambda i: v_accept[i])
            tail_vs = order_.map(lambda i: vs[i])

            _v_done, _v_accept, _vs = zip_next(itrs_order)

            order_v_done = _v_done + tail_done
            order_v_accept = _v_accept + tail_accept
            order_vs = _vs + tail_vs

            v_done = inds_order.map(lambda i: order_v_done[i])
            v_accept = inds_order.map(lambda i: order_v_accept[i])
            vs = inds_order.map(lambda i: order_vs[i])

            order = i_range.sort(lambda i: (not v_done[i], vs[i]))
            
            acc_accept = acc_accept.clear()
            acc_vs = acc_vs.clear()
            acc_i = acc_i.clear()
            continue

        # if we get here, we've cleared any equal to the left
        # in the above
        # so we're definitely dealing with the (left) min

        while not min_done and (
            i_next is None 
            or not (v_min == v_next or op(v_min, v_next))
        ):
            yield f_accept(
                acc_done,
                acc_accept.append(min_accept),
                acc_vs.append(v_min),
            ), v_min
            min_done, min_accept, v_min = try_next(itrs[i_min])

        if min_done:
            acc_done = acc_done.append(i_min)
            order = order.prepend(i_next)
            continue

        if v_min == v_next:
            order = xt.iTuple((i_min, i_next)).extend(order)
            continue

        if i_next is None:
            continue

        insert_at = order.enumerate().first_where(
            lambda ind, i: op(vs[i], v_min), star = True
        )
        if insert_at is None:
            order = order.append(i_min)
        else:
            order = order.insert(i=insert_at[0], v = i_min)

        order = order.prepend(i_next)
        
# ---------------------------------------------------------------

def union(itrs):
    """
    >>> from .calendars import *
    >>> cal0 = Stateless.is_weekday(0)
    >>> cal1 = Stateless.is_weekday(1)
    >>> cal2 = Stateless.is_weekday(2)
    >>> itr0 = cal0.iterate(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterate(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(0, 1, 0, 1)
    >>> _ = itr0.send(year(2020, d=3))
    >>> itr2 = cal2.iterate(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1, itr2]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=8, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(0, 2, 0, 2, 0, 1, 2, 0)
    >>> itr0 = cal0.iterate(year(2020, d=3), days(1), end = year(2020, d=5))
    >>> itr1 = cal1.iterate(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(1, 1, 1, 1)
    """
    yield from joint(
        itrs,
        lambda done, accept, vs: done.len() == itrs.len(),
        lambda done, accept, vs: accept.len() and accept.any(),
    )

# ---------------------------------------------------------------

def intersection(itrs):
    """
    >>> from .calendars import *
    >>> cal0 = Stateless.is_weekday([0, 1])
    >>> cal1 = Stateless.is_weekday([1, 2])
    >>> itr0 = cal0.iterate(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterate(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(1, 1, 1, 1)
    >>> cal2 = Stateless.is_weekday([1, 2, 3])
    >>> _ = itr1.send(year(2020, d=3))
    >>> itr2 = cal2.iterate(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1, itr2]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(1, 1, 1, 1)
    >>> _ = itr0.send(year(2020, d=3))
    >>> cal2 = Stateless.is_weekday([2, 3])
    >>> itr2 = cal2.iterate(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1, itr2]))
    >>> xt.iTuple.n_from(itr, 120).any(lambda y, v: y, star = True)
    False
    >>> itr0 = cal0.iterate(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterate(year(2020, d=3), days(1), end = year(2020, d=5))
    >>> itr = intersection(xt.iTuple([itr0, itr1]))
    >>> xt.iTuple.n_from(itr, 120).any(lambda y, v: y, star = True)
    False
    """
    yield from joint(
        itrs,
        lambda done, accept, vs: done.len(),
        lambda done, accept, vs: not done.len() and (
            accept.len() == itrs.len()
            and accept.all()
        )
    )

# ---------------------------------------------------------------

# default to where y=true
def steps_between():
    return
   
# ---------------------------------------------------------------

# various units between
# with either a kwarg for if only whole units 

# or to acc as fraction

# or separate methods?

# ---------------------------------------------------------------
