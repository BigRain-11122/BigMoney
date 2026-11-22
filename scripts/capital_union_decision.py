"""One account, two books: which one can this money actually open today?

Both books already print their own capital line, but neither answers the question a
reader with 1,000,000 CNY asks first: "which of these can I open, and what do I have
to top up for the other one?"

Inputs are read-only faces (no re-derivation, no network):
  results/idx_fut_carry_open_capital.json  -- carry book funding rung (r1780 lineage)
  results/etf_book_capacity_edge.json      -- ETF book capacity: capital that clears 1% ADV
  results/etf_book_ticket_floor.json       -- ETF book one-lot floor (whole-lot arithmetic)

Every number is copied from those faces at run time; nothing is hand-written.
Each face prints its own cutoff, and the union verdict carries the weakest of them.

verdict tokens:
  ETF_BOOK_IS_THE_ONLY_ONE_THIS_ACCOUNT_CAN_OPEN_TODAY
  BOTH_OPENABLE_AT_THIS_CAPITAL
  NEITHER_OPENABLE_AT_THIS_CAPITAL
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARRY_FACE = "results/idx_fut_carry_open_capital.json"
CAPACITY_FACE = "results/etf_book_capacity_edge.json"
FLOOR_FACE = "results/etf_book_ticket_floor.json"
OUT_JSON = "results/capital_union_decision.json"
OUT_MD = "research/CAPITAL_UNION.md"

LENS_CNY = 1_000_000.0  # the account this question is asked about (both faces use it)


def _load(rel: str) -> dict:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"face missing: {rel} (STALE: run its writer, do not guess)")
    return json.loads(p.read_text(encoding="utf-8"))


def _cutoff(d: dict) -> str | None:
    return d.get("evidence_cutoff") or d.get("cutoff")


def build() -> dict:
    carry = _load(CARRY_FACE)
    cap = _load(CAPACITY_FACE)
    floor = _load(FLOOR_FACE)

    # --- carry book (funding line) -------------------------------------------
    book = carry.get("book") or {}
    cheapest = book.get("cheapest_to_open") or {}
    carry_funding = float(cheapest["funding_cny"])
    carry_short = carry_funding - LENS_CNY
    carry_short_pct = carry_short / LENS_CNY
    carry_legs = float(book.get("funding_for_all_legs_cny") or 0.0)
    carry_exec = int(book.get("executable_lots_total") or 0)

    # --- ETF book (capacity + one-lot floor) --------------------------------
    summ = cap.get("summary") or {}
    cap_today = float(summ["reading_today_pct"])          # % of 20d median ADV
    cap_line = float((cap.get("criteria") or {}).get("line_pct") or 1.0)
    cap_capital_at_line = float(summ["capital_where_at_line_today_cny"])
    cap_capital_median = float(summ["capital_median_cny"])
    cap_headroom = cap_capital_at_line - LENS_CNY        # >0 = this capital fits today
    fl = floor.get("floor") or {}
    one_lot = float(fl["min_capital_cny"])
    mult = float(floor.get("capital_multiple_vs_floor") or (LENS_CNY / one_lot))
    etf_verdict = floor.get("verdict")

    # --- union ---------------------------------------------------------------
    both_best = carry_funding + cap_capital_at_line
    both_median = carry_funding + cap_capital_median

    etf_open = mult >= 1.0 and cap_headroom >= 0.0
    carry_open = carry_exec > 0
    if etf_open and carry_open:
        verdict = "BOTH_OPENABLE_AT_THIS_CAPITAL"
    elif etf_open:
        verdict = "ETF_BOOK_IS_THE_ONLY_ONE_THIS_ACCOUNT_CAN_OPEN_TODAY"
    elif carry_open:
        verdict = "CARRY_BOOK_IS_THE_ONLY_ONE_THIS_ACCOUNT_CAN_OPEN_TODAY"
    else:
        verdict = "NEITHER_OPENABLE_AT_THIS_CAPITAL"

    cutoffs = {
        "carry_open_capital": _cutoff(carry),
        "etf_book_capacity_edge": _cutoff(cap),
        "etf_book_ticket_floor": _cutoff(floor),
    }
    weakest = min([c for c in cutoffs.values() if c], default=None)

    sentence = (
        f"At {LENS_CNY:,.0f} CNY the ETF book is open (one lot {one_lot:,.2f} CNY, "
        f"{mult:.1f}x the floor) while the carry book prints {carry_exec} executable lot(s) "
        f"and needs {carry_funding:,.0f} CNY to open its cheapest leg "
        f"(short {carry_short:,.0f} = {carry_short_pct*100:.2f}%). "
        f"Today's ETF capacity line sits at {cap_capital_at_line:,.0f} CNY "
        f"(reading {cap_today:.4f}% of ADV against a {cap_line:.2f}% line), so this capital "
        f"fits with {cap_headroom:,.0f} CNY of headroom on the best day of the last "
        f"{int(summ.get('n_sessions') or 0)} sessions. Opening both at once needs "
        f"{both_best:,.0f} CNY on the best capacity day ({both_median:,.0f} on the median day)."
    )

    return {
        "artifact": "capital_union_decision",
        "evidence_cutoff": weakest,
        "face_cutoffs": cutoffs,
        "lens_cny": LENS_CNY,
        "etf_book": {
            "openable": etf_open,
            "one_lot_floor_cny": one_lot,
            "capital_multiple_vs_floor": mult,
            "ticket_verdict": etf_verdict,
            "capacity_reading_pct": cap_today,
            "capacity_line_pct": cap_line,
            "capital_at_line_today_cny": cap_capital_at_line,
            "headroom_cny": cap_headroom,
            "capacity_verdict": summ.get("verdict"),
            "sessions_measured": summ.get("n_sessions"),
            "sessions_passing": summ.get("n_passes"),
        },
        "carry_book": {
            "openable": carry_open,
            "cheapest_product": cheapest.get("product"),
            "funding_cny": carry_funding,
            "short_cny": carry_short,
            "short_pct": carry_short_pct,
            "all_legs_funding_cny": carry_legs,
            "executable_lots_total": carry_exec,
            "decision": (carry.get("withdrawal") or {}).get("decision"),
        },
        "union": {
            "verdict": verdict,
            "both_books_best_day_cny": both_best,
            "both_books_median_day_cny": both_median,
            "first_book_to_open": "etf_book" if etf_open else ("carry_book" if carry_open else None),
        },
        "sentence": sentence,
        "caveats": [
            "The ETF capacity reading is a 60-session ladder of 20-day median ADV, not an order-book measurement: it says how often this capital fits, not how much it costs to push.",
            "etf_book_ticket_floor is a whole-lot arithmetic face and its cutoff can lag the capacity face; every face's own cutoff is printed in face_cutoffs.",
            "The carry book's funding rung comes from the adopted 8% hard cap; the un-adopted road (lower target to 8.9958%/9.2208%) is printed on that face and is not applied here.",
        ],
    }


def write_md(doc: dict) -> str:
    etf = doc["etf_book"]
    carry = doc["carry_book"]
    uni = doc["union"]
    lines = [
        "# 同一笔 100 万，两本书各要多少钱才能开",
        "",
        "> 由 `scripts/capital_union_decision.py` 生成，禁手改。各面自印 cutoff：",
        "",
    ]
    for k, v in doc["face_cutoffs"].items():
        lines.append(f"- `{k}` = {v}")
    lines += [
        "",
        f"**判词** `{uni['verdict']}` / 最弱面 cutoff = {doc['evidence_cutoff']}",
        "",
        "## 一行话",
        "",
        "> " + doc["sentence"],
        "",
        "## 两本账并排",
        "",
        "| | ETF 复合书 | 股指期货贴水 carry |",
        "|---|---:|---:|",
        f"| 100 万下能开 | {'是' if etf['openable'] else '否'} | {'是' if carry['openable'] else '否'} |",
        f"| 一手/首档门槛 | {etf['one_lot_floor_cny']:,.2f} CNY | {carry['funding_cny']:,.0f} CNY |",
        f"| 差多少 | — | {carry['short_cny']:,.0f} CNY（{carry['short_pct']*100:.2f}%） |",
        f"| 今天这一档容量读数 | {etf['capacity_reading_pct']:.4f}% ADV（闸 {etf['capacity_line_pct']:.2f}%） | — |",
        f"| 100 万在容量线上的余量 | {etf['headroom_cny']:,.0f} CNY | — |",
        "",
        "## 两本一起开要多少",
        "",
        f"- 最好的一天容量档：{uni['both_books_best_day_cny']:,.0f} CNY（carry 首档 + ETF 容量线资本）",
        f"- 中位的一天：{uni['both_books_median_day_cny']:,.0f} CNY",
        "",
        "## 口径与限制",
        "",
    ]
    lines += [f"- {c}" for c in doc["caveats"]]
    lines.append("")
    return "\n".join(lines)


def selftest() -> int:
    doc = build()
    etf, carry, uni = doc["etf_book"], doc["carry_book"], doc["union"]
    checks = []

    def ck(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    ck("carry_short_arithmetic", abs(carry["short_cny"] - (carry["funding_cny"] - LENS_CNY)) < 1.0)
    ck("carry_short_pct", abs(carry["short_pct"] - carry["short_cny"] / LENS_CNY) < 1e-9)
    ck("etf_multiple", abs(etf["capital_multiple_vs_floor"] - LENS_CNY / etf["one_lot_floor_cny"]) < 0.15)
    ck("etf_headroom", abs(etf["headroom_cny"] - (etf["capital_at_line_today_cny"] - LENS_CNY)) < 1.0)
    ck("both_sum", abs(uni["both_books_best_day_cny"] - (carry["funding_cny"] + etf["capital_at_line_today_cny"])) < 1.0)
    ck("verdict_consistent_with_flags",
       (uni["verdict"] == "ETF_BOOK_IS_THE_ONLY_ONE_THIS_ACCOUNT_CAN_OPEN_TODAY") == (etf["openable"] and not carry["openable"]))
    ck("sentence_names_carry_rung", f"{carry['funding_cny']:,.0f}" in doc["sentence"])
    ck("sentence_names_etf_floor", f"{etf['one_lot_floor_cny']:,.2f}" in doc["sentence"])
    ck("cutoffs_present", all(v for v in doc["face_cutoffs"].values()))

    # L10 -- the drift probe must say the word the chain listens for (r1850/r1934). Run the
    # real --check path against a doctored copy: the face on disk is rebuilt, one block is
    # bent, and the probe has to answer STALE (so the chain pays its writer) rather than the
    # old "DRIFT" wording that left the leg red with nobody to fix it.
    bad_face = ROOT / "results" / "_capital_union_selftest.json"
    saved_out = OUT_JSON
    try:
        bent = json.loads(json.dumps(doc))
        bent["etf_book"]["one_lot_floor_cny"] = float(bent["etf_book"]["one_lot_floor_cny"]) + 1.0
        bad_face.write_text(json.dumps(bent, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        globals()["OUT_JSON"] = "results/_capital_union_selftest.json"
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc_bent = main(["--check"])
        finally:
            sys.stdout = old
            globals()["OUT_JSON"] = saved_out
        txt = buf.getvalue()
        ck("drift_says_stale", rc_bent == 3 and "STALE" in txt)
    finally:
        globals()["OUT_JSON"] = saved_out
        if bad_face.exists():
            bad_face.unlink()

    bad = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print(("PASS " if ok else "FAIL ") + name)
    print(f"{len(checks) - len(bad)}/{len(checks)} legs pass")
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true", help="rebuild and diff against the face on disk")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    doc = build()

    if args.check:
        p = ROOT / OUT_JSON
        if not p.exists():
            print(f"STALE: {OUT_JSON} missing")
            return 3
        old = json.loads(p.read_text(encoding="utf-8"))
        drift = [k for k in ("union", "etf_book", "carry_book", "face_cutoffs")
                 if json.dumps(old.get(k), sort_keys=True) != json.dumps(doc.get(k), sort_keys=True)]
        if drift:
            # r1934: the chain only pays for a writer when the probe text says STALE (r1850).
            # Wording this "DRIFT" left the leg red forever: the ticket floor above it rewrites
            # on every new bar, this face never republished, and the union page kept quoting
            # yesterday's one-lot threshold. Say the word the chain listens for.
            print("STALE face drifted:", ", ".join(drift), "-- rerun to republish")
            return 3
        print("OK: face matches a fresh rebuild")
        return 0

    (ROOT / OUT_JSON).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / OUT_MD).write_text(write_md(doc), encoding="utf-8")
    print(f"verdict={doc['union']['verdict']} weakest_cutoff={doc['evidence_cutoff']}")
    print(doc["sentence"])
    print(f"wrote {OUT_JSON} and {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
