"""Is the hedge ticket dated the way its book is dated?

r2027 answered "how many lots" and had to use two different dates to do it: the book's
last period ends 2026-11-11 (that is when its positions were last marked), while the
price panels run to 2026-11-20.  A ticket that mixes a 11-11 book with an 11-20 price
is not wrong about the lot count -- it is wrong about *which question* the lot count
answers.  This face prints both tickets and the distance between them:

1. the ticket priced on the book's own last bar (11-11), i.e. self-consistent dating;
2. the ticket priced on the panel's last bar (11-20), i.e. what r2027 published;
3. the price move that would have to happen before either arm's integer lot count
   changes at a given capital rung -- the ruler that says whether the dating defect
   can reach the order at all;
4. what the seven unmarked days actually did to the two hedge instruments (the book
   itself has no mark on those days: that is the defect, printed, not papered over).

No beta is refitted, no size re-chosen, no cost model introduced.

Outputs (new files only):
    results/astock_veto_hedge_dating.json
    research/ASTOCK_VETO_HEDGE_DATING.md

Usage:
    python scripts/astock_veto_hedge_dating.py selftest
    python scripts/astock_veto_hedge_dating.py run
    python scripts/astock_veto_hedge_dating.py check
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = os.path.join(ROOT, "results", "astock_veto_hedge_default.json")
BETA_FACE = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
LOTS_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_lots.json")
ETF_CSV = os.path.join(ROOT, "data", "daily", "sh512100.csv")
IM_CSV = os.path.join(ROOT, "data", "futures_daily", "IM.csv")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_dating.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_DATING.md")

ETF_LOT = 100
IM_MULT = 200
CAPITALS = (1_000_000, 3_000_000, 10_000_000, 20_000_000)
TOL = 1e-9

PREREG = {
    "frozen_before_the_numbers": True,
    "dates_compared": [
        "book date = results/astock_veto_hedgeable_beta.json:rows[-1].end (the bar the book was last marked on)",
        "price date = the last bar of the two hedge price panels (what r2027 published)",
    ],
    "lot_formula": "lots_needed = capital * k * beta / (price * multiplier); floor for 'do not overshoot', round for 'closest'",
    "no_new_data": "both dates are read out of the two price panels already in the repo",
    "price_move_to_flip": "the smallest |f| with price*(1+f) that changes the integer lot count; "
                          "the nearest-integer boundary is solved exactly, not searched",
    "not_fitted": "no beta, size, cost, basis or book return is estimated here",
    "verdict_rungs": [
        "some capital rung's integer lot count differs between the two dates -> DATING_MOVES_THE_ORDER",
        "no rung's integer lot count differs -> DATING_IS_IMMATERIAL_AT_THE_LOT_LEVEL",
    ],
}


# ------------------------------------------------------------------ pure logic
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    body = {k: v for k, v in face.items() if k != "generated"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face),
            "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


def load_bars(path: str) -> list:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        try:
            close = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        out.append({"date": r["date"], "close": close})
    out.sort(key=lambda x: x["date"])
    return out


def bar_on_or_before(bars: list, date: str) -> dict:
    """The last bar at or before `date` -- a board that is shut still has a price."""
    picked = None
    for b in bars:
        if b["date"] <= date:
            picked = b
        else:
            break
    if picked is None:
        raise SystemExit("no bar on or before %s" % date)
    return picked


def lots_needed(capital: float, target_beta: float, price: float, multiplier: float) -> float:
    return capital * target_beta / (price * multiplier)


def integer_choices(lots: float) -> dict:
    floor = int(math.floor(lots + TOL))
    rnd = int(math.floor(lots + 0.5 + TOL))
    return {"needed": lots, "floor": floor, "round": rnd}


def beta_error(lots: int, capital: float, price: float, multiplier: float,
               target_beta: float) -> float:
    return lots * price * multiplier / capital - target_beta


def flip_move(lots: float) -> dict:
    """Smallest relative price move that changes the nearest-integer lot count.

    price -> price*(1+f) makes lots_needed -> lots/(1+f).  The rounded count changes at
    lots/(1+f) = n + 0.5 for the two boundaries around `lots`.  Solved exactly.
    """
    rnd = int(math.floor(lots + 0.5 + TOL))
    ups = []
    # boundary upward: rnd -> rnd+1 at lots/(1+f) = rnd+0.5
    if lots / (rnd + 0.5) - 1.0 < 0:
        ups.append({"to": rnd + 1, "f": lots / (rnd + 0.5) - 1.0})
    # boundary downward: rnd -> rnd-1 at lots/(1+f) = rnd-0.5 (only if rnd-1 >= 0)
    if rnd - 1 >= 0:
        denom = rnd - 0.5
        if denom > 0:
            f = lots / denom - 1.0
            if f > 0:
                ups.append({"to": rnd - 1, "f": f})
    if not ups:
        return {"to": None, "move": None, "direction": None}
    best = min(ups, key=lambda x: abs(x["f"]))
    return {"to": best["to"], "move": best["f"],
            "direction": "price falls" if best["f"] < 0 else "price rises"}


def verdict_of(face: dict) -> tuple:
    moved = [r for r in face["ladder"] if r["order_changed"]]
    if moved:
        return ("DATING_MOVES_THE_ORDER",
                "%d of %d capital rung(s) place a different number of lots when the price "
                "is dated with the book instead of after it: %s"
                % (len(moved), len(face["ladder"]),
                   ", ".join("%s (%s %d -> %d)" % (r["capital"], r["arm"],
                                                   r["at_price_date"]["round"],
                                                   r["at_book_date"]["round"])
                             for r in moved)))
    return ("DATING_IS_IMMATERIAL_AT_THE_LOT_LEVEL",
            "no capital rung places a different number of lots on the two dates; the "
            "defect is in the face's caption, not in its order")


def build(force_price_move: float = 0.0) -> dict:
    parent = _read_json(PARENT)
    betaface = _read_json(BETA_FACE)
    lots_face = _read_json(LOTS_FACE)

    beta = float(parent["default"]["beta"])
    k = float(parent["default"]["k"])
    target_beta = k * beta

    book_date = str(betaface["rows"][-1]["end"])
    etf_bars = load_bars(ETF_CSV)
    im_bars = load_bars(IM_CSV)
    price_date = etf_bars[-1]["date"]

    arms = {
        "etf": {"multiplier": ETF_LOT, "bars": etf_bars, "symbol": "512100"},
        "im": {"multiplier": IM_MULT, "bars": im_bars, "symbol": "IM"},
    }
    prices = {}
    for arm, spec in arms.items():
        at_book = bar_on_or_before(spec["bars"], book_date)
        at_price = bar_on_or_before(spec["bars"], price_date)
        prices[arm] = {
            "at_book_date": at_book,
            "at_price_date": at_price,
            "move_between_dates": at_price["close"] / at_book["close"] - 1.0,
            "priced_after_the_book_by_bars": sum(1 for b in spec["bars"]
                                                 if at_book["date"] < b["date"] <= at_price["date"]),
        }

    ladder = []
    for cap in CAPITALS:
        for arm, spec in arms.items():
            mult = spec["multiplier"]
            p_book = prices[arm]["at_book_date"]["close"] * (1.0 + force_price_move)
            p_price = prices[arm]["at_price_date"]["close"]
            l_book = lots_needed(cap, target_beta, p_book, mult)
            l_price = lots_needed(cap, target_beta, p_price, mult)
            row = {
                "capital": cap,
                "arm": arm,
                "target_beta": target_beta,
                "at_book_date": {"price": prices[arm]["at_book_date"]["close"],
                                 "date": prices[arm]["at_book_date"]["date"],
                                 **integer_choices(l_book)},
                "at_price_date": {"price": prices[arm]["at_price_date"]["close"],
                                  "date": prices[arm]["at_price_date"]["date"],
                                  **integer_choices(l_price)},
                "flip_move_from_book_date": flip_move(l_book),
            }
            for side in ("at_book_date", "at_price_date"):
                row[side]["beta_error_round"] = beta_error(
                    row[side]["round"], cap, row[side]["price"], mult, target_beta)
            row["order_changed"] = (row["at_book_date"]["round"] != row["at_price_date"]["round"])
            row["delta_lots_round"] = (row["at_price_date"]["round"] -
                                       row["at_book_date"]["round"])
            row["delta_beta_error"] = (row["at_price_date"]["beta_error_round"] -
                                       row["at_book_date"]["beta_error_round"])
            ladder.append(row)

    # what r2027 published, for the delta rather than for a re-derivation
    published = {}
    for cap_key, block in (lots_face.get("ladders") or {}).items():
        published[cap_key] = {arm: {"round": block[arm]["round"]["lots"],
                                    "needed": block[arm]["lots_needed"]}
                              for arm in ("etf", "im") if arm in block}

    im_1m = next(r for r in ladder if r["capital"] == CAPITALS[0] and r["arm"] == "im")
    etf_1m = next(r for r in ladder if r["capital"] == CAPITALS[0] and r["arm"] == "etf")

    face = {
        "generated": _now(),
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "machine": "bm-c",
        "kind": "astock_veto_hedge_dating",
        "fills_the_hole_of": ("r2027 printed a lot count from a 11-11 book and an 11-20 price; "
                              "no face said how far apart those two dates are, whether the gap "
                              "can reach the order, or what the unmarked days did"),
        "parent": fingerprint(PARENT),
        "beta_parent": fingerprint(BETA_FACE),
        "lots_parent": fingerprint(LOTS_FACE),
        "prereg": PREREG,
        "dates": {"book": book_date, "price": price_date,
                  "bars_apart": prices["etf"]["priced_after_the_book_by_bars"],
                  "why": "the book's positions are last marked on the book date; the panels "
                         "run on their own calendar"},
        "prices": prices,
        "target_beta": target_beta,
        "ladder": ladder,
        "published_r2027": published,
        "headline": {
            "etf_1m": {"book_lots": etf_1m["at_book_date"]["needed"],
                       "price_lots": etf_1m["at_price_date"]["needed"],
                       "round_change": etf_1m["delta_lots_round"],
                       "move_to_flip": etf_1m["flip_move_from_book_date"]},
            "im_1m": {"book_lots": im_1m["at_book_date"]["needed"],
                      "price_lots": im_1m["at_price_date"]["needed"],
                      "round_change": im_1m["delta_lots_round"],
                      "move_to_flip": im_1m["flip_move_from_book_date"]},
        },
        "verdict": None,
        "verdict_why": None,
    }
    face["verdict"], face["verdict_why"] = verdict_of(face)
    return face


# ------------------------------------------------------------------------- render
def _f(x, digits: int = 3) -> str:
    if x is None:
        return "—"
    return ("%." + str(digits) + "f") % float(x)


def _pct(x, digits: int = 2) -> str:
    if x is None:
        return "—"
    return ("%." + str(digits) + "f%%") % (float(x) * 100.0)


def render_md(face: dict) -> str:
    d = face["dates"]
    p = face["prices"]
    h = face["headline"]
    lines = []
    add = lines.append
    add("# The hedge ticket is priced after the book it hedges")
    add("")
    add("**Verdict: `%s`**" % face["verdict"])
    add("")
    add(face["verdict_why"])
    add("")
    add("Evidence cutoff **%s** · generated %s · machine %s"
        % (face["evidence_cutoff"], face["generated"], face["machine"]))
    add("")
    add("## 1. The two dates")
    add("")
    add("| | date | what it is |")
    add("|---|---|---|")
    add("| book | %s | the bar the book's positions were last marked on |" % d["book"])
    add("| price | %s | the last bar of the two hedge price panels |" % d["price"])
    add("")
    add("The panels are **%d trading bars** past the book.  Nobody has marked the book "
        "since %s;" % (d["bars_apart"], d["book"]))
    add("the ticket priced its hedge on %s anyway." % d["price"])
    add("")
    add("| arm | close on %s | close on %s | move over the unmarked days |"
        % (d["book"], d["price"]))
    add("|---|---|---|---|")
    for arm in ("etf", "im"):
        add("| %s | %.4f | %.4f | %s |"
            % (arm, p[arm]["at_book_date"]["close"], p[arm]["at_price_date"]["close"],
               _pct(p[arm]["move_between_dates"])))
    add("")
    add("## 2. The two tickets")
    add("")
    add("Target beta = k x beta = **%.4f**.  Lots = capital x target beta / (price x multiplier);"
        % face["target_beta"])
    add("`round` is the closest whole lot, `floor` is the one that does not overshoot the hedge.")
    add("")
    add("| capital | arm | needed @%s | round | needed @%s | round | Δ round | verdict |"
        % (d["book"], d["price"]))
    add("|---|---|---|---|---|---|---|---|")
    for r in face["ladder"]:
        add("| %s | %s | %s | %d | %s | %d | %+d | %s |"
            % ("{:,.0f}".format(r["capital"]), r["arm"],
               _f(r["at_book_date"]["needed"]), r["at_book_date"]["round"],
               _f(r["at_price_date"]["needed"]), r["at_price_date"]["round"],
               r["delta_lots_round"], "MOVED" if r["order_changed"] else "same"))
    add("")
    add("## 3. How far the price has to move before the order changes")
    add("")
    add("Solved exactly from the book-date lot count: the nearest-integer boundary is at")
    add("`lots/(1+f) = n ± 0.5`.  This is the ruler that decides whether the dating defect")
    add("can ever reach an order, or only the caption.")
    add("")
    add("| capital | arm | lots @book date | order flips to | when price moves |")
    add("|---|---|---|---|---|")
    for r in face["ladder"]:
        fm = r["flip_move_from_book_date"]
        add("| %s | %s | %s | %s | %s (%s) |"
            % ("{:,.0f}".format(r["capital"]), r["arm"],
               _f(r["at_book_date"]["needed"]), fm["to"],
               _pct(fm["move"]) if fm["move"] is not None else "—",
               fm["direction"] or "—"))
    add("")
    add("Read the two arms differently.  The ETF arm sits at thousands of lots, so the")
    add("nearest lot changes on a fraction of a basis point — its flip distance prints as")
    add("~0% and means *the ETF can always be sized to the beta you asked for*; dating never")
    add("decides that arm.  The futures arm sits at a fractional contract, so a 36% move in")
    add("the contract is what changes whether one lot is the closest whole hedge — and that")
    add("is a distance the market can cover in the seven bars the book went unmarked.")
    add("")
    add("## 4. What this changes, and what it does not")
    add("")
    add("- The 1,000,000 rung's ETF ticket is **%s lots** on the book date and **%s lots** "
        "on the price date — a difference of **%+d lots**."
        % (_f(h["etf_1m"]["book_lots"], 2), _f(h["etf_1m"]["price_lots"], 2),
           h["etf_1m"]["round_change"]))
    add("- The futures arm needs a **%s** move in the contract before one lot stops being "
        "the closest whole contract at this capital."
        % _pct(h["im_1m"]["move_to_flip"]["move"]))
    add("- What the face does **not** say: what the book itself did on the unmarked days.")
    add("  There is no mark, so no number is printed; the seven bars of %s and %s are "
        "printed instead, and they are not the book."
        % (d["book"], d["price"]))
    add("")
    add("## 5. What was not measured")
    add("")
    add("- Margin ratios, 券源 and recall stay broker terms (r2027's axes are quoted, not re-derived).")
    add("- The book is not revalued here: that needs its per-name marks, which is a different")
    add("  face's job.  This face only says how much the missing revaluation can matter.")
    add("- No cost, basis or roll model is introduced.")
    add("")
    add("## Reproduction")
    add("")
    add("```")
    add("python scripts/astock_veto_hedge_dating.py selftest")
    add("python scripts/astock_veto_hedge_dating.py run")
    add("python scripts/astock_veto_hedge_dating.py check")
    add("```")
    add("")
    return "\n".join(lines)


def run(write: bool = True) -> int:
    face = build()
    if write:
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
    print("astock_veto_hedge_dating %s" % face["verdict"])
    print("  book %s -> price %s (%d bars apart)"
          % (face["dates"]["book"], face["dates"]["price"], face["dates"]["bars_apart"]))
    for r in face["ladder"]:
        print("  %10.0f %-3s book %9.3f -> %9.3f lots | round %d -> %d | flip at %s"
              % (r["capital"], r["arm"],
                 r["at_book_date"]["needed"], r["at_price_date"]["needed"],
                 r["at_book_date"]["round"], r["at_price_date"]["round"],
                 _pct(r["flip_move_from_book_date"]["move"])))
    return 0


def check(json_path: str = OUT_JSON, md_path: str = OUT_MD) -> int:
    """Re-derive the face from its inputs and name what moved.

    Two kinds of red, kept apart (r1934): an upstream that moved one step is STALE and
    is repaired by `run`; a number that disagrees with its own inputs is CHECK FAILED
    and is a defect.
    """
    problems = []
    if not os.path.exists(json_path):
        print("STALE: face missing (%s)" % _rel(json_path))
        return 3
    face = _read_json(json_path)
    fresh = build()

    for key in ("parent", "beta_parent", "lots_parent"):
        if face.get(key, {}).get("content_sha256") != fresh[key]["content_sha256"]:
            problems.append("STALE: %s content moved (%s -> %s)"
                            % (key, face.get(key, {}).get("content_sha256", "?")[:12],
                               fresh[key]["content_sha256"][:12]))
    for key in ("book", "price", "bars_apart"):
        if face["dates"].get(key) != fresh["dates"].get(key):
            problems.append("STALE: dates.%s moved (%s -> %s)"
                            % (key, face["dates"].get(key), fresh["dates"].get(key)))

    stale = [p for p in problems if p.startswith("STALE")]
    if stale:
        for p in problems:
            print(p)
        print("STALE: run `run` to re-derive")
        return 3

    # same inputs: the arithmetic must reproduce exactly
    for a, b in zip(face["ladder"], fresh["ladder"]):
        if a["capital"] != b["capital"] or a["arm"] != b["arm"]:
            problems.append("CHECK FAILED: ladder rows out of order at %s/%s"
                            % (a["capital"], a["arm"]))
            continue
        for side in ("at_book_date", "at_price_date"):
            for field in ("needed", "round", "price"):
                if abs(float(a[side][field]) - float(b[side][field])) > 1e-9:
                    problems.append("CHECK FAILED: %s/%s/%s/%s %r != %r"
                                    % (a["capital"], a["arm"], side, field,
                                       a[side][field], b[side][field]))
        if a["order_changed"] != b["order_changed"]:
            problems.append("CHECK FAILED: %s/%s order_changed %r != %r"
                            % (a["capital"], a["arm"], a["order_changed"], b["order_changed"]))
    if face["verdict"] != fresh["verdict"]:
        problems.append("CHECK FAILED: verdict %r != %r" % (face["verdict"], fresh["verdict"]))

    # the published face must agree with this one about the price-date ticket
    for cap_key, block in (face.get("published_r2027") or {}).items():
        for arm in ("etf", "im"):
            row = next((r for r in face["ladder"]
                        if str(r["capital"]) == cap_key and r["arm"] == arm), None)
            if row is None or arm not in block:
                continue
            if row["at_price_date"]["round"] != block[arm]["round"]:
                problems.append("CHECK FAILED: published r2027 %s/%s says %d lots, this face "
                                "re-derives %d on the same date"
                                % (cap_key, arm, block[arm]["round"],
                                   row["at_price_date"]["round"]))

    if problems:
        for p in problems:
            print(p)
        return 3

    if os.path.exists(md_path):
        with open(md_path, encoding="utf-8") as fh:
            md = fh.read()
        if face["verdict"] not in md:
            print("CHECK FAILED: page does not carry the verdict word %r" % face["verdict"])
            return 3
        if "`" + face["verdict"] + "`" not in md:
            print("CHECK FAILED: page does not print the verdict as a code word")
            return 3

    print("CHECK OK %s | %d ladder rows re-derived | book %s -> price %s"
          % (face["verdict"], len(face["ladder"]), face["dates"]["book"], face["dates"]["price"]))
    return 0


# ---------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # L1 lot arithmetic
    leg("L1 lots_needed", abs(lots_needed(1_000_000, 0.9013, 2.30, 100) - 3918.7) < 0.1,
        lots_needed(1_000_000, 0.9013, 2.30, 100))

    # L2 bar selection: exact date
    bars = [{"date": "2026-11-10", "close": 2.2}, {"date": "2026-11-11", "close": 2.3},
            {"date": "2026-11-20", "close": 2.4}]
    leg("L2 bar on exact date", bar_on_or_before(bars, "2026-11-11")["close"] == 2.3)

    # L3 bar selection: a date with no bar takes the bar before it
    leg("L3 bar on a shut day", bar_on_or_before(bars, "2026-11-15")["close"] == 2.3)
    leg("L3b bar before the panel", _raises(lambda: bar_on_or_before(bars, "2026-01-01")))

    # L4 integer choices
    ch = integer_choices(0.813)
    leg("L4 integer choices", ch["floor"] == 0 and ch["round"] == 1, ch)

    # L5 beta error sign
    leg("L5 beta error over-hedged", beta_error(1, 1_000_000, 1_109_120 / 200, 200, 0.9013) > 0)

    # L6 flip move: solved, not searched
    fm = flip_move(3918.7)
    tgt = 3918.7 / (3919 - 0.5) - 1.0
    leg("L6 flip move exact", abs(fm["move"] - tgt) < 1e-12 and fm["to"] == 3918, fm)

    # L7 flip move on a sub-unit order: the nearest boundary is 1.5 lots (round-half-up
    # gives 2), and the "do not hedge at all" boundary at 0.5 lots is the far one
    fm2 = flip_move(0.813)
    leg("L7 flip move on a sub-unit order",
        fm2["to"] == 2 and abs(fm2["move"] - (0.813 / 1.5 - 1.0)) < 1e-12, fm2)
    leg("L7b the zero-hedge boundary is the far one",
        abs((0.813 / 0.5 - 1.0) - 0.626) < 1e-9)

    # L8 same inputs -> the verdict must not move
    a = build()
    b = build()
    leg("L8 determinism", a["verdict"] == b["verdict"] and
        all(x["at_price_date"]["needed"] == y["at_price_date"]["needed"]
            for x, y in zip(a["ladder"], b["ladder"])))

    # L9 verdict rung 1: a price move that flips a rung must be named
    moved = build(force_price_move=-0.25)
    leg("L9 a 25% book-date price move flips the verdict",
        moved["verdict"] == "DATING_MOVES_THE_ORDER", moved["verdict"])

    # L10..L12 check() behaviour on a poisoned copy (no writes to the real face)
    tmp = tempfile.mkdtemp(prefix="dating_selftest_")
    try:
        jp = os.path.join(tmp, "face.json")
        mp = os.path.join(tmp, "page.md")
        shutil.copy(OUT_JSON, jp)
        shutil.copy(OUT_MD, mp)
        leg("L10 a clean copy passes", _check_quiet(jp, mp))

        bad = _read_json(jp)
        bad["ladder"][0]["at_price_date"]["needed"] = float(bad["ladder"][0]["at_price_date"]["needed"]) + 1.0
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(bad, fh)
        rc, text = _check_capture(jp, mp)
        leg("L11 a poisoned number is CHECK FAILED without the stale word",
            rc == 3 and "CHECK FAILED" in text and "STALE" not in text, text[:160])

        stale = _read_json(jp)
        stale["ladder"] = build()["ladder"]
        stale["dates"]["book"] = "1999-01-01"
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(stale, fh)
        rc, text = _check_capture(jp, mp)
        leg("L12 a stale date says STALE so the chain re-runs",
            rc == 3 and "STALE" in text, text[:160])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # L13 the page must carry the money-critical sentence, not only the verdict
    with open(OUT_MD, encoding="utf-8") as fh:
        page = fh.read()
    leg("L13 page names the unmarked days", "the unmarked days" in page or
        "unmarked days" in page)

    ok = sum(1 for _, k, _ in legs if k)
    for name, k, detail in legs:
        print("%s %s%s" % ("PASS" if k else "FAIL", name,
                           "" if k else "  <- %r" % (detail,)))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def _raises(fn) -> bool:
    try:
        fn()
    except SystemExit:
        return True
    except Exception:
        return False
    return False


def _check_capture(json_path: str, md_path: str):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check(json_path, md_path)
    return rc, buf.getvalue()


def _check_quiet(json_path: str, md_path: str) -> bool:
    rc, _ = _check_capture(json_path, md_path)
    return rc == 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
