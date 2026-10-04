import json, difflib
P = r"results\runnable_pool.json"
raw = open(P, "rb").read().decode("utf-8")
assert raw.count('"id": "THEME-JUDGE-P2"') == 1
assert raw.count("theme-judge-p2-burn-0of1") == 1
crlf = "\r\n" in raw
nl = "\r\n" if crlf else "\n"
lines = raw.split(nl)
idx_id = [k for k, ln in enumerate(lines) if '"id": "THEME-JUDGE-P2"' in ln]
idx_shard = [k for k, ln in enumerate(lines) if "theme-judge-p2-burn-0of1" in ln]
idx_upd = [k for k, ln in enumerate(lines) if ln.startswith(' "updated_at"')]
assert len(idx_id) == 1 and len(idx_shard) == 1 and len(idx_upd) == 1, (idx_id, idx_shard, idx_upd)
i_id, i_sh, i_upd = idx_id[0], idx_shard[0], idx_upd[0]
assert i_id < i_sh, (i_id, i_sh)
# entry status line = first '"status": "ready",' after i_id
i_est = [k for k in range(i_id, i_sh) if lines[k].strip() == '"status": "ready",']
assert len(i_est) == 1, i_est
i_est = i_est[0]
# shard status line = first '"status": "ready",' after i_sh (within a few lines)
i_sst = [k for k in range(i_sh, min(i_sh + 30, len(lines))) if lines[k].strip() == '"status": "ready",']
assert len(i_sst) == 1, i_sst
i_sst = i_sst[0]
orig_lines = list(lines)
# 1) entry status -> done
indent_e = lines[i_est][: len(lines[i_est]) - len(lines[i_est].lstrip())]
lines[i_est] = indent_e + '"status": "done",'
# 2) shard status -> done + insert done_at line after it
indent_s = lines[i_sst][: len(lines[i_sst]) - len(lines[i_sst].lstrip())]
lines[i_sst] = indent_s + '"status": "done",'
lines.insert(i_sst + 1, indent_s + '"done_at": "2026-10-04T13:14:13+08:00",')
# 3) updated_at
indent_u = lines[i_upd][: len(lines[i_upd]) - len(lines[i_upd].lstrip())]
lines[i_upd] = indent_u + '"updated_at": "2026-10-04T13:26:30+08:00",'
out = nl.join(lines)
open(P, "wb").write(out.encode("utf-8"))
# verification: reparse + targeted diff
d2 = json.loads(open(P, "rb").read().decode("utf-8"))
assert len(d2["entries"]) == 368
states = {}
for e in d2["entries"]:
    if e.get("id") in ("THEME-JUDGE-P1", "THEME-JUDGE-P2"):
        states[e["id"]] = (e["status"], [(s["key"], s["status"], s.get("done_at")) for s in e["shards"]])
assert states["THEME-JUDGE-P2"][0] == "done", states
assert states["THEME-JUDGE-P2"][1][0][1] == "done", states
assert states["THEME-JUDGE-P1"][0] == "done", states
diff = [l for l in difflib.unified_diff(orig_lines, lines, lineterm="", n=0) if l[:1] in "+-" and l not in ("+++", "---")]
print("changed_lines=", len(diff))
for l in diff:
    print(repr(l))
print("STATES:", json.dumps(states, ensure_ascii=False))
print("POOL_FLIP_SURGICAL_OK")
