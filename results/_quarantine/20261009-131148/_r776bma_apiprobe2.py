# -*- coding: utf-8 -*-
"""API check: theme_ignition_census detect function signature."""
import inspect
import sys

sys.path.insert(0, "scripts")
import theme_ignition_census as tic

print("funcs:", [x for x in dir(tic) if not x.startswith("_") and callable(getattr(tic, x))])
for name in dir(tic):
    if name.startswith("detect") or name.startswith("ignition"):
        obj = getattr(tic, name)
        if callable(obj):
            print(name, inspect.signature(obj))
