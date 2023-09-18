
# ---------------------------------------------------------------

# https://github.com/domokane/FinancePy/blob/master/financepy/utils/schedule.py

# ---------------------------------------------------------------

# TODO: eom
# TODO: adjust term (default yes in cds, no in swap)

def generate_forward(
    ddt1, ddt2, tenor, iterator=None,
):
    return


def generate_backward(
    ddt1, ddt2, tenor, iterator=None,
):
    return

def generate(
    ddt1, ddt2, tenor, schedule=None, # = direction
):
    return

# ---------------------------------------------------------------

# then payments generated as

# year_frac (= day_factor) between each pair of dates in schwedule
# payment = frac * notional * coupon

# optional payment lag from coupon date

# ---------------------------------------------------------------

# payments == flows can then be valued against a given discount curve

# ---------------------------------------------------------------
