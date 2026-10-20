"""Data-face freshness / coverage reporter (E30, dept:data, lane-agnostic read).

Why this exists (r1106 measurement, digest
research/digests/DIGEST-20261021-e35-broad-book-screens.md Q-D/Q-E):
the r1106 read of the broad-book screens could not tell "strategy decay"
from "data decay" -- 1,671 of 1,725 data/daily panels stopped on exactly
2026-09-22 (a one-off bulk import), so any trailing liquidity / turnover
filter silently lost coverage while every downstream readout looked fine.
E29 (scripts/update_etf_universe.py) added the missing refresh leg for the
ETF population; nothing measured whether it actually closed the gap, and
the same defect class can reappear on any family. This module is the
standing measure: a last-bar-date histogram over the whole panel face plus
the coverage counts each consumer depends on.

Design:
  * Read-only, zero network, zero engine, zero judgement: it counts dates
    already on disk. No writes outside results/ + docs/panel_coverage/.
  * Cheap tail read (512 B) per file -- the same trick as E29's
    last_bar_date, kept local so this stays importable without requests /
    MiniRacer (the pull legs need them; a census leg must not).
  * Reference date is the face maximum, not a calendar guess: coverage is
    reported as "files at face_max" (fresh) and "files within 3 calendar
    days of face_max" (a lag); beyond that is staleness. Calendar-day
    distance is used instead of "previous trading day" because no panel
    needs to exist for the in-between days.
  * Family split by symbol prefix (15=sz ETF, 51/52/53/55/56/58=sh ETF,
    others=stock/other) so "ETF face refreshed, stock face not" is legible
    at a glance.

Outputs: results/panel_coverage.json (machine face, carries evidence_cutoff)
+ docs/panel_coverage/COVERAGE-YYYYMMDD.md (one-pager, regenerated in place).

Exit contract: 0 ok | 2 mechanism failure (unreadable panel root).

Subcommands: run [--data-dir PATH] [--top N] | selftest
"""

import datetime as dt
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "daily")
OUT_JSON = os.path.join(ROOT, "results", "panel_coverage.json")
OUT_MD_DIR = os.path.join(ROOT, "docs", "panel_coverage")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NAME_RE = re.compile(r"^(sh|sz)?(\d{6})(_[A-Za-z0-9]+)?\.csv$")
LAG_DAYS = 3
ETF_PREFIXES = ("15", "51", "52", "53", "55", "56", "58")


def last_bar_date(path):
    """Cheap tail read: last data row's date (str) or None."""
    try:
        with io.open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 512))
            tail = f.read().decode("utf-8", "replace")
        for line in reversed(tail.splitlines()):
            d = line.split(",")[0].strip()
            if DATE_RE.match(d):
                return d
    except Exception:
        return None
    return None


def classify(name):
    """(symbol, family) from a panel file name; family drives the split."""
    m = NAME_RE.match(name)
    if not m:
        return None, "other"
    exch, code, suffix = m.group(1), m.group(2), m.group(3)
    sym = (exch or ("sz" if code.startswith("15") else "sh")) + code
    if suffix:
        return sym, "specialist"
    if code.startswith("15"):
        return sym, "sz-etf"
    if code.startswith(ETF_PREFIXES):
        return sym, "sh-etf"
    return sym, "stock-other"


