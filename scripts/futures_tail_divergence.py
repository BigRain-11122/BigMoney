"""Futures lane: every tail on the disk, and every cutoff a face claims.

WHY (r1843, live 2026-11-19): three published faces of the SAME book print three
different days and each one is internally consistent --

    results/idx_fut_real_nav.json          evidence_cutoff 2026-11-16
    results/idx_fut_carry_paper/LEDGER.json contract_cutoff 2026-11-17
    results/idx_fut_contract_roll.json     evidence_cutoff 2026-11-18
    results/idx_fut_desk_sheet.json        evidence_cutoff 2026-11-18

None of them is lying. The contract panel (`data/futures_contracts`) has had no
writer since 2026-11-16 22:30, so the roll book can only see contracts through
11-16; the paper ledger marks IC from the main-continuous panel, which stops at
11-17; and `data/futures_daily/IF|IH|IM.csv` reach 11-18 while `IC.csv` does not
-- the IC leg of the very book that carries it is one session behind its
siblings.

The lane freshness row cannot see any of this: it reads `panel_tail_csv`, which
takes the NEWEST file of a panel. A panel whose newest file is current and whose
IC file (or whose whole contract directory) is behind still prints `in_sync`.

What this face answers, and nothing else: for every file on both panels, where
does its tail sit; how many sessions behind its own panel's newest file is that;
and which of those tails each published face is actually anchored to. It writes
only new files (`results/futures_tail_divergence.json`) -- no shared face, no
panel, no ledger is touched.

Consumer map (read out of the scripts, not guessed):
    idx_fut_real_nav      -> data/futures_contracts   (idx_fut_contract_roll.CONTRACT_DIR)
    idx_fut_contract_roll -> data/futures_contracts
    idx_fut_carry_paper   -> roll book (contracts) for rolls, marks from its own face

Usage:
    python scripts/futures_tail_divergence.py run
    python scripts/futures_tail_divergence.py --check
    python scripts/futures_tail_divergence.py selftest
"""

import datetime
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PANELS = [
    {"name": "futures_daily", "dir": "data/futures_daily", "pattern": ".csv",
     "what": "main continuous, one row per session"},
    {"name": "futures_contracts", "dir": "data/futures_contracts", "pattern": ".csv",
     "what": "per-contract level, the roll book's input", "expiring": True},
]

CFFEX_MONTHS = ("IC", "IF", "IH", "IM")

# (face path, keys to read, panel the face is anchored to or None when undeclared)
FACES = [
    ("results/idx_fut_real_nav.json", ["evidence_cutoff"], "futures_contracts"),
    ("results/idx_fut_contract_roll.json", ["evidence_cutoff"], "futures_contracts"),
    ("results/idx_fut_desk_sheet.json", ["evidence_cutoff"], None),
    ("results/idx_fut_carry_paper/LEDGER.json",
     ["contract_cutoff", "evidence_cutoff"], None),
]

OUT = os.path.join(ROOT, "results", "futures_tail_divergence.json")

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def _display(path):
    """Repo-relative when possible, absolute otherwise (a C: fixture under a K: repo
    must not raise -- r1594/r1745 family, third copy)."""
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:
        return path
    return path if rel.startswith("..") else rel.replace(os.sep, "/")


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def tail_of_csv(path):
    """Last dated row -> 'YYYY-MM-DD' | None. Reads from the end, never the head."""
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        m = DATE_RE.match(line.strip())
        if m:
            return m.group(1)
    return None


def third_friday(year, month):
    """CFFEX stock-index futures stop trading on the third Friday of their month.

    Checked against the panel itself before being used: IC2609 ends 2026-09-18,
    IC2610 ends 2026-10-16, IC2608 ends 2026-08-21 -- all three are that month's
    third Friday, so this rule reproduces the vendor's calendar rather than
    assuming one.
    """
    d = datetime.date(year, month, 1)
    offset = (4 - d.weekday()) % 7          # Mon=0 ... Fri=4
    return d + datetime.timedelta(days=offset + 14)


def contract_expiry(symbol):
    """'IC2612' -> '2026-12-18' | None when the name is not a dated CFFEX contract."""
    m = re.match(r"^(%s)(\d{2})(\d{2})$" % "|".join(CFFEX_MONTHS), symbol)
    if not m:
        return None
    year, month = 2000 + int(m.group(2)), int(m.group(3))
    if not 1 <= month <= 12:
        return None
    return third_friday(year, month).isoformat()


