"""Futures lane: does every mark the carry book has published still have a quote behind it?

WHY (r1845, live 2026-11-19): the paper book `results/idx_fut_carry_paper/LEDGER.json`
prints IC and IM with a **2026-11-17** bar, and the page beside it prints
"contract bars to 2026-11-17". The contract panel those marks are supposed to come
from (`data/futures_contracts`) has no 11-17 row for either contract: `IC2612.csv`
and `IM2612.csv` were last written 2026-11-16 22:30 and end on 11-16. The published
11-17 close (6194.8 / 6023.0) is, to the tick, the **main-continuous** close of the
same day (`data/futures_daily/IC.csv`, `IM.csv`).

So the book is carrying a mark the contract panel cannot reproduce, wearing a
contract's label. Nobody could see it: the ledger is append-only (a re-run today
appends nothing, it never retracts), `contract_cutoff` is a `max()` across accounts
so one current leg hides a stale one, and the lane freshness row reads the newest
file of a panel. Each face is internally consistent; the pair is not.

What this face answers, and nothing else:
  * for every published bar of every account: is `(contract, date)` on the contract
    panel, and if not, is the close the main-continuous close of that date
    (the main-continuous close of that date, `matches_continuous`) or a number no panel
    on disk can produce (`no_quote_on_disk`);
  * how many sessions that bar sits past the contract panel's own last quote;
  * what money rides on those unbacked bars.

It writes only new files (`results/futures_book_marks.json`,
`research/FUTURES_BOOK_MARKS.md`). It never edits the ledger, the panel, or any
published face -- retracting a bar is a decision for the book's owner, not a side
effect of a report.

Usage:
    python scripts/futures_book_marks.py run
    python scripts/futures_book_marks.py --check
    python scripts/futures_book_marks.py selftest
"""

import datetime
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

LEDGER = os.path.join(ROOT, "results", "idx_fut_carry_paper", "LEDGER.json")
CONTRACT_DIR = os.path.join(ROOT, "data", "futures_contracts")
DAILY_DIR = os.path.join(ROOT, "data", "futures_daily")
OUT = os.path.join(ROOT, "results", "futures_book_marks.json")
DOC = os.path.join(ROOT, "research", "FUTURES_BOOK_MARKS.md")

TOL = 1e-6          # a mark is "the same close" at the tick, not near it


def _display(path):
    try:
        rel = os.path.relpath(path, ROOT)
    except ValueError:                      # another drive (fixtures under %TEMP%)
        return path
    return rel if not rel.startswith("..") else path


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ inputs
def contract_panel(prod, cont_dir=None):
    """{sym: {date: close}} for this product, read from the CSVs on disk.

    The panel is the whole point of the check, so it is read here rather than
    imported: a reader that also pulls, or that falls back to another panel, would
    answer a different question than "what is on this disk today".
    """
    import idx_fut_basis as base
    d = cont_dir or CONTRACT_DIR
    if not os.path.isdir(d):
        return {}
    out = {}
    for name in sorted(os.listdir(d)):
        if not name.startswith(prod) or not name.endswith(".csv"):
            continue
        sym = name[:-4]
        tail = sym[len(prod):]
        if len(tail) != 4 or not tail.isdigit():
            continue
        series = {}
        try:
            rows = base.read_csv_rows(os.path.join(d, name))
        except (OSError, UnicodeDecodeError):
            continue
        for r in rows:
            date = str(r.get("date") or "")[:10]
            try:
                close = float(r["close"])
            except (KeyError, TypeError, ValueError):
                continue
            if date:
                series[date] = close
        if series:
            out[sym] = series
    return out


def continuous_closes(prod, daily_dir=None):
    """{date: close} of the main-continuous panel -- the fallback source a mark
    could have been spliced from, which is exactly what has to be named out loud."""
    import idx_fut_basis as base
    path = os.path.join(daily_dir or DAILY_DIR, prod + ".csv")
    if not os.path.isfile(path):
        return {}
    out = {}
    for r in base.read_csv_rows(path):
        date = str(r.get("date") or "")[:10]
        try:
            out[date] = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
    return out


def load_ledger(path=None):
    return read_json(path or LEDGER)


