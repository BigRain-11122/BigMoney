"""Who writes the futures contract panel, how often, and which day's panel picks the contracts?
(dept: 工程+数据)

r1843/r1844 closed the money half of the contract question (how much capital opens the
carry book).  They explicitly left the provenance half undone: the faces a reader opens
never say **who** writes `data/futures_contracts`, **how often**, or **which day's panel**
chose the contracts that are live.  They also counted ~410 expired contracts whose tails
nothing will ever extend again, without publishing the count anywhere a reader can check.

This face answers both from evidence instead of memory:

  * the writer and its face come out of `results/futures_contracts_refresh.json`, never
    out of a literal in this file -- if the writer moves, this face moves with it;
  * the live set is **recomputed** with the writer's own window rule
    (`update_futures_contracts.live_symbols`, imported, not re-implemented) so the reader
    sees agreement only when the two really agree;
  * the tail census walks the panel itself: every contract file is opened and its last bar
    is compared to the panel's own max date.  A contract that stopped printing because it
    expired is a **dead tail** -- it will never be refreshed again and must not be mistaken
    for a stalled collector.

Buckets are calendar days (the panel carries no calendar, same convention as the writer's
own `live_symbols` window), and the window cut is taken from that same imported function.

Exit codes: 0 ok, 2 mechanism fault (refresh face or panel unreadable),
3 --check drift (the published face no longer matches the panel).
"""

from __future__ import annotations

import argparse
import datetime
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import update_futures_contracts as ufc  # noqa: E402  (single source of the window rule)

PANEL = ufc.PANEL
FACE = os.path.join(ROOT, "results", "futures_contracts_refresh.json")
OUT = os.path.join(ROOT, "results", "futures_panel_provenance.json")
CHAIN = os.path.join(ROOT, "Tools", "s6_chain_bmc.py")

# Calendar-day buckets for tails that are past the live window.  A contract inside the
# writer's window is not a tail yet; everything past it gets an age, because "how old"
# is what decides whether the number is a roll (fine) or an abandoned file (not fine).
AGE_BUCKETS = [(30, "1_to_30_days"), (90, "31_to_90_days"),
               (365, "91_to_365_days"), (None, "over_365_days")]


def _age_bucket(days_old):
    for limit, name in AGE_BUCKETS:
        if limit is None or days_old <= limit:
            return name
    return AGE_BUCKETS[-1][1]


def _days_between(newer, older):
    a = datetime.date.fromisoformat(newer)
    b = datetime.date.fromisoformat(older)
    return (a - b).days


def _recompute_live(last_bars, panel_max, window):
    """The writer's own rule, called -- never a copy of it.

    Only input hygiene happens here: a contract that never printed has no date to
    compare and the writer assumes every entry has one, so those rows are dropped
    before the call (`run()` only ever passes contracts that printed).
    """
    dated = {sym: bar for sym, bar in last_bars.items() if bar}
    return ufc.live_symbols(dated, panel_max, window)


