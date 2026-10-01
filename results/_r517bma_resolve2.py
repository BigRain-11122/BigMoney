# r517 bm-a: resolve remaining UU batch from rebase stop 1/3 (pick b12b515c5 onto origin)
# Recipes: append-log line union (r188); twin-regen take-new by generated ts with SAME side for all twins (r98/r99/r100/r329 - md bytes direct from same side blob);
# snapshot take-new by updated/ts (R216); _attrition_guard_scan manual-classified snapshot take-new.
import subprocess, json, re

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def blob(spec):
    return subprocess.check_output(["git", "-C", REPO, "show", spec])

def find_ts(obj, best=("", "")):
    # deep scan for ts-like keys: generated/updated/ts/generated_at, value ^20\d{2}-
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = k.lower().replace("_", "").replace("-", "")
            if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", v):
                if kn in ("generated", "generatedat", "updated", "updatedat", "ts", "scannedat", "runtime", "asof") and v > best[1]:
                    best = (k, v)
            r = find_ts(v, best)
            if r[1] > best[1]:
                best = r
    elif isinstance(obj, list):
        for item in obj:
            r = find_ts(item, best)
            if r[1] > best[1]:
                best = r
    return best

def side_of(path):
    b2 = json.loads(blob(f":2:{path}").decode("utf-8"))
    b3 = json.loads(blob(f":3:{path}").decode("utf-8"))
    t2 = find_ts(b2)
    t3 = find_ts(b3)
    print(f"  {path}: :2: ts={t2} :3: ts={t3}")
    if t3[1] > t2[1]:
        return 3
    if t2[1] > t3[1]:
        return 2
    return None  # tie -> HEAD (origin, :2:) per r140 same-second tie law

def take_side(path, side):
    data = blob(f":{side}:{path}")
    p = REPO + "\\" + path.replace("/", "\\")
    with open(p, "wb") as f:
        f.write(data)
    print(f"  wrote {path} from :{side}: ({len(data)} bytes)")

print("== pool_core_samples.jsonl: append-log union ==")
PATH = "results/pool_core_samples.jsonl"
b2, b3 = blob(f":2:{PATH}"), blob(f":3:{PATH}")
l2 = [ln.rstrip(b"\r") for ln in b2.split(b"\n") if ln.rstrip(b"\r")]
l3 = [ln.rstrip(b"\r") for ln in b3.split(b"\n") if ln.rstrip(b"\r")]
set2 = set(l2)
suffix3 = [ln for ln in l3 if ln not in set2]
merged = l2 + suffix3
lost = [ln for ln in l2 + l3 if ln not in set(merged)]
assert not lost, "ZERO-LOSS FAILED"
for i, ln in enumerate(merged):
    json.loads(ln.decode("utf-8"))
sep = b"\r\n" if b"\r\n" in b2 else b"\n"
out = sep.join(merged) + sep
open(REPO + "\\" + PATH.replace("/", "\\"), "wb").write(out)
print(f"  union: {len(l2)}+{len(suffix3)}={len(merged)} lines, all parse-valid")

print("== twin pairs: take-new same-side ==")
for group in [
    ["docs/daily_report/REPORT-2026-10-01.json", "docs/daily_report/REPORT-2026-10-01.md"],
    ["docs/live_usage/LIVE-2026-10-01.json", "docs/live_usage/LIVE-2026-10-01.md",
     "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"],
]:
    side = side_of(group[0])  # probe json face only; tie -> :2: (r140)
    if side is None:
        side = 2
        print(f"  {group[0]}: ts tie -> take :2: (HEAD tie law r140)")
    for p in group:
        take_side(p, side)

print("== plain snapshots: take-new ==")
for path in ["results/fundamental_b_layer_filter.json", "results/_attrition_guard_scan.json"]:
    side = side_of(path)
    if side is None:
        side = 2
        print(f"  {path}: ts tie -> take :2:")
    take_side(path, side)

print("== parse-verify all written json files ==")
for path in ["results/pool_core_samples.jsonl", "docs/daily_report/REPORT-2026-10-01.json",
             "docs/live_usage/LIVE-2026-10-01.json", "docs/live_usage/LIVE-latest.json",
             "results/fundamental_b_layer_filter.json", "results/_attrition_guard_scan.json"]:
    raw = open(REPO + "\\" + path.replace("/", "\\"), "rb").read()
    if path.endswith(".jsonl"):
        for ln in raw.decode("utf-8").splitlines():
            if ln.strip():
                json.loads(ln)
    else:
        json.loads(raw.decode("utf-8"))
    print(f"  OK {path}")
print("DONE")
