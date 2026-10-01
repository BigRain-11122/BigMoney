# r524 bm-a: W12 shard provenance check (double-freeze collision window --
# bm-b engine burned some W12 shards same-window per pool_core_samples).
# Read-only: audit.machine provenance of all 12 origin W12 shard products.
import subprocess
import json

for i in list(range(11, -1, -1)):
    raw = subprocess.check_output(
        ["git", "show",
         f"origin/main:results/p2cal_ext/n1_w12/shard-{i}-of-12.json"])
    d = json.loads(raw)
    a = d.get("audit") or {}
    fams = d.get("families") or {}
    a_runs = (fams.get("A_random_engine_exit") or {}).get("runs") or []
    b_runs = (fams.get("B_random_entry_random_exit") or {}).get("runs") or []
    print(f"shard-{i}: machine={a.get('machine')} workers={a.get('workers')} "
          f"elapsed={a.get('elapsed_sec')} A={len(a_runs)} B={len(b_runs)} "
          f"n_bt={a.get('n_backtests')} cutoff={d.get('evidence_cutoff')} "
          f"prereg={d.get('preregistered_doc')}")
