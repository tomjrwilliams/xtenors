

import datetime

from financepy.utils.frequency import FrequencyTypes
from financepy.utils.day_count import DayCount, DayCountTypes
from financepy.utils.date import Date as Date

import xtenors
import xtuples as xt

from . import utils

# ---------------------------------------------------------------

# round(answer[0], 4) == 0.3889
def year_frac_30_360_bond_financepy(
    start = Date(1, 1, 2019),
    end = Date(21, 5, 2019),
):
    def f():
        finFreq = FrequencyTypes.ANNUAL
        day_count_type = DayCountTypes.THIRTY_360_BOND
        day_count = DayCount(day_count_type)
        return day_count.year_frac(start, end, end, finFreq)[0]
    f.__name__ = utils.outer_func_name()
    return f 

def year_frac_30_360_bond_xtenors_py(
    start = datetime.date(2019, 1, 1),
    end = datetime.date(2019, 5, 21),
):
    def f():
        return xtenors.counts.day_factor_py(
            start,
            end,
            count=xtenors.conventions.Day_Count.N_30_360_BOND,
        )
    f.__name__ = utils.outer_func_name()
    return f

def year_frac_30_360_bond_xtenors_C(
    start = datetime.date(2019, 1, 1),
    end = datetime.date(2019, 5, 21),
):
    def f():
        return xtenors.counts.day_factor_C(
            start,
            end,
            count=xtenors.conventions.Day_Count.N_30_360_BOND,
        )
    f.__name__ = utils.outer_func_name()
    return f

def test_day_counts():
    print(":")
    
    utils.compare(
        year_frac_30_360_bond_xtenors_py(), 
        year_frac_30_360_bond_xtenors_C(),
        iters=10 ** 6
    )
    utils.compare(
        year_frac_30_360_bond_financepy(), 
        year_frac_30_360_bond_xtenors_C(), 
        fastest=1,
    )

    print("--")

# ---------------------------------------------------------------

# https://github.com/domokane/FinancePy/blob/master/tests/test_FinDayCount.py


# start = Date(1, 1, 2019)
# end = Date(21, 5, 2019)
# finFreq = FrequencyTypes.ANNUAL


# def test_year_frace_THIRTY_360_BOND():
#     day_count_type = DayCountTypes.THIRTY_360_BOND
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3889


# def test_year_frace_THIRTY_E_360():
#     day_count_type = DayCountTypes.THIRTY_E_360
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3889


# def test_year_frace_THIRTY_E_360_ISDA():
#     day_count_type = DayCountTypes.THIRTY_E_360_ISDA
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3889


# def test_year_frace_THIRTY_E_PLUS_360():
#     day_count_type = DayCountTypes.THIRTY_E_PLUS_360
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3889


# def test_year_frace_ACT_ACT_ISDA():
#     day_count_type = DayCountTypes.ACT_ACT_ISDA
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3836


# def test_year_frace_ACT_ACT_ICMA():
#     day_count_type = DayCountTypes.ACT_ACT_ICMA
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 1.0000


# def test_year_frace_ACT_365F():
#     day_count_type = DayCountTypes.ACT_365F
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3836


# def test_year_frace_ACT_360():
#     day_count_type = DayCountTypes.ACT_360
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3889


# def test_year_frace_ACT_365L():
#     day_count_type = DayCountTypes.ACT_365L
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3836


# def test_year_frace_SIMPLE():
#     day_count_type = DayCountTypes.SIMPLE
#     day_count = DayCount(day_count_type)
#     answer = day_count.year_frac(start, end, end, finFreq)

#     assert round(answer[0], 4) == 0.3836

# ---------------------------------------------------------------
