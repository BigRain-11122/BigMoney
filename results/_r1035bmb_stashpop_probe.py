# r1035 S0 stash-pop UU resolver: 5 faces newer-wins + token_usage per-machine UNION (r1008 law)
import subprocess, json, re, io

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NEWER = [
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
]
UNION_FILE = "results/token_usage.json"
UNSTAGE = [
    "content/drama/QUEUE.md", "content/drama/ROUND-LOG.md", "content/drama/loop_state.json",
    "fleet/machine-health.json",
    "results/astock_daily_update_status.json", "results/etf_daily_pull_status.json",
    "results/minute_feed_status.json",
]

def git(args):
    r = subprocess.run(["git", "-C", REPO] + args, capture_output=True, text=False)
    return r.returncode, r.stdout, r.stderr

TS_PAT = re.compile(r'"(generated|ts|updated|updated_at|asof|checked_at|scan_ts)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})')

def latest_ts(txt):
    best = None
    for m in TS_PAT.finditer(txt):
        v = m.group(2).replace(" ", "T")
        if best is None or v > best:
            best = v
    return best

report = {}
for f in NEWER:
    _, ours, _ = git(["show", ":2:" + f])   # HEAD side (bm-c r1125 line)
    _, theirs, _ = git(["show", ":3:" + f]) # stash side (bm-b r1034 chain)
    to = latest_ts(ours.decode("utf-8", errors="replace")) if ours else None
    tt = latest_ts(theirs.decode("utf-8", errors="replace")) if theirs else None
    if tt is not None and (to is None or tt >= to):
        winner, side = theirs, "stash(bm-b)"
    elif to is not None:
        winner, side = ours, "HEAD(origin)"
    else:
        winner, side = theirs, "stash(bm-b,fallback)"
    with io.open(REPO + "\\" + f.replace("/", "\\"), "wb") as fh:
        fh.write(winner)
    rc, _, e = git(["add", "--", f])
    report[f] = {"head_ts": to, "stash_ts": tt, "winner": side, "add_rc": rc}

# token_usage.json per-machine UNION
_, h2, _ = git(["show", ":2:" + UNION_FILE])
_, h3, _ = git(["show", ":3:" + UNION_FILE])
try:
    j2 = json.loads(h2.decode("utf-8")) if h2 else {}
    j3 = json.loads(h3.decode("utf-8")) if h3 else {}
except Exception as ex:
    j2, j3 = None, None
    report[UNION_FILE] = {"error": "json parse fail: " + str(ex)}
if j2 is not None:
    merged = j2
    m3 = j3.get("machines", {}) if isinstance(j3, dict) else {}
    m2 = j2.get("machines", {}) if isinstance(j2, dict) else {}
    for k, v in m3.items():
        if k == "bm-b" or k not in m2:
            merged["machines"][k] = v  # bm-b row from stash (ours); other machines keep HEAD side
    # top-level non-machine scalar fields: keep HEAD (newer commit line), honest
    with io.open(REPO + "\\" + UNION_FILE.replace("/", "\\"), "wb") as fh:
        fh.write(json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8"))
    rc, _, e = git(["add", "--", UNION_FILE])
    report[UNION_FILE] = {"union": "machines keys=" + ",".join(sorted(merged.get("machines", {}).keys())), "add_rc": rc}

# unstage daemon/policy faces (keep as dirty worktree, do NOT commit)
for f in UNSTAGE:
    rc, _, e = git(["restore", "--staged", "--", f])
    report.setdefault("unstage", {})[f] = rc

print(json.dumps(report, ensure_ascii=False, indent=1))
