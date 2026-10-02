# r568 S0 rebase conflict resolver: 7 shared regen JSON faces (take wall-clock newer side)
# + pool_core_samples.jsonl (append-only line-union dedupe, conflict-region domain law r294).
# Bytes-level IO per r530 (no read_text/write_text).
import json, subprocess, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def stage_blob(stage, path):
    out = subprocess.check_output(["git", "-C", REPO, "show", f":{stage}:{path}"])
    return out

def ts_of(obj):
    # find any timestamp-ish scalar key
    best = ""
    for k in ("generated", "generated_at", "asof", "cutoff", "timestamp", "updated", "updated_at", "run_at", "last_run"):
        v = obj.get(k)
        if isinstance(v, str) and v:
            return v, k
    return None, None

REGEN = [
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]

def parse_js(blob):
    s = blob.decode("utf-8", "replace").strip()
    if s.startswith("var "):
        i = s.find("=")
        s = s[i+1:].strip()
        if s.endswith(";"):
            s = s[:-1]
    return json.loads(s)

report = []
for p in REGEN:
    ours = stage_blob(2, p)
    theirs = stage_blob(3, p)
    try:
        o = json.loads(ours) if p.endswith(".json") else parse_js(ours)
        t = json.loads(theirs) if p.endswith(".json") else parse_js(theirs)
        ot, ok = ts_of(o)
        tt, tk = ts_of(t)
        take = "theirs" if (tt or "") >= (ot or "") else "ours"
        reason = f"ts ours={ok}:{ot} theirs={tk}:{tt}"
    except Exception as e:
        take = "theirs"
        reason = f"parse-fail ({e}) -> take theirs (origin newer lineage)"
    blob = theirs if take == "theirs" else ours
    with open(REPO + "\\" + p.replace("/", "\\"), "wb") as f:
        f.write(blob)
    report.append(f"{p}: take {take} ({reason})")

# append-only jsonl: line-union dedupe (whole-file here is the conflict domain: both sides append-only)
p = "results/pool_core_samples.jsonl"
ours = stage_blob(2, p).decode("utf-8", "replace").splitlines()
theirs = stage_blob(3, p).decode("utf-8", "replace").splitlines()
seen = set()
merged = []
for line in theirs + ours:  # origin-side lines first, then mine; exact-dup dedupe
    if line.strip() and line not in seen:
        seen.add(line)
        merged.append(line)
nl = open(REPO + "\\" + p.replace("/", "\\"), "rb").read()[-1:] == b"\n"
with open(REPO + "\\" + p.replace("/", "\\"), "wb") as f:
    f.write(("\r\n" if b"\r\n" in stage_blob(3, p) else "\n").join(merged).encode("utf-8"))
    if merged:
        f.write(b"\r\n" if b"\r\n" in stage_blob(3, p) else b"\n")
report.append(f"{p}: union dedupe ours={len(ours)} theirs={len(theirs)} merged={len(merged)}")

print("\n".join(report))
