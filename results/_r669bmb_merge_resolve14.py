# r669 bm-b merge resolver (14 UU regen faces)
# Laws: r656 HEAD:/MERGE_HEAD: direct blob reads; r461 ts_norm (T->space, first 19 chars);
#       r456/r466 token_usage per-key union w/ side-pick>0 assert + freshness fallback;
#       r453 marker line-start check; assert-before-write; UTF-8 out file, no console CJK
import subprocess, json, re, hashlib

OUT = r"results\_r669bmb_merge_resolve.json"
report = {"ts_pairs": {}, "side_picked": {}, "notes": []}

SIMPLE = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
TOKEN = "results/token_usage.json"

TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

def norm(ts: str) -> str:
    return ts.replace("T", " ")[:19]  # r461 normalization

def max_ts(blob: bytes) -> str:
    best = ""
    for m in TS_RE.finditer(blob.decode("utf-8", "replace")):
        v = norm(m.group(0))
        if v > best:
            best = v
    return best

def blob(rev: str, path: str) -> bytes:
    p = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"blob read fail {rev}:{path}: {p.stderr[:200]}")
    return p.stdout

resolved_files = {}

for path in SIMPLE:
    ours = blob("HEAD", path)
    theirs = blob("MERGE_HEAD", path)
    mo, mt = max_ts(ours), max_ts(theirs)
    report["ts_pairs"][path] = {"ours": mo, "theirs": mt}
    if mt > mo:
        win, side = theirs, "theirs"
    else:
        win, side = ours, "ours"  # ours on tie (r655 default + tie means same derive)
    report["side_picked"][path] = side
    assert not re.search(b"^<{7}", win, re.M), f"marker in winning blob {path}"
    if path.endswith(".json"):
        json.loads(win.decode("utf-8"))  # reparse gate
    resolved_files[path] = win

# token_usage.json: per-key union of machines (r456/r466)
ours_b = blob("HEAD", TOKEN)
theirs_b = blob("MERGE_HEAD", TOKEN)
oj = json.loads(ours_b.decode("utf-8"))
tj = json.loads(theirs_b.decode("utf-8"))
side_pick = 0
merged = dict(tj)  # start from theirs top level
om = oj.get("machines", {})
tm = tj.get("machines", {})
for k, v in om.items():
    if k not in tm or json.dumps(om.get(k), sort_keys=True) != json.dumps(tm.get(k), sort_keys=True):
        merged.setdefault("machines", {})[k] = v  # self-owned entries win from ours
        side_pick += 1
for k in ("ts", "updated", "generated_at"):
    if k in oj and k in tj:
        merged[k] = oj[k] if norm(str(oj[k])) >= norm(str(tj[k])) else tj[k]
    elif k in oj:
        merged[k] = oj[k]
assert side_pick > 0, "r456 law: per-key union zero side-pick = must fall back to whole-face freshness"
report["side_picked"][TOKEN] = f"per-key-union side_pick={side_pick}"
win_tok = (json.dumps(merged, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
json.loads(win_tok.decode("utf-8"))
resolved_files[TOKEN] = win_tok

# write all resolved faces
for path, data in resolved_files.items():
    with open(path, "wb") as f:
        f.write(data)
    # post-write verify: no line-start conflict markers
    chk = open(path, "rb").read()
    assert not re.search(b"^<{7}", chk, re.M), f"marker survived {path}"
    assert not re.search(b"^={7}$", chk, re.M) and not re.search(b"^>{7}", chk, re.M), f"raw marker {path}"

report["resolved_count"] = len(resolved_files)
report["verdict"] = "RESOLVED-PENDING-ADD"
open(OUT, "wb").write(json.dumps(report, ensure_ascii=True, indent=1).encode("ascii"))
print("RESOLVED", len(resolved_files), "faces; sides:", {k.split('/')[-1]: v for k, v in report["side_picked"].items()})
