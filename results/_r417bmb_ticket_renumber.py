# -*- coding: utf-8 -*-
"""r417 bm-b: ticket renumber T-118 -> T-119 (collision yield to bm-c's W7 freeze
ticket which landed on origin first per commit-time law). Byte-safe raw-text
replacements + json parse-verify. Idempotent (second run = zero replacements)."""
import json
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"

SUBS = [
    ("T-2026-09-29-118", "T-2026-09-29-119"),
    ("T-118 drift-debt", "T-119 drift-debt"),
    ("（T-118 五波漂移债清偿）", "（T-119 五波漂移债清偿）"),
    ("（T-118 漂移债清偿）", "（T-119 漂移债清偿）"),
    ("回填（T-118）", "回填（T-119）"),
]

TARGETS = [
    "research/TRIAL_LABOR_W1_PREREG.md",
    "research/TRIAL_LABOR_W2_PREREG.md",
    "research/TRIAL_LABOR_W3_PREREG.md",
    "research/TRIAL_LABOR_W4_PREREG.md",
    "research/TRIAL_LABOR_W5_PREREG.md",
    "docs/trial_labor/CEO-REPORT-WAVE1-20260929.md",
    "docs/trial_labor/CEO-REPORT-WAVE2-5-20260929.md",
    "results/gate_attrition.json",
    "results/gate_attrition.bm-b.json",
]

for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    raw = io.open(p, encoding="utf-8", newline="").read()
    n = 0
    for old, new in SUBS:
        c = raw.count(old)
        if c:
            raw = raw.replace(old, new)
            n += c
    if n:
        with io.open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(raw)
    if rel.endswith(".json"):
        json.loads(io.open(p, encoding="utf-8").read())  # parse-verify
    print(f"{rel}: {n} replacement(s)")