def scan(data_dir=None, top=10):
    """Walk the panel face and return the coverage report dict."""
    data_dir = data_dir or DATA_DIR
    files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    rows = []
    unreadable = []
    for path in files:
        name = os.path.basename(path)
        sym, family = classify(name)
        last = last_bar_date(path)
        if last is None:
            unreadable.append(name)
            continue
        rows.append({"file": name, "symbol": sym or name, "family": family,
                     "last_bar": last})
    if not rows:
        return {"files_scanned": len(files), "files_dated": 0,
                "unreadable": unreadable, "evidence_cutoff": None,
                "histogram": [], "face_max": None,
                "coverage_at_max": 0, "coverage_within_3d": 0,
                "stale_files": 0, "lag_days": LAG_DAYS,
                "families": {}, "stale_top": []}

    hist = {}
    for r in rows:
        hist[r["last_bar"]] = hist.get(r["last_bar"], 0) + 1
    dates = sorted(hist, reverse=True)
    face_max = dates[0]
    at_max = sum(1 for r in rows if r["last_bar"] == face_max)
    fmax = dt.date(*[int(x) for x in face_max.split("-")])
    within = 0
    stale_n = 0
    for r in rows:
        gap = (fmax - dt.date(*[int(x) for x in r["last_bar"].split("-")])).days
        if gap <= LAG_DAYS:
            within += 1
        else:
            stale_n += 1

    families = {}
    for r in rows:
        f = families.setdefault(r["family"], {"n": 0, "at_max": 0,
                                              "min_last": face_max})
        f["n"] += 1
        if r["last_bar"] == face_max:
            f["at_max"] += 1
        if r["last_bar"] < f["min_last"]:
            f["min_last"] = r["last_bar"]

    stale = sorted(rows, key=lambda r: (r["last_bar"], r["file"]))[:int(top)]
    return {
        "files_scanned": len(files),
        "files_dated": len(rows),
        "unreadable": unreadable,
        "evidence_cutoff": face_max,
        "face_max": face_max,
        "coverage_at_max": at_max,
        "coverage_within_3d": within,
        "stale_files": stale_n,
        "lag_days": LAG_DAYS,
        "histogram": [{"last_bar": d, "n": hist[d]} for d in dates],
        "families": families,
        "stale_top": stale,
    }


def render_md(rep, ts):
    lines = ["# Panel coverage report %s" % rep.get("evidence_cutoff"),
             "",
             "Generated %s (L1 deterministic census: no network, no engine, "
             "no judgement). Source: `scripts/panel_coverage_report.py`."
             % ts,
             "",
             "## Headline",
             "",
             "* files scanned: **%d** (dated **%d**, unreadable/empty **%d**)"
             % (rep["files_scanned"], rep["files_dated"],
                len(rep["unreadable"])),
             "* face max bar: **%s**" % rep.get("face_max"),
             "* at face max: **%d / %d** (%.1f%%)"
             % (rep["coverage_at_max"], rep["files_dated"],
                100.0 * rep["coverage_at_max"] / max(1, rep["files_dated"])),
             "* within %d calendar days of face max: **%d / %d**"
             % (rep.get("lag_days", LAG_DAYS), rep["coverage_within_3d"],
                rep["files_dated"]),
             "* stale (older than %d calendar days): **%d**"
             % (rep.get("lag_days", LAG_DAYS), rep.get("stale_files", 0)),
             "",
             "## Last-bar histogram (top 10)",
             "",
             "| last bar | files |",
             "|---|---|"]
    for h in rep["histogram"][:10]:
        lines.append("| %s | %d |" % (h["last_bar"], h["n"]))
    lines += ["", "## By family", "",
              "| family | files | at face max | oldest bar |",
              "|---|---|---|---|"]
    for f, v in sorted(rep["families"].items()):
        lines.append("| %s | %d | %d | %s |"
                     % (f, v["n"], v["at_max"], v["min_last"]))
    lines += ["", "## Stalest panels", "",
              "| file | last bar |", "|---|---|"]
    for r in rep["stale_top"]:
        lines.append("| %s | %s |" % (r["file"], r["last_bar"]))
    lines += ["",
              "Reading rule (digest e35 Q-D/Q-E): a panel a few days behind "
              "is a lag; a panel stuck on an old date is staleness. Check the "
              "histogram before blaming any screen or sleeve for 'decay'.", ""]
    return "\n".join(lines)


