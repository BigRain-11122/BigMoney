"""r482 bm-c round-start probe: orders diff-scan + W3 shard pool/claim/checkpoint
status + inbox unread scan. Read-only except probe output file (r446 file-law)."""
import json
import os

out = []

# --- orders same-shape set diff (r477 law: full filenames with .md) ---
orders = set(f for f in os.listdir("fleet/orders")
             if f.startswith("O-") and f.endswith(".md"))
hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
unacked = sorted(orders - ack)
extra = sorted(e for e in (ack - orders) if not e.startswith("README"))
out.append("ORDERS %d ack %d unacked %s extra_non_readme %s"
           % (len(orders), len(ack), unacked, extra))

# --- W3 shard pool status + claim ---
pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
w3e = [e for e in pool["entries"]
       if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD")]
out.append("POOL total %d w3 %d" % (len(pool["entries"]), len(w3e)))
for e in w3e:
    sh = e["shards"][0]
    out.append("W3 %s status=%s owner=%s owner_since=%s keepalive=%s"
               % (e["id"], e.get("status"), sh.get("owner"),
                  sh.get("owner_since"), sh.get("keepalive_at")))
# any other non-done pool entries (engine supply face)
others = [(e["id"], e.get("status")) for e in pool["entries"]
          if not str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN-SHARD")
          and e.get("status") != "done"]
out.append("POOL other non-done: %s" % (others[:10],))

# --- W3 checkpoint progress ---
ck = "results/mass_trial/w3_screen_checkpoint.jsonl"
if os.path.exists(ck):
    n = 0
    last = None
    with open(ck, "rb") as f:
        for line in f:
            if line.strip():
                n += 1
                last = line
    out.append("CHECKPOINT rows %d last %s" % (n, (last[:300] if last else None)))
else:
    out.append("CHECKPOINT missing")

# --- engine state face (Tools copy = bm-c registration face, r467 law) ---
for p in ("results/saturation_engine_state.bm-c.json",
          "results/saturation_engine/face_bm-c.json"):
    try:
        st = json.load(open(p, encoding="utf-8"))
        keys = {k: st[k] for k in st
                if k in ("last_tick", "ticks", "quarantined", "crash_counts",
                         "last_action", "round", "epoch")}
        out.append("ENGINEFACE %s %s" % (p, json.dumps(keys, ensure_ascii=False)))
    except Exception as ex:
        out.append("ENGINEFACE %s ERR %s" % (p, ex))

# --- inbox unread scan ---
ib = "fleet/inbox"
proc = set(os.listdir(os.path.join(ib, "processed"))) if os.path.isdir(os.path.join(ib, "processed")) else set()
unread = []
for f in sorted(os.listdir(ib)):
    if f.endswith(".md") and f not in proc:
        unread.append(f)
out.append("INBOX unread %s" % (unread,))

open("results/_r482bmc_round_scan_out.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("PROBE_DONE rows", len(out))
