"""ETF book -- is the vol-target verdict a reading of the surface or a typed sentence?

The shared chain runs `python scripts/etf_book_vol_target_gate.py check`. Until this
file existed the leg was a phantom: the canonical leg list named it and no script
answered, so a suite could report the S6 chain complete while one of its two hundred
legs had never once executed.

What it checks, and why it is not a fragile re-typing exercise:

  * Every ARM WORD published in results/etf_vol_target_sweep.json is RE-DERIVED from
    that file's own 15 cells per book, through the sweep's own `verdict()` (imported,
    not copied). A hand-edited verdict or a stale surface therefore reads red.
  * Every axis aggregate (min / max / range_pp / values / sharpe / maxdd / spreads /
    surface extremes) is recomputed from the cells and compared to what was published.
  * The SCALE-INVARIANCE deltas are computed here and were never published: the same
    (window, target) cell on a 5-name book and a 12-name book. The point of the sweep
    is that the vol-target judgement is a property of the RULE, not of the width; if
    the two widths disagree on an arm word, this face says so instead of quoting the
    wider book's nicer number.

No panel, no engine, no network: a pure JSON read plus arithmetic. Usage:

  python scripts/etf_book_vol_target_gate.py check
  python scripts/etf_book_vol_target_gate.py --selftest      # offline fixtures
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from etf_vol_target_sweep import verdict as sweep_verdict  # single implementation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "etf_vol_target_sweep.json")

# Tolerances, frozen here so the gate cannot drift with the face it audits.
VALUE_TOL = 5e-3      # axis `values` are rounded to 2dp of a percentage
RATIO_TOL = 5e-4      # sharpe / maxdd / cagr are published unrounded (3dp at most)
WORD_TOL = 0.0        # the arm word is a string: either it is the same or it is not


def _cells(book):
    """(window, target) -> cell, rebuilt from the published cells only."""
    return {(c["window"], c["target"]): c for c in book["cells"]}


def _spreads(cells, published):
    win = sorted({w for (w, _t) in cells})
    tgt = sorted({t for (_w, t) in cells})
    pw, pt = published

    def _sh(key):
        return cells[key]["full"]["sharpe"]

    w_vals = [_sh((w, pt)) for w in win if (w, pt) in cells]
    t_vals = [_sh((pw, t)) for t in tgt if (pw, t) in cells]
    return {
        "window": round(max(w_vals) - min(w_vals), 3) if w_vals else None,
        "target": round(max(t_vals) - min(t_vals), 3) if t_vals else None,
    }


def _axis(cells, published, axis):
    """Rebuild one axis aggregate: fixed at the other published coordinate."""
    pw, pt = published
    if axis == "window":
        keys = sorted({w for (w, _t) in cells})
        sel = [(w, pt) for w in keys]
        label = lambda k: str(k[0])
    else:
        keys = sorted({t for (_w, t) in cells})
        sel = [(pw, t) for t in keys]
        label = lambda k: str(k[1])
    sel = [k for k in sel if k in cells]
    if not sel:
        return None
    cagr = {label(k): round(cells[k]["full"]["cagr"] * 100, 2) for k in sel}
    sharpe = {label(k): cells[k]["full"]["sharpe"] for k in sel}
    maxdd = {label(k): cells[k]["full"]["maxdd"] for k in sel}
    return {
        "min": min(cells[k]["full"]["cagr"] for k in sel),
        "max": max(cells[k]["full"]["cagr"] for k in sel),
        "range_pp": round((max(cells[k]["full"]["cagr"] for k in sel)
                           - min(cells[k]["full"]["cagr"] for k in sel)) * 100, 2),
        "values": cagr,
        "sharpe": sharpe,
        "maxdd": maxdd,
    }


def _surface(cells, published):
    """Best/worst/range plus the RANK of the published cell inside its own surface.

    The rank is the field that makes the verdict actionable -- 'the shipped setting
    sits 6th of 15 by CAGR' is a different claim from 'it is the best cell'.
    """
    cagrs = [c["full"]["cagr"] for c in cells.values()]
    order = sorted(cells.items(), key=lambda kv: -kv[1]["full"]["cagr"])
    rank = next((i + 1 for i, (k, _c) in enumerate(order) if k == tuple(published)), None)
    return {
        "best_cagr": max(cagrs),
        "worst_cagr": min(cagrs),
        "range_pp": round((max(cagrs) - min(cagrs)) * 100, 2),
        "published_rank": rank,
        "n_cells": len(cells),
    }


def _close(a, b, tol):
    """Numeric comparison with a tolerance; anything else must be exactly equal."""
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tol
    return a == b


def _compare(published, rebuilt, tol, path, drift):
    if isinstance(published, dict) and isinstance(rebuilt, dict):
        for k in sorted(set(published) | set(rebuilt)):
            _compare(published.get(k), rebuilt.get(k), tol, path + "." + str(k), drift)
    else:
        if not _close(published, rebuilt, tol):
            drift.append({"field": path, "published": published, "rebuilt": rebuilt})


def rebuild_book(book):
    """Everything the gate can re-derive from one book's own cells."""
    pair = tuple(book["_published_pair"])
    cells = _cells(book)
    out = {"cells": cells}
    out["sharpe_spread"] = _spreads(cells, pair)
    out["window_axis"] = _axis(cells, pair, "window")
    out["target_axis"] = _axis(cells, pair, "target")
    out["surface"] = _surface(cells, pair)
    dd = [c["full"]["maxdd"] for c in cells.values()]
    out["maxdd_worst"], out["maxdd_best"] = min(dd), max(dd)
    out["verdict"] = sweep_verdict({
        "sharpe_spread": out["sharpe_spread"],
        "target_axis": out["target_axis"],
        "window_axis": out["window_axis"],
    })
    return out


