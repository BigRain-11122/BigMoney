# -*- coding: utf-8 -*-
import re, json, subprocess

# --- unmerged files ---
out = subprocess.check_output(["git", "diff", "--name-only", "--diff-filter=U"]).decode()
print("UNMERGED:", out.strip().splitlines())

# --- update_status.json: same-day idempotent face -> compare wall-clock ts of :2 (origin) vs :3 (mine) ---
for stage, name in (("2", "origin/theirs"), ("3", "mine")):
    b = subprocess.check_output(["git", "show", f":{stage}:results/update_status.json"])
    ts = re.search(rb'"ts":\s*"([^"]+)"', b)
    print(f"stage{stage} ({name}) ts={ts.group(1).decode() if ts else 'NONE'} bytes={len(b)}")

# --- x2_watch_log.jsonl: append-only -> union of conflict-region lines ---
b = subprocess.check_output(["git", "show", ":2:results/x2_watch_log.jsonl"]).decode()
o_lines = b.splitlines()
b3 = subprocess.check_output(["git", "show", ":3:results/x2_watch_log.jsonl"]).decode()
m_lines = b3.splitlines()
print("x2 stage2 lines:", len(o_lines), "stage3 lines:", len(m_lines))
print("stage2 tail:", o_lines[-1][:150] if o_lines else "empty")
print("stage3 tail:", m_lines[-1][:150] if m_lines else "empty")
# union: lines in either, order by line key where possible
union = list(o_lines)
added = 0
seen = set(json.loads(l)["ts"] if l.strip().startswith("{") and '"ts"' in l else l for l in o_lines if l.strip())
for l in m_lines:
    k = None
    if l.strip().startswith("{"):
        try:
            k = json.loads(l).get("ts")
        except Exception:
            k = l
    else:
        k = l
    if k not in seen:
        union.append(l)
        seen.add(k)
        added += 1
print("union lines:", len(union), "added-from-mine:", added)
with open("results/x2_watch_log.jsonl", "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(union) + ("\n" if union else ""))
print("x2 union written")
