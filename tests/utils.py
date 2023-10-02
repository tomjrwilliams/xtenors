
import inspect

import itertools

import datetime

import numpy

# ---------------------------------------------------------------

def lineno(n_back = 0):
    frame = inspect.currentframe().f_back
    for _ in range(n_back):
        frame = frame.f_back
    return frame.f_lineno

def outer_func_name(n_back = 0):
    frame = inspect.currentframe().f_back
    for _ in range(n_back):
        frame = frame.f_back
    return frame.f_code.co_name

# ---------------------------------------------------------------

tolerances=dict(
    rtol=1e-3,
    atol=1e-2,
)

def is_close(
    v1, v2, b=True, results=None, n_max=0, dp=3, **tols
):
    if results is None:
        results = dict(
            v1=numpy.round(v1, dp), v2=numpy.round(v2, dp)
        )

    tols = {**tolerances, **tols}
    diff = numpy.subtract(v1, v2)

    n_diff = ((
        numpy.isclose(v1, v2, **tols)
    ) != b).sum()

    assert n_diff <= n_max, dict(
        **results,
        diff=numpy.round(diff, 3),
        n_diff=n_diff,
        diff_max=numpy.max(numpy.abs(diff))
    )

    return True

# ---------------------------------------------------------------

def log_time(start, times):
    end = datetime.datetime.now()
    t = (end - start).microseconds
    times.append(t)
    return end, t

def time_func(*fs, iters = 10 ** 5, max_time = 10 * (10 ** 6)):
    
    n = len(fs)
    f_times = itertools.cycle(zip(
        range(n), fs, [[] for _ in fs]
    ))

    runs = int(iters / 100)
    start = datetime.datetime.now()

    total = 0

    for _ in range(100):
        for _ in range(n):

            i, f, times = next(f_times)

            res = [f() for _ in range(runs)]
            start, t = log_time(start, times)
            
            total += t
            if total > max_time:
                break
        
        # discard one instance
        # so each time we start with a different func
        i, _, _ = next(f_times)
    
    while i < n - 1:
        i, _, _ = next(f_times)
        
    return tuple(
        f() for f in fs
    ) + tuple(
        numpy.mean(times) / 1000
        for _, (_, _, times) in zip(range(n), f_times)
    )

    # in milliseconds

# ---------------------------------------------------------------

def compare(
    f1,
    f2,
    cast_left = None,
    cast_right = None,
    fastest = None,
    **kwargs,
):

    print("--")

    res_1, res_2, millis_1, millis_2 = time_func(f1, f2, **kwargs)

    if cast_left is not None:
        res_1 = cast_left(res_1)

    if cast_right is not None:
        res_2 = cast_right(res_2)

    res_match = (
        res_1 == res_2
        if not isinstance(res_1, float)
        else is_close(res_1, res_2)
    )

    failed = not (res_match and (
        round(millis_2, 1) <= round(millis_1, 1)
        if fastest == 1
        else round(millis_1, 1) <= round(millis_2, 1)
        if fastest == 0
        else True
    ))

    result = {
        **{
            "pass": not failed,
            "line": lineno(n_back=1),
        },
        **({} if fastest is None else {
            "fastest": fastest,
        }),
        **{
            "milliseconds": {
                f1.__name__: round(millis_1, 2),
                f2.__name__: round(millis_2, 2),
            },
            "result": res_1 if res_match else {
                f1.__name__: res_1,
                f2.__name__: res_2,
            },
        },
    }
    for k, v in result.items():
        print(k, v)

    assert not failed, result

# ---------------------------------------------------------------