def arm_words(v, names=("target", "window")):
    """The arm word each axis carries, split for a machine comparison.

    Deliberately narrow: the verdict sentence also contains a parenthetical that
    holds '=>' and ' -8.0%..', so a generic 'key=value' split invents keys. Only
    the two axes this face governs are read, and only the word before ' ('.
    """
    out = {}
    for part in v.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        k, rest = part.split("=", 1)
        k = k.strip()
        if k in names:
            out[k] = rest.split(" (")[0].strip()
    return out


def check(path=OUT, publish_report=False):
    if not os.path.exists(path):
        print("CHECK FAIL: surface artifact missing at %s" % path)
        return 1
    d = json.load(open(path, encoding="utf-8"))
    pair = (d["published"][0], d["published"][1])
    drift, words, scale = [], {}, {}

    for name in sorted(d["books"]):
        book = dict(d["books"][name])
        book["_published_pair"] = pair
        rb = rebuild_book(book)
        for field in ("sharpe_spread", "window_axis", "target_axis", "surface"):
            _compare(book[field], rb[field], VALUE_TOL if field.endswith("axis") else RATIO_TOL,
                     "%s.%s" % (name, field), drift)
        for field in ("maxdd_worst", "maxdd_best"):
            if not _close(book[field], rb[field], RATIO_TOL):
                drift.append({"field": "%s.%s" % (name, field),
                              "published": book[field], "rebuilt": rb[field]})
        if book["verdict"] != rb["verdict"]:
            drift.append({"field": "%s.verdict" % name,
                          "published": book["verdict"], "rebuilt": rb["verdict"]})
        words[name] = arm_words(book["verdict"])

    # Scale invariance: same rule, two book widths.
    n5, n12 = d["books"].get("n5"), d["books"].get("n12")
    if n5 and n12:
        c5, c12 = _cells(n5), _cells(n12)
        shared = sorted(set(c5) & set(c12))
        deltas = []
        for k in shared:
            deltas.append({
                "window": k[0], "target": k[1],
                "cagr_pp": round((c12[k]["full"]["cagr"] - c5[k]["full"]["cagr"]) * 100, 2),
                "sharpe": round(c12[k]["full"]["sharpe"] - c5[k]["full"]["sharpe"], 3),
            })
        disagree = [ax for ax in ("target", "window")
                    if words["n5"].get(ax) != words["n12"].get(ax)]
        scale = {
            "shared_cells": len(shared),
            "deltas": deltas,
            "arm_words": words,
            "disagree_axes": disagree,
            "scale_invariant": not disagree,
        }

    state = "OK" if not drift else "FAIL"
    print("CHECK %s: %s words=%s" % (state, "VOL_TARGET_VERDICT_REPRODUCED" if not drift
                                     else "VERDICT_DRIFT", json.dumps(words, ensure_ascii=False)))
    for item in drift[:20]:
        print("  drift %s published=%r rebuilt=%r" % (item["field"], item["published"],
                                                      item["rebuilt"]))
    if scale:
        print("scale: shared_cells=%d arm_words_agree=%s disagree=%s"
              % (scale["shared_cells"], scale["scale_invariant"],
                 scale["disagree_axes"] or "none"))
        flank = [x for x in scale["deltas"] if x["sharpe"] < 0]
        print("scale deltas: n12-n5 sharpe in [%.3f, %.3f], %d of %d cells favour the wider book"
              % (min(x["sharpe"] for x in scale["deltas"]),
                 max(x["sharpe"] for x in scale["deltas"]), flank and len(flank) or 0,
                 len(scale["deltas"])))
    if publish_report:
        print(json.dumps({"drift": drift, "scale": scale}, ensure_ascii=False))
    return 0 if not drift else 1


