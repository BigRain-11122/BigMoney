# -*- coding: utf-8 -*-
"""Find where append_ledger writes + verify THEME_DEEPEN_P1 landed."""
import glob
import inspect
import json
import sys

sys.path.insert(0, "scripts")
import science_gates as sg

src = inspect.getsource(sg.append_ledger)
print(src[1200:3000])
print("--- ledger_head source ---")
print(inspect.getsource(sg.ledger_head)[:1200])
