"""r696 bm-b merge resolver: 17 UU faces vs bm-c r497/r498 + bm-a r698 waves.
Laws: r440 per-face newer-wins + r484 no-blind-side + r657-2 dual-side raw
bytes via git show HEAD:/MERGE_HEAD: (MERGE_HEAD alive, add never precedes)
+ r461 ts_norm + r456/r466 token per-key union side_pick>0 assert +
freshness fallback + md/js-twins locked to their json pick + r675/r479/r453
CODELY block-union (origin verbatim + my unique lines, containment filter,
origin structure not reduced, my marker exactly once) + pool auto-merge
double-change assert (bm-a N2 SHARD-3 done-flip + my CONTEST-RC/SHARD-2
claims survive). Fail-closed BEFORE any add (r657-3; add = separate single
batch step per r673). Lineage: _r694bmb_merge_resolve.py adaptation (canon
read per r461); r696 deltas = (a) CODELY union leg (new this window),
(b) pool assert re-targeted to N2-W15 SHARD-3 done + my claim faces.  """
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
]
TWIN_FACES = [  # twin face -> its json face (pick follows the json twin)
    ("docs/daily_report/REPORT-2026-10-04.md", "docs/daily_report/REPORT-2026-10-04.json"),
    ("docs/live_usage/LIVE-2026-10-04.md", "docs/live_usage/LIVE-2026-10-04.json"),
    ("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"),
]
TOKEN_FACE = "results/token_usage.json"
CODELY_FACE = "CODELY.md"
POOL_FACE = "results/runnable_pool.json"
MY_CODELY_MARK = "r696 bm-b] ls-tree"
RECEIPT = os.path.join(ROOT, "results", "_r696bmb_merge_resolve.json")


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
    """Depth-first search for first TS_KEYS hit; returns (keypath, norm)."""
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
    """r453 law: marker judgment by LINE-START, never substring -- pit text
    legally embeds '<<<<<<<' literals (r657 L68 precedent)."""
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


def resolve_codely():
    """r675 block-union + r479 containment filter: MERGE_HEAD verbatim as
    base, append my-side lines absent from theirs (byte-containment skip),
    keep my entry exactly once, origin structure not reduced."""
    ours_b = git_bytes("HEAD", CODELY_FACE)
    theirs_b = git_bytes("MERGE_HEAD", CODELY_FACE)
    assert not _marker_lines(ours_b) and not _marker_lines(theirs_b), \
        "side blob has line-start marker (r453)"
    ours_txt = ours_b.decode("utf-8")
    theirs_txt = theirs_b.decode("utf-8")
    ours_lines = ours_txt.split("\n")
    theirs_lines = theirs_txt.split("\n")
    # r419 furniture guard: blank lines match both sides trivially -- only
    # non-blank lines participate in the union math (base_idx scan over raw
    # lines lets the trailing "" push the anchor past real new entries).
    theirs_set = {l for l in theirs_lines if l.strip()}
    missing = []
    for ln in ours_lines:
        if not ln.strip():
            continue
        if ln in theirs_set or ln in theirs_txt:  # r479 containment
            continue
        missing.append(ln)
    out_lines = list(theirs_lines)
    while out_lines and out_lines[-1] == "":
        out_lines.pop()
    out_lines.extend(missing)
    out_txt = "\n".join(out_lines) + "\n"
    raw = write_resolved(CODELY_FACE, out_txt.encode("utf-8"))
    # assertions
    assert raw.count(MY_CODELY_MARK.encode("utf-8")) == 1, "my CODELY entry must appear exactly once"
    t_struct = len([l for l in theirs_lines if l.strip()])
    o_struct = len([l for l in out_lines if l.strip()])
    assert o_struct >= t_struct, "origin structure reduced (r675 collapse guard)"
    for ln in missing:
        assert out_txt.count(ln) == 1, f"double-recorded line: {ln[:60]}"
    return {"face": CODELY_FACE, "pick": "block-union(origin-verbatim+my-unique)",
            "my_new_lines": len(missing),
            "theirs_struct_lines": t_struct, "union_struct_lines": o_struct}


def verify_pool_double_change():
    """runnable_pool.json auto-merged (no UU): assert BOTH sides' semantic
    changes survived -- (bm-a r697-698) PERPETUAL-N2-W15-SHARD-3 done-flip
    (outcome=ok claim-by-file O-2210), (mine) CONTEST-YTD-P1-RC-0OF1 claim
    owner=bm-b + N2-W15 SHARD-2 claim owner=bm-b."""
    raw = open(os.path.join(ROOT, POOL_FACE), "rb").read()
    assert not _marker_lines(raw), "marker in pool"
    doc = json.loads(raw.decode("utf-8"))
    e_n23 = [x for x in doc["entries"] if x.get("id") == "PERPETUAL-N2-W15-SHARD-3"]
    assert len(e_n23) == 1, "N2 SHARD-3 entry missing"
    s3 = e_n23[0]["shards"][0]
    assert s3.get("status") == "done", f"bm-a SHARD-3 done-flip lost: {s3.get('status')}"
    e_rc = [x for x in doc["entries"] if x.get("id") == "CONTEST-YTD-P1-RC-0OF1"]
    assert len(e_rc) == 1 and e_rc[0]["shards"][0].get("owner") == "bm-b", \
        "my CONTEST-RC claim lost"
    e_n22 = [x for x in doc["entries"] if x.get("id") == "PERPETUAL-N2-W15-SHARD-2"]
    assert len(e_n22) == 1 and e_n22[0]["shards"][0].get("owner") == "bm-b", \
        "my N2 SHARD-2 claim lost"
    return {"face": POOL_FACE, "pick": "auto-merge verified",
            "n2_s3_status": s3.get("status"),
            "rc_owner": e_rc[0]["shards"][0].get("owner"),
            "n2_s2_owner": e_n22[0]["shards"][0].get("owner")}


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
    table.append(resolve_token())
    table.append(resolve_codely())
    table.append(verify_pool_double_change())
    receipt = {
        "resolver": "r696 bm-b merge (17 UU vs bm-c r497/498 + bm-a r698 waves: "
                    "12 json regen + 3 md twins + token union + CODELY block-union)",
        "law": "r440 per-face newer-wins + r456/r466 token union+fallback + "
               "md/js-twin lock + r675/r479/r453 CODELY block-union + pool "
               "double-change assert",
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
        err = os.path.join(ROOT, "results", "_r696bmb_merge_resolve_err.txt")
        with open(err, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("RESOLVER_FAIL see", err)
        raise