# ------------------------------------------------------------------ selftest

def _fixture(flip=None):
    """A small surface whose rebuilt verdict is known, with an optional planted edit."""
    cells = []
    for w in (30, 60, 120):
        for t in (0.06, 0.08, 0.10):
            # Sharpe flat across targets (a risk dial) but falling with the window.
            sharpe = {30: 1.20, 60: 1.10, 120: 0.90}[w]
            cagr = sharpe * t * 1.2
            if flip and (w, t) == flip[0]:
                sharpe = flip[1]
            cells.append({"n": 5, "window": w, "target": t,
                          "full": {"cagr": cagr, "sharpe": sharpe,
                                   "maxdd": -t * 1.5, "vol": t, "years": 6.0},
                          "turnover": 1.0})
    book = {"cells": cells, "_published_pair": (60, 0.08)}
    rb = rebuild_book(book)
    return {k: v for k, v in rb.items() if k != "cells"}, rb


def selftest():
    ok = []

    def chk(name, cond, note=""):
        ok.append((name, bool(cond), note))

    pub, rb = _fixture()
    chk("fixture rebuilds every aggregate",
        set(pub) == {"sharpe_spread", "window_axis", "target_axis", "surface",
                     "maxdd_worst", "maxdd_best", "verdict"}, str(sorted(pub)))
    chk("flat-target surface reads as a risk dial", "RISK DIAL" in rb["verdict"], rb["verdict"])
    chk("window axis with falling Sharpe reads load-bearing",
        "LOAD-BEARING" in rb["verdict"], rb["verdict"])

    # A planted edit must be caught. Two design points the first drafts of this leg got
    # wrong and now pin: (a) the drift is PUBLISHED vs REBUILT, so the planted value has
    # to be the REBUILT side (comparing two rebuilds of the same cells is vacuous), and
    # (b) it must land on a cell the verdict reads -- the axes are frozen at the
    # published coordinate, so (120, 0.10) sits off both axes and moves nothing.
    _pub0, rb2 = _fixture(flip=((120, 0.08), 1.45))
    drift = []
    _compare({"verdict": pub["verdict"]}, {"verdict": rb2["verdict"]}, WORD_TOL, "x", drift)
    chk("a planted edit on the window axis is caught as drift", drift, str(drift))

    # ...and the off-axis cell genuinely does not move the words (the gate is narrow
    # by design, not by accident).
    _pub3, rb3 = _fixture(flip=((120, 0.10), 1.45))
    chk("a cell off both axes changes no arm word",
        arm_words(pub["verdict"]) == arm_words(rb3["verdict"]),
        str(arm_words(rb3["verdict"])))

    # Words are split for machine comparison, not substring-matched.
    w = arm_words("target=RISK DIAL (x); window=LOAD-BEARING (y)")
    chk("arm words split cleanly", w == {"target": "RISK DIAL", "window": "LOAD-BEARING"}, str(w))

    # Tolerances are the ones the gate uses.
    chk("value tolerance accepts a 2dp percentage rounding", _close(11.49, 11.494, VALUE_TOL))
    chk("value tolerance rejects a real move", not _close(11.49, 12.03, VALUE_TOL))
    chk("ratio tolerance is tighter than any published change",
        not _close(1.132, 1.168, RATIO_TOL))

    n_pass = sum(1 for _, c, _ in ok if c)
    for name, c, note in ok:
        print("[%s] %s | %s" % ("PASS" if c else "FAIL", name, note))
    print("selftest %d/%d" % (n_pass, len(ok)))
    return 0 if n_pass == len(ok) else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "check"
    if arg == "--selftest":
        sys.exit(selftest())
    if arg == "check":
        sys.exit(check())
    print(__doc__)
    sys.exit(2)