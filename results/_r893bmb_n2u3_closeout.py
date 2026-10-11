# r893 bm-b: N2U3 leg-2 probe false-crash closeout (r860 three-piece: claim + tombstone)
# Evidence: probe burn COMPLETED 19:06:39 (ckpt/probe_receipt.json face=probe 256eps/8 workers,
# train+pretrain receipts); 19:12:06 fuse crash = post-completion confirm artifact (r860 gap:
# trial-labor runner writes no pool_claims handshake; 25-min confirmer killed lingering tree).
import json, os, datetime

FUSE = "results/crash_fuse.json"
SIG = "scripts/alphagen_rl_p1.py|probe,--episodes,256"
CLAIM_DIR = os.path.join("results", "pool_claims", "N2U3-ALPHAGEN-RL-P1-LEG2-PROBE")
CLAIM = os.path.join(CLAIM_DIR, "n2u3-leg2-probe.bm-b.json")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# piece 2: worker-claim file (state=closed + outcome=ok -> harvest flip input)
os.makedirs(CLAIM_DIR, exist_ok=True)
claim = {
    "machine_id": "bm-b",
    "state": "closed",
    "outcome": "ok",
    "pid": 25280,
    "started": "2026-10-11T18:45:40+08:00",
    "closed_at": "2026-10-11T19:06:39+08:00",
    "heartbeat": "2026-10-11T19:06:39+08:00",
    "exit_code": 0,
    "result_ref": "results/alphagen_rl_p1/ckpt/probe_receipt.json (+train_receipt.json, train_policy.npz, pretrain_policy.npz, train_log.jsonl)",
    "note": "r893 r860 three-piece: burn completed 19:06:39 (probe ok, 256 eps, 8 workers, elapsed 1237.9s); 19:12:06 fuse crash = post-completion 25-min confirmer artifact, not a real mid-burn crash",
}
tmp = CLAIM + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(claim, fh, ensure_ascii=False, indent=1)
os.replace(tmp, CLAIM)
print("claim file written:", CLAIM)

# piece 1: tombstone false-crash sig (sigs -> cleared, r824/r860/r873 manual tombstone paradigm)
with open(FUSE, encoding="utf-8") as fh:
    fuse = json.load(fh)
sig_entry = fuse["sigs"].pop(SIG, None)
assert sig_entry is not None, "sig not found in fuse sigs section"
cleared = {
    "crashes": sig_entry.get("count", 1),
    "old_code_sha256": sig_entry.get("code_sha256"),
    "cleared_by": "bm-b",
    "cleared_ts": NOW,
    "reason": ("r893 bm-b manual tombstone: 19:12:06 crash = post-completion 25-min confirm artifact "
               "(probe burn COMPLETED 19:06:39: ckpt/probe_receipt.json face=probe episodes=256 "
               "updates=8 pool_members=8 workers=8 elapsed_sec=1237.9 + train/pretrain receipts; "
               "r860 gap = trial-labor runner writes no pool_claims handshake; confirmer killed "
               "lingering pid-25280 tree after ok-summary). Claim file + harvest flip landed this "
               "window (r860 three-piece). Runner code unchanged (frozen wave, commit 8f49d6eea)."),
}
fuse.setdefault("cleared", {})[SIG] = cleared
tmp = FUSE + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(fuse, fh, ensure_ascii=False, indent=1)
os.replace(tmp, FUSE)
print("fuse sigs section now has alphagen keys:",
      [k for k in fuse["sigs"] if "alphagen_rl_p1" in k])
print("cleared tombstone recorded:", SIG)
print("OK three-piece pieces 1+2 landed at", NOW)
