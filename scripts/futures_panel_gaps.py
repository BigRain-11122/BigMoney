"""What the 83 never-printed contract files are, and whether the source still has them.

r1887 (bm-c).  r1867 put the panel census on the CEO page: 418 contract files,
335 with bars, **83 that never printed a single row**.  The page says the 83
exist but not what they are, and the open question was whether they are our own
collection gap (worth a backfill) or names the source never served (write off).

This face answers that in two steps and keeps them apart:

  1. classification from the disk alone -- a header-only file is one of
     * not listed yet  (expiry year still ahead of the panel's own last bar)
     * expired before the panel window (its whole life predates the oldest bar
       any contract on disk carries)
     * expired inside the window (the real anomaly: the life overlaps bars we
       already hold, so a gap there is ours)
  2. an upstream probe of a deterministic sample of the second group: ask the
     same sina endpoint update_futures_contracts.py uses, for the contract
     itself.  Rows back = the history exists and our panel is the gap; `null`
     back = the source does not serve that contract and no backfill can work.

Rules:
  * the classification runs offline and is what `--check` re-derives; the probe
    is opt-in (`--probe`) because it needs the network and 2.5s of politeness
    per name;
  * a missing probe is printed as "not asked", never as zero rows (r98);
  * the verdict is chosen by the counts, not written by hand.
"""
from __future__ import annotations

import argparse
import glob
import io
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "futures_contracts")
OUT = os.path.join(ROOT, "results", "futures_panel_gaps.json")
SYMBOL_RE = re.compile(r"^(IF|IH|IC|IM)(\d{2})(\d{2})$")
RAW_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
           "var%20_F={sym}/InnerFuturesNewService.getDailyKLine?symbol={sym}")
SLEEP_S = 2.5


def _panel():
    """{symbol: (rows, header, last_date)} for every file on disk."""
    out = {}
    for path in sorted(glob.glob(os.path.join(PANEL, "*.csv"))):
        sym = os.path.splitext(os.path.basename(path))[0]
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
        rows = max(0, len(lines) - 1)
        last = lines[1].split(",")[0] if rows else None
        out[sym] = {"rows": rows, "header": lines[0] if lines else "", "last": last}
    return out


def _expiry_yyyymm(sym: str):
    m = SYMBOL_RE.match(sym)
    if not m:
        return None
    return 2000 + int(m.group(2)), int(m.group(3))


def classify(panel):
    """Split the header-only files by *why* they have no rows.

    `panel_max` is the newest bar any contract carries -- the panel's own clock.
    A contract expiring after it cannot have printed, and saying so keeps a
    2027 contract out of the same bucket as a 2017 one.
    """
    printed = [v["last"] for v in panel.values() if v["last"]]
    panel_max = max(printed) if printed else None
    panel_min = min(printed) if printed else None
    if panel_max is None:
        return {"panel_max": None, "panel_min": None, "not_listed_yet": [],
                "expired_before_window": [], "expired_inside_window": [],
                "unreadable_names": []}
    head_only = [s for s, v in panel.items() if v["rows"] == 0]
    not_listed, before, inside, junk = [], [], [], []
    for sym in head_only:
        got = _expiry_yyyymm(sym)
        if got is None:
            junk.append(sym)
            continue
        year, month = got
        expiry = "%04d-%02d" % (year, month)
        if expiry > panel_max[:7]:
            not_listed.append({"symbol": sym, "expiry_month": expiry})
        elif expiry < panel_min[:7]:
            before.append({"symbol": sym, "expiry_month": expiry})
        else:
            inside.append({"symbol": sym, "expiry_month": expiry})
    return {
        "panel_max": panel_max,
        "panel_min": panel_min,
        "not_listed_yet": not_listed,
        "expired_before_window": before,
        "expired_inside_window": inside,
        "unreadable_names": junk,
    }


