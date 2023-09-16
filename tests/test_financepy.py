
import timeit
import datetime

from financepy.utils.date import Date as FinDate

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
        "from financepy.utils.date import Date as FinDate",
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

def compare_speeds(f1, f2, **kwargs):

    spec1 = make_spec(f1, **kwargs)
    spec2 = make_spec(f2, **kwargs)
    
    print("--")

    res1 = timeit.timeit(stmt=spec1["stmt"], setup=spec1["setup"])
    res2 = timeit.timeit(stmt=spec2["stmt"], setup=spec2["setup"])

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
        d = FinDate(1, 1, 2010)
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

# TODO: test results as well

def add_tenor_financepy(_tenor_):
    def f():
        d = FinDate(1, 1, 2010)
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
