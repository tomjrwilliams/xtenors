

import datetime

from financepy.utils.frequency import FrequencyTypes # type: ignore
from financepy.utils.day_count import DayCount, DayCountTypes # type: ignore
from financepy.utils.date import Date as Date # type: ignore

import xtenors
import xtuples as xt

from . import utils

# ---------------------------------------------------------------

def parse_tenor_py(tenor = "3D"):
    def f():
        return xtenors.Tenor.parse(tenor)
    f.__name__ = utils.outer_func_name()
    return f

# TODO: comp to financepy tenor construction?

# def parse_tenor_C(tenor = "3D"):
#     def f():
#         return xtenors.Tenor.parse_C(tenor)
#     f.__name__ = utils.outer_func_name()
#     return f

# ---------------------------------------------------------------

def test_parse_tenor():
    print(":")

    tenor = "3D"
    # utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "3Y"
    # utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "-3D"
    # utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "-3W"
    # utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))
    tenor = "0M"
    # utils.compare(parse_tenor_py(tenor), parse_tenor_C(tenor))

    print("--")

# ---------------------------------------------------------------