# ------------------------------------------------------------------ assess
def assess(ledger, panels, continuous, calendar=None):
    """One record per account bar: is it backed, and by which panel.

    `panels` is {product: {sym: {date: close}}}, `continuous` is {product: {date: close}},
    both injected so the selftest never reads the live disk.
    """
    accounts = (ledger or {}).get("accounts") or {}
    products = {}
    for prod, acct in sorted(accounts.items()):
        bars = acct.get("rows") or []
        panel = panels.get(prod) or {}
        cont = continuous.get(prod) or {}
        if not panel:
            products[prod] = {"state": "panel_missing", "account_contract": acct.get("contract"),
                              "bars": len(bars), "unbacked": []}
            continue
        panel_last = max((max(s) for s in panel.values() if s), default=None)
        unbacked = []
        for r in bars:
            date = str(r.get("date") or "")[:10]
            sym = r.get("contract")
            series = panel.get(sym) or {}
            if date in series:
                continue
            close = r.get("close")
            if close is not None and date in cont and abs(float(close) - cont[date]) <= TOL:
                cause = "matches_continuous"
            else:
                cause = "no_quote_on_disk"
            unbacked.append({
                "date": date, "contract": sym, "close": close,
                "pnl_cny": r.get("pnl_cny"), "cause": cause,
                "continuous_close": cont.get(date),
                "sessions_past_panel": sessions_between(calendar, panel_last, date),
            })
        products[prod] = {
            "state": "unbacked_marks" if unbacked else "backed",
            "account_contract": acct.get("contract") or (bars[-1].get("contract") if bars else None),
            "bars": len(bars),
            "first": bars[0]["date"] if bars else None,
            "last": bars[-1]["date"] if bars else None,
            "panel_last_quote": panel_last,
            "unbacked": unbacked,
            "unbacked_n": len(unbacked),
            "unbacked_pnl_cny": round(sum(abs(float(u["pnl_cny"] or 0.0)) for u in unbacked), 2),
        }

    states = [p["state"] for p in products.values()]
    if not products:
        verdict = "NO_BOOK"
    elif all(s == "backed" for s in states):
        verdict = "BOOK_MARKS_SUPPORTED"
    elif all(s == "panel_missing" for s in states):
        verdict = "PANEL_MISSING"
    else:
        verdict = "BOOK_MARKS_UNSUPPORTED"

    last_days = [b["last"] for b in products.values() if b.get("last")]
    return {
        "face": "futures_book_marks",
        "verdict": verdict,
        "evidence_cutoff": max(last_days) if last_days else None,
        "source_book": _display(LEDGER),
        "products": products,
        "totals": {
            "products": len(products),
            "unbacked_bars": sum(p.get("unbacked_n") or 0 for p in products.values()),
            "unbacked_abs_pnl_cny": round(
                sum(p.get("unbacked_pnl_cny") or 0.0 for p in products.values()), 2),
        },
    }


def sessions_between(calendar, a, b):
    """Sessions strictly between a and b on the repo calendar (0 when unknown or equal)."""
    if not a or not b or a == b:
        return 0
    if calendar:
        days = [d for d in calendar if a < d <= b]
        if days:
            return len(days)
    return 0


