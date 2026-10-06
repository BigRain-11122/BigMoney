"""r794 bm-b cycle-2 (c2) resolver: pull-rebase #2 window onto bm-c r650 tip.

Recipes per bigmoney-conflict-resolve skill + receipts lineage:
- append-log *.jsonl -> multiset line-union zero-loss (r188/r217, treasure_guard rc3 union sanction)
- lane-daemon faces -> live-wins deep-ts probe; wt markers -> ours/stage2 (R208/R216, r140 tie->HEAD)
- rolling-ledger (compute_audit/regime_state) -> values-union by (ts,machine) + tie->stage2 + state-fields take-new (r522/r88/r140)
- stage reads via ls-files -u sha -> cat-file (r648); bytes via subprocess (r209)
Receipt: per-run line appended to root _r794bmb_c2_runs.jsonl (untracked, survives replays);
final results/ receipt written post-rebase at S7 closeout.
"""
import subprocess, json, os, re, sys, time
from collections import Counter

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RUNLOG = os.path.join(REPO, "_r794bmb_c2_runs.jsonl")
MARKER = re.compile(r"^(<{7}|>{7}|\|{7}).*$|^={7}\s*$")

APPEND_LOG = [
    "results/fund_divlowvol_p1/nulls.jsonl",
    "results/fund_quality_p1/nulls.jsonl",
    "results/saturation_engine/history_bm-b.jsonl",
]
LIVE_WINS = {
    "results/saturation_engine/face_bm-b.json": lambda o: o.get("ts"),
    "results/saturation_engine/state_bm-b.json": lambda o: (o.get("last_tick") or {}).get("ts"),
    "results/p1d_gates.json": lambda o: (o.get("meta") or {}).get("date"),
}
ROLLING_LEDGER = {
    "results/compute_audit.json": ["history"],
    "results/regime_state.json": ["history", "transitions"],
}
TS_KEYS = ["ts", "time", "t", "timestamp", "epoch", "date", "asof", "as_of"]
SIDE_TS_KEYS = ["updated", "ts", "asof", "as_of", "date", "generated", "generated_at"]


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d %r" % (args, r.returncode, r.stderr[:300]))
    return r.stdout


def stages():
    out = git("ls-files", "-u").decode("utf-8", "replace")
    m = {}
    for ln in out.splitlines():
        meta, _, path = ln.partition("\t")
        f = meta.split()
        if len(f) == 3 and path:
            m.setdefault(path, {})[int(f[2])] = f[1]
    return m


def clean_lines(raw_bytes):
    txt = raw_bytes.decode("utf-8", "replace")
    all_lines = txt.splitlines()
    markers = sum(1 for l in all_lines if MARKER.match(l))
    return [l for l in all_lines if not MARKER.match(l)], markers


def line_ts(line):
    try:
        o = json.loads(line)
    except Exception:
        return None
    if not isinstance(o, dict):
        return None
    for k in TS_KEYS:
        if k in o:
            return str(o[k])
    return None


def resolve_ledger(path, st):
    b2 = git("cat-file", "-p", st[2])
    b3 = git("cat-file", "-p", st[3])
    with open(os.path.join(REPO, path), "rb") as fh:
        bwt = fh.read()
    l2, m2 = clean_lines(b2)
    l3, m3 = clean_lines(b3)
    lw, mw = clean_lines(bwt)
    uni = Counter(l2) | Counter(l3) | Counter(lw)
    order = list(l2)
    remaining = uni - Counter(l2)
    for src in (l3, lw):
        for x in src:
            if remaining[x] > 0:
                remaining[x] -= 1
                order.append(x)
    ts_all = [line_ts(x) for x in order]
    ts_sorted = all(t is not None for t in ts_all)
    if ts_sorted and len(set(ts_all)) > 1:
        order = [x for _, _, x in sorted(zip(ts_all, range(len(order)), order))]
    body = "\n".join(order).encode("utf-8")
    if b2.endswith(b"\n"):
        body += b"\n"
    with open(os.path.join(REPO, path), "wb") as fh:
        fh.write(body)
    return {
        "class": "append-log multiset line-union zero-loss (r188/r217)",
        "len_stage2": len(l2), "len_stage3": len(l3), "len_wt_stripped": len(lw),
        "markers_in_wt": mw, "union_lines": len(order), "union_unique": len(uni),
        "ts_sorted": ts_sorted,
        "stage2_sha": st.get(2, ""), "stage3_sha": st.get(3, ""),
    }


