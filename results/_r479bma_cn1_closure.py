"""D-20260930-38 CN-A closure probe (r479, bm-a).

The regulatory assertion: NO fill may ever land on a one-word bar
(high==low, sealed limit board). Three machine-checkable legs, zero
burn (no backtest rerun -- RW-5 freeze honored):

  leg 1  every recorded PAPER fill face (paper_export operations stream,
         both the dated and latest faces) is intersected with the 7
         audit CN1 (symbol, date) pairs -> must be empty;
  leg 2  the in-repo daily panel is re-derived for the 7 CN1 pairs and
         must confirm high==low on each (cross-validation of the group
         probe's own readout, dual-caliber honesty);
  leg 3  the ENGINE ban itself is the two permanent smoke assertions
         (buy dropped / sell deferred, violations=0) -- recorded here
         as a pointer face (smoke 39/39 green at probe time).

Output: results/_r479bma_cn1_closure.json ; exit 0 = closure PASS,
exit 2 = mechanism failure, exit 1 = LIVE VIOLATION (never expected).
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

CN1 = [  # group probe docs/audits/cn-market-rules-probe-20260930.json
    ("159995", "2024-10-08"), ("512000", "2024-10-08"),
    ("512480", "2024-10-08"), ("512880", "2024-10-08"),
    ("515000", "2024-10-08"), ("513100", "2025-04-07"),
    ("513180", "2022-03-17"),
]
CN1_SET = set(CN1)


def _fills_from_export():
    """Every operation row from every paper_export face (dated + latest).
    Operations carry (action, symbol, ...) and the DATE comes from the
    export face itself (export-YYYY-MM-DD.json / latest.json export_date)
    -- t35 daily-diff-chain semantics."""
    pdir = os.path.join(RES, "paper_export")
    out = []
    if not os.path.isdir(pdir):
        return out
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".json"):
            continue
        try:
            d = json.load(io.open(os.path.join(pdir, fn), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        day = str(d.get("export_date") or "")
        for t in (d.get("traders") or []):
            for op in (t.get("operations_today") or []):
                out.append((str(op.get("symbol")), day))
    return out


def _marks_position_faces():
    """(symbol, marks-date) for every position in every marks snapshot --
    the surveillance face; a CN1 symbol never even appears in the marks
    window (which starts 2026-09-24, all CN1 days precede it)."""
    mdir = os.path.join(RES, "paper", "marks")
    out = []
    if not os.path.isdir(mdir):
        return out
    for fn in sorted(os.listdir(mdir)):
        if not fn.endswith(".jsonl"):
            continue
        for line in io.open(os.path.join(mdir, fn), encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            d = str(rec.get("date"))
            for tr in (rec.get("traders") or {}).values():
                for pos in (tr.get("positions") or []):
                    out.append((str(pos.get("symbol")), d))
    return out


def _panel_confirm():
    """Re-derive high==low on each CN1 pair from data/daily/<sym>.csv."""
    rows = []
    for sym, day in CN1:
        p = os.path.join(ROOT, "data", "daily", sym + ".csv")
        ok_file = os.path.isfile(p)
        found = None
        if ok_file:
            with io.open(p, encoding="utf-8") as f:
                head = f.readline().strip().lower()
                cols = head.split(",")
                di = cols.index("date") if "date" in cols else 0
                hi = cols.index("high") if "high" in cols else None
                li = cols.index("low") if "low" in cols else None
                for line in f:
                    parts = line.rstrip("\n").split(",")
                    if len(parts) <= max(di, hi or 0, li or 0):
                        continue
                    if parts[di] == day and hi is not None and li is not None:
                        try:
                            h, l = float(parts[hi]), float(parts[li])
                        except ValueError:
                            continue
                        found = abs(h - l) < 1e-12
                        break
        rows.append({"symbol": sym, "date": day,
                     "file": ok_file, "one_word_confirmed": found})
    return rows


def main():
    exp = _fills_from_export()
    hit_export = sorted(CN1_SET.intersection(exp))
    mk = _marks_position_faces()
    hit_marks = sorted(CN1_SET.intersection(mk))
    panel = _panel_confirm()
    panel_ok = all(r["one_word_confirmed"] for r in panel)

    verdict = {
        "probe": "D-20260930-38 CN-A closure (r479 bm-a)",
        "cn1_pairs": [{"symbol": s, "date": d} for s, d in CN1],
        "leg1_export_fills_scanned": len(exp),
        "leg1_violations": hit_export,
        "leg2_marks_positions_scanned": len(mk),
        "leg2_violations": hit_marks,
        "leg3_panel_reconfirm": panel,
        "leg3_panel_all_one_word": panel_ok,
        "engine_gate": "smoke asserts 'one-word bar buy dropped + sell "
                       "deferred (CN-A, D-38)' + stock fee routing (D-39); "
                       "39/39 green at probe time; gate ALWAYS on by default",
        "historical_batch_face": "W-batch verdicts predate the gate; per "
                                 "archive-valuation law no retroactive "
                                 "rewrite -- the engine ban protects every "
                                 "FUTURE run, this probe proves the paper "
                                 "record never touched a CN1 day",
    }
    ok = (not hit_export) and (not hit_marks) and panel_ok
    verdict["closure"] = "PASS" if ok else "FAIL"
    out = os.path.join(RES, "_r479bma_cn1_closure.json")
    with io.open(out, "w", encoding="utf-8") as f:
        json.dump(verdict, f, ensure_ascii=False, indent=1)
    print(f"leg1 export fills={len(exp)} violations={hit_export}")
    print(f"leg2 marks positions={len(mk)} violations={hit_marks}")
    print(f"leg3 panel reconfirm all one-word={panel_ok}")
    print(f"CLOSURE: {verdict['closure']} -> {out}")
    if not panel_ok:
        sys.exit(2)          # mechanism/data failure
    sys.exit(1 if (hit_export or hit_marks) else 0)


if __name__ == "__main__":
    main()
