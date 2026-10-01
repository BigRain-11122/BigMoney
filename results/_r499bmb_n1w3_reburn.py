"""r499 bm-b: N1-W3 missing-shard product landing (shards 1..11).

Pool face says 12/12 done (fleet burned: bm-a/bm-c hold uncommitted local
copies), but the repo-of-record carries only shard-0. The verdict face
(finalize) reads all 12 shard files from results/p2cal_ext/n1_w3/, so the
missing 11 are re-derived locally under the checkpoint law: "deterministic
rerun byte-equal; re-run of a shard = byte-equal idempotent overwrite"
(PERPETUAL_N1_W3_PREREG.md sec.3). No new trials, no ledger delta beyond the
frozen +2,200; pool statuses untouched (all done, no re-arm).
"""
import subprocess, sys, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
SHARD_DIR = os.path.join(ROOT, "results", "p2cal_ext", "n1_w3")

def shard_valid(k: int) -> bool:
    fp = os.path.join(SHARD_DIR, f"shard-{k}-of-12.json")
    if not os.path.exists(fp):
        return False
    try:
        import json
        d = json.load(open(fp, encoding="utf-8"))
        return d.get("batch") == "PERPETUAL-N1-W3" and d.get("shard") == k
    except Exception:
        return False

rcs = {}
t0 = time.time()
for k in range(1, 12):
    if shard_valid(k):
        print(f"shard {k}: already present+valid, skip", flush=True)
        rcs[k] = 0
        continue
    r = subprocess.run(
        [sys.executable, RUNNER, "run", "--shard", str(k), "--of", "12",
         "--wave", "3", "--workers", "8"],
        capture_output=True, text=True, cwd=ROOT)
    rcs[k] = r.returncode
    tail = (r.stdout or "").strip().splitlines()[-2:]
    print(f"shard {k}: rc={r.returncode} {' | '.join(tail)}", flush=True)
    if r.returncode != 0:
        print((r.stderr or "").strip()[-500:], flush=True)

bad = [k for k, v in rcs.items() if v != 0]
print(f"DRIVER DONE rc_all={'0' if not bad else '1'} "
      f"bad={bad} elapsed={time.time()-t0:.0f}s", flush=True)
sys.exit(0 if not bad else 1)
