# r502 bm-b S0 resolver v2 (healing): pool_core_samples.jsonl append-log union (r188/r217, classifier=append-log)
# - origin side 41022dd2d contains bm-c r311 rebase remnant line ('||||||| parent of f77133f64 ...') = diff3 marker,
#   parse-verify (r185) correctly refused it; healed union drops marker, keeps all 109 origin data lines + 4 bm-b lines.
# - invoked after git reset --soft 41022dd2d (local-only commits squashed; corrupted marker-embedded blob never pushed).
import subprocess, json

PATH = "results/pool_core_samples.jsonl"

def blob(rev):
    return subprocess.check_output(["git", "show", rev]).decode("utf-8")

origin_lines = blob("41022dd2d:" + PATH).splitlines()
mine_lines = blob("5a4c0d023:" + PATH).splitlines()

# healed origin side: keep data lines, drop conflict-marker garbage (parse-verify enforced below)
o_data = [l for l in origin_lines if l.strip() and not l.startswith(("<<<<<<<", "=======", ">>>>>>>", "|||||||"))]

seen = set(o_data)
out = list(o_data)
added = 0
for ln in mine_lines:
    if ln.strip() and ln not in seen:
        seen.add(ln)
        out.append(ln)
        added += 1

# parse-verify EVERY line before write (r185 law)
for ln in out:
    json.loads(ln)

with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(out) + "\n")

assert len(out) == len(set(out)), "dup lines after union"
print("healed union lines:", len(out), "(origin data", len(o_data), "+ bm-b new", added, ")")
print("PARSE-VERIFY OK; wrote", PATH)