def _git_tracked(rel_dir):
    """How many files of this panel git actually carries (None when git is unavailable).

    A panel that is gitignored and has no writer in the repository cannot be
    repaired by any round: it is not a slow lane, it is a directory someone
    copied in once. Those two states look identical on a freshness board.
    """
    import subprocess
    try:
        out = subprocess.run(["git", "ls-files", "--", rel_dir],
                             cwd=ROOT, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return len([l for l in out.stdout.splitlines() if l.strip()])


def panel_census(panel, root=None):
    base = os.path.join(root or ROOT, panel["dir"])
    out = {"panel": panel["name"], "dir": panel["dir"], "what": panel["what"],
           "files": 0, "read": 0, "newest": None, "tails": {}, "laggards": []}
    if not os.path.isdir(base):
        out["missing"] = True
        return out
    names = sorted(n for n in os.listdir(base)
                   if n.endswith(panel["pattern"]) and not n.startswith("_"))
    out["files"] = len(names)
    tails = {}
    for n in names:
        d = tail_of_csv(os.path.join(base, n))
        if d:
            tails[n[:-len(panel["pattern"])]] = d
    out["read"] = len(tails)
    out["tails"] = tails
    if not tails:
        return out
    out["newest"] = max(tails.values())
    out["laggards"] = sorted(
        ({"symbol": s, "tail": d} for s, d in tails.items() if d < out["newest"]),
        key=lambda r: (r["tail"], r["symbol"]))
    return out


def sessions_between(calendar, a, b):
    """Sessions in (a, b]. Negative when b < a -- the caller must print direction."""
    if a == b:
        return 0
    lo, hi = (a, b) if a < b else (b, a)
    n = sum(1 for d in calendar if lo < d <= hi)
    return n if b > a else -n


def attach_lag(census, calendar):
    newest = census.get("newest")
    if not newest:
        return census
    for row in census["laggards"]:
        row["sessions_behind"] = sessions_between(calendar, row["tail"], newest)
    census["n_laggards"] = len(census["laggards"])
    census["deepest_lag"] = max((r["sessions_behind"] for r in census["laggards"]),
                                default=0)
    return census


def classify_expiring(census):
    """A contract whose expiry is behind the panel's newest bar is finished, and its
    stale tail is the correct behaviour. Only live contracts can be laggards.

    Without this split the contract panel reports forty expired months as
    'laggards 178 sessions behind' and the one live hole -- if there is one -- is
    invisible in the noise.
    """
    newest = census.get("newest")
    if not newest:
        return census
    live, expired, undated = {}, [], []
    for sym, tail in sorted(census["tails"].items()):
        exp = contract_expiry(sym)
        if exp is None:
            undated.append(sym)
        elif exp < newest:
            expired.append({"symbol": sym, "tail": tail, "expiry": exp})
        else:
            live[sym] = tail
    census["n_expired"] = len(expired)
    census["n_live"] = len(live)
    census["undated_symbols"] = undated
    census["live_tails"] = live
    lag = [{"symbol": s, "tail": d, "expiry": contract_expiry(s)}
           for s, d in live.items() if d < newest]
    lag.sort(key=lambda r: (r["tail"], r["symbol"]))
    census["laggards"] = lag
    census["live_newest"] = max(live.values()) if live else None
    return census


def face_cutoffs(root=None):
    rows = []
    for path, keys, panel in FACES:
        full = os.path.join(root or ROOT, path)
        row = {"face": path, "anchored_to": panel, "cutoffs": {}}
        if not os.path.isfile(full):
            row["missing"] = True
            rows.append(row)
            continue
        try:
            doc = read_json(full)
        except (OSError, ValueError):
            row["unreadable"] = True
            rows.append(row)
            continue
        for k in keys:
            row["cutoffs"][k] = doc.get(k)
        rows.append(row)
    return rows


def build(calendar=None, root=None):
    if calendar is None:
        from scripts import exchange_calendar_audit as CA
        calendar = CA.load_calendar()
    panels = []
    for p in PANELS:
        c = panel_census(p, root)
        if p.get("expiring"):
            c = classify_expiring(c)
        c = attach_lag(c, calendar)
        if root is None:
            c["git_tracked_files"] = _git_tracked(p["dir"])
        panels.append(c)
    faces = face_cutoffs(root)

    # the same day seen from the two panels: a directory can be a writer-gap
    # without holding a single per-symbol hole, and the two are different repairs
    cross = {"panel_newest": {p["panel"]: p.get("newest") for p in panels}}
    a = cross["panel_newest"].get("futures_daily")
    b = cross["panel_newest"].get("futures_contracts")
    if a and b:
        cross["daily_vs_contracts_sessions"] = sessions_between(calendar, b, a)
        cross["oldest_panel"] = "futures_contracts" if b < a else (
            "futures_daily" if a < b else None)

    # every distinct day any of them claims
    claims = []
    for p in panels:
        if p.get("newest"):
            claims.append({"source": "panel:" + p["panel"], "day": p["newest"]})
    for row in faces:
        for k, v in (row.get("cutoffs") or {}).items():
            if v:
                claims.append({"source": "%s#%s" % (row["face"], k), "day": v})

    days = sorted({c["day"] for c in claims})
    spread = sessions_between(calendar, days[0], days[-1]) if days else 0
    verdict = ("NO_TAILS" if not days else
               "SINGLE_TAIL" if len(days) == 1 else
               "DIVERGENT")
    oldest = [c for c in claims if days and c["day"] == days[0]]
    newest = [c for c in claims if days and c["day"] == days[-1]]

    return {
        "face": "futures_tail_divergence",
        "verdict": verdict,
        "evidence_cutoff": days[-1] if days else None,
        "spread_sessions": spread,
        "distinct_days": days,
        "panels": panels,
        "cross_panel": cross,
        "faces": faces,
        "claims": claims,
        "oldest_claims": oldest,
        "newest_claims": newest,
        "note": ("Every claim is anchored to a different disk. A reader who asks "
                 "'what day is the carry book at' gets four answers; this face "
                 "exists so the answer always arrives with the file it came from."),
    }


def _summary(doc):
    lines = ["futures tail divergence -- verdict %s (spread %d sessions)"
             % (doc["verdict"], doc["spread_sessions"])]
    for p in doc["panels"]:
        if p.get("missing"):
            lines.append("  %-18s MISSING (%s)" % (p["panel"], p["dir"]))
            continue
        extra = ""
        if p.get("n_live") is not None:
            extra = " live=%d expired=%d live_newest=%s" % (
                p.get("n_live"), p.get("n_expired"), p.get("live_newest"))
        if p.get("git_tracked_files") is not None:
            extra += " git=%d" % p["git_tracked_files"]
        lines.append("  %-18s newest=%s files=%d read=%d laggards=%d deepest=%d%s"
                     % (p["panel"], p["newest"], p["files"], p["read"],
                        p.get("n_laggards", 0), p.get("deepest_lag", 0), extra))
        for r in (p.get("laggards") or [])[:8]:
            lines.append("    %-10s %s  -%d session(s)"
                         % (r["symbol"], r["tail"], r["sessions_behind"]))
        if len(p.get("laggards") or []) > 8:
            lines.append("    ... %d more" % (len(p["laggards"]) - 8))
    cp = doc.get("cross_panel") or {}
    if cp.get("oldest_panel"):
        lines.append("  cross-panel: %s is %d session(s) behind"
                     % (cp["oldest_panel"], abs(cp["daily_vs_contracts_sessions"])))
    for f in doc["faces"]:
        tag = f["face"].split("/")[-1]
        cut = f.get("cutoffs") or {}
        if f.get("missing"):
            lines.append("  %-28s MISSING" % tag)
            continue
        parts = ", ".join("%s=%s" % (k, v) for k, v in cut.items())
        lines.append("  %-28s %s%s" % (tag, parts,
                                       "" if f["anchored_to"] else "  (source undeclared)"))
    return "\n".join(lines)


# ---------------------------------------------------------------- selftest

def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def selftest():
    legs = []
    cal = ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19"]

    # L1 tail_of_csv reads the last dated row, not a header and not a trailing blank
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "X.csv")
        _write(p, "date,open,close\n2026-11-16,1,2\n2026-11-17,3,4\n\n")
        legs.append(("L1 tail reads last dated row", tail_of_csv(p) == "2026-11-17"))

        # L2 a file with no dated row contributes no tail (not a zero)
        p2 = os.path.join(tmp, "EMPTY.csv")
        _write(p2, "date,open,close\n")
        legs.append(("L2 header-only file has no tail", tail_of_csv(p2) is None))

        # L3 panel census names the laggard and how many sessions behind it is
        d = os.path.join(tmp, "panel")
        _write(os.path.join(d, "IC.csv"), "date,close\n2026-11-17,6194.8\n")
        _write(os.path.join(d, "IM.csv"), "date,close\n2026-11-18,5987.4\n")
        c = attach_lag(panel_census({"name": "p", "dir": "panel", "pattern": ".csv",
                                     "what": ""}, tmp), cal)
        legs.append(("L3 newest is the max, IC named as laggard",
                     c["newest"] == "2026-11-18" and [r["symbol"] for r in c["laggards"]] == ["IC"]))
        legs.append(("L3b laggard carries sessions_behind=1",
                     c["laggards"][0]["sessions_behind"] == 1 and c["deepest_lag"] == 1))

        # L4 sessions_between is direction-aware: going back is negative
        legs.append(("L4 direction", sessions_between(cal, "2026-11-18", "2026-11-16") == -2
                     and sessions_between(cal, "2026-11-16", "2026-11-18") == 2))

        # L5 faces missing from disk are reported missing, never as zero
        legs.append(("L5 missing face is not a zero",
                     face_cutoffs(tmp)[0].get("missing") is True))

        # L6 build() on a whole synthetic repo: three faces, one panel -> DIVERGENT
        root = os.path.join(tmp, "repo")
        _write(os.path.join(root, "data", "futures_daily", "IC.csv"),
               "date,close\n2026-11-17,1\n")
        _write(os.path.join(root, "data", "futures_daily", "IM.csv"),
               "date,close\n2026-11-18,1\n")
        _write(os.path.join(root, "data", "futures_contracts", "IC2612.csv"),
               "date,close\n2026-11-16,1\n")
        _write(os.path.join(root, "results", "idx_fut_real_nav.json"),
               '{"evidence_cutoff": "2026-11-16"}')
        _write(os.path.join(root, "results", "idx_fut_contract_roll.json"),
               '{"evidence_cutoff": "2026-11-18"}')
        _write(os.path.join(root, "results", "idx_fut_desk_sheet.json"),
               '{"evidence_cutoff": "2026-11-18"}')
        _write(os.path.join(root, "results", "idx_fut_carry_paper", "LEDGER.json"),
               '{"contract_cutoff": "2026-11-17", "evidence_cutoff": "2026-11-18"}')
        doc = build(calendar=cal, root=root)
        legs.append(("L6 three days -> DIVERGENT with spread 2",
                     doc["verdict"] == "DIVERGENT" and doc["spread_sessions"] == 2
                     and doc["distinct_days"] == ["2026-11-16", "2026-11-17", "2026-11-18"]))
        legs.append(("L6b every distinct day names its own source",
                     {c["day"] for c in doc["oldest_claims"]} == {"2026-11-16"}
                     and len({c["source"] for c in doc["claims"]}) == len(doc["claims"])))

        # L7 one day everywhere -> SINGLE_TAIL (the healthy reading)
        for name in ("idx_fut_real_nav.json", "idx_fut_contract_roll.json",
                     "idx_fut_desk_sheet.json"):
            _write(os.path.join(root, "results", name),
                   '{"evidence_cutoff": "2026-11-18"}')
        _write(os.path.join(root, "results", "idx_fut_carry_paper", "LEDGER.json"),
               '{"contract_cutoff": "2026-11-18", "evidence_cutoff": "2026-11-18"}')
        _write(os.path.join(root, "data", "futures_daily", "IC.csv"),
               "date,close\n2026-11-18,1\n")
        _write(os.path.join(root, "data", "futures_contracts", "IC2612.csv"),
               "date,close\n2026-11-18,1\n")
        doc2 = build(calendar=cal, root=root)
        legs.append(("L7 all on one day -> SINGLE_TAIL",
                     doc2["verdict"] == "SINGLE_TAIL" and doc2["spread_sessions"] == 0))
        legs.append(("L7b summary prints the verdict line",
                     _summary(doc2).startswith("futures tail divergence -- verdict SINGLE_TAIL")))

        # L8 the expiry rule reproduces the tails the vendor itself produced --
        # these three are the panel's own last rows, not a calendar we invented
        legs.append(("L8 third Friday matches IC2608/2609/2610 tails",
                     contract_expiry("IC2608") == "2026-08-21"
                     and contract_expiry("IC2609") == "2026-09-18"
                     and contract_expiry("IC2610") == "2026-10-16"))
        legs.append(("L8b a name without a month is not given a fake expiry",
                     contract_expiry("IC000300") is None and contract_expiry("ZZ2612") is None))

        # L9 an expired contract's stale tail is correct behaviour, not a laggard:
        # 40 expired months must not bury the one live hole
        exp = classify_expiring({
            "tails": {"IC2609": "2026-09-18", "IC2612": "2026-11-16",
                      "IM2612": "2026-11-16"},
            "newest": "2026-11-16", "laggards": []})
        legs.append(("L9 expired contract is not a laggard",
                     exp["n_expired"] == 1 and exp["n_live"] == 2
                     and exp["laggards"] == []))
        exp2 = classify_expiring({
            "tails": {"IC2612": "2026-11-16", "IM2612": "2026-11-18"},
            "newest": "2026-11-18", "laggards": []})
        legs.append(("L9b a LIVE contract one session behind is named",
                     [r["symbol"] for r in exp2["laggards"]] == ["IC2612"]))

    ok = sum(1 for _, v in legs if v)
    for name, good in legs:
        print("%s %s" % ("PASS" if good else "FAIL", name))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "selftest":
        return selftest()
    doc = build()
    if cmd == "check":
        if not os.path.isfile(OUT):
            print("CHECK_FAIL no face at %s" % _display(OUT))
            return 3
        prev = read_json(OUT)
        same = (prev.get("verdict") == doc["verdict"]
                and prev.get("distinct_days") == doc["distinct_days"])
        print("CHECK_%s verdict=%s days=%s" % ("OK" if same else "FAIL",
                                              doc["verdict"], doc["distinct_days"]))
        return 0 if same else 3
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(_summary(doc))
    print("wrote %s" % _display(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
