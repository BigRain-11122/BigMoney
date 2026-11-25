#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for r2114 (results/idx_fut_carry_rebudget_floor.json)

Every control is run against the PUBLISHED face and the LIVE check(), not against a
re-implementation: an assertion that only agrees with itself proves nothing (r1935).
Temp copies are mutated in place, check() is called through the real module, and the
originals are restored byte-for-byte in a finally block.

Usage: python results/_r2114bmc_floor_negative.py
"""
from __future__ import print_function

import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "scripts", "idx_fut_carry_rebudget_floor.py")
FACE = os.path.join(ROOT, "results", "idx_fut_carry_rebudget_floor.json")
PAGE = os.path.join(ROOT, "research", "IDX_FUT_CARRY_REBUDGET_FLOOR.md")
CAP = os.path.join(ROOT, "results", "etf_book_capacity_edge.json")

spec = importlib.util.spec_from_file_location("r2114face", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

results = []


def ctl(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def load(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(obj, path):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return fh.read()


face = load(FACE)
page = read_text(PAGE)

# ---------------------------------------------------------------- published-face identities
ctl("verdict is a frozen token", face.get("verdict") in mod.VERDICTS, face.get("verdict"))

bad = []
for rung_key, entry in (face.get("rungs") or {}).items():
    for set_key, s in (entry.get("sets") or {}).items():
        for leg_key, row in s["legs"].items():
            if row["weight_x_nav"] <= 0:
                continue
            if abs(row["one_lot_floor_nav_cny"] * row["weight_x_nav"]
                   - row["notional_per_lot_cny"]) > 0.05:
                bad.append((rung_key, set_key, leg_key))
ctl("floor x weight == one lot's notional on every leg", not bad, str(bad[:2]))

bad = []
for rung_key, entry in (face.get("rungs") or {}).items():
    s = (entry.get("sets") or {}).get("as_built") or {}
    for leg_key, lots in (("IC_leg", entry.get("ic_lots_published")),
                          ("IM_leg", entry.get("im_lots_published"))):
        row = (s.get("legs") or {}).get(leg_key) or {}
        want = (lots or 0) * row.get("notional_per_lot_cny", 0) / mod.NAV_LENS_CNY
        if abs(want - row.get("weight_x_nav", 0)) > 1e-4:
            bad.append((rung_key, leg_key, want, row.get("weight_x_nav")))
ctl("as-built weights are whole lots at the 1M lens", not bad, str(bad[:2]))

reb = face["rungs"]["1/1"]["sets"]["re_budget"]
w = reb["window"]
legs = reb["legs"]
ctl("re-budget lower end is the max per-leg floor",
    abs(max(r["one_lot_floor_nav_cny"] for r in legs.values()) - w["lower_cny"]) <= 0.01,
    "{} vs {}".format(max(r["one_lot_floor_nav_cny"] for r in legs.values()), w["lower_cny"]))
ctl("re-budget binding leg is IM (the larger floor)", reb["binding_leg"] == "IM_leg",
    reb["binding_leg"])
ctl("upper end == capacity today / equity weight",
    abs(face["equity_capacity"]["today_cny"] / reb["equity"]["weight_x_nav"]
        - w["upper_today_cny"]) <= 0.02, w["upper_today_cny"])
ctl("verdict follows the rule on today's reading",
    (reb["verdict"] == mod.V_OPEN) == (w["lower_cny"] <= w["upper_today_cny"]),
    reb["verdict"])
ctl("empty window names the equity weight that would fit",
    abs(w["equity_weight_that_would_fit_at_floor"]
        - face["equity_capacity"]["today_cny"] / w["lower_cny"]) <= 1e-6,
    w["equity_weight_that_would_fit_at_floor"])
ctl("floor_over_upper_today == lower / upper",
    abs(w["floor_over_upper_today"] - w["lower_cny"] / w["upper_today_cny"]) <= 1e-5,
    w["floor_over_upper_today"])

ctl("rung 0/1 carries no re-budget (nothing invented)",
    "re_budget" not in (face["rungs"]["0/1"].get("sets") or {}),
    ",".join(sorted((face["rungs"]["0/1"].get("sets") or {}).keys())))

# notionals must be the margin face's own numbers, not re-derived here
margin = load(os.path.join(ROOT, "results", "idx_fut_carry_margin.json"))
bad = []
for prod in ("IC", "IM"):
    if face["notionals"][prod]["notional_per_lot_cny"] != margin["products"][prod]["notional_per_lot_cny"]:
        bad.append(prod)
ctl("per-lot notionals are imported verbatim from the margin face", not bad, str(bad))

# the median estimator must stay the capacity face's own (upper middle element)
cap = load(CAP)
readings = sorted(s["capital_where_at_line_cny"] for s in cap["sessions"])
ctl("capacity median uses the source's upper-middle definition",
    abs(readings[len(readings) // 2] - face["equity_capacity"]["median_cny"]) <= 0.01,
    "{} vs {}".format(readings[len(readings) // 2], face["equity_capacity"]["median_cny"]))
ctl("cross-face capacity summary matches",
    (face["cross_face"]["capacity_summary"] or {}).get("status") == "CROSS_FACE_MATCHES",
    (face["cross_face"]["capacity_summary"] or {}).get("status"))
ctl("open-capital rung is named a different ruler",
    (face["cross_face"]["open_capital"] or {}).get("status") == "DIFFERENT_RULER_NAMED",
    (face["cross_face"]["open_capital"] or {}).get("status"))

# ---------------------------------------------------------------- page
ctl("page prints the verdict token", face["verdict"] in page)
ctl("page prints both ends of the window", "下限" in page and "上限" in page)
ctl("page prints the multiple of the breach", "2.67" in page)
ctl("page prints the equity weight that would fit", "0.3742" in page)
ctl("page prints no literal double percent", "%%" not in page)
ctl("page names the ADV line's own five names", all(n in page for n in face["equity_capacity"]["names"]))

# ---------------------------------------------------------------- live check() three states
tmpdir = tempfile.mkdtemp(prefix="r2114neg_")
saved_out, saved_doc = mod.OUT_PATH, mod.DOC_PATH
try:
    tmp_face = os.path.join(tmpdir, "face.json")
    tmp_page = os.path.join(tmpdir, "face.md")
    shutil.copyfile(FACE, tmp_face)
    shutil.copyfile(PAGE, tmp_page)
    mod.OUT_PATH, mod.DOC_PATH = tmp_face, tmp_page

    def run_check():
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = mod.check()
        finally:
            sys.stdout = old
        return rc, buf.getvalue()

    rc, out = run_check()
    ctl("check() passes on untouched copies", rc == 0, out.splitlines()[:1])

    tampered = load(tmp_face)
    tampered["rungs"]["1/1"]["sets"]["re_budget"]["window"]["upper_today_cny"] += 5000.0
    dump(tampered, tmp_face)
    rc, out = run_check()
    ctl("a hand-edited window number says CHECK FAILED and not STALE",
        rc == 3 and "CHECK FAILED" in out and "STALE" not in out, out.splitlines()[:1])

    moved = load(tmp_face)
    moved["inputs"]["capacity_edge"]["sha256"] = "f" * 64
    dump(moved, tmp_face)
    rc, out = run_check()
    ctl("a moved input face says STALE", rc == 3 and "STALE" in out, out.splitlines()[:1])

    dump(load(FACE), tmp_face)
    with io.open(tmp_page, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page.replace("窗口", "窗 口", 1))
    rc, out = run_check()
    ctl("a page that no longer re-renders says STALE",
        rc == 3 and "STALE" in out and "re-render" in out, out.splitlines()[:1])

    with io.open(tmp_page, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(page)
    rc, out = run_check()
    ctl("restoring the page and the face turns it green again", rc == 0, out.splitlines()[:1])
finally:
    mod.OUT_PATH, mod.DOC_PATH = saved_out, saved_doc
    shutil.rmtree(tmpdir, ignore_errors=True)

failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(("PASS " if ok else "FAIL ") + name + (("  <- " + str(detail)) if (detail and not ok) else ""))
print("{} controls, {} failed -> {}".format(
    len(results), len(failed), "ALL_CONTROLS_PASS" if not failed else "CONTROLS_FAILED"))
sys.exit(0 if not failed else 1)