def write_outputs(rep, ts, md_dir=None, out_json=None):
    out_json = out_json or OUT_JSON
    md_dir = md_dir or OUT_MD_DIR
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    os.makedirs(md_dir, exist_ok=True)
    payload = dict(rep)
    payload["ts"] = ts
    with io.open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    day = (rep.get("evidence_cutoff") or ts[:10]).replace("-", "")
    md_path = os.path.join(md_dir, "COVERAGE-%s.md" % day)
    with io.open(md_path, "w", encoding="utf-8") as f:
        f.write(render_md(rep, ts))
    return out_json, md_path


def _selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        def put(name, dates):
            with io.open(os.path.join(td, name), "w", encoding="utf-8") as f:
                f.write("date,open,high,low,close,volume,amount\n")
                for d in dates:
                    f.write("%s,1,1,1,1,1,1\n" % d)
        # C1 families
        assert classify("sh510300.csv") == ("sh510300", "sh-etf")
        assert classify("sz159915.csv") == ("sz159915", "sz-etf")
        assert classify("510300.csv") == ("sh510300", "sh-etf")
        assert classify("sh600000.csv") == ("sh600000", "stock-other")
        assert classify("sh510880_t73.csv")[1] == "specialist"

        # C2 tail read + empty file honesty
        put("sh510300.csv", ["2026-09-22", "2026-10-20"])
        put("sz159915.csv", ["2026-09-22"])
        with io.open(os.path.join(td, "sh511010.csv"), "w") as f:
            f.write("date,open\n")            # header only -> unreadable
        assert last_bar_date(os.path.join(td, "sh510300.csv")) == "2026-10-20"
        assert last_bar_date(os.path.join(td, "sh511010.csv")) is None

        # C3 coverage arithmetic: face max = 10-20, one laggard, one empty
        rep = scan(td, top=5)
        assert rep["files_scanned"] == 3 and rep["files_dated"] == 2
        assert rep["unreadable"] == ["sh511010.csv"]
        assert rep["face_max"] == "2026-10-20"
        assert rep["coverage_at_max"] == 1
        assert rep["coverage_within_3d"] == 1 and rep["stale_files"] == 1
        assert rep["families"]["sz-etf"]["at_max"] == 0
        assert rep["histogram"][0] == {"last_bar": "2026-10-20", "n": 1}

        # C4 outputs: md renders, json round-trips, cutoff carried
        md_dir = os.path.join(td, "docs")
        js = os.path.join(td, "results", "panel_coverage.json")
        write_outputs(rep, "2026-10-21T03:00:00+08:00", md_dir, js)
        back = json.load(io.open(js, encoding="utf-8"))
        assert back["evidence_cutoff"] == "2026-10-20"
        md = io.open(os.path.join(md_dir, "COVERAGE-20261020.md"),
                     encoding="utf-8").read()
        assert "face max bar: **2026-10-20**" in md
    print("selftest: 4/4 PASS")
    return 0


def main(argv):
    a = argv[1:]
    cmd = a[0] if a else "run"
    if cmd == "selftest":
        return _selftest()
    if cmd != "run":
        print("unknown subcommand: %s" % cmd)
        return 2
    data_dir = a[a.index("--data-dir") + 1] if "--data-dir" in a else None
    top = int(a[a.index("--top") + 1]) if "--top" in a else 10
    if data_dir and not os.path.isdir(data_dir):
        print("panel root missing: %s" % data_dir)
        return 2
    if not os.path.isdir(data_dir or DATA_DIR):
        print("panel root missing: %s" % (data_dir or DATA_DIR))
        return 2
    rep = scan(data_dir, top=top)
    ts = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    js, md = write_outputs(rep, ts)
    print("scanned=%d dated=%d face_max=%s at_max=%d within_%dd=%d stale=%d "
          "unreadable=%d"
          % (rep["files_scanned"], rep["files_dated"], rep["face_max"],
             rep["coverage_at_max"], LAG_DAYS, rep["coverage_within_3d"],
             rep["stale_files"], len(rep["unreadable"])))
    print("wrote %s" % os.path.relpath(js, ROOT))
    print("wrote %s" % os.path.relpath(md, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))