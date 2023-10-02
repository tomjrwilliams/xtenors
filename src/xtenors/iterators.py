
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


@xt.nTuple.decorate()
class Iterator(typing.NamedTuple):

    start: DDT
    step: datetime.timedelta
    accept: typing.Optional[typing.Callable[[DDT], bool]] = None
    done: typing.Optional[typing.Callable[[DDT], bool]] = None
    end: typing.Optional[DDT] = None

    f: typing.Optional[typing.Callable] = None

    def direction(self):
        """
        >>> itr = Iterator(year(2020), days(1))
        >>> itr.direction()
        1
        >>> itr = Iterator(year(2020), days(-1))
        >>> itr.direction()
        -1
        """
        return 1 if self.start + self.step > self.start else -1

    def update(self, **kwargs):
        # """
        # >>> itr.send(lambda d: d.year != 2020)
        # (False, datetime.date(2020, 1, 2))
        # >>> next(itr)
        # (False, datetime.date(2020, 1, 1))
        # >>> itr.send(lambda d: (True, True))
        # (False, datetime.date(2020, 1, 2))
        # >>> list(itr)
        # []
        # """
        self = self._replace(**kwargs)
        return self.gen()

    def gen(self):
        """
        >>> itr, gen = Iterator(year(2020), days(1)).gen()
        >>> xt.iTuple.n_from(gen, 2).mapstar(lambda y, v: v)
        iTuple(datetime.date(2020, 1, 1), datetime.date(2020, 1, 2))
        >>> itr, gen = itr.update_from_current(gen, step=days(-1))
        >>> xt.iTuple.n_from(gen, 2).mapstar(lambda y, v: v)
        iTuple(datetime.date(2020, 1, 2), datetime.date(2020, 1, 1))
        >>> gen.send(1)
        (False, datetime.date(2019, 12, 31))
        >>> next(gen)
        (True, datetime.date(2019, 12, 30))
        >>> gen.send(2)
        (False, datetime.date(2019, 12, 28))
        >>> next(gen)
        (True, datetime.date(2019, 12, 27))
        >>> gen.send(-5)
        (False, datetime.date(2020, 1, 1))
        """
        def f():
            current = self.start

            f_accept = (
                self.accept
                if self.accept is not None
                else lambda _: True
            )
            f_done = (
                self.done
                if self.done is not None
                else lambda _: False
            )
            
            mask = False
            done = False
            accept = True

            end = self.end
            step = self.step

            while not done:
                done = f_done(current)
                if done:
                    continue
                if not mask:
                    accept = f_accept(current)
                given: typing.Optional[int] = yield accept, current
                if end is not None:
                    done = end == current
                if given is None:
                    current += step
                    mask = False
                    continue
                if given == 0:
                    current -= step
                else:
                    current += step * given
                mask = True
                accept = False
        return self, f()

    def __call__(self):
        _, gen = self.gen()
        return gen

    @classmethod
    def current(cls, gen):
        _, _ = next(gen)
        _, _ = gen.send(-2)
        _, v_current = next(gen)
        return v_current

    @classmethod
    def from_current(
        cls,
        gen,  
        step: datetime.timedelta,
        accept: typing.Optional[typing.Callable[[DDT], bool]] = None,
        done: typing.Optional[typing.Callable[[DDT], bool]] = None,
        end: typing.Optional[DDT] = None,
    ):
        current = cls.current(gen)
        return cls(
            current,
            step,
            accept=accept,
            done=done,
            end=end,
        )

    def update_from_current(
        self,
        gen,  
        **kwargs
    ):
        current = self.current(gen)
        return self.update(start=current, **kwargs)

    @classmethod
    def to_current(
        cls,
        gen,  
        start: DDT,
        step: datetime.timedelta,
        accept: typing.Optional[typing.Callable[[DDT], bool]] = None,
        done: typing.Optional[typing.Callable[[DDT], bool]] = None,
    ):
        current = cls.current(gen)
        return cls(
            start,
            step,
            accept=accept,
            done=done,
            end=current,
        )

    def update_to_current(
        self,
        gen,  
        **kwargs
    ):
        current = self.current(gen)
        return self.update(end=current, **kwargs)

    def update_accept(self, and_f = None, or_f = None, f = None):
        return

    def update_done(self, and_f = None, or_f = None, f = None):
        return 

    def steps_where(
        self,
        where: typing.Optional[typing.Callable] = None,
    ) -> int:
        _, gen = self.gen()
        res = xt.iTuple.from_where(gen)
        return res if where is None else where(res)

    def n_steps_where(self):
        return self.steps_where(where=lambda it: it.len() - 1)

    def steps_until(
        self,
        where: typing.Optional[typing.Callable] = None,
    ) -> int:
        _, gen = self.gen()
        res = xt.iTuple.from_while(gen, value = False)
        return res if where is None else where(res)

    def n_steps_until(self):
        return self.steps_until(where=lambda it: it.len())
        
    def steps_while(
        self,
        where: typing.Optional[typing.Callable] = None,
    ) -> int:
        _, gen = self.gen()
        res = xt.iTuple.from_while(gen, value = True)
        return res if where is None else where(res)

    def n_steps_while(self):
        return self.steps_while(where=lambda it: it.len() - 1)

