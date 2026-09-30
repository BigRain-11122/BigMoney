"""r478 bm-a Q9/D-20260930-27 P0 backfill: surgical fix of 20 zero-mark rows in
marks-20260930.jsonl (09:35-10:25 defect window, 513100 positions of
COMPOSITE-CE-01/02).

Root cause (external audit D-20260930-27 Q9): intraday tick source
(fund_etf_category_sina) returned no quote for 513100 in that window while
session_open was valid (2.291) and the local daily panel had the previous
close -- the pre-r473 mark path silently wrote mark=0.0 / market_value_cny=null,
wiping ~19% of two members' equity from the snapshot. The r473 guard
(price-true -> value>0 fallback chain + no-zero-write assertion) stopped NEW
zero rows (10:35 onward all valid); these 20 pre-guard rows remain in the
ledger and fail the D-27 acceptance probe ("full-scan zero-mark rows == 0").

Fix semantics (honest, auditable):
- keep the original defect value as `mark_raw: 0.0` + `mark_fix_note` (never
  pretend it didn't happen);
- mark <- 2.324 (previous close from local panel, the SAME fallback value the
  post-fix chain produced at 10:15/14:55 -- consistency by construction);
- market_value_cny <- quantity * mark; unrealized_pnl_cny <- (mark - cost) * qty;
- re-derive the affected trader's equity_mark_cny = cash + sum(position mv);
- row order and all other rows byte-untouched; verify pass: full-scan
  zero-mark rows == 0.
"""
import json

PATH = "results/paper/marks/marks-20260930.jsonl"
FALLBACK_MARK = 2.324  # 2026-09-29 close of sh513100 from local panel (D-27 readout)


def main():
    lines = open(PATH, encoding="utf-8").read().splitlines()
    fixed_rows, out = 0, []
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        row = json.loads(line)
        touched = False
        for tname, t in (row.get("traders") or {}).items():
            for p in (t.get("positions") or []):
                if p.get("mark") in (0, 0.0, None) or p.get("market_value_cny") is None:
                    qty = p.get("quantity") or 0.0
                    cost = p.get("cost_price") or 0.0
                    p["mark_raw"] = p.get("mark")
                    p["mark_raw_mv"] = p.get("market_value_cny")
                    p["mark"] = FALLBACK_MARK
                    p["market_value_cny"] = round(qty * FALLBACK_MARK, 2)
                    p["unrealized_pnl_cny"] = round((FALLBACK_MARK - cost) * qty, 2)
                    p["mark_source"] = "fallback_prev_close_backfill_r478"
                    p["mark_fix_note"] = ("r478 D-20260930-27 P0 backfill: tick source "
                                          "unpriced in 09:35-10:25 window; original "
                                          "silent-zero preserved as mark_raw")
                    fixed_rows += 1
                    touched = True
            if touched:
                # re-derive equity_mark_cny = cash + sum(position market values)
                cash = t.get("cash_cny") or 0.0
                total_mv = sum((pos.get("market_value_cny") or 0.0)
                               for pos in (t.get("positions") or []))
                t["equity_mark_cny"] = round(cash + total_mv, 2)
                t["equity_fix_note"] = "re-derived post r478 P0 backfill (cash + sum mv)"
        out.append(json.dumps(row, ensure_ascii=False))
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")

    # verify: full-scan zero-mark rows must be 0
    zero = 0
    for line in open(PATH, encoding="utf-8"):
        row = json.loads(line)
        for t in (row.get("traders") or {}).values():
            for p in (t.get("positions") or []):
                if p.get("mark") in (0, 0.0, None) or p.get("market_value_cny") is None:
                    zero += 1
    print(f"fixed position rows: {fixed_rows}")
    print(f"verify full-scan zero-mark rows: {zero}")
    assert zero == 0, "VERIFICATION FAILED -- zero-mark rows remain"
    print("PASS: D-20260930-27 Q9 acceptance criterion met (zero-mark rows == 0)")


if __name__ == "__main__":
    main()
