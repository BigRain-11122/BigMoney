"""r794 bm-b takeover-2 resolver: pick2 (6a0a85ef1) 6-UU faces, canon recipes.

Laws applied:
- r648: rebase-window stage reads via ls-files -u sha -> git cat-file -p (never :N:)
- r209: all blob reads via subprocess bytes, no PS redirection
- r188/r217 + treasure_guard rc3 sanction: append-only ledgers -> multiset line-union zero-loss
- R208/R216 lane live-wins: daemon-owned faces take fresh valid worktree bytes verbatim
- r413: multiset-union multiplicity-preserved, ts-sorted when all lines carry ts
Re-runnable for a possible pick3 window (re-probes ls-files -u each run).
"""
import subprocess, json, os, re, sys
from collections import Counter

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RECEIPT = os.path.join(REPO, "results", "_r794bmb_rebase_resolve.json")
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
TS_KEYS = ["ts", "time", "t", "timestamp", "epoch", "date", "asof", "as_of"]


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
        "class": "append-log multiset line-union zero-loss (r188/r217 + treasure_guard rc3 union sanction)",
        "len_stage2": len(l2), "len_stage3": len(l3), "len_wt_stripped": len(lw),
        "markers_in_wt": mw,
        "union_lines": len(order),
        "union_unique": len(uni),
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
    # candidates: side tag, ts, bytes (r140: same-ts tie -> HEAD/stage2)
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
    prio = {"stage2": 2, "stage3": 0, "worktree": 1}  # higher ts wins; tie -> stage2
    best = max(cands, key=lambda c: (c[1], prio[c[0]]))
    if best[0] != "worktree":
        with open(os.path.join(REPO, path), "wb") as fh:
            fh.write(best[2])
    got = {c[0]: c[1] for c in cands}
    return {
        "class": "lane-daemon live-wins deep-ts probe (R208/R216; wt markers -> ours/stage2 live side per pit-git-resolver ours-live-wins)",
        "took": best[0],
        "ts_map": got,
        "json_valid": True,
        "stage2_sha": st.get(2, ""), "stage3_sha": st.get(3, ""),
    }


def main():
    st = stages()
    report = {"faces": {}, "unknown": []}
    for p in APPEND_LOG:
        if p in st and 2 in st[p] and 3 in st[p]:
            report["faces"][p] = resolve_ledger(p, st[p])
        elif p in st:
            report["unknown"].append({"path": p, "why": "missing stage blobs"})
    for p, getter in LIVE_WINS.items():
        if p in st and 2 in st[p] and 3 in st[p]:
            report["faces"][p] = resolve_live(p, st[p], getter)
    for p in st:
        if p not in APPEND_LOG and p not in LIVE_WINS:
            report["unknown"].append({"path": p, "why": "not in recipe map - manual"})
    if report["unknown"]:
        report["verdict"] = "FAIL-CLOSED: unknown faces present"
        print(json.dumps(report, indent=1, ensure_ascii=False))
        sys.exit(2)
    report["verdict"] = "PASS"
    report["resolved_at"] = "r794 bm-b takeover-2 (dead-session corpse takeover; per-pick sections below)"
    with open(RECEIPT, "r", encoding="utf-8") as fh:
        receipt = json.load(fh)
    try:
        with open(os.path.join(REPO, ".git", "rebase-merge", "msgnum")) as fh:
            pick_no = int(fh.read().strip())
    except Exception:
        pick_no = 0
    key = "pick%d_final_r794_takeover2" % pick_no
    if key in receipt:
        receipt[key + "_b"] = report
    else:
        receipt[key] = report
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