# ---------------------------------------------------------------

def try_next(gen):
    try:
        y, v = next(gen)
        return False, y, v
    except StopIteration as e:
        return True, None, None

def zip_next(gens):
    return gens.map(try_next).zip().map(xt.iTuple)
    
# ---------------------------------------------------------------

def joint(
    itrs,
    f_done,
    f_accept,
):
    assert itrs.len() > 1, itrs.len()

    dirs = itrs.map(lambda itr: itr.direction())
    assert dirs.all(lambda d: d == dirs[0]), dirs

    op = operator.gt if dirs[0] == 1 else operator.lt

    i_range = xt.iTuple.range(itrs.len())

    _, gens = itrs.map(lambda itr: itr.gen()).zip().map(xt.iTuple)
    
    v_done, v_accept, vs = zip_next(gens)
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
            
            v_done, v_accept, vs = zip_next(gens)
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

            gens_order = inds[:offset].map(lambda i: gens[i])

            order_ = order.prepend(i_next)
            tail_done = order_.map(lambda i: v_done[i])
            tail_accept = order_.map(lambda i: v_accept[i])
            tail_vs = order_.map(lambda i: vs[i])

            _v_done, _v_accept, _vs = zip_next(gens_order)

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
            min_done, min_accept, v_min = try_next(gens[i_min])

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
    >>> cal0 = Weekday(0)
    >>> cal1 = Weekday(1)
    >>> cal2 = Weekday(2)
    >>> itr0 = cal0.iterator(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterator(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(0, 1, 0, 1)
    >>> itr2 = cal2.iterator(year(2020, d=3), days(1))
    >>> itr = union(xt.iTuple([itr0, itr1, itr2]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=8, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(0, 1, 2, 0, 1, 2, 0, 1)
    >>> itr0 = cal0.iterator(year(2020, d=3), days(1), end = year(2020, d=5))
    >>> itr1 = cal1.iterator(year(2020, d=3), days(1))
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
    >>> cal0 = Weekday(xt.iTuple([0, 1]))
    >>> cal1 = Weekday(xt.iTuple([1, 2]))
    >>> itr0 = cal0.iterator(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterator(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(1, 1, 1, 1)
    >>> cal2 = Weekday(xt.iTuple([1, 2, 3]))
    >>> itr2 = cal2.iterator(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1, itr2]))
    >>> xt.iTuple.from_where(itr, lambda y, v: y, n=4, star=True).mapstar(lambda y, v: v.weekday())
    iTuple(1, 1, 1, 1)
    >>> cal2 = Weekday(xt.iTuple([2, 3]))
    >>> itr2 = cal2.iterator(year(2020, d=3), days(1))
    >>> itr = intersection(xt.iTuple([itr0, itr1, itr2]))
    >>> xt.iTuple.n_from(itr, 120).any(lambda y, v: y, star = True)
    False
    >>> itr0 = cal0.iterator(year(2020, d=3), days(1))
    >>> itr1 = cal1.iterator(year(2020, d=3), days(1), end = year(2020, d=5))
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

# various units between
# with either a kwarg for if only whole units 

# or to acc as fraction

# or separate methods?

# ---------------------------------------------------------------