# ------------------------------------------------------------------ render
def render(doc):
    out = []
    out.append("# does every mark in the carry book still have a quote behind it?")
    out.append("")
    out.append("verdict **%s** | book (%s) | generated %s"
               % (doc["verdict"], doc["source_book"], doc["generated"]))
    out.append("")
    t = doc["totals"]
    out.append("%d bar(s) of %d account(s) carry **%d mark(s) no contract panel on disk can "
               "reproduce**, holding **CNY %s** of absolute P&L. A bar that cannot be "
               "re-derived is not a wrong number -- it is a number whose evidence is gone."
               % (sum(p.get("bars") or 0 for p in doc["products"].values()), t["products"],
                  t["unbacked_bars"], "{:,.0f}".format(t["unbacked_abs_pnl_cny"])))
    out.append("")
    out.append("| product | holds | bars | last bar | panel last quote | unbacked | what they are |")
    out.append("|---|---|---|---|---|---|---|")
    for prod, p in sorted(doc["products"].items()):
        if p["state"] == "panel_missing":
            out.append("| %s | %s | %d | -- | **panel missing** | -- | cannot be checked |"
                       % (prod, p.get("account_contract") or "--", p.get("bars") or 0))
            continue
        causes = sorted({u["cause"] for u in p["unbacked"]})
        out.append("| %s | %s | %d | %s | %s | %d | %s |"
                   % (prod, p.get("account_contract") or "--", p["bars"], p["last"],
                      p["panel_last_quote"], p["unbacked_n"],
                      ", ".join(causes) + (" (+%d session(s) past the panel)"
                                           % max(u["sessions_past_panel"] for u in p["unbacked"])
                                           if p["unbacked"] else "")))
    out.append("")
    out.append("## the bars, one by one")
    out.append("")
    for prod, p in sorted(doc["products"].items()):
        if not p.get("unbacked"):
            continue
        out.append("### %s" % prod)
        out.append("")
        out.append("| date | contract | close printed | contract panel | main-continuous | cause | P&L on the bar |")
        out.append("|---|---|---|---|---|---|---|")
        for u in p["unbacked"]:
            out.append("| %s | %s | %s | **no quote** | %s | %s | %s |"
                       % (u["date"], u["contract"], u["close"],
                          "--" if u["continuous_close"] is None else u["continuous_close"],
                          u["cause"],
                          "--" if u["pnl_cny"] is None else "{:,.0f}".format(u["pnl_cny"])))
        out.append("")
    out.append("## what the files say")
    out.append("")
    out.append("| product | csv files | newest file | written | directory written |")
    out.append("|---|---|---|---|---|")
    for prod, p in sorted(doc["products"].items()):
        s = p.get("panel_stamps") or {}
        out.append("| %s | %s | %s | %s | %s |"
                   % (prod, s.get("files", "--"), s.get("newest_file", "--"),
                      s.get("newest_file_write", "--"), s.get("dir_write", "--")))
    out.append("")
    out.append("A book bar dated after every file in the panel cannot have come from those "
               "files. When that is true the two readings above stop being symmetric: the "
               "splice reading needs a writer that is not on this disk, while the lost-row "
               "reading needs the panel to have gone backwards without a file being written. "
               "This face says which dates and which files; it does not pick between them.")
    out.append("")
    out.append("`matches_continuous` = the printed close equals the main-continuous close of that "
               "date to the tick. Two readings fit and this disk cannot separate them: either the "
               "contract quoted that number that day and the panel has since lost the row, or the "
               "bar was marked from the other panel under this contract's label. "
               "`no_quote_on_disk` = no panel on disk produces that number at all.")
    out.append("")
    out.append("This face retracts nothing. Taking a bar off a forward series is the book "
               "owner's decision; what is printed here is only that the evidence for it is not "
               "on this disk today.")
    out.append("")
    return "\n".join(out)


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def mk_ledger(rows_by_prod):
        return {"accounts": {p: {"contract": rows[-1]["contract"], "rows": rows}
                             for p, rows in rows_by_prod.items()}}

    def bar(date, sym, close, pnl):
        return {"date": date, "contract": sym, "close": close, "pnl_cny": pnl, "nav_cny": 0.0}

    cal = ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18"]

    # L1 every bar backed -> supported, nothing named
    led = mk_ledger({"IC": [bar("2026-11-16", "IC2612", 6218.4, 0.0)]})
    doc = assess(led, {"IC": {"IC2612": {"2026-11-16": 6218.4}}}, {"IC": {}}, cal)
    legs.append(("L1 backed book reads supported",
                 doc["verdict"] == "BOOK_MARKS_SUPPORTED" and doc["totals"]["unbacked_bars"] == 0))

    # L2 a bar whose close equals the continuous close is named a continuous mark
    led = mk_ledger({"IC": [bar("2026-11-16", "IC2612", 6218.4, 0.0),
                            bar("2026-11-17", "IC2612", 6194.8, -18880.0)]})
    doc = assess(led, {"IC": {"IC2612": {"2026-11-16": 6218.4}}},
                 {"IC": {"2026-11-17": 6194.8}}, cal)
    u = doc["products"]["IC"]["unbacked"]
    legs.append(("L2 continuous-spliced bar is named, with its cause",
                 doc["verdict"] == "BOOK_MARKS_UNSUPPORTED" and len(u) == 1
                 and u[0]["cause"] == "matches_continuous" and u[0]["date"] == "2026-11-17"))

    # L3 a close that no panel produces is NOT laundered into "continuous"
    doc = assess(led, {"IC": {"IC2612": {"2026-11-16": 6218.4}}},
                 {"IC": {"2026-11-17": 6100.0}}, cal)
    legs.append(("L3 a close no panel produces stays no_quote_on_disk",
                 doc["products"]["IC"]["unbacked"][0]["cause"] == "no_quote_on_disk"))

    # L4 no ledger at all is NO_BOOK, never "supported"
    legs.append(("L4 an absent book is NO_BOOK",
                 assess({}, {}, {}, cal)["verdict"] == "NO_BOOK"))

    # L5 a product whose panel is absent is unmeasurable, not backed
    led = mk_ledger({"IC": [bar("2026-11-17", "IC2612", 6194.8, 0.0)]})
    doc = assess(led, {}, {}, cal)
    legs.append(("L5 a missing panel is unmeasurable, not supported",
                 doc["products"]["IC"]["state"] == "panel_missing"
                 and doc["verdict"] == "PANEL_MISSING"))

    # L6 the session distance is counted on the calendar, and equals 0 on the panel's own day
    led = mk_ledger({"IC": [bar("2026-11-17", "IC2612", 6194.8, 0.0)]})
    doc = assess(led, {"IC": {"IC2612": {"2026-11-16": 6218.4}}}, {"IC": {}}, cal)
    legs.append(("L6 sessions past the panel come from the calendar",
                 doc["products"]["IC"]["unbacked"][0]["sessions_past_panel"] == 1))
    doc = assess(led, {"IC": {"IC2612": {"2026-11-17": 6194.8}}}, {"IC": {}}, cal)
    legs.append(("L6b the panel's own day is zero sessions and backed",
                 doc["verdict"] == "BOOK_MARKS_SUPPORTED"))

    # L7 the money on unbacked bars is summed as absolute P&L, not netted to zero
    led = mk_ledger({"IC": [bar("2026-11-17", "IC2612", 1.0, -500.0)],
                     "IM": [bar("2026-11-17", "IM2612", 2.0, 300.0)]})
    doc = assess(led, {"IC": {"IC2612": {"2026-11-16": 1.0}},
                       "IM": {"IM2612": {"2026-11-16": 2.0}}}, {}, cal)
    legs.append(("L7 unbacked P&L is |sum| not net",
                 abs(doc["totals"]["unbacked_abs_pnl_cny"] - 800.0) < 1e-9))

    bad = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print("%-4s %s" % ("PASS" if ok else "FAIL", n))
    print("futures_book_marks selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_stamps(prod, cont_dir=None):
    """When were the CSVs behind this product last written?  A bar that is newer than
    every file in the panel cannot have come from these files, whatever it says."""
    d = cont_dir or CONTRACT_DIR
    if not os.path.isdir(d):
        return {}
    hits = [os.path.join(d, n) for n in os.listdir(d)
            if n.startswith(prod) and n.endswith(".csv")]
    if not hits:
        return {"files": 0}
    newest = max(hits, key=os.path.getmtime)
    return {
        "files": len(hits),
        "newest_file": os.path.basename(newest),
        "newest_file_write": datetime.datetime.fromtimestamp(
            os.path.getmtime(newest)).strftime("%Y-%m-%dT%H:%M:%S"),
        "dir_write": datetime.datetime.fromtimestamp(
            os.path.getmtime(d)).strftime("%Y-%m-%dT%H:%M:%S"),
    }


def build(calendar=None, ledger_path=None, cont_dir=None, daily_dir=None):
    ledger = load_ledger(ledger_path)
    prods = sorted((ledger.get("accounts") or {}).keys())
    panels = {p: contract_panel(p, cont_dir) for p in prods}
    cont = {p: continuous_closes(p, daily_dir) for p in prods}
    doc = assess(ledger, panels, cont, calendar)
    for p in prods:
        doc["products"].setdefault(p, {})["panel_stamps"] = write_stamps(p, cont_dir)
    if cont_dir is None and daily_dir is None:
        doc["contract_dir"] = _display(CONTRACT_DIR)
        doc["contract_dir_files"] = len([n for n in os.listdir(CONTRACT_DIR)
                                         if n.endswith(".csv")]) if os.path.isdir(CONTRACT_DIR) else 0
    doc["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return doc


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "selftest":
        return selftest()
    from scripts import exchange_calendar_audit as CA
    cal = CA.load_calendar()
    doc = build(calendar=cal)
    if cmd == "check":
        if not os.path.isfile(OUT):
            print("CHECK_FAIL no face at %s" % _display(OUT))
            return 2
        old = read_json(OUT)
        same = (old.get("verdict") == doc["verdict"]
                and (old.get("totals") or {}).get("unbacked_bars") == doc["totals"]["unbacked_bars"])
        print("CHECK_%s verdict=%s unbacked=%d"
              % ("OK" if same else "DRIFT", doc["verdict"], doc["totals"]["unbacked_bars"]))
        return 0 if same else 3
    _write(OUT, json.dumps(doc, ensure_ascii=False, indent=1))
    _write(DOC, render(doc))
    print("futures_book_marks: verdict %s | %d unbacked mark(s) | CNY %s"
          % (doc["verdict"], doc["totals"]["unbacked_bars"],
             "{:,.0f}".format(doc["totals"]["unbacked_abs_pnl_cny"])))
    for prod, p in sorted(doc["products"].items()):
        if p.get("unbacked"):
            for u in p["unbacked"]:
                print("  %s %s %s close=%s cause=%s +%d session(s)"
                      % (prod, u["contract"], u["date"], u["close"], u["cause"],
                         u["sessions_past_panel"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
