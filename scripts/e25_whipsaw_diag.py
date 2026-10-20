"""E25 whipsaw diagnostic for the per-member trend filter (descriptive only).

r1095 opened the E25 family: on the five-member ladder, holding a member only
while its close sits above its own N-day moving average is a WASH at N=100
(-0.1bp/yr vs always-on equal weight) and a LOSS at N=50/150/200 (-139..-219
bp/yr) while paying 22-38bp/yr of turnover.  This face asks WHY, without
inventing a new strategy:

  * how often does each member's filter CROSS (fake/down and up), per year?
  * what does the ladder earn in the 20 bars AFTER each entry crossing and
    AFTER each exit crossing?  A filter that enters late shows weak forward
    returns after entries and strong ones after exits (it is buying tops and
    selling bottoms).
  * how much of the time is each member OUT of its own trend?

Causality: the crossing at day i is decided from closes <= i; the forward
window is i+1..i+20.  No gate, no prereg, no trial count, no verdict.

Modes
  run       : results/e25_whipsaw/WHIPSAW-<date>.json
  selftest  : hermetic checks (exit 0/1)
"""

from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from e24_ladder_weighting import LADDER, load_panel  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "e25_whipsaw")
WINDOWS = (50, 100, 200)
FWD = 20


def ma(values, i, win):
    if i - win + 1 < 0:
        return None
    seg = values[i - win + 1:i + 1]
    if any(v is None for v in seg):
        return None
    return statistics.fmean(seg)


def crossings(prices, win):
    """(entry_days, exit_days) where the close crosses its own win-day MA."""
    entries, exits, prev = [], [], None
    for i in range(len(prices)):
        m = ma(prices, i, win)
        if m is None or prices[i] is None:
            prev = None
            continue
        state = prices[i] > m
        if prev is not None and state != prev:
            (entries if state else exits).append(i)
        prev = state
    return entries, exits


def fwd_return(prices, i, h=FWD):
    if i + h >= len(prices):
        return None
    a, b = prices[i + h], prices[i]
    if a is None or b is None or b <= 0:
        return None
    return a / b - 1.0


def summarize(member_faces):
    per_window = {}
    for win in WINDOWS:
        ent, ext, expo = [], [], []
        for f in member_faces.values():
            d = f["windows"].get(str(win))
            if not d:
                continue
            ent.extend(d["entry_fwd_bp"])
            ext.extend(d["exit_fwd_bp"])
            expo.append(d["exposure_share"])
        per_window[str(win)] = {
            "entries": sum(f["windows"].get(str(win), {}).get("entries", 0)
                           for f in member_faces.values()),
            "exits": sum(f["windows"].get(str(win), {}).get("exits", 0)
                         for f in member_faces.values()),
            "mean_entry_fwd_bp": round(statistics.fmean(ent), 1) if ent else None,
            "mean_exit_fwd_bp": round(statistics.fmean(ext), 1) if ext else None,
            "entry_minus_exit_bp": (round(statistics.fmean(ent) - statistics.fmean(ext), 1)
                                    if ent and ext else None),
            "mean_member_exposure": round(statistics.fmean(expo), 3) if expo else None,
        }
    return per_window


