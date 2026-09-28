import json

POOL = "results/runnable_pool.json"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

entries = pool["entries"]
jud = next(e for e in entries if e["id"] == "TRIAL-LABOR-W5-JUDGE")
assert jud["status"] == "waiting", f"judge status {jud['status']} != waiting"
assert jud["lane_owner"] == "bm-b"

# --- flip W5-JUDGE waiting -> ready (flip executor = deep-panel machine round bm-b;
#     gates per data_gates (W4-JUDGE precedent), all three PASS this round) ---
jud["status"] = "ready"
jud["ready_at"] = "2026-09-29T02:53:00+08:00"
jud["flip_by"] = "bm-b r404"
jud["flip_evidence"] = (
    "(1) serial-position re-confirm PASS: W2/W3/W4-JUDGE + MASS-W1-JUDGE all done (pool census 107: "
    "only non-done = V3-TOURNAMENT entered 09-28 15:18 own-physical-dep blocked (bm-c runner unbuilt) "
    "= not newly-entered in-flight face, RAM serial gate auto-orders (prereg L6); GRID-S3 done; "
    "(2) judge-prep PASS on deep-panel machine bm-b (t18 sidecar family): manifest PASS 48 members, "
    "census L/D == frozen, survivors 372, gate meta L/D na-window 199/199, vol meta 519/519 "
    "(leg-L anchors 594calm/518wild), yang meta zero-warmup 819yang/812red, exit 0; "
    "(3) RAM r354 three-sample PASS: [13.79, 13.77, 13.45] GB free across 30s window, all >= 4GB"
)
sh = jud["shards"][0]
assert sh["key"] == "judge-0of1" and sh["status"] == "waiting"
sh["status"] = "ready"

with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# round-trip self-verify
with open(POOL, encoding="utf-8") as fh:
    p2 = json.load(fh)
j2 = next(e for e in p2["entries"] if e["id"] == "TRIAL-LABOR-W5-JUDGE")
assert j2["status"] == "ready" and j2["shards"][0]["status"] == "ready"
assert j2["lane_owner"] == "bm-b" and "flip_evidence" in j2
print("pool flip OK: W5-JUDGE waiting->ready (judge-0of1 ready); entries=", len(p2["entries"]))
