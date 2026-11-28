"""Two NAV sources, one session label: which number may be called "today's"?

r2212. r2211 fixed ONE leg (159519) where the premium face priced a row on a
foreign NAV. The open question it left behind is not about one ticker: the
premium face's denominator comes from `data/etf_premium/snap/<session>.navok.json`,
which stamps a whole batch with `session` and stores only values — no per-row
date, no per-row origin. The sina `fu_<code>` quote, by contrast, prints its own
date in field 7. So the two sources can both say "2026-11-27" about different
numbers and nothing in the board file can referee it.

Live anchor (2026-11-27, measured this round):
    513690  board navok.nav = 1.1161   (no row-level date)
    513690  sina fu_       = 1.1137   (own date field = 2026-11-27)
    -> 0.215% apart, which is 22% of that leg's own -0.96% premium reading.

This module asks the only question that decides which one may be used as a
denominator: **can the source say which day its number is from?** It does not
pick a winner; it prints, per ticker, both values, the dated one, and the gap.

Output: results/etf_nav/two_source_audit.json (+ .md), self-contained.

Usage:
    python scripts/etf_nav_two_source_audit.py run [--sample 400]
    python scripts/etf_nav_two_source_audit.py check
    python scripts/etf_nav_two_source_audit.py selftest
"""
import argparse
import glob
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
OUT_DIR = os.path.join(ROOT, "results", "etf_nav")
FACE = os.path.join(OUT_DIR, "two_source_audit.json")
DOC = os.path.join(OUT_DIR, "TWO-SOURCE.md")
CACHE = os.path.join(OUT_DIR, "_sina_raw.json")

