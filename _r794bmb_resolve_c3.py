"""r794 bm-b takeover resolver (c3): d013bef61 pick-1 window after add -u pollution.

Context: ls-files -u destroyed by blanket add -u (17 marker-polluted staged faces).
Recovery: stage2 blob = HEAD:<path> (rebased ours), stage3 blob = d013bef61:<path> (picked theirs).
Recipes (bigmoney-conflict-resolve canon + r793 pick-2 precedent):
- rolling-ledger (compute_audit/regime_state) -> values-union by (ts,machine) + tie->stage2 + state-fields take-new (r522/r88/r140)
- all other 15 faces (doc twins + snapshots) -> deep-ts probe newer-wins; no-ts-or-tie -> stage2 (r140)
Stage reads via git show <rev>:<path> (r648 sha-channel spirit: never trust marker-polluted worktree).
Receipt: append to _r794bmb_c3_runs.jsonl.
"""
import subprocess, json, os, re, sys, time

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RUNLOG = os.path.join(REPO, "_r794bmb_c3_runs.jsonl")
S2, S3 = "HEAD", "d013bef61"
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")

ROLLING = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["history", "transitions"],
}
SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
SIDE_TS_KEYS = ["generated", "generated_at", "updated", "updated_at", "ts", "asof", "as_of", "date"]


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d %r" % (args, r.returncode, r.stderr[:300]))
    return r.stdout


def blob(rev, path):
    return git("show", "%s:%s" % (rev, path))


def deep_ts(b):
    ts = TS_RE.findall(b.decode("utf-8", "replace"))
    return max(ts) if ts else ""


def resolve_rolling(path, keys):
    o2 = json.loads(blob(S2, path).decode("utf-8", "replace"))
    o3 = json.loads(blob(S3, path).decode("utf-8", "replace"))

    def side_ts(o):
        for k in SIDE_TS_KEYS:
            if isinstance(o.get(k), str):
                return o[k]
        return ""
    s2ts, s3ts = side_ts(o2), side_ts(o3)
    state_src = o2 if (s2ts, 0) >= (s3ts, 0) else o3
    out, info = {}, {"ledgers": {}, "state_took": "stage2" if state_src is o2 else "stage3",
                     "stage2_ts": s2ts, "stage3_ts": s3ts}

    def ekey(e):
        return (str(e.get("ts", "")), str(e.get("machine", "")))
    for k in keys:
        l2, l3 = o2.get(k, []), o3.get(k, [])
        merged = {}
        for e in l3:
            merged[ekey(e)] = e
        for e in l2:
            merged[ekey(e)] = e
        out[k] = sorted(merged.values(), key=lambda e: str(e.get("ts", "")))
        info["ledgers"][k] = {"len_stage2": len(l2), "len_stage3": len(l3), "union": len(out[k])}
    for k, v in state_src.items():
        if k not in keys:
            out[k] = v
    with open(os.path.join(REPO, path), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    info["class"] = "rolling-ledger values-union (r522) + tie->stage2 (r140) + state-fields take-new"
    return info


def resolve_snapshot(path):
    b2, b3 = blob(S2, path), blob(S3, path)
    t2, t3 = deep_ts(b2), deep_ts(b3)
    if t3 > t2:
        winner, wb = "stage3", b3
    else:
        winner, wb = "stage2", b2  # tie or missing -> stage2 (r140)
    with open(os.path.join(REPO, path), "wb") as fh:
        fh.write(wb)
    return {"class": "deep-ts newer-wins (tie/none->stage2 r140)", "took": winner,
            "stage2_ts": t2, "stage3_ts": t3}


def main():
    report = {"faces": {}, "unknown": [], "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
              "mode": "c3 takeover: add -u polluted 17 staged faces; stage2=HEAD stage3=d013bef61"}
    for p, keys in ROLLING.items():
        report["faces"][p] = resolve_rolling(p, keys)
    for p in SNAPSHOTS:
        report["faces"][p] = resolve_snapshot(p)
    with open(RUNLOG, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(report, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(0 if not report["unknown"] else 2)


if __name__ == "__main__":
    main()
