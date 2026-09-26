# r231d (bm-b round 231): P1E-SYNTH pool shard flip ready->done after harvest
# (pool-flip-is-round-work r203; landed 07:47:20, flip before next autofill tick
# per r224 law). Entry status ready->done same as P1E-NULLS family precedent.
import json

PATH = "results/runnable_pool.json"
raw = open(PATH, encoding="utf-8-sig").read()
pool = json.loads(raw)

entries = pool if isinstance(pool, list) else None
if entries is None:
    # dict-of-entries form: find the P1E-SYNTH entry anywhere in the structure
    def find_entries(obj):
        if isinstance(obj, list):
            for x in obj:
                if isinstance(x, dict) and x.get("id") == "P1E-SYNTH":
                    return obj
                r = find_entries(x)
                if r is not None:
                    return r
        elif isinstance(obj, dict):
            for v in obj.values():
                r = find_entries(v)
                if r is not None:
                    return r
        return None
    entries = find_entries(pool)
assert entries is not None, "P1E-SYNTH entry not found"

e = next(x for x in entries if x.get("id") == "P1E-SYNTH")
sh = e["shards"][0]
assert sh["key"] == "p1e-synth-0of1", sh["key"]
assert sh["status"] == "ready", f"shard not ready: {sh['status']}"
sh["status"] = "done"
sh["done_flip"] = {
    "ts": "2026-09-26 07:59",
    "by": "bm-b r231",
    "evidence": (
        "artifact p1e_synth_parts.json landed 07:47:20 (runner pid17616 "
        "launched 07:04:04 via autofill tick claim, elapsed 2586.9s, 179 IC "
        "passes, single-proc); harvest-round finalize exit 0: verdict FAIL "
        "V1 (primary IS IC 0.0700 < thr 0.0762 = max(0.02, nullA_p95 "
        "0.0762, nullB_p95 0.0019), rank 5/21), V2 0.552 / V3 116.6% / A3 "
        "8011 all pass = V1 single-point death (shelf effect, prereg sec.5 "
        "pred-7 hit); ledger 184754->184826 (+72, prev_total = canonical "
        "ledger_head after r231 chain-fork fix, narrow _chain_head_total "
        "183292 missed nested dirs); gate_attrition row auto-booked by "
        "finalize (kind=measurement delta=72); prereg sec.7 backfilled + "
        "STRATEGY_LIBRARY Zoo row FAIL disposition same commit; "
        "p1e_synth.json + p1e_synth_results.csv saved"),
}
e["status"] = "done"

body = json.dumps(pool, ensure_ascii=False, indent=1)
bom = raw.startswith("\ufeff")
with open(PATH, "w", encoding="utf-8-sig" if bom else "utf-8",
          newline="\r\n" if "\r\n" in raw else "\n") as fh:
    fh.write(body + "\n")
# parse-verify (r185)
json.loads(open(PATH, encoding="utf-8-sig").read())
print("flipped: P1E-SYNTH entry+shard -> done; bom_kept:", bom)
