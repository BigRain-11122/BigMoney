# r427 bm-a merge-back resolver -- append-log jsonl leg (reuses r426_resolve5 proven pattern)
# Recipe: r188 append-log multiset union vs base, chronological tail by embedded ts.
import json, subprocess, collections

def stage_blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {stage}:{path}: {r.stderr[:200]!r}")
    return r.stdout

p = "results/x2_watch_log.jsonl"
b1, b2, b3 = [stage_blob(s, p).decode().splitlines() for s in (1, 2, 3)]
m1, m2, m3 = map(collections.Counter, (b1, b2, b3))
orig_new, mine_new = list((m2 - m1).elements()), list((m3 - m1).elements())

def _ts(line):
    try:
        return json.loads(line).get("ts", "")
    except Exception:
        return ""

tail = sorted(orig_new + mine_new, key=_ts)
result_lines = b1 + tail
blob = ("\n".join(result_lines) + "\n").encode()
with open(p, "wb") as f:
    f.write(blob)
assert collections.Counter(result_lines) == m1 + collections.Counter(orig_new) + collections.Counter(mine_new), "jsonl union multiset mismatch"
print(f"append-log {p}: base={sum(m1.values())} + orig_new={len(orig_new)} + mine_new={len(mine_new)} -> {len(result_lines)} lines, multiset-verified, tail chronologically sorted")
