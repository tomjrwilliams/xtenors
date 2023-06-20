
# ---------------------------------------------------------------

import sys
import pathlib
import importlib.util

path = pathlib.Path("./src/xtenors/__init__.py").resolve()
spec = importlib.util.spec_from_file_location(
    "xtenors", str(path)
    #
)

xtenors = importlib.util.module_from_spec(spec)
sys.modules["xtenors"] = xtenors
spec.loader.exec_module(xtenors)

# ---------------------------------------------------------------

print(xtenors.Tenor("D", 1))
print(xtenors.conventions.LIBRARY().PYTHON)

# ---------------------------------------------------------------
