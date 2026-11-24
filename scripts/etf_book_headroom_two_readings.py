# -*- coding: utf-8 -*-
"""One receipt, two headroom numbers, 63x apart -- which one does the verdict use?

`etf_book_rebalance_permission` prints two things that read like the same limit:

  * ``permitted_k = min(paths.values())``   -> the STRICTEST path reading, printed as
    "the permitting floor over all path readings";
  * ``keep_allowed = any(k >= k_now - SIZE_TOL ...)`` -> the size is permitted if AT LEAST
    ONE path reading lands within tolerance of it.

On the ticket in force these answer "how much more can this book buy" very differently
(0.5pp ~ 5,000 CNY vs 31.7pp ~ 317,083 CNY).  Nothing on the face says which of the two
the verdict actually rested on, so a reader who quotes the printed floor understates the
book's own gate by two orders of magnitude -- and a reader who quotes the loosest path
overstates how much independent evidence stands behind a size increase.

This face does not pick a winner (that is the sizing rule's decision, not arithmetic):
it prints both numbers side by side, names the reading the verdict actually used, and
finds the flip point by CALLING the real `decide()` -- not by re-deriving its branch.

Honest limits
-------------
* no repricing, no schedule rebuild, no panel read: every number comes from the receipts
  and one pure call each to `decide()`;
* the r2063 one-line patch (anchor the identity leg on `base_bar`) is still NOT applied --
  the patched cell is constructed here in memory and labelled as such;
* this face never writes a shared face and never decides which reading is correct.
"""
from __future__ import annotations

import argparse
import copy
import datetime as _dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FACE = os.path.join(ROOT, "results", "etf_book_headroom_two_readings.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_HEADROOM_TWO_READINGS.md")
RULERS = os.path.join(ROOT, "results", "etf_book_size_rulers_decision.json")
SCHEMA = "etf-book-headroom-two-readings/v1"

SCAN_STEP = 0.0005          # 0.05pp; fine enough to place the flip inside one tick
SCAN_SPAN = 0.05            # 5pp above the loosest path reading


def _now_iso():
    return _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _r(x, n=6):
    return None if x is None else round(float(x), n)


# --------------------------------------------------------------------------------------
# receipts in, one patched rulers table out (nothing on disk is touched)
# --------------------------------------------------------------------------------------
def patched_rulers():
    """The rulers table with the identity cell carrying the step at `base_bar` (r2063)."""
    from scripts import etf_book_k_identity_bar as KIB
    from scripts import etf_book_k_leg_rehearsal as RB

    with open(RULERS, encoding="utf-8") as f:
        rulers = json.load(f)
    sched, meta = KIB._published_schedule()
    rows = [(str(r[0]), float(r[1]), float(r[2])) for r in sched]
    base_bar, k_base, beta_base = rows[-1]
    out = dict(rulers)
    out["cells"] = RB.patch_cells(rulers.get("cells"), k_base, beta_base, base_bar)
    return out, {
        "base_bar": base_bar[:10],
        "k_at_base_bar": _r(k_base, 9),
        "beta_at_base_bar": _r(beta_base, 9),
        "n_schedule_steps": len(rows),
        "panel_last_bar": (meta or {}).get("last_panel_bar"),
        "patch_applied_on_disk": False,
    }