def sample_of(rows, n=4):
    """Deterministic spread: oldest, newest, and evenly spaced in between."""
    rows = sorted(rows, key=lambda r: r["symbol"])
    if len(rows) <= n:
        return [r["symbol"] for r in rows]
    idx = sorted({0, len(rows) - 1} |
                 {round(i * (len(rows) - 1) / (n - 1)) for i in range(n)})
    return [rows[i]["symbol"] for i in idx]


def probe(symbols, sleep=SLEEP_S):
    """Ask the ingest endpoint for each contract.  Rows back == it still exists."""
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    out = []
    for i, sym in enumerate(symbols):
        if i:
            time.sleep(sleep)
        rec = {"symbol": sym}
        try:
            raw = opener.open(RAW_URL.replace("{sym}", sym), timeout=25
                              ).read().decode("utf-8", "replace")
            m = re.search(r"\((\[.*\]|null)\)", raw, re.S)
            if m is None:
                rec.update(ok=False, error="no jsonp payload")
            elif m.group(1) == "null":
                rec.update(ok=True, rows=0)
            else:
                rows = json.loads(m.group(1))
                rec.update(ok=True, rows=len(rows),
                           first=rows[0].get("d"), last=rows[-1].get("d"))
        except Exception as exc:                       # honest, not fatal
            rec.update(ok=False, error="%s: %s" % (type(exc).__name__, exc))
        out.append(rec)
    return out


def verdict_of(cls, probes, control=None):
    """A null answer only means something if the same probe can say yes.

    `control` is a set of contracts we already hold bars for.  If the endpoint
    returns rows for those and null for the gaps, the nulls are the source's
    answer; if the controls also come back empty, the probe is telling us
    nothing and must not be read as "no history exists" (r1865).
    """
    control = control or []
    if not cls.get("panel_max"):
        return "NO_PANEL"
    if not probes:
        return ("GAP_INSIDE_OUR_WINDOW_UNPROBED"
                if cls["expired_inside_window"] else "NOT_ASKED")
    asked = [p for p in probes if p.get("ok")]
    if not asked:
        return "SOURCE_UNREACHABLE"
    ctl = [c for c in control if c.get("ok")]
    if not ctl or not all(c.get("rows") for c in ctl):
        return "PROBE_UNTRUSTWORTHY"
    with_rows = [p for p in asked if p.get("rows")]
    if not with_rows:
        return ("SOURCE_SERVES_NONE_CONTROL_HELD"
                if cls["expired_inside_window"]
                else "SOURCE_RETAINS_NONE_OF_THESE")
    if len(with_rows) == len(asked):
        return "BACKFILLABLE_FROM_UPSTREAM"
    return "SOURCE_KEEPS_SOME"


def controls_of(panel, cls):
    """Two dead contracts we *do* hold bars for -- the probe's positive control.

    Taken from disk, not hardcoded: the busiest and the thinnest dead name.
    """
    dead = [(s, v["rows"]) for s, v in panel.items()
            if v["rows"] and v["last"] and v["last"] < (cls.get("panel_max") or "")]
    if not dead:
        return []
    dead.sort(key=lambda kv: (kv[1], kv[0]))
    return [dead[0][0], dead[-1][0]]


