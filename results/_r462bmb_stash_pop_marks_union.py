# r462 bm-b: stash-pop conflict union for marks-20260930.jsonl (append-log recipe r188)
# ours = stage2 (HEAD=origin after pull), theirs = stage3 (local stash lane rows)
import subprocess, sys, json

PATH = "results/paper/marks/marks-20260930.jsonl"

def blob(stage):
    return subprocess.run(["git", "show", f":{stage}:{PATH}"],
                         capture_output=True).stdout.decode("utf-8")

ours = blob(2)
theirs = blob(3)

o_lines = [l for l in ours.splitlines() if l.strip()]
t_lines = [l for l in theirs.splitlines() if l.strip()]

seen = set()
union = []
for line in o_lines + t_lines:
    key = line  # full-line identity; jsonl rows are unique by ts+trader content
    if key not in seen:
        seen.add(key)
        union.append(line)

# sort by ts to keep chronological append order
def ts_of(line):
    try:
        return json.loads(line).get("ts", "")
    except Exception:
        return ""
union.sort(key=ts_of)

assert len(union) == len(seen)
for line in union:
    json.loads(line)  # parse validation before write

with open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(union) + "\n")

print(f"ours={len(o_lines)} theirs={len(t_lines)} union={len(union)}")
print("first_ts=", ts_of(union[0]), "last_ts=", ts_of(union[-1]))
