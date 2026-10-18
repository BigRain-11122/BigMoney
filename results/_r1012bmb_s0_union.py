"""r1012 S0 post-FF shared-face reconcile: union append-only jsonl (zero-loss), report json regen faces (origin-newer-wins expected)."""
import json, os, subprocess, hashlib

BK = r"results/_r1012bmb_s0_backup"
JSONL = ["results/x2_watch_log.jsonl", "results/post_review.jsonl"]
JSON_FACES = ["results/futures_update_status.json", "results/lhb_update_status.json", "results/watermark_red.json", "results/post_review/REPORT-20261018.md"]
report = {"round": 1012, "step": "s0_post_ff_union"}

def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]

for f in JSONL:
    bk_path = os.path.join(BK, os.path.basename(f))
    if not os.path.exists(bk_path):
        report[f] = {"error": "no backup", "skipped": True}
        continue
    with open(bk_path, "rb") as fh:
        local_lines = [l for l in fh.read().splitlines() if l.strip()]
    with open(f, "rb") as fh:
        origin_lines = [l for l in fh.read().splitlines() if l.strip()]
    o_set = set(origin_lines)
    local_unique = [l for l in local_lines if l not in o_set]
    if local_unique:
        merged = origin_lines + local_unique
        with open(f, "wb") as fh:
            fh.write(("\n".join(l.decode("utf-8", "replace") for l in merged) + "\n").encode("utf-8"))
        report[f] = {"action": "UNION_APPENDED", "origin_lines": len(origin_lines), "local_unique_appended": len(local_unique)}
    else:
        report[f] = {"action": "SUBSET_OK_ORIGIN_KEPT", "origin_lines": len(origin_lines), "local_unique": 0}

for f in JSON_FACES:
    bk_path = os.path.join(BK, os.path.basename(f))
    if not os.path.exists(bk_path):
        report[f] = {"error": "no backup"}
        continue
    with open(bk_path, "rb") as fh:
        local_b = fh.read()
    with open(f, "rb") as fh:
        origin_b = fh.read()
    report[f] = {"action": "ORIGIN_NEWER_WINS_DISCARDED_LOCAL", "local_sha16": sha(local_b), "origin_sha16": sha(origin_b), "identical": local_b == origin_b,
                 "note": "local face = r1011 S6 22:03 regen, origin = bm-a r1068 23:1x / bm-c converge newer generation; pure regen faces, zero unique data expected"}

with open("results/_r1012bmb_s0_overlap.json", "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1))
