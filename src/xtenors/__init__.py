

import os
import sys
import pathlib

if pathlib.Path(os.getcwd()).parts[-1] == "xtenors":
    sys.path.append("./__local__")

    import PATHS

    if PATHS.XTUPLES not in sys.path:
        sys.path.append(PATHS.XTUPLES)
        print(sys.path)

# import all modules, so can load individually
from . import dates
from . import units
from . import conventions
from . import iteration
from . import calendars
from . import arithmetic
from . import adjustments
from . import counts

# also convenience import other specific commonly used items
from .dates import *
from .units import *
from .iteration import Iterator
from .counts import day_count, day_factor
from .adjustments import adjust
from .xtenors import *