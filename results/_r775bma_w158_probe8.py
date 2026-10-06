# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
p158 = n1mod.WAVE_CONFIGS[158]["prereg"]
print("type:", type(p158))
print("first 3 elements:", p158[:3] if isinstance(p158, tuple) else p158[:120])
print("full head:", "".join(p158)[:200] if isinstance(p158, tuple) else str(p158)[:200])
