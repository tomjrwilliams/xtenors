

import datetime

from financepy.utils.frequency import FrequencyTypes
from financepy.utils.day_count import DayCount, DayCountTypes
from financepy.utils.date import Date as Date

import xtenors
import xtuples as xt

from . import utils

# ---------------------------------------------------------------

def add_financepy(f_add):
    def f():
        d = Date(1, 1, 2010)
        return f_add(d)
    f.__name__ = utils.outer_func_name()
    return f

def add_xtenor(**kws):
    def f():
        d = datetime.date(2010, 1, 1)
        return xtenors.arithmetic.add(d, **kws)
    f.__name__ = utils.outer_func_name()
    return f

def add_xtenor_py(**kws):
    def f():
        d = datetime.date(2010, 1, 1)
        return xtenors.arithmetic.add_py(d, **kws)
    f.__name__ = utils.outer_func_name()
    return f

def add_xtenor_C(**kws):
    def f():
        d = datetime.date(2010, 1, 1)
        return xtenors.arithmetic.add_C(d, **kws)
    f.__name__ = utils.outer_func_name()
    return f

# ---------------------------------------------------------------

def test_add():
    print(":")
    its = dict(iters=10 ** 6)

    kws=dict(years=3)
    utils.compare(add_xtenor_py(**kws), add_xtenor_C(**kws), **its)
    utils.compare(
        add_financepy(lambda d: d.add_years(3)),
        add_xtenor(**kws), 
        cast_left = lambda d: d.datetime(),
        fastest=1,
    )
    
    kws=dict(years=3, months =3)
    utils.compare(add_xtenor_py(**kws), add_xtenor_C(**kws), **its)
    utils.compare(
        add_financepy(lambda d: d.add_years(3).add_months(3)),
        add_xtenor(**kws), 
        cast_left = lambda d: d.datetime(),
        fastest=1,
    )
    
    kws=dict(years=-2, months=1)
    utils.compare(add_xtenor_py(**kws), add_xtenor_C(**kws), **its)
    utils.compare(
        add_financepy(lambda d: d.add_years(-2).add_months(1)),
        add_xtenor(**kws), 
        cast_left = lambda d: d.datetime(),
        fastest=1,
    )
    
    kws=dict(years=2, months=-3)
    utils.compare(add_xtenor_py(**kws), add_xtenor_C(**kws), **its)
    utils.compare(
        add_financepy(lambda d: d.add_years(2).add_months(-3)),
        add_xtenor(**kws), 
        cast_left = lambda d: d.datetime(),
        fastest=1,
    )

    print("--")
    
# ---------------------------------------------------------------