def resolve_live(path, st, ts_get):
    with open(os.path.join(REPO, path), "rb") as fh:
        bwt = fh.read()
    txt = bwt.decode("utf-8", "replace")
    wt_has_markers = any(MARKER.match(l) for l in txt.splitlines())
    wt_obj = None
    if not wt_has_markers:
        try:
            wt_obj = json.loads(txt)
        except Exception:
            wt_obj = None
    cands = []
    for side, which in (("stage2", 2), ("stage3", 3)):
        try:
            b = git("cat-file", "-p", st[which])
            cands.append((side, str(ts_get(json.loads(b.decode("utf-8", "replace")))), b))
        except Exception:
            pass
    if wt_obj is not None:
        cands.append(("worktree", str(ts_get(wt_obj)), bwt))
    if not cands:
        raise RuntimeError("FAIL-CLOSED %s: no parseable side" % path)
    prio = {"stage2": 2, "stage3": 0, "worktree": 1}  # tie -> stage2 (r140)
    best = max(cands, key=lambda c: (c[1], prio[c[0]]))
    if best[0] != "worktree":
        with open(os.path.join(REPO, path), "wb") as fh:
            fh.write(best[2])
    return {
        "class": "lane-daemon live-wins deep-ts probe (R208/R216; tie->stage2 r140)",
        "took": best[0], "ts_map": {c[0]: c[1] for c in cands}, "json_valid": True,
        "stage2_sha": st.get(2, ""), "stage3_sha": st.get(3, ""),
    }


def resolve_rolling(path, st, ledger_keys):
    o2 = json.loads(git("cat-file", "-p", st[2]).decode("utf-8", "replace"))
    o3 = json.loads(git("cat-file", "-p", st[3]).decode("utf-8", "replace"))

    def side_ts(o):
        for k in SIDE_TS_KEYS:
            if isinstance(o.get(k), str):
                return o[k]
        return ""

    s2ts, s3ts = side_ts(o2), side_ts(o3)
    state_src = o2 if (s2ts, 0) >= (s3ts, 0) else o3  # tie -> stage2 (r140)
    out = {}
    info = {"ledgers": {}, "state_took": "stage2" if state_src is o2 else "stage3",
            "stage2_ts": s2ts, "stage3_ts": s3ts}

    def ekey(e):
        return (str(e.get("ts", "")), str(e.get("machine", "")))

    for k in ledger_keys:
        l2 = o2.get(k, [])
        l3 = o3.get(k, [])
        merged = {}
        for e in l3:
            merged[ekey(e)] = e
        for e in l2:
            merged[ekey(e)] = e
        ordered = sorted(merged.values(), key=lambda e: str(e.get("ts", "")))
        out[k] = ordered
        info["ledgers"][k] = {"len_stage2": len(l2), "len_stage3": len(l3), "union": len(ordered)}
    for k, v in state_src.items():
        if k not in ledger_keys:
            out[k] = v
    with open(os.path.join(REPO, path), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    info["class"] = "rolling-ledger values-union (r522) + tie->stage2 (r140) + state-fields take-new"
    info["stage2_sha"] = st.get(2, "")
    info["stage3_sha"] = st.get(3, "")
    return info


def main():
    st = stages()
    report = {"faces": {}, "unknown": [], "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
    try:
        with open(os.path.join(REPO, ".git", "rebase-merge", "msgnum")) as fh:
            report["pick"] = int(fh.read().strip())
    except Exception:
        report["pick"] = 0
    for p in APPEND_LOG:
        if p in st and 2 in st[p] and 3 in st[p]:
            report["faces"][p] = resolve_ledger(p, st[p])
    for p, getter in LIVE_WINS.items():
        if p in st and 2 in st[p] and 3 in st[p]:
            report["faces"][p] = resolve_live(p, st[p], getter)
    for p, keys in ROLLING_LEDGER.items():
        if p in st and 2 in st[p] and 3 in st[p]:
            report["faces"][p] = resolve_rolling(p, st[p], keys)
    for p in st:
        if p not in APPEND_LOG and p not in LIVE_WINS and p not in ROLLING_LEDGER:
            report["unknown"].append({"path": p, "why": "not in recipe map - manual"})
    with open(RUNLOG, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(report, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(2 if report["unknown"] else 0)


if __name__ == "__main__":
    main()