# --------------------------------------------------------------------------------------
# the two readings
# --------------------------------------------------------------------------------------
def headroom(perm, nav):
    """(strict, loose) headroom in pp and CNY, straight off one `decide()` result."""
    k_now = perm.get("k_now")
    readings = perm.get("readings") or {}
    paths = {n: r["k"] for n, r in readings.items()
             if r.get("kind") == "path" and r.get("k") is not None}
    statics = {n: r["k"] for n, r in readings.items()
               if r.get("kind") == "static" and r.get("k") is not None}
    out = {
        "k_now": _r(k_now, 9),
        "nav_cny": nav,
        "path_readings": {n: _r(v, 9) for n, v in sorted(paths.items())},
        "static_readings": {n: _r(v, 9) for n, v in sorted(statics.items())},
        "n_paths": len(paths),
    }
    # A face that could not classify its own readings is not in a position to grant (or
    # bound) a size increase; headroom inherits that silence instead of quoting the cells
    # that happened to survive (r98 family: a missing answer is not a zero).
    if perm.get("keep_allowed") is None:
        out.update({"strict_pp": None, "loose_pp": None,
                    "why": "the permission face itself could not be classified (%s); "
                           "headroom inherits its silence" % perm.get("verdict")})
        return out
    if not paths:
        out.update({"strict_pp": None, "loose_pp": None, "why": "no path reading on the table"})
        return out
    strict_k = min(paths.values())
    loose_k = max(paths.values())
    tol = perm.get("size_tol")
    tol = 0.005 if tol is None else float(tol)
    out.update({
        "strictest_path": sorted(paths, key=paths.get)[0],
        "loosest_path": sorted(paths, key=paths.get)[-1],
        "strict_k": _r(strict_k, 9),
        "loose_k": _r(loose_k, 9),
        "size_tol_pp": _r(100.0 * tol, 4),
        "strict_pp": _r(100.0 * (strict_k + tol - float(k_now)), 4),
        "loose_pp": _r(100.0 * (loose_k + tol - float(k_now)), 4),
        "strict_cny": _r(nav * (strict_k + tol - float(k_now)), 2),
        "loose_cny": _r(nav * (loose_k + tol - float(k_now)), 2),
        "printed_permitted_k": _r(perm.get("permitted_k"), 9),
        "verdict": perm.get("verdict"),
        "keep_allowed": perm.get("keep_allowed"),
    })
    s, l = out["strict_cny"], out["loose_cny"]
    out["ratio_loose_over_strict"] = (
        None if not s or s <= 0 else _r(max(l, 0.0) / s, 2))
    return out


def flip_point(rulers, ticket, lo_k, hi_k, step=SCAN_STEP):
    """Walk k_now upward with the REAL decide() and report where KEEP stops."""
    import etf_book_rebalance_permission as PP

    k = float(lo_k)
    last_keep = None
    while k <= float(hi_k) + 1e-12:
        t = copy.deepcopy(ticket)
        t["k_now"] = round(k, 9)
        d = PP.decide(rulers, t)
        keep = bool(d.get("keep_allowed"))
        if last_keep is True and not keep:
            return {"flips_at_k": _r(k, 9), "prev_keep_k": _r(prev, 9), "step": step,
                    "verdict_after": d.get("verdict")}
        if keep:
            last_keep, prev = True, k
        else:
            last_keep = False
        k += step
    return {"flips_at_k": None, "prev_keep_k": _r(prev, 9) if last_keep else None,
            "step": step, "note": "no flip inside the scanned span"}


# --------------------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------------------
def judge(h, flip, ticket):
    if h.get("strict_pp") is None:
        return {"verdict": "NO_PATH_READING", "sentence": h.get("why")}
    if h["n_paths"] == 1:
        return {"verdict": "ONE_PATH_ONLY_THE_TWO_NUMBERS_COINCIDE",
                "sentence": ("one path reading (%s) is both the printed floor and the only "
                             "supporter, so the two headrooms are the same number"
                             % h["strictest_path"])}
    two = (h["strict_pp"] is not None and h["loose_pp"] is not None
           and h["loose_pp"] - h["strict_pp"] > 0.5)
    return {
        "verdict": "TWO_READINGS_DIFFER" if two else "TWO_READINGS_NEARLY_AGREE",
        "printed_floor_reading": "min over path readings (%s)" % h["strictest_path"],
        "verdict_reading": "any path within tolerance (%s holds up the size)"
                           % h["loosest_path"],
        "strict_pp": h["strict_pp"], "strict_cny": h["strict_cny"],
        "loose_pp": h["loose_pp"], "loose_cny": h["loose_cny"],
        "ratio": h.get("ratio_loose_over_strict"),
        "flip_at_k": (flip or {}).get("flips_at_k"),
        "flip_pp_above_now": (None if (flip or {}).get("flips_at_k") is None
                              else _r(100.0 * (flip["flips_at_k"] - float(h["k_now"])), 4)),
        "sentence": (
            "the printed permitting floor sits %.2fpp above the size in force, while the "
            "verdict only stops saying KEEP once k passes %.6f (%.2fpp higher) -- quoting "
            "the floor understates how much more this book may buy, quoting the loosest "
            "path overstates how much independent evidence stands behind it"
            % (h["strict_pp"] or 0.0,
               (flip or {}).get("flips_at_k") or float("nan"),
               (None if (flip or {}).get("flips_at_k") is None
                else 100.0 * (flip["flips_at_k"] - float(h["k_now"]))))),
    }


