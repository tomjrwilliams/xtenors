

import datetime

from financepy.utils.frequency import FrequencyTypes
from financepy.utils.day_count import DayCount, DayCountTypes
from financepy.utils.date import Date as Date

import xtenors
import xtuples as xt

from . import utils

# ---------------------------------------------------------------

def parse_tenor_py(tenor = "3D"):
    def f():
        return xtenors.Tenor.parse_py(tenor)
    f.__name__ = utils.outer_func_name()
    return f

def parse_tenor_C(tenor = "3D"):
    def f():
        return xtenors.Tenor.parse_C(tenor)
    f.__name__ = utils.outer_func_name()
    return f

# ---------------------------------------------------------------

def test_parse_tenor():
    print(":")

    tenor = "3D"
    utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "3Y"
    utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "-3D"
    utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "-3W"
    utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "0M"
    utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))

    print("--")

# ---------------------------------------------------------------
