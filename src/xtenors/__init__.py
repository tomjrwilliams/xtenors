

import os
import sys
import pathlib

if pathlib.Path(os.getcwd()).parts[-1] == "xtenors":
    sys.path.append("./__local__")

    import PATHS

    if PATHS.XTUPLES not in sys.path:
        sys.path.append(PATHS.XTUPLES)
        print(sys.path)

from . import dates
from . import units
from . import conventions
from . import iteration
from . import calendars
from .xtenors import *