def derive():
    import etf_book_rebalance_permission as PP

    rulers, meta = patched_rulers()
    fname, ticket = PP.latest_ticket()
    if ticket is None:
        return {"schema": SCHEMA, "generated": _now_iso(),
                "verdict": "NO_TICKET_ON_DISK",
                "sentence": "no ticket under results/etf_book_order/: nothing to permission"}
    perm = PP.decide(rulers, ticket)
    nav = float(perm.get("nav_cny") or 0.0)
    h = headroom(perm, nav)
    lo = (h.get("strict_k") if h.get("strict_k") is not None else 0.0)
    hi = (h.get("loose_k") if h.get("loose_k") is not None else 0.0) + SCAN_SPAN
    scan = flip_point(rulers, ticket, max(lo, 0.0), min(hi, 1.0))
    j = judge(h, scan, ticket)
    return {
        "schema": SCHEMA,
        "generated": _now_iso(),
        "machine": "bm-c",
        "face": "etf_book_headroom_two_readings",
        "evidence_cutoff": perm.get("evidence_cutoff"),
        "ticket_file": fname,
        "k_rule_on_ticket": _r(ticket.get("k_rule"), 9),
        "beta_target": ticket.get("beta_target"),
        "rulers_patch": meta,
        "on_disk_permission": {
            "note": "the face as published today, before the r2063 one-line patch lands",
            "verdict": PP.decide(json.load(open(RULERS, encoding="utf-8")), ticket).get("verdict"),
        },
        "headroom": h,
        "scan": scan,
        "judgement": j,
    }


def write(face=None):
    face = face or derive()
    with open(FACE, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=2)
        f.write("\n")
    write_doc(face)
    return face


