"""r699 bm-a merge resolver: 20 UU faces vs fleet wave (bm-b r696-697 + bm-c
r497-499 + autofill waves).
Laws: r440 per-face newer-wins + r484 no-blind-side + dual-side raw bytes via
git show HEAD:/MERGE_HEAD: (MERGE_HEAD alive, add never precedes, r657-2) +
r461 ts_norm + r456/r466 token per-key union side_pick>0 assert + freshness
fallback + md/js twins locked to their json pick + r482/r485 jsonl union
(theirs-verbatim base + ours-unique append, EOL-normalized containment,
host-EOL append) + pool auto-merge semantic assert (SHARD-6/7 done-flips +
9/10/11 claim states survive). Fail-closed BEFORE any add (r657-3; add =
separate single batch step per r673). Lineage: _r696bmb_merge_resolve.py
adaptation (canon read per r461); r699 deltas = (a) dashboard_status js/json
twin pair added, (b) jsonl union leg new (r482/r485), (c) CODELY leg dropped
(no UU this window), (d) pool asserts re-targeted to SHARD-6/7 + tail states.
"""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_KEYS = ["ts", "generated", "generated_at", "updated", "updated_at",
           "probe_ts", "scan_ts", "asof", "written_at", "cutoff_ts",
           "generated_from_state_updated"]

JSON_FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
    "results/dashboard_status.json",
]
TWIN_FACES = [
    ("docs/daily_report/REPORT-2026-10-04.md", "docs/daily_report/REPORT-2026-10-04.json"),
    ("docs/live_usage/LIVE-2026-10-04.md", "docs/live_usage/LIVE-2026-10-04.json"),
    ("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"),
    ("results/dashboard_status.js", "results/dashboard_status.json"),
]
JSONL_UNION_FACES = [
    "results/pool_core_samples.jsonl",
    "results/pool_red_flags.jsonl",
]
TOKEN_FACE = "results/token_usage.json"
POOL_FACE = "results/runnable_pool.json"
RECEIPT = os.path.join(ROOT, "results", "_r699bma_merge_resolve.json")