def build(do_probe=False, n=4):
    panel = _panel()
    cls = classify(panel)
    probes, control, carried = [], [], None
    if do_probe:
        # the names whose life overlaps bars we already hold are the ones a
        # backfill could actually serve, so they are asked first
        asked = sample_of(cls["expired_inside_window"] or [], n)
        asked += [s for s in sample_of(cls["expired_before_window"], n)
                  if s not in asked]
        if asked:
            probes = probe(asked)
            control = probe(controls_of(panel, cls), sleep=SLEEP_S)
    elif os.path.exists(OUT):
        # the chain runs this offline every pass; a probe costs ~30s of network
        # and its answer cannot change while the header-only set is unchanged,
        # so it is carried forward rather than dropped (or re-bought)
        try:
            old = json.load(io.open(OUT, encoding="utf-8"))
        except Exception:
            old = {}
        same = (len(old.get("expired_before_window") or []) == len(cls["expired_before_window"])
                and len(old.get("expired_inside_window") or []) == len(cls["expired_inside_window"])
                and [r["symbol"] for r in old.get("expired_before_window") or []]
                == [r["symbol"] for r in cls["expired_before_window"]])
        if same and (old.get("probe") or {}).get("records"):
            probes = old["probe"]["records"]
            control = old["probe"].get("control_records") or []
            carried = old.get("generated")
    last = cls.get("panel_max")
    return {
        "schema": "futures_panel_gaps/v1",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": last,
        "panel": "data/futures_contracts",
        "census": {
            "contracts_on_disk": len(panel),
            "contracts_with_bars": sum(1 for v in panel.values() if v["rows"]),
            "contracts_header_only": sum(1 for v in panel.values() if not v["rows"]),
            "not_listed_yet": len(cls["not_listed_yet"]),
            "expired_before_window": len(cls["expired_before_window"]),
            "expired_inside_window": len(cls["expired_inside_window"]),
            "unreadable_names": len(cls["unreadable_names"]),
            "panel_first_bar": cls.get("panel_min"),
            "panel_last_bar": cls.get("panel_max"),
        },
        "not_listed_yet": cls["not_listed_yet"],
        "expired_before_window": cls["expired_before_window"],
        "expired_inside_window": cls["expired_inside_window"],
        "probe": {"asked": [p["symbol"] for p in probes], "records": probes,
                  "control": [c["symbol"] for c in control], "control_records": control,
                  "carried_from": carried, "endpoint": RAW_URL},
        "verdict": verdict_of(cls, probes, control),
    }


