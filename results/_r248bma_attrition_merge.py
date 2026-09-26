# -*- coding: utf-8 -*-
"""R248 bm-a: gate_attrition dual-list consumer-chain repair (zero-loss merge).

Defect (live since 09-25 15:06): three producers (ce_admission_intake /
div_lowvol_backtest / cn_rev_tilt_p1) appended attrition rows to a
misnamed "history" list, while every canonical consumer reads "entries"
(bandit_queue UCB1, monthly_briefing C4, science_audit C4) -> 3 batch rows
silently invisible (r239 consumer-chain family: record persisted where the
consumer face does not read).

Repair (mechanical, zero judgment change):
  1. copy the 3 history-only rows into "entries" at ts-ascending positions
     (producer write-order law: entries is ts-ascending append);
  2. leave "history" untouched (append-only zero-loss; residue documented);
  3. producers root-fixed in the same round (att["history"] -> att["entries"]).

Exit 0 = merged (or already merged, idempotent). Exit 2 = shape red, no write.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTR = os.path.join(ROOT, "results", "gate_attrition.json")


def main() -> int:
    d = json.load(io.open(ATTR, encoding="utf-8"))
    entries, history = d.get("entries"), d.get("history")
    if not isinstance(entries, list) or not isinstance(history, list):
        print("FAIL: entries/history not lists")
        return 2

    eb = {e.get("batch") for e in entries}
    orphans = [h for h in history if h.get("batch") not in eb]
    if not orphans:
        print(json.dumps({"merge": "already-clean", "entries_n": len(entries)}, ensure_ascii=False))
        return 0

    for row in orphans:
        ts = str(row.get("ts", ""))
        pos = len(entries)
        for i, e in enumerate(entries):
            if str(e.get("ts", "")) > ts:
                pos = i
                break
        entries.insert(pos, row)

    ts_list = [str(e.get("ts", "")) for e in entries]
    if ts_list != sorted(ts_list):
        print("FAIL: entries not ts-ascending after merge -- aborting write")
        return 2

    with io.open(ATTR, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print(json.dumps({
        "merge": "done",
        "merged_batches": [r.get("batch") for r in orphans],
        "entries_n": len(entries),
        "history_left_untouched_n": len(history),
        "note": "history kept as zero-loss residue; consumers read entries",
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
