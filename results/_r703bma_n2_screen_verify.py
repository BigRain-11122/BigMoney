# r703 bm-a probe: N2-W15 screen product verification (read-only) + pool claim closure census
# Laws: r685 dup-probe rerun on adoption (read-only face), r693 adoption-probe precedent,
#       pit-95 zero-second-ledger (NEVER re-run screen-finalize; read-only verify only)
import json, os, csv, sys

R = "results/n2_w15"
ok = []
bad = []

# 1. screen.json internal consistency
s = json.load(open(os.path.join(R, "n2_w15_screen.json"), encoding="utf-8"))
tl = s.get("trials_ledger", {})
if tl.get("total") == tl.get("prev_total", 0) + tl.get("batch_trials", 0):
    ok.append(f"ledger-math {tl.get('prev_total')}+{tl.get('batch_trials')}=={tl.get('total')}")
else:
    bad.append("ledger-math MISMATCH")
if s.get("n_survivors") == len(s.get("survivors", [])):
    ok.append(f"n_survivors==len(survivors)=={s.get('n_survivors')}")
else:
    bad.append("n_survivors MISMATCH vs survivors list")
if s.get("dup_probe", {}).get("n_dup_ids") == 0 and not s.get("dup_probe", {}).get("first_dups"):
    ok.append("dup_probe n_dup_ids=0 keep-first")
else:
    bad.append(f"dup_probe nonzero: {s.get('dup_probe')}")

# 2. cells csv: survivor ids subset of csv candidate_id; distinct count check
csv_rows = list(csv.DictReader(open(os.path.join(R, "n2_w15_screen_cells.csv"), encoding="utf-8-sig")))
csv_ids = [r.get("candidate_id") for r in csv_rows]
surv_ids = set(s.get("survivors", []))
distinct = s.get("n_distinct")
if distinct is not None and distinct == len(csv_ids):
    ok.append(f"csv rows==n_distinct=={distinct}")
else:
    bad.append(f"csv rows {len(csv_ids)} != n_distinct {distinct}")
missing = surv_ids - set(csv_ids)
if not missing:
    ok.append("survivors subset of csv cells (0 missing)")
else:
    bad.append(f"{len(missing)} survivors missing from csv")

# 3. checkpoint shards census: 12/12 non-empty
ck = os.path.join(R, "checkpoint")
shard_lines = {}
for i in range(12):
    p = os.path.join(ck, f"n2_screen_shard_{i}of12.jsonl")
    if os.path.exists(p):
        n = sum(1 for _ in open(p, encoding="utf-8"))
        shard_lines[i] = n
        if n == 0:
            bad.append(f"shard-{i} EMPTY (r670 non-empty payload law)")
    else:
        bad.append(f"shard-{i} checkpoint MISSING")
tot = sum(shard_lines.values())
ok.append(f"checkpoint shards {len(shard_lines)}/12, cell-rows total {tot}")

# 4. pool claim closure census (finalize gate precondition, entry_id canon form)
claims_dir = "results/pool_claims"
NSHARDS = 12
open_shards = []
closed = 0
for i in range(NSHARDS):
    eid = f"PERPETUAL-N2-W15-SHARD-{i}"
    d = os.path.join(claims_dir, eid)
    files = [f for f in os.listdir(d) if f.endswith(".json")] if os.path.isdir(d) else []
    if files:
        closed += 1
    else:
        open_shards.append(eid)
ok.append(f"pool claims closed {closed}/12; open={open_shards[:6]}")

print("== VERIFY OK ==")
for line in ok:
    print("  OK:", line)
print("== VERIFY BAD ==")
for line in bad:
    print("  BAD:", line)
print("VERDICT:", "PASS" if not bad else "FAIL")
sys.exit(0 if not bad else 1)