def selftest():
    ok = []

    def leg(name, cond):
        ok.append((name, bool(cond)))

    panel = {"IC2612": {"rows": 5, "header": "d,o", "last": "2026-11-20"},
             "IC1701": {"rows": 0, "header": "d,o", "last": None},
             "IF2701": {"rows": 0, "header": "d,o", "last": None},
             "IH1903": {"rows": 4, "header": "d,o", "last": "2019-03-15"},
             "IM2207": {"rows": 0, "header": "d,o", "last": None},
             "junk": {"rows": 0, "header": "d,o", "last": None}}
    cls = classify(panel)
    leg("L1 panel max is the newest bar any contract carries",
        cls["panel_max"] == "2026-11-20")
    leg("L2 a 2027 contract is not listed yet, not a gap",
        [r["symbol"] for r in cls["not_listed_yet"]] == ["IF2701"])
    leg("L3 a 2017 contract expired before the window",
        [r["symbol"] for r in cls["expired_before_window"]] == ["IC1701"])
    leg("L4 a 2022-07 contract expiring inside the window is the anomaly",
        [r["symbol"] for r in cls["expired_inside_window"]] == ["IM2207"])
    leg("L5 a name that is not a contract goes to its own bucket",
        cls["unreadable_names"] == ["junk"])
    leg("L6 every header-only file lands in exactly one bucket",
        sum(len(cls[k]) for k in ("not_listed_yet", "expired_before_window",
                                  "expired_inside_window", "unreadable_names")) == 4)
    leg("L7 sample is deterministic and spreads over the set",
        sample_of(cls["expired_before_window"]) == ["IC1701"])
    rows = [{"symbol": "IC1701"}, {"symbol": "IC1702"}, {"symbol": "IC1703"},
            {"symbol": "IC1704"}, {"symbol": "IC1705"}]
    leg("L8 sample with more names keeps the ends and stays sorted",
        sample_of(rows, 3)[0] == "IC1701" and sample_of(rows, 3)[-1] == "IC1705")
    # the probe legs need a panel with no inside-window anomaly, otherwise the
    # anomaly would (correctly) take its own verdict -- see L14/L15
    cls2 = dict(cls, expired_inside_window=[])
    ctl = [{"ok": True, "rows": 163}]
    leg("L9 a not-asked probe is not a zero",
        verdict_of(cls2, []) == "NOT_ASKED")
    leg("L10 all-null probes says the source keeps none of these",
        verdict_of(cls2, [{"ok": True, "rows": 0}], ctl)
        == "SOURCE_RETAINS_NONE_OF_THESE")
    leg("L11 rows back says the panel is the gap",
        verdict_of(cls2, [{"ok": True, "rows": 120}], ctl)
        == "BACKFILLABLE_FROM_UPSTREAM")
    leg("L12 mixed probes says so instead of picking a side",
        verdict_of(cls2, [{"ok": True, "rows": 0}, {"ok": True, "rows": 9}], ctl)
        == "SOURCE_KEEPS_SOME")
    leg("L13 an unreachable source is not a verdict about history",
        verdict_of(cls2, [{"ok": False, "error": "timeout"}], ctl)
        == "SOURCE_UNREACHABLE")
    leg("L14 nulls without a positive control prove nothing",
        verdict_of(cls2, [{"ok": True, "rows": 0}], [{"ok": True, "rows": 0}])
        == "PROBE_UNTRUSTWORTHY")
    leg("L15 a gap inside the window plus nulls says the source serves none",
        verdict_of({"panel_max": "2026-11-20", "expired_inside_window": [{"x": 1}]},
                   [{"ok": True, "rows": 0}], ctl) == "SOURCE_SERVES_NONE_CONTROL_HELD")
    leg("L16 the same gap with no probe stays an open gap",
        verdict_of({"panel_max": "2026-11-20", "expired_inside_window": [{"x": 1}]}, [])
        == "GAP_INSIDE_OUR_WINDOW_UNPROBED")
    leg("L17 no panel means no answer",
        verdict_of({"panel_max": None}, []) == "NO_PANEL")
    panel2 = {"IC2612": {"rows": 5, "header": "", "last": "2026-11-20"},
              "IC1906": {"rows": 163, "header": "", "last": "2019-03-15"},
              "IH1903": {"rows": 1, "header": "", "last": "2019-03-15"}}
    leg("L18 controls are dead names we hold bars for, thickest and thinnest",
        controls_of(panel2, {"panel_max": "2026-11-20"}) == ["IH1903", "IC1906"])
    bad = [n for n, c in ok if not c]
    for n, c in ok:
        print(("PASS " if c else "FAIL ") + n)
    print("futures_panel_gaps selftest %d/%d" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true",
                    help="ask the source about a sample of the pre-window names")
    ap.add_argument("--sample", type=int, default=4)
    ap.add_argument("--check", action="store_true",
                    help="re-derive the offline classification and compare")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write", action="store_true", help="write the face")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    face = build(do_probe=args.probe, n=args.sample)
    if args.check:
        if not os.path.exists(OUT):
            print("STALE face missing: %s" % OUT)
            return 3
        old = json.load(io.open(OUT, encoding="utf-8"))
        a, b = face["census"], old.get("census") or {}
        if a == b:
            print("CHECK_OK census_idle verdict=%s" % old.get("verdict"))
            return 0
        diff = [k for k in a if a[k] != b.get(k)]
        print("STALE census moved: %s" % ", ".join(diff))
        return 3
    if args.write:
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
    c = face["census"]
    print("verdict=%s" % face["verdict"])
    print("header_only=%d (not_listed_yet=%d expired_before_window=%d "
          "expired_inside_window=%d unreadable=%d)"
          % (c["contracts_header_only"], c["not_listed_yet"],
             c["expired_before_window"], c["expired_inside_window"],
             c["unreadable_names"]))
    for p in face["probe"]["records"]:
        print("  probe %s ok=%s rows=%s first=%s last=%s %s"
              % (p["symbol"], p.get("ok"), p.get("rows"), p.get("first"),
                 p.get("last"), p.get("error") or ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
