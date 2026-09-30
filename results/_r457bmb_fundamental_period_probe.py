"""_r457bmb_fundamental_period_probe.py -- falsification probe for the
update_fundamental rc=2 boundary bug first live-fired 2026-09-30 10:45.

Question: is ak.stock_yjbb_em(20260930)'s TypeError ('NoneType' object is
not subscriptable) the source's not-published-yet answer (deterministic,
period-specific) or a transport failure (endpoint-wide)?

Discriminator: same endpoint, same call shape, three periods --
  A. 20260930  (quarter ends TODAY, zero Q3 disclosures -> expect null result raise)
  B. 20260630  (fully published interim  -> expect >= MIN_ROWS rows)
  C. 20251231  (fully published annual   -> expect >= MIN_ROWS rows)

If B and C succeed while A raises the NoneType-subscript TypeError, the
exception is period-specific payload-null semantics, not transport.
Facts -> results/_r457bmb_fundamental_period_probe.json (r464 anchor law:
probe records live-fire facts the fix decision cites).
"""
import json
import time
import traceback

import akshare as ak

MIN_ROWS = 4000  # mirror scripts/update_fundamental.py MIN_ROWS
FACTS_PATH = "results/_r457bmb_fundamental_period_probe.json"


def try_period(period):
    t0 = time.time()
    try:
        df = ak.stock_yjbb_em(date=period)
        rows = 0 if df is None else len(df)
        return {"period": period, "ok": True, "rows": rows,
                "elapsed_s": round(time.time() - t0, 1),
                "error": None}
    except Exception as e:  # noqa: BLE001 -- the probe's subject
        return {"period": period, "ok": False, "rows": None,
                "elapsed_s": round(time.time() - t0, 1),
                "error_type": type(e).__name__, "error": str(e)[:200]}


def main():
    facts = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
             "akshare_version": ak.__version__,
             "machine": "bm-b", "round": 457,
             "question": "20260930 TypeError = unpublished-null vs transport?",
             "arms": []}
    for p in ("20260930", "20260630", "20251231"):
        r = try_period(p)
        facts["arms"].append(r)
        print(json.dumps(r, ensure_ascii=False))
    a, b, c = facts["arms"]
    verdict = {
        "A_unpublished_raise": (not a["ok"]) and a.get("error_type") == "TypeError"
        and "'NoneType' object is not subscriptable" in a["error"],
        "B_published_ok": b["ok"] and b["rows"] >= MIN_ROWS,
        "C_published_ok": c["ok"] and c["rows"] >= MIN_ROWS,
    }
    facts["verdict"] = verdict
    facts["conclusion"] = ("period-specific unpublished-null signal, transport "
                           "healthy" if all(verdict.values())
                           else "NOT period-specific -- do not patch, report")
    facts["conclusion_all_pass"] = all(verdict.values())
    with open(FACTS_PATH, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=2, ensure_ascii=False)
    print("ALL_PASS:", facts["conclusion_all_pass"])
    print("facts ->", FACTS_PATH)
    # keep the raising arm's traceback visible for the log
    if not all(verdict.values()):
        traceback.print_exc()


if __name__ == "__main__":
    main()
