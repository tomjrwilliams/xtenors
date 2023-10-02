

import datetime

from financepy.utils.frequency import FrequencyTypes
from financepy.utils.day_count import DayCount, DayCountTypes
from financepy.utils.date import Date as Date

import xtenors
import xtuples as xt

from . import utils

# ---------------------------------------------------------------

def add_tenor_financepy(tenor):
    def f():
        d = Date(1, 1, 2010)
        return d.add_tenor(tenor)
    f.__name__ = utils.outer_func_name()
    return f

def add_tenor_xtenors(tenor):
    def f():
        d = datetime.date(2010, 1, 1)
        return xtenors.Tenor.parse(tenor).add(d)
    f.__name__ = utils.outer_func_name()
    return f
    
# ---------------------------------------------------------------


def test_add_tenors():
    print(":")
    
    tenor = "1Y"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "1M"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "1W"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "1D"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "3Y"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "3M"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "3W"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "3D"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "-3Y"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "-3M"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "-3W"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )
    
    tenor = "-3D"
    utils.compare(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        cast_left=lambda d: d.datetime(),
        fastest=1,
    )

    print("--")

# ---------------------------------------------------------------
