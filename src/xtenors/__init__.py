

import os
import sys
import pathlib

if pathlib.Path(os.getcwd()).parts[-1] == "xtenors":
    sys.path.append("./__local__")

    import PATHS

    if PATHS.XTUPLES not in sys.path:
        sys.path.append(PATHS.XTUPLES)
        print(sys.path)

# from .xtenors import (
#     UNIT,
#     cast_date,
#     calendar_iterator,
#     next_valid_date,
#     adjust_date_forward,
#     adjust_date_backward,
#     adjust_date,
#     day_count,
#     tenor_add,
#     tenor_rsub,
#     tenor_sub,
#     tenor_between,
#     update_unit,
#     update_n,
#     Tenor,
# )