def build_face(fwd=FWD):
    cal, closes, _amounts = load_panel()
    members = [s for s in LADDER if s in closes]
    member_faces = {}
    for s in members:
        prices = [closes[s].get(d) for d in cal]
        n_days = sum(1 for v in prices if v is not None)
        per_win = {}
        for win in WINDOWS:
            ent, ext = crossings(prices, win)
            ent_f = [fwd_return(prices, i, fwd) for i in ent]
            ext_f = [fwd_return(prices, i, fwd) for i in ext]
            ent_f = [v * 1e4 for v in ent_f if v is not None]
            ext_f = [v * 1e4 for v in ext_f if v is not None]
            live_days = None
            # share of usable history where the member is above its own MA
            above = tot = 0
            for i in range(len(prices)):
                m = ma(prices, i, win)
                if m is None or prices[i] is None:
                    continue
                tot += 1
                if prices[i] > m:
                    above += 1
            live_days = tot
            per_win[str(win)] = {
                "entries": len(ent),
                "exits": len(ext),
                "entry_fwd_bp": [round(v, 1) for v in ent_f],
                "exit_fwd_bp": [round(v, 1) for v in ext_f],
                "exposure_share": round(above / tot, 4) if tot else None,
                "usable_days": live_days,
            }
        member_faces[s] = {"bars": n_days, "windows": per_win}

    years = len(cal) / 252.0
    return {
        "face": "E25 per-member trend-filter whipsaw diagnostic (five-member ladder)",
        "evidence_cutoff": cal[-1] if cal else None,
        "start": cal[0] if cal else None,
        "years": round(years, 2),
        "forward_bars": fwd,
        "members": members,
        "per_window": summarize(member_faces),
        "per_member": member_faces,
        "labels": {
            "descriptive": True,
            "prereg": None,
            "trial_count": 0,
            "reading": ("entries and exits are read at the crossing close (causal); the "
                        "forward window is the next %d bars" % fwd),
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def selftest():
    fails = []
    n = {"n": 0}

    def chk(name, cond):
        n["n"] += 1
        print(("  PASS " if cond else "  FAIL ") + name)
        if not cond:
            fails.append(name)

    # 40 flat bars then a strictly rising run: exactly one entry crossing
    prices = [10.0] * 40 + [10.0 * (1.002 ** k) for k in range(1, 41)]
    ent, ext = crossings(prices, 20)
    chk("one entry crossing on a breakout", len(ent) == 1 and not ext)
    chk("crossing day is causal (first bar above its MA)", ent[0] == 40)
    chk("ma needs a full window", ma([10.0] * 10, 5, 20) is None)
    chk("fwd_return needs h bars ahead", fwd_return([10.0] * 5, 0, 20) is None)
    chk("fwd_return compounds", abs(fwd_return([10.0, 11.0], 0, 1) - 0.1) < 1e-12)
    # a rise followed by a strictly falling run -> one exit crossing
    up = [10.0 * (1.002 ** k) for k in range(40)]
    down = [up[-1] * (0.995 ** k) for k in range(1, 41)]
    ent, ext = crossings(up + down, 20)
    chk("one exit crossing on a breakdown", len(ext) == 1 and not ent)
    # summarize handles a single member face
    one = {"x": {"windows": {"50": {"entries": 2, "exits": 2,
                                    "entry_fwd_bp": [10.0, 20.0],
                                    "exit_fwd_bp": [-5.0, -15.0],
                                    "exposure_share": 0.6}}}}
    s = summarize(one)
    chk("summary averages entry minus exit", abs(s["50"]["entry_minus_exit_bp"] - 25.0) < 1e-9)
    chk("summary counts crossings", s["50"]["entries"] == 2)
    print("selftest: %d/%d PASS" % (n["n"] - len(fails), n["n"]))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    runp = sub.add_parser("run", help="compute the whipsaw diagnostic")
    runp.add_argument("--fwd", type=int, default=FWD,
                      help="forward window in bars (default %d)" % FWD)
    sub.add_parser("selftest", help="hermetic self checks")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"
    if cmd == "selftest":
        return selftest()

    face = build_face(args.fwd)
    os.makedirs(OUTDIR, exist_ok=True)
    stamp = (face["evidence_cutoff"] or "").replace("-", "")
    # the forward window is a face parameter: keep one file per (fwd, day)
    path = os.path.join(OUTDIR, "WHIPSAW-f%d-%s.json" % (face["forward_bars"], stamp))
    for p in (path, os.path.join(OUTDIR, "latest.json")):
        with io.open(p, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps({"per_window": face["per_window"], "years": face["years"]},
                     ensure_ascii=False, indent=1))
    print("face: %s" % os.path.relpath(path, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())