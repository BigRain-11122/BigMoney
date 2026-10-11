"""r875 bm-c diagnostic: why autofill _pick refuses E16-ALPHAGEN-RG ready shards."""
import json, sys
sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools")
import autofill as af

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
pool = json.load(open(ROOT + r"\results\runnable_pool.json", encoding="utf-8"))
myid = "bm-c"

buf = []
orig_log = af._log
af._log = lambda m: buf.append(m)

e_ids = [e["id"] for e in pool["entries"] if "E16" in e.get("id", "")]
print("E16 entries in pool:", e_ids)
for eid in e_ids:
    e = next(x for x in pool["entries"] if x["id"] == eid)
    print("=" * 60)
    print(f"entry {eid}: status={e.get('status')} runner={bool(e.get('runner'))} "
          f"lane_owner={e.get('lane_owner')!r} priority={e.get('priority')} "
          f"workers_plan={e.get('workers_plan')!r}")
    gr = af._host_gate_reason(e)
    print(f"  host_gate_reason: {gr}")
    lo = e.get("lane_owner")
    if lo not in (None, "", "ANY", myid):
        print(f"  -> LANE OWNER MISMATCH {lo}")
    if not e.get("workers_plan"):
        print("  -> NO workers_plan (O-2130 law)")
    if af._runner_alive(e.get("runner", "")):
        print("  -> runner alive (no double-run)")
    for sh in e.get("shards", []):
        sd = af._strand_defer_age_min(eid, sh.get("key"))
        xc = af._ext_claim_age_min(eid, sh.get("key"))
        ow = sh.get("owner")
        print(f"  shard {sh.get('key')}: status={sh.get('status')} owner={ow!r} "
              f"strand_defer={sd} ext_claim_age={xc}")
af._log = orig_log
print("=" * 60)
e, sh = af._pick(pool, myid)
print("pick result entry:", e.get("id") if e else None, "shard:", sh.get("key") if sh else None)
print("log lines during pick:")
for m in buf[-25:]:
    print(" ", m)
