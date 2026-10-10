# -*- coding: utf-8 -*-
"""r963 probe: dump actual prereg-source regions for each failing pr anchor."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = open(os.path.join(ROOT, "research", "PERPETUAL_N1_W204_PREREG.md"),
         encoding="utf-8").read()
t = t.replace("2026", "\x00Y26")

anchors = [
    ("pre-header2", "engine_owner 行 192 注册在册"),
    ("pre-arch1", "本机 bm-c 实例"),
    ("pre-claim-src", "本窗领取令=CEO 直令"),
    ("pre-universe", "W203=bm-a r930 席位"),
    ("pre-receipt", "ADMIT 回执=results/_w204bmc"),
    ("pre-claim2", "本机引擎队列空转+py_cpu"),
    ("pre-seat2", "本机席位 MSG-\x00Y261010-0022-bmc-w204-seat"),
    ("pre-claim3", "引擎线第 194 波"),
    ("pre-ignite", "实例=live daemon"),
    ("pre-B-tier", "entry rng=**463_604+j**"),
    ("pre-disjoint3", "本波机验 ADMIT"),
]
for tag, a in anchors:
    i = t.find(a)
    if i < 0:
        print("[%s] ANCHOR NOT FOUND: %r" % (tag, a))
        continue
    print("[%s] ..." % tag)
    print(t[i:i + 420].replace("\x00Y26", "2026"))
    print("-" * 70)