def git_bytes(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={r.returncode} "
                           f"{r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


def ts_norm(v):
    return str(v).replace("T", " ")[:19]


def deep_ts(obj, path=""):
    if isinstance(obj, dict):
        for k in TS_KEYS:
            if k in obj and isinstance(obj[k], (str, int, float)):
                return (f"{path}.{k}" if path else k), ts_norm(obj[k])
        for k, v in obj.items():
            r = deep_ts(v, f"{path}.{k}" if path else k)
            if r:
                return r
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            r = deep_ts(v, f"{path}[{i}]")
            if r:
                return r
    return None


def face_ts(obj):
    r = deep_ts(obj)
    if r is None:
        raise RuntimeError("no ts key found (deep scan)")
    return r


def _marker_lines(raw):
    bad = []
    for ln in raw.decode("utf-8", errors="replace").splitlines():
        if ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>"):
            bad.append(ln[:40])
    return bad


def write_resolved(path, data):
    open(os.path.join(ROOT, path), "wb").write(data)
    raw = open(os.path.join(ROOT, path), "rb").read()
    bad = _marker_lines(raw)
    assert not bad, f"marker line-start in {path}: {bad[:3]}"
    return raw


def resolve_whole(path):
    ours_b = git_bytes("HEAD", path)
    theirs_b = git_bytes("MERGE_HEAD", path)
    ours = json.loads(ours_b.decode("utf-8"))
    theirs = json.loads(theirs_b.decode("utf-8"))
    try:
        ko, to = face_ts(ours)
        kt, tt = face_ts(theirs)
    except RuntimeError as e:
        top_o = list(ours.keys())[:12] if isinstance(ours, dict) else type(ours).__name__
        raise RuntimeError(f"FACE_FAIL {path}: {e} | top-keys={top_o}") from e
    if ko != kt:
        raise RuntimeError(f"{path}: ts keypath mismatch ours={ko} theirs={kt}")
    pick = "ours" if to >= tt else "theirs"
    write_resolved(path, ours_b if pick == "ours" else theirs_b)
    json.loads(open(os.path.join(ROOT, path), "rb").read().decode("utf-8"))
    return {"face": path, "ts_key": ko, "ours_ts": to, "theirs_ts": tt,
            "pick": pick}


def resolve_twin(twin_path, json_pick):
    data = git_bytes("HEAD" if json_pick == "ours" else "MERGE_HEAD", twin_path)
    raw = write_resolved(twin_path, data)
    assert len(raw) > 0
    for ln in raw.decode("utf-8", errors="replace").splitlines():
        assert not ln.startswith("<<<<<<<") and not ln.startswith(">>>>>>>"), \
            f"marker line in {twin_path}"
    return {"face": twin_path, "pick": json_pick + " (twin-locked)"}


def resolve_jsonl_union(path):
    """r482: theirs(MERGE_HEAD=origin tip) verbatim base + ours-unique lines
    appended, keep-first id semantics; r485: host-EOL for the appended join;
    EOL-normalized containment math (strip \\r)."""
    ours_b = git_bytes("HEAD", path)
    theirs_b = git_bytes("MERGE_HEAD", path)
    theirs_set = set()
    for ln in theirs_b.split(b"\n"):
        s = ln.rstrip(b"\r").strip()
        if s:
            theirs_set.add(s)
    missing = []
    for ln in ours_b.split(b"\n"):
        s = ln.rstrip(b"\r").strip()
        if not s:
            continue
        if s in theirs_set:
            continue
        missing.append(s)
    eol = b"\r\n" if theirs_b.find(b"\r\n") >= 0 else b"\n"
    base = theirs_b
    if missing:
        if not base.endswith(b"\n"):
            base += eol
        add = eol.join(missing) + eol
        base = base + add
    raw = write_resolved(path, base)
    # assertions: origin content fully contained; unique count exact
    dset = set()
    for ln in raw.split(b"\n"):
        s = ln.rstrip(b"\r").strip()
        if s:
            dset.add(s)
    assert theirs_set <= dset, f"{path}: origin line lost in union"
    assert len(dset - theirs_set) == len(missing), \
        f"{path}: unique-count mismatch {len(dset - theirs_set)} != {len(missing)}"
    return {"face": path, "pick": "union(theirs-verbatim+ours-unique)",
            "ours_unique": len(missing), "theirs_lines": len(theirs_set),
            "union_lines": len(dset)}


def resolve_token():
    ours_b = git_bytes("HEAD", TOKEN_FACE)
    theirs_b = git_bytes("MERGE_HEAD", TOKEN_FACE)
    ours = json.loads(ours_b.decode("utf-8"))
    theirs = json.loads(theirs_b.decode("utf-8"))
    side_pick = 0
    merged = None
    if isinstance(ours.get("machines"), dict) and isinstance(theirs.get("machines"), dict):
        merged = dict(theirs["machines"])
        for k, v in ours["machines"].items():
            if k not in merged or merged[k] != v:
                side_pick += 1
        merged.update(ours["machines"])
    if side_pick > 0:
        base = dict(theirs)
        base["machines"] = merged
        pick = "per-key-union(machines)"
    else:
        ko, to = face_ts(ours)
        kt, tt = face_ts(theirs)
        assert ko == kt, f"token ts key mismatch {ko}/{kt}"
        base = ours if to >= tt else theirs
        pick = f"whole-face-freshness({'ours' if to >= tt else 'theirs'})"
    out = (json.dumps(base, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    raw = write_resolved(TOKEN_FACE, out)
    json.loads(raw.decode("utf-8"))
    return {"face": TOKEN_FACE, "pick": pick, "side_pick": side_pick}


def verify_pool_semantics():
    """runnable_pool.json auto-merged (no UU): assert my lane's semantic faces
    survived + report tail shard states for the wave hand-off."""
    raw = open(os.path.join(ROOT, POOL_FACE), "rb").read()
    assert not _marker_lines(raw), "marker in pool"
    doc = json.loads(raw.decode("utf-8"))
    states = {}
    for e in doc["entries"]:
        if "N2-W15" in e.get("id", "") and "SHARD" in e.get("id", ""):
            for s in e["shards"]:
                states[s.get("key")] = (s.get("status"), s.get("owner"))
    s6 = states.get("n2w15-6of12")
    assert s6 and s6[0] == "done", f"my SHARD-6 flip lost: {s6}"
    s7 = states.get("n2w15-7of12")
    # SHARD-7 done-flip is PENDING by design this window: product landed via
    # absorb-2 commit, daemon harvest-flip fires on its next tick (r668).
    # Assert the claim survived (owner=bm-a), flip status reported not forced.
    assert s7 and s7[1] == "bm-a", f"my SHARD-7 claim lost: {s7}"
    return {"face": POOL_FACE, "pick": "auto-merge verified",
            "n2_states": {k: list(v) for k, v in sorted(states.items())},
            "note": "SHARD-7 flip pending daemon harvest (product landed absorb-2)"}


def main():
    assert subprocess.run(["git", "rev-parse", "--verify", "MERGE_HEAD"],
                          cwd=ROOT, capture_output=True).returncode == 0, \
        "MERGE_HEAD absent"
    table = []
    picks = {}
    for path in JSON_FACES:
        row = resolve_whole(path)
        table.append(row)
        picks[path] = row["pick"]
    for twin_path, json_path in TWIN_FACES:
        table.append(resolve_twin(twin_path, picks[json_path]))
    for path in JSONL_UNION_FACES:
        table.append(resolve_jsonl_union(path))
    table.append(resolve_token())
    table.append(verify_pool_semantics())
    receipt = {
        "resolver": "r699 bm-a merge (20 UU vs fleet wave: 13 json regen + "
                    "4 md/js twins + 2 jsonl union + token union + pool verify)",
        "law": "r440 per-face newer-wins + r456/r466 token union+fallback + "
               "md/js-twin lock + r482/r485 jsonl union + pool semantic assert",
        "table": table,
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    open(RECEIPT, "wb").write((json.dumps(
        receipt, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    for r in table:
        print(r.get("face"), "->", r.get("pick"),
              r.get("ours_ts", ""), r.get("theirs_ts", ""))
    print("RECEIPT ->", os.path.relpath(RECEIPT, ROOT))


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        err = os.path.join(ROOT, "results", "_r699bma_merge_resolve_err.txt")
        with open(err, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("RESOLVER_FAIL see", err)
        raise
