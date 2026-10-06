# -*- coding: utf-8 -*-
import io
b = io.open(r"research\PERPETUAL_N1_W158_PREREG.md", encoding="utf-8").read()
tail = b[-1200:]
print(tail)