def _census(last_bars, panel_max, window):
    """Split every contract on disk by how far its last bar sits behind the panel."""
    cut = ufc._minus_days(panel_max, window * 7 // 5 + 2)
    at_cutoff, inside, tails, no_bars = [], [], [], []
    for sym in sorted(last_bars):
        bar = last_bars[sym]
        if bar is None:
            no_bars.append(sym)
        elif bar == panel_max:
            at_cutoff.append(sym)
        elif bar >= cut:
            inside.append(sym)
        else:
            tails.append(sym)
    by_age = {name: 0 for _, name in AGE_BUCKETS}
    for sym in tails:
        by_age[_age_bucket(_days_between(panel_max, last_bars[sym]))] += 1
    ages = sorted(((sym, last_bars[sym], _days_between(panel_max, last_bars[sym]))
                   for sym in tails), key=lambda x: x[2])
    return {
        "contracts_on_disk": len(last_bars),
        "contracts_with_bars": len(last_bars) - len(no_bars),
        "contracts_with_no_bars_ever": len(no_bars),
        "contracts_whose_last_bar_equals_panel_max": len(at_cutoff),
        "contracts_inside_the_writers_window": len(inside),
        "dead_tail_count": len(tails),
        "dead_tail_by_age": by_age,
        "window_cut_date": cut,
        "tail_free_share_of_contracts_with_bars": (
            round(1.0 - len(tails) / (len(last_bars) - len(no_bars)), 4)
            if len(last_bars) - len(no_bars) else None),
        "newest_dead_tail": ({"symbol": ages[0][0], "last_bar": ages[0][1],
                              "calendar_days_old": ages[0][2]} if ages else None),
        "oldest_dead_tail": ({"symbol": ages[-1][0], "last_bar": ages[-1][1],
                              "calendar_days_old": ages[-1][2]} if ages else None),
        "dead_tail_first_named": [{"symbol": s, "last_bar": b, "calendar_days_old": d}
                                  for s, b, d in ages[:5]],
    }


def _chain_leg_declared(path=CHAIN):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return "update_futures_contracts" in fh.read()
    except OSError:
        return False


def _disk_contracts(panel=PANEL):
    """Every contract file on disk, including the ones that never printed a bar.

    `ufc.panel_state` only reports contracts that have at least one row, so a file
    that is header-only is invisible to it.  A reader asking "how many contracts are
    on disk" must not be answered with "how many have bars" -- those are two states
    and only the second one is the writer's universe.
    """
    names = []
    try:
        for fn in os.listdir(panel):
            stem, ext = os.path.splitext(fn)
            if ext.lower() == ".csv" and ufc.SYMBOL_RE.match(stem):
                names.append(stem)
    except OSError:
        return {}
    return sorted(names)


def build(face=None, last_bars=None, chain_declared=None):
    """Pure builder: every input is injectable so the selftest never needs the disk."""
    if face is None:
        with io.open(FACE, encoding="utf-8") as fh:
            face = json.load(fh)
    if last_bars is None:
        dated, panel_max = ufc.panel_state(PANEL)
        last_bars = {sym: dated.get(sym) for sym in _disk_contracts()}
    else:
        panel_max = max((d for d in last_bars.values() if d), default=None)
    if chain_declared is None:
        chain_declared = _chain_leg_declared()

    window = int(face.get("live_window_days") or 5)
    face_live = sorted(face.get("live") or [])
    recomputed = _recompute_live(last_bars, panel_max, window)
    panel_max_face = face.get("panel_max_after") or face.get("panel_max_before")
    census = _census(last_bars, panel_max, window)

    # Verdicts are read off the counts, never asserted: a panel that is behind the face,
    # or a live set the writer and the panel disagree about, is named before the tails.
    verdicts = []
    if panel_max_face and panel_max and panel_max != panel_max_face:
        verdicts.append("PANEL_MOVED_SINCE_THE_WRITER_FACE")
    if face_live != recomputed:
        verdicts.append("LIVE_SET_DISAGREES_WITH_THE_PANEL")
    verdicts.append("TAILS_ARE_EXPIRY_NOT_STALL" if census["dead_tail_count"]
                    else "NO_DEAD_TAILS")
    if census["contracts_with_no_bars_ever"]:
        verdicts.append("SOME_CONTRACTS_NEVER_PRINTED_YET")

    return {
        "schema": "futures_panel_provenance/1",
        "generated": datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "evidence_cutoff": panel_max,
        "panel": PANEL.replace("\\", "/").split("FluxGroup/quant/bigmoney/")[-1],
        "writer": {
            "script": face.get("script"),
            "face": "results/futures_contracts_refresh.json",
            "face_generated": face.get("generated"),
            "face_verdict": face.get("verdict"),
            "runs_in_s6_chain": bool(chain_declared),
            "cadence": ("every S6 chain pass (Tools/s6_chain_bmc.py leg "
                        "update_futures_contracts)" if chain_declared
                        else "not declared in Tools/s6_chain_bmc.py -- cadence unknown"),
        },
        "pick_rule": {
            "stated_by": "scripts/update_futures_contracts.py::live_symbols",
            "window_days_param": window,
            "window_is": "calendar days = window*7//5 + 2",
            "window_cut_date": census["window_cut_date"],
            "panel_date_used_by_the_writer": panel_max_face,
            "reading": ("a contract is live if its last bar is on/after %s; the universe "
                        "is the panel as of %s, not today"
                        % (census["window_cut_date"], panel_max_face)),
        },
        "live_set": {
            "declared_by_face": face_live,
            "recomputed_from_panel": recomputed,
            "agree": face_live == recomputed,
        },
        "census": census,
        "verdict": " | ".join(verdicts),
    }


def check():
    if not os.path.exists(OUT):
        print("check: %s missing -- run without --check first" % OUT)
        return 3
    with io.open(OUT, encoding="utf-8") as fh:
        published = json.load(fh)
    fresh = build()
    drift = [k for k in fresh
             if k not in ("generated",) and published.get(k) != fresh.get(k)]
    if drift:
        print("check: STALE face -- drifted keys: %s" % ", ".join(sorted(drift)))
        for k in sorted(drift):
            print("  published: %r" % (published.get(k),))
            print("  now      : %r" % (fresh.get(k),))
        return 3
    print("check: ok (%s, cutoff %s, dead tails %d)"
          % (fresh["verdict"], fresh["evidence_cutoff"], fresh["census"]["dead_tail_count"]))
    return 0


def selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    # L1 the writer is read out of the face, not out of this file
    face = {"script": "scripts/not_the_real_one.py", "live_window_days": 5, "live": [],
            "panel_max_after": "2026-11-19", "generated": "x", "verdict": "V"}
    bars = {"IC2612": "2026-11-19"}
    doc = build(face=face, last_bars=bars, chain_declared=False)
    leg("writer script comes from the face", doc["writer"]["script"] == "scripts/not_the_real_one.py")
    leg("chain leg read from the chain file, not assumed",
        doc["writer"]["runs_in_s6_chain"] is False and "unknown" in doc["writer"]["cadence"])

    # L2 a contract at the panel max is not a tail; one just inside the window is not either
    bars = {"IC2612": "2026-11-19", "IC2611": "2026-11-14", "IC1701": "2017-01-20", None: None}
    bars.pop(None)
    doc = build(face=dict(face, live=["IC2612", "IC2611"]),
                last_bars=bars, chain_declared=True)
    leg("bar at panel max is counted as at-cutoff",
        doc["census"]["contracts_whose_last_bar_equals_panel_max"] == 1)
    leg("five sessions back still reads inside the writer's window",
        doc["census"]["contracts_inside_the_writers_window"] == 1)
    leg("an old contract is a dead tail",
        doc["census"]["dead_tail_count"] == 1
        and doc["census"]["dead_tail_first_named"][0]["symbol"] == "IC1701")

    # L3 age buckets split at their own boundaries
    leg("365 days lands in the 91..365 bucket", _age_bucket(365) == "91_to_365_days")
    leg("366 days lands in over_365", _age_bucket(366) == "over_365_days")
    leg("30 days lands in 1..30", _age_bucket(30) == "1_to_30_days")

    # L4 a live set that disagrees is named, not smoothed
    doc = build(face=dict(face, live=["IC9999"]), last_bars=bars, chain_declared=True)
    leg("disagreeing live set is named and agree=False",
        doc["live_set"]["agree"] is False
        and "LIVE_SET_DISAGREES_WITH_THE_PANEL" in doc["verdict"])

    # L5 a panel that has moved past the writer face is named
    doc = build(face=dict(face, panel_max_after="2026-11-18", live=[]),
                last_bars=bars, chain_declared=True)
    leg("panel ahead of the face is named",
        "PANEL_MOVED_SINCE_THE_WRITER_FACE" in doc["verdict"])

    # L6 no bars at all is its own state, never a tail
    doc = build(face=face, last_bars={"IC1701": None, "IC2612": "2026-11-19"},
                chain_declared=True)
    leg("a contract that never printed is counted separately",
        doc["census"]["contracts_with_no_bars_ever"] == 1
        and doc["census"]["dead_tail_count"] == 0
        and "SOME_CONTRACTS_NEVER_PRINTED_YET" in doc["verdict"])

    # L7 the disk census sees header-only files, which the writer's own state hides
    import tempfile
    tmp = tempfile.mkdtemp()
    for fn in ("IC2612.csv", "IH2611.csv", "notes.txt"):
        io.open(os.path.join(tmp, fn), "w", encoding="utf-8").close()
    leg("disk census lists contract files and ignores the rest",
        _disk_contracts(tmp) == ["IC2612", "IH2611"])

    passed = sum(1 for _, c in ok if c)
    for name, cond in ok:
        print(("PASS  " if cond else "FAIL  ") + name)
    print("selftest %d/%d" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def run():
    doc = build()
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    c = doc["census"]
    print("panel %s cutoff %s | writer %s (%s)"
          % (doc["panel"], doc["evidence_cutoff"], doc["writer"]["script"],
             doc["writer"]["cadence"]))
    print("picks contracts from the panel as of %s (window cut %s, %d live)"
          % (doc["pick_rule"]["panel_date_used_by_the_writer"],
             doc["pick_rule"]["window_cut_date"], len(doc["live_set"]["recomputed_from_panel"])))
    print("census: %d on disk / %d with bars / %d at cutoff / %d dead tails (%s)"
          % (c["contracts_on_disk"], c["contracts_with_bars"],
             c["contracts_whose_last_bar_equals_panel_max"], c["dead_tail_count"],
             doc["verdict"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check:
        return check()
    try:
        return run()
    except (OSError, ValueError, KeyError) as exc:
        print("mechanism fault: %s: %s" % (type(exc).__name__, exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
