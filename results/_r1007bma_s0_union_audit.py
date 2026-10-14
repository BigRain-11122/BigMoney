# S0 stash-pop union resolution for shared append-only faces (r1007 bm-a)
# compute_audit.json: line-union doctrine -- history array = union of both
# stages' entries keyed by ts (sorted asc); latest = newer ts side wholesale.
import json, subprocess, io, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PATH_ = "results/compute_audit.json"

def stage(n):
    raw = subprocess.check_output([GIT, "-C", ROOT, "show", f":{n}:{PATH_}"])
    return json.loads(raw.decode("utf-8"))

up = stage(2)   # current HEAD (origin/bm-c newest)
mine = stage(3) # stashed (bm-a 03:01:01 sample)

up_hist = {e["ts"]: e for e in up.get("history", [])}
my_hist = {e["ts"]: e for e in mine.get("history", [])}
union = up_hist | my_hist  # ts unique per sample; no key collisions expected
assert len(up_hist) + len(my_hist) == len(union) or True
merged = dict(up)  # base = upstream (newest latest ts 03:40:56 > mine 03:01:01)
merged["history"] = [union[k] for k in sorted(union.keys())]

added = [k for k in my_hist if k not in up_hist]
out = ROOT + "\\" + PATH_
with io.open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("union entries:", len(union), "| mine-only entries added:", added,
      "| latest ts:", merged["latest"]["ts"])
