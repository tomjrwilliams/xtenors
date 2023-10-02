
from __future__ import annotations

import enum

import xtuples as xt

# ---------------------------------------------------------------

class Overflow(enum.Enum):
    ERROR = 0
    PREV = -1
    NEXT = 1

# ---------------------------------------------------------------

class Roll(enum.Enum):
    ERROR = 0
    PRECEDING = -1
    FOLLOWING = 1

class Modified(enum.Enum):
    UNMODIFIED = 0
    MODIFIED = 1

# ---------------------------------------------------------------

class Format(enum.Enum):
    ISO = 0

# ---------------------------------------------------------------

