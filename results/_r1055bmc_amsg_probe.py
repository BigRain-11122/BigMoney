# -*- coding: utf-8 -*-
import io
t = io.open(r"results\_w254bmc_derive_editor.py", encoding="utf-8").read()
i1 = t.find('"P5e-tail-amsg")')
i0 = t.rfind("rep(", 0, i1)
print(t[i0:i1 + 15])
