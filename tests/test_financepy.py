
import timeit
import datetime

import numpy


from financepy.utils.frequency import FrequencyTypes
from financepy.utils.day_count import DayCount, DayCountTypes
from financepy.utils.date import Date as Date

import xtenors
import xtuples as xt

now = datetime.datetime.now

print("\n--")

# ---------------------------------------------------------------

def unindent(s):
    ls = s.split("\n")
    white = min(xt.iTuple(ls).filter(lambda s: len(s.strip())).map(
        lambda l: xt.iTuple(l).take_while(lambda c: c == " ").len()
    ))
    return "\n".join([
        "import datetime",
        "import xtenors",
        "import xtuples as xt",
        "from financepy.utils.date import Date",
        "from financepy.utils.frequency import FrequencyTypes",
        "from financepy.utils.day_count import DayCount, DayCountTypes",
    ] + [l[white:] for l in ls])

import inspect
def make_spec(f, **kwargs):
    source = unindent(inspect.getsource(f))
    for k, v in kwargs.items():
        # assuming is string
        source = source.replace(k, '"{}"'.format(v))
    name = f.__name__
    return dict(
        stmt="f()",
        setup=source,
        name=name,
        f=f,
    )

def time_func(f, iters = 10 ** 5, max_run = 10 * (10 ** 6)):
    total_run = 0
    samples = []
    start = datetime.datetime.now()
    runs = int(iters / 100)
    for i in range(100):
        res = [f() for _ in range(runs)]
        end = datetime.datetime.now()
        t = (end - start).microseconds
        samples.append(t)
        total_run += t
        if total_run > max_run:
            break
        start = end
    average = numpy.mean(samples)
    return average / 1000 # in milliseconds

def compare_speeds(f1, f2, **kwargs):

    spec1 = make_spec(f1, **kwargs)
    spec2 = make_spec(f2, **kwargs)
    
    print("--")

    res1 = time_func(f1)
    res2 = time_func(f2)

    # res1 = timeit.timeit(stmt=spec1["stmt"], setup=spec1["setup"])
    # res2 = timeit.timeit(stmt=spec2["stmt"], setup=spec2["setup"])

    # TODO: check result same

    assert res2 < res1, {
        spec1["name"]: res1,
        spec2["name"]: res2,
    }
    print({
        spec1["name"]: res1,
        spec2["name"]: res2,
    })

# ---------------------------------------------------------------

# TODO: test results as well

def add_years_financepy():
    def f():
        d = Date(1, 1, 2010)
        return d.add_years(3)
    f.__name__ = "add_years_financepy"
    return f

def add_years_xtenors():
    def f():
        d = datetime.date(2010, 1, 1)
        return xtenors.arithmetic.add(d, years=3)
    f.__name__ = "add_years_xtenors"
    return f

def test_add_years():
    compare_speeds(add_years_financepy(), add_years_xtenors())
    

# ---------------------------------------------------------------

# round(answer[0], 4) == 0.3889
def year_frac_30_360_bond_financepy():
    def f():
        start = Date(1, 1, 2019)
        end = Date(21, 5, 2019)
        finFreq = FrequencyTypes.ANNUAL
        day_count_type = DayCountTypes.THIRTY_360_BOND
        day_count = DayCount(day_count_type)
        return day_count.year_frac(start, end, end, finFreq)
    f.__name__ = "year_frac_30_360_bond_financepy"
    return f 

def year_frac_30_360_bond_xtenors():
    # flags=xt.Flags().set(
    #     xtenors.conventions.Day_Count.N_30_360_BOND,
    #     xtenors.conventions.Day_Count_Factor.N_360,
    # )
    def f():
        start = datetime.date(2019, 1, 1)
        end = datetime.date(2019, 5, 21)
        return xtenors.day_factor(
            start,
            end,
            freq=1.,
            count=xtenors.conventions.Day_Count.N_30_360_BOND,
            factor=xtenors.conventions.Day_Count_Factor.N_360,
            # flags=flags,
        )
    f.__name__ = "year_frac_30_360_bond_xtenors"
    return f

def test_day_counts():
    compare_speeds(
        year_frac_30_360_bond_financepy(), 
        year_frac_30_360_bond_xtenors(), 
    )

# ---------------------------------------------------------------

# TODO: test results as well

def add_tenor_financepy(_tenor_):
    def f():
        d = Date(1, 1, 2010)
        return d.add_tenor(_tenor_)
    f.__name__ = "f_add_tenor_financepy{}".format(_tenor_.replace(
        "-", "_"
    ))
    return f

def add_tenor_xtenors(_tenor_):
    def f():
        d = datetime.date(2010, 1, 1)
        return xtenors.Tenor.parse(_tenor_).add(d)
    f.__name__ = "f_add_tenor_xtenors{}".format(_tenor_.replace(
        "-", "_"
    ))
    return f

def test_add_tenors():
    
    tenor = "1Y"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "1M"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "1W"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "1D"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "3Y"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "3M"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "3W"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "3D"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "-3Y"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "-3M"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "-3W"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )
    
    tenor = "-3D"
    compare_speeds(
        add_tenor_financepy(tenor), 
        add_tenor_xtenors(tenor),
        _tenor_=tenor,
    )

# ---------------------------------------------------------------

# TODO: 

# add business days (both results and speed)

# TODO:

# date adjustment (both results and speed)

# TODO:

# day counts (both results and speed)

# TODO: 

# schedule generation (both results and speed)

# ---------------------------------------------------------------
