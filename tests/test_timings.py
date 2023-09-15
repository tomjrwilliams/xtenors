
import datetime

from financepy.utils.date import Date as FinDate

import xtenors

now = datetime.datetime.now

print("\n--")

# ---------------------------------------------------------------

def compare_speeds(f1, f2, iters = 1000):
    
    print("--")

    start1 = now()
    res1 = [f1() for _ in range(iters)]
    end1 = now()

    start2 = now()
    res2 = [f2() for _ in range(iters)]
    end2 = now()

    res1 = (end1-start1).microseconds / 1000
    res2 = (end2-start2).microseconds / 1000

    # TODO: check result same

    assert res2 < res1, {
        f1.__name__: res1,
        f2.__name__: res2,
    }
    print({
        f1.__name__: res1,
        f2.__name__: res2,
    })

# ---------------------------------------------------------------

def add_years_financepy():
    d = FinDate(1, 1, 2010)
    return d.add_years(3)

def add_years_xtenors():
    d = datetime.date(2010, 1, 1)
    return xtenors.arithmetic.add(d, years=3)

def test_add_years():
    compare_speeds(add_years_financepy, add_years_xtenors)
    
# ---------------------------------------------------------------

def add_tenor_financepy(tenor):
    def f():
        d = FinDate(1, 1, 2010)
        return d.add_tenor(tenor)
    f.__name__ = "f_add_tenor_financepy{}".format(tenor)
    return f

def add_tenor_xtenors(tenor):
    def f():
        d = datetime.date(2010, 1, 1)
        return xtenors.Tenor.parse(tenor).add(d)
    f.__name__ = "f_add_tenor_xtenors{}".format(tenor)
    return f

def test_add_tenors():
    
    tenor = "1Y"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "1M"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "1W"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "1D"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "3Y"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "3M"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "3W"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "3D"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "-3Y"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "-3M"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "-3W"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))
    
    tenor = "-3D"
    compare_speeds(add_tenor_financepy(tenor), add_tenor_xtenors(tenor))

# ---------------------------------------------------------------