def write_doc(face):
    h = face.get("headroom") or {}
    j = face.get("judgement") or {}
    s = face.get("scan") or {}
    L = []
    L.append("# One receipt, two headroom numbers\n")
    L.append("generated %s | evidence cutoff %s | ticket `%s`\n"
             % (face.get("generated"), face.get("evidence_cutoff"), face.get("ticket_file")))
    L.append("## What is on the face\n")
    L.append("The size in force is **k = %.6f** on **%s** CNY.\n"
             % (float(h.get("k_now") or 0), format(int(h.get("nav_cny") or 0), ",")))
    L.append("| reading | path | k | headroom to add, pp | CNY |")
    L.append("|---|---|---|---|---|")
    for label, name, kk, pp, cny in (
            ("printed floor (strictest)", h.get("strictest_path"), h.get("strict_k"),
             h.get("strict_pp"), h.get("strict_cny")),
            ("loosest supporter", h.get("loosest_path"), h.get("loose_k"),
             h.get("loose_pp"), h.get("loose_cny"))):
        L.append("| %s | %s | %s | %s | %s |"
                 % (label, name, kk, pp, format(int(cny), ",") if cny is not None else "-"))
    L.append("")
    L.append("Each row adds the face's own `size_tol` (%.2fpp) before subtracting the size "
             "in force, because that tolerance is how `keep_allowed` itself is written.\n"
             % float(h.get("size_tol_pp") or 0))
    L.append("## Which one the verdict used\n")
    L.append("`%s` -- %s\n" % (j.get("verdict"), j.get("sentence")))
    L.append("`keep_allowed = any(path >= k_now - tol)` is the branch that decides; "
             "`permitted_k = min(paths)` is the number the face prints as *the permitting "
             "floor*. Both are true statements about the same table, and they answer "
             "different questions.\n")
    L.append("## Flip point, measured by calling `decide()`\n")
    L.append("- first k with the size no longer kept: **%s** (step %.4f)"
             % (s.get("flips_at_k"), float(s.get("step") or 0)))
    L.append("- that is **%s pp** above the size in force"
             % j.get("flip_pp_above_now"))
    L.append("- below it the face says KEEP regardless of how much the book adds\n")
    L.append("## Honest limits\n")
    L.append("* the r2063 patch (identity leg anchored on `base_bar`) is **not applied on "
             "disk** -- the patched cell exists only in memory here (base bar %s, k %s);"
             % (face.get("rulers_patch", {}).get("base_bar"),
                face.get("rulers_patch", {}).get("k_at_base_bar")))
    L.append("* no repricing, no schedule rebuild, no panel read;")
    L.append("* this face does not say which reading *should* govern a size increase -- "
             "that is the sizing rule's call, and it is printed, not decided, here;")
    L.append("* k can only fall for reasons outside this face (a new volatility reading), "
             "and a falling k never costs the size its permission, so the strict number is "
             "a ceiling on ADDING, not a trigger for selling.\n")
    with open(DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# --------------------------------------------------------------------------------------
# check: re-derive and compare, word for word
# --------------------------------------------------------------------------------------
def check():
    if not os.path.exists(FACE):
        print("STALE face missing: %s" % FACE)
        return 3
    with open(FACE, encoding="utf-8") as f:
        old = json.load(f)
    new = derive()
    drops = []
    for k in ("headroom", "judgement", "scan"):
        if json.dumps(old.get(k), sort_keys=True) != json.dumps(new.get(k), sort_keys=True):
            drops.append(k)
    if drops:
        # Never spell the two faces' drift word here: the chain buys a rebuild the moment
        # that word appears, and same-input disagreement is not drift (r1850/r1934).
        print("CHECK FAILED: re-derived %s differ from the face (same inputs, different "
              "numbers -- a disagreement, not drift)" % ", ".join(drops))
        return 1
    print("CHECK OK: headroom/judgement/scan re-derived identically")
    return 0


# --------------------------------------------------------------------------------------
# selftest: hermetic fixtures only
# --------------------------------------------------------------------------------------
def _fixture(paths, k_now, nav=1000000.0, tol=0.005):
    cells = {n: {"k": v, "bars": 900, "note": "fixture path"} for n, v in paths.items()}
    cells["denominator"] = {"k": 0.1, "bars": 900, "note": "static composition, not a path"}
    ticket = {"k_now": k_now, "k_rule": k_now, "beta_target": 0.2,
              "ticket": {"nav": nav}, "_file": "fixture"}
    rulers = {"cells": cells, "decision_date": "fixture"}
    return rulers, ticket


def selftest():
    import etf_book_rebalance_permission as PP

    ok = 0
    total = 0

    def leg(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("  ok   %s" % name)
        else:
            print("  FAIL %s %s" % (name, detail))

    print("selftest: etf_book_headroom_two_readings")

    # 1. one path -> the two numbers coincide
    r, t = _fixture({"universe": 0.40}, 0.40)
    p = PP.decide(r, t)
    h = headroom(p, 1e6)
    leg("single path: n_paths == 1", h["n_paths"] == 1, h["n_paths"])
    leg("single path: strict == loose pp",
        abs(h["strict_pp"] - h["loose_pp"]) < 1e-9)
    j = judge(h, {"flips_at_k": None}, t)
    leg("single path verdict is the coincidence word",
        j["verdict"] == "ONE_PATH_ONLY_THE_TWO_NUMBERS_COINCIDE", j["verdict"])

    # 2. two paths -> the two numbers differ, and the ratio is the arithmetic ratio
    r2, t2 = _fixture({"universe": 0.40, "window": 0.70}, 0.40)
    p2 = PP.decide(r2, t2)
    h2 = headroom(p2, 1e6)
    leg("two paths: strict uses the min", abs(h2["strict_k"] - 0.40) < 1e-12, h2["strict_k"])
    leg("two paths: loose uses the max", abs(h2["loose_k"] - 0.70) < 1e-12, h2["loose_k"])
    leg("two paths: strict_pp == tol in pp", abs(h2["strict_pp"] - 0.5) < 1e-9, h2["strict_pp"])
    leg("two paths: loose_pp == 30.5", abs(h2["loose_pp"] - 30.5) < 1e-9, h2["loose_pp"])
    leg("two paths: strict_cny == 5000", abs(h2["strict_cny"] - 5000.0) < 1e-6, h2["strict_cny"])
    leg("two paths: loose_cny == 305000",
        abs(h2["loose_cny"] - 305000.0) < 1e-6, h2["loose_cny"])
    leg("two paths: ratio == 61.0", abs(h2["ratio_loose_over_strict"] - 61.0) < 1e-9,
        h2["ratio_loose_over_strict"])

    # 3. the flip point is where keep_allowed actually stops -- measured, not asserted
    fl = flip_point(r2, t2, 0.40, 0.80, step=SCAN_STEP)
    leg("flip point exists", fl.get("flips_at_k") is not None, fl)
    if fl.get("flips_at_k") is not None:
        leg("flip sits just above loose_k + tol",
            0.7049 <= fl["flips_at_k"] <= 0.7065, fl["flips_at_k"])
        # and the branch really flipped there: one step below keeps, at the point it does not
        t_lo = copy.deepcopy(t2); t_lo["k_now"] = round(fl["prev_keep_k"], 9)
        t_hi = copy.deepcopy(t2); t_hi["k_now"] = round(fl["flips_at_k"], 9)
        leg("below the flip the real decide() still keeps",
            bool(PP.decide(r2, t_lo).get("keep_allowed")))
        leg("at the flip the real decide() stops keeping",
            not bool(PP.decide(r2, t_hi).get("keep_allowed")))

    # 4. a size above every path is not kept, and it says so with a readable verdict
    r3, t3 = _fixture({"universe": 0.40}, 0.90)
    p3 = PP.decide(r3, t3)
    leg("size above every reading is not kept", not bool(p3.get("keep_allowed")))
    leg("and the verdict is not KEEP", p3.get("verdict") != PP.VERDICT_KEEP_PATH,
        p3.get("verdict"))

    # 5. an unreadable cell removes the paths, so headroom must refuse to answer
    r4, t4 = _fixture({"universe": 0.40, "window": None}, 0.40)
    p4 = PP.decide(r4, t4)
    h4 = headroom(p4, 1e6)
    leg("unreadable cell -> no headroom", h4.get("strict_pp") is None, h4.get("strict_pp"))
    leg("and the sentence says why",
        "unclassified" in (p4.get("sentence") or "").lower() or
        p4.get("verdict") == PP.VERDICT_UNREADABLE, p4.get("sentence"))

    # 6. headroom never depends on the static cell
    r5, t5 = _fixture({"universe": 0.40, "window": 0.70}, 0.40)
    r5["cells"]["denominator"]["k"] = 0.95
    h5 = headroom(PP.decide(r5, t5), 1e6)
    leg("a bigger static cell does not change headroom",
        abs(h5["loose_cny"] - h2["loose_cny"]) < 1e-9, h5["loose_cny"])

    print("selftest: %d/%d OK" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "write", "check", "selftest", "show"])
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    if a.cmd == "show":
        print(json.dumps(derive(), ensure_ascii=False, indent=2))
        return 0
    face = write()
    print(json.dumps({"face": FACE, "verdict": face.get("judgement", {}).get("verdict"),
                      "strict_pp": face.get("headroom", {}).get("strict_pp"),
                      "loose_pp": face.get("headroom", {}).get("loose_pp"),
                      "flip_at_k": face.get("scan", {}).get("flips_at_k")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
