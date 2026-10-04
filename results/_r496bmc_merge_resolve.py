"""r496 bm-c merge resolver: 31 UU S6 shared-regen faces (push-race vs bm-a
r695/r696 wave + bm-b keepalive, mirror of r495's 31-face case). Laws: r440
per-face newer-wins + r484 no-blind-side + r657-2 dual-side raw bytes via git
show HEAD:/MERGE_HEAD: (MERGE_HEAD alive, add never precedes) + r461 ts_norm
+ r456/r466 token per-key union side_pick>0 assert + freshness fallback +
md/js-twins locked to their json pick + r656 x2_watch append-only line-level
union (canon \\n sets, keep-first, containment both sides) + deep-embedded
ts scan (r494 deep-nested leg). Fail-closed BEFORE any add (r657-3; add =
separate single batch step per r673). Lineage: _r495bmc_merge_resolve.py
verbatim adaptation (read per r461), only round labels + receipt path."""
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
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
TWIN_FACES = [  # twin face -> its json face (pick follows the json twin)
    ("docs/daily_report/REPORT-2026-10-04.md", "docs/daily_report/REPORT-2026-10-04.json"),
    ("docs/live_usage/LIVE-2026-10-04.md", "docs/live_usage/LIVE-2026-10-04.json"),
    ("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"),
    ("results/dashboard_status.js", "results/dashboard_status.json"),
]
TOKEN_FACE = "results/token_usage.json"
X2_FACE = "results/x2_watch_log.jsonl"
RECEIPT = os.path.join(ROOT, "results", "_r496bmc_merge_resolve.json")


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


def write_resolved(path, data):
    open(os.path.join(ROOT, path), "wb").write(data)
    raw = open(os.path.join(ROOT, path), "rb").read()
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, f"marker in {path}"
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


def resolve_x2_union():
    """r656 law: append-only jsonl line-level union on canon \\n sets,
    keep-first dedup, containment both sides, zero-dup after union."""
    ours_b = git_bytes("HEAD", X2_FACE)
    theirs_b = git_bytes("MERGE_HEAD", X2_FACE)
    ours_lines = ours_b.decode("utf-8", "replace").split("\n")
    theirs_lines = theirs_b.decode("utf-8", "replace").split("\n")
    seen = set()
    out_lines = []
    for ln in ours_lines + theirs_lines:
        if ln not in seen:
            seen.add(ln)
            out_lines.append(ln)
    # containment both sides (canon line sets)
    assert set(l for l in ours_lines if l.strip()) <= set(l for l in out_lines if l.strip())
    assert set(l for l in theirs_lines if l.strip()) <= set(l for l in out_lines if l.strip())
    assert len([l for l in out_lines if l.strip()]) == \
        len(set(l for l in out_lines if l.strip())), "dup non-blank line after union"
    out = ("\n".join(out_lines)).encode("utf-8")
    raw = write_resolved(X2_FACE, out)
    n_o = len([l for l in ours_lines if l.strip()])
    n_t = len([l for l in theirs_lines if l.strip()])
    n_u = len([l for l in out_lines if l.strip()])
    return {"face": X2_FACE, "pick": "line-union(keep-first)",
            "ours_n": n_o, "theirs_n": n_t, "union_n": n_u}


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
    table.append(resolve_x2_union())
    receipt = {
        "resolver": "r496 bm-c merge (31 UU S6 shared-regen faces vs bm-a r695/r696 wave + bm-b keepalive)",
        "law": "r440 per-face newer-wins + r456/r466 token union+fallback + md/js-twin lock + r656 x2 line-union",
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
        err = os.path.join(ROOT, "results", "_r496bmc_merge_resolve_err.txt")
        with open(err, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("RESOLVER_FAIL see", err)
        raise