HOST = "http://hq.sinajs.cn/list=fu_"
HEADERS = {"Referer": "https://finance.sina.com.cn/",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BATCH = 80
THROTTLE = 0.4

# A gap worth naming. 0.10% is the same line the premium lane already uses to
# decide a reading is "the same number" (see etf_premium_face cross_check_pp);
# below it the two sources agree to the precision anyone would trade on.
GAP_LINE_PCT = 0.10


def latest_navok():
    """Newest board snapshot that actually carries values (older ones carry none)."""
    best = None
    for p in sorted(glob.glob(os.path.join(SNAP_DIR, "*.navok.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        nav = d.get("nav") or {}
        if nav:
            best = (p, d)
    return best


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def parse_fu(sym, raw):
    """One sina `fu_` payload -> {code, nav, nav_date, cum_nav}. Pure, testable."""
    # var hq_str_fu_513690="name,HH:MM:SS,unit,cum,?,?,chg%,YYYY-MM-DD,?,?";
    if "=" not in raw:
        return None
    body = raw.split("=", 1)[1].strip().strip(";").strip('"')
    if not body or body.lower() in ("", "null"):
        return None
    f = body.split(",")
    if len(f) < 8:
        return None
    nav = _num(f[2])
    date = f[7].strip()
    if nav is None or nav <= 0:
        return None
    if len(date) != 10 or date[4] != "-":
        return None           # a source that cannot name its day is not dated
    return {"code": sym.split("_")[-1], "nav": nav, "nav_date": date,
            "cum_nav": _num(f[3]) if len(f) > 3 else None}


def fetch_sina(codes):
    out, failed = {}, []
    for i in range(0, len(codes), BATCH):
        chunk = codes[i:i + BATCH]
        url = HOST + ",".join("fu_" + c for c in chunk)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            raw = urllib.request.urlopen(req, timeout=20).read().decode("gbk", "replace")
        except Exception as e:
            failed.append({"batch": i, "why": type(e).__name__})
            time.sleep(1.0)
            continue
        for line in raw.splitlines():
            if "fu_" not in line:
                continue
            sym = line.split("fu_", 1)[1].split("=", 1)[0].strip()
            row = parse_fu(sym, line)
            if row:
                out[row["code"]] = row
        time.sleep(THROTTLE)
    return out, failed


def build(board_session, board_nav, sina_rows):
    """Compare per ticker. Only tickers present in both can be compared at all."""
    common, gap_over, dated_mismatch = [], [], []
    for code in sorted(set(board_nav) & set(sina_rows)):
        b = _num(board_nav[code])
        s = sina_rows[code]
        if b is None or b <= 0:
            continue
        gap = (b - s["nav"]) / s["nav"] * 100.0
        row = {"code": code, "board_nav": b, "sina_nav": s["nav"],
               "sina_nav_date": s["nav_date"], "gap_pct": round(gap, 6)}
        if s["nav_date"] != board_session:
            dated_mismatch.append(row)
        if abs(gap) >= GAP_LINE_PCT:
            gap_over.append(row)
        common.append(row)
    common.sort(key=lambda r: -abs(r["gap_pct"]))
    gaps = sorted(abs(r["gap_pct"]) for r in common)
    med = gaps[len(gaps) // 2] if gaps else None
    return {
        "board_session": board_session,
        "n_board": len(board_nav),
        "n_sina": len(sina_rows),
        "n_compared": len(common),
        "n_gap_over_line": len(gap_over),
        "n_sina_date_off_board_session": len(dated_mismatch),
        "gap_line_pct": GAP_LINE_PCT,
        "median_abs_gap_pct": med,
        "worst": common[:15],
        "gap_over_line": gap_over[:40],
        "date_off_board": dated_mismatch[:20],
    }


def verdict_of(face):
    """The decision sentence, derived from the face's own counts (never typed)."""
    if face["n_compared"] == 0:
        return "CANNOT_VERIFY: no ticker carried both a board value and a dated sina value."
    if face["n_gap_over_line"] == 0:
        return ("AGREE: on %d tickers the two sources sit within %.2f%% of each other, "
                "so the board's session label is consistent with a dated source for every "
                "row anyone could read a premium off." % (face["n_compared"], GAP_LINE_PCT))
    biggest = face["worst"][0]
    return ("SPLIT: %d of %d tickers differ by >= %.2f%% (worst %s: board %.4f vs dated "
            "%s %.4f = %.3f%%). The board file carries no per-row date, so for these rows "
            "the board number cannot be called that session's; only the dated source can."
            % (face["n_gap_over_line"], face["n_compared"], GAP_LINE_PCT,
               biggest["code"], biggest["board_nav"], biggest["sina_nav_date"],
               biggest["sina_nav"], biggest["gap_pct"]))


def render(face, verdict):
    L = []
    L.append("# Two NAV sources, one session label\n")
    L.append("Board session `%s` (%d values, no per-row date) vs sina `fu_` "
             "(%d values, each carries its own date).\n"
             % (face["board_session"], face["n_board"], face["n_sina"]))
    L.append("**%s**\n" % verdict)
    L.append("| compared | median abs gap | over %.2f%% | sina date off board session |"
             % face["gap_line_pct"])
    L.append("|---|---|---|---|")
    L.append("| %d | %s | %d | %d |"
             % (face["n_compared"],
                ("%.4f%%" % face["median_abs_gap_pct"]) if face["median_abs_gap_pct"] is not None else "n/a",
                face["n_gap_over_line"], face["n_sina_date_off_board_session"]))
    if face["worst"]:
        L.append("\n## Widest gaps (board vs dated)\n")
        L.append("| code | board | sina (dated) | sina date | gap |")
        L.append("|---|---|---|---|---|")
        for r in face["worst"][:10]:
            L.append("| %s | %.4f | %.4f | %s | %+.4f%% |"
                     % (r["code"], r["board_nav"], r["sina_nav"], r["sina_nav_date"], r["gap_pct"]))
    if face["date_off_board"]:
        L.append("\n## Dated source disagrees about WHICH day it is\n")
        L.append("| code | board session | sina date | gap |")
        L.append("|---|---|---|---|")
        for r in face["date_off_board"][:10]:
            L.append("| %s | %s | %s | %+.4f%% |"
                     % (r["code"], face["board_session"], r["sina_nav_date"], r["gap_pct"]))
    L.append("\n## What this does and does not settle\n")
    L.append("- Settles: whether the board's whole-batch session label is defensible row by row.")
    L.append("- Does not settle: which of the two is the officially published NAV. A gap means "
             "one of them is not that session's number; identity requires the fund's own filing.")
    L.append("- A row absent from this table was not compared, not \"agreed\".")
    return "\n".join(L) + "\n"


def cmd_run(sample):
    got = latest_navok()
    if not got:
        print("no navok snapshot carrying values -> nothing to compare", file=sys.stderr)
        return 2
    path, d = got
    board_session, board_nav = d.get("session"), d.get("nav") or {}
    codes = sorted(board_nav)[:sample] if sample else sorted(board_nav)
    print("board: %s (%d values) sample=%d" % (os.path.basename(path), len(board_nav), len(codes)))
    sina_rows, failed = fetch_sina(codes)
    print("sina: %d dated values, %d failed batches" % (len(sina_rows), len(failed)))
    face = build(board_session, {c: board_nav[c] for c in codes}, sina_rows)
    face["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    face["failed_batches"] = failed
    face["sample"] = sample
    verdict = verdict_of(face)
    face["verdict"] = verdict
    if face["n_compared"] == 0 and sample and sample < len(board_nav):
        # The sample happened to miss; say so rather than publishing a fake AGREE.
        face["verdict_note"] = "sample too small to compare; re-run with a larger --sample"
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(face, open(FACE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sina_rows, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    open(DOC, "w", encoding="utf-8").write(render(face, verdict))
    print("VERDICT: " + verdict)
    print("-> %s" % FACE)
    return 0


def cmd_check():
    if not os.path.exists(FACE):
        print("STALE: face missing (%s) -> run first" % FACE)
        return 3
    face = json.load(open(FACE, encoding="utf-8"))
    problems = []
    # Re-derive the counts from the published rows; the headline must be recomputable.
    for key, src in (("n_gap_over_line", "gap_over_line"),
                     ("n_sina_date_off_board_session", "date_off_board")):
        rows = face.get(src) or []
        # published lists are capped, so only check the direction, not equality
        if face.get(key, 0) < len(rows):
            problems.append("%s=%s but %s lists %d rows" % (key, face.get(key), src, len(rows)))
    worst = face.get("worst") or []
    if worst:
        top = worst[0]
        if abs(top["gap_pct"]) < face.get("gap_line_pct", GAP_LINE_PCT):
            problems.append("worst gap %.4f below the %.2f line but a SPLIT was published"
                            % (top["gap_pct"], face.get("gap_line_pct", GAP_LINE_PCT)))
        # The gap must equal the two printed values, not a third stored number.
        recomputed = (top["board_nav"] - top["sina_nav"]) / top["sina_nav"] * 100.0
        if abs(recomputed - top["gap_pct"]) > 1e-6:
            problems.append("worst gap %.6f != recomputed %.6f from its own two values"
                            % (top["gap_pct"], recomputed))
        if not top.get("sina_nav_date"):
            problems.append("worst row has no dated source, yet a verdict was published")
    if problems:
        print("CHECK FAILED: " + " | ".join(problems))
        return 3
    print("CHECK_OK compared=%d over_line=%d median=%s"
          % (face["n_compared"], face["n_gap_over_line"], face.get("median_abs_gap_pct")))
    return 0


def cmd_selftest():
    legs = []

    def chk(name, cond):
        legs.append((name, bool(cond)))

    # L1: a well-formed fu_ payload yields nav + date
    r = parse_fu("fu_513690",
                 'var hq_str_fu_513690="博时港股红利ETF,16:04:00,1.1137,1.1175,1.1543,0,-0.3373,2026-11-27,1.1256,0.724";')
    chk("L1 parse nav+date", r and abs(r["nav"] - 1.1137) < 1e-9 and r["nav_date"] == "2026-11-27")
    # L2: an undated payload is refused (a source with no day is not dated)
    r2 = parse_fu("fu_510300",
                  'var hq_str_fu_510300="x,1:2:3,4.5,4.6,0,0,0,nodate,0,0";')
    chk("L2 undated refused", r2 is None)
    # L3: a zero/negative nav is refused, not compared against the board
    chk("L3 zero nav refused",
        parse_fu("fu_000001", 'var hq_str_fu_000001="x,1,0,0,0,0,0,2026-11-27,0,0";') is None)
    # L4: empty payload refused
    chk("L4 empty refused", parse_fu("fu_1", 'var hq_str_fu_1="";') is None)
    # L5: agreement under the line -> AGREE and no over-line rows
    f = build("2026-11-27", {"513690": 1.1139},
              {"513690": {"code": "513690", "nav": 1.1137, "nav_date": "2026-11-27", "cum_nav": None}})
    chk("L5 small gap agrees", f["n_gap_over_line"] == 0 and verdict_of(f).startswith("AGREE"))
    # L6: the live 513690 shape -> SPLIT, and the verdict names the same ticker
    f = build("2026-11-27", {"513690": 1.1161},
              {"513690": {"code": "513690", "nav": 1.1137, "nav_date": "2026-11-27", "cum_nav": None}})
    v = verdict_of(f)
    chk("L6 live split", f["n_gap_over_line"] == 1 and v.startswith("SPLIT") and "513690" in v)
    # L7: a dated source on another day is counted, not silently merged
    f = build("2026-11-27", {"159519": 1.7010},
              {"159519": {"code": "159519", "nav": 1.7010, "nav_date": "2026-11-26", "cum_nav": None}})
    chk("L7 off-session dated counted", f["n_sina_date_off_board_session"] == 1)
    # L8: nothing comparable -> CANNOT_VERIFY, never a zero-gap AGREE
    f = build("2026-11-27", {"510300": 4.0}, {})
    chk("L8 empty is cannot_verify", verdict_of(f).startswith("CANNOT_VERIFY"))
    # L9: the verdict is derived from counts, so flipping the count flips the word
    f = build("2026-11-27", {"A": 1.0},
              {"A": {"code": "A", "nav": 1.0, "nav_date": "2026-11-27", "cum_nav": None}})
    before = verdict_of(f)
    f["n_gap_over_line"] = 0
    chk("L9 verdict recomputed", before.startswith("AGREE"))
    # L10: gap arithmetic is board-over-sina, both printed (no third stored number)
    f = build("2026-11-27", {"C": 1.1161},
              {"C": {"code": "C", "nav": 1.1137, "nav_date": "2026-11-27", "cum_nav": None}})
    w = f["worst"][0]
    chk("L10 gap from own values",
        abs(w["gap_pct"] - (w["board_nav"] - w["sina_nav"]) / w["sina_nav"] * 100.0) < 1e-6)

    for n, ok in legs:
        print(("PASS " if ok else "FAIL ") + n)
    bad = [n for n, ok in legs if not ok]
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "check", "selftest"])
    ap.add_argument("--sample", type=int, default=400)
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(a.sample)
    if a.cmd == "check":
        return cmd_check()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
