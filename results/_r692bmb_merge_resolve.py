"""r692 bm-b merge resolver: 14 UU S6 shared-regen faces (push-race vs bm-c
r494 concurrent close). Laws: r440 S6-regen per-face newer-wins + r484
no-blind-side + r657-2 dual-side raw bytes via git show HEAD:/MERGE_HEAD:
(MERGE_HEAD alive, add never precedes) + r461 ts_norm (T->space [:19]) +
r456/r466 token_usage per-key union with side_pick>0 assert and whole-face
freshness fallback + md-twins locked to their json pick (twin consistency).
Gates: reparse every resolved json + marker scan (line-start per r453) +
receipt table. Fail-closed: any gate failure -> exception BEFORE any add
(r657-3; add happens in a separate later step, single batch call per r673).
Lineage: _r494bmc_merge_resolve.py verbatim adaptation (read per r461),
face set = actual r692 UU set."""
import datetime
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_KEYS = ["ts", "generated", "generated_at", "updated", "updated_at",
           "probe_ts", "scan_ts", "asof"]

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
    "results/update_status.json",
]
MD_TWINS = [  # md face -> its json face (pick follows the json twin)
    ("docs/daily_report/REPORT-2026-10-04.md", "docs/daily_report/REPORT-2026-10-04.json"),
    ("docs/live_usage/LIVE-2026-10-04.md", "docs/live_usage/LIVE-2026-10-04.json"),
    ("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json"),
]
TOKEN_FACE = "results/token_usage.json"
RECEIPT = os.path.join(ROOT, "results", "_r692bmb_merge_resolve.json")


def git_bytes(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={r.returncode} "
                           f"{r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


def ts_norm(v):
    return str(v).replace("T", " ")[:19]


def face_ts(obj):
    for k in TS_KEYS:
        if k in obj and isinstance(obj[k], (str, int, float)):
            return k, ts_norm(obj[k])
    for holder in ("latest", "status", "state"):
        sub = obj.get(holder)
        if isinstance(sub, dict):
            for k in TS_KEYS:
                if k in sub and isinstance(sub[k], (str, int, float)):
                    return f"{holder}.{k}", ts_norm(sub[k])
    raise RuntimeError("no ts key found")


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
    ko, to = face_ts(ours)
    kt, tt = face_ts(theirs)
    if ko != kt:
        raise RuntimeError(f"{path}: ts key mismatch ours={ko} theirs={kt}")
    pick = "ours" if to >= tt else "theirs"
    write_resolved(path, ours_b if pick == "ours" else theirs_b)
    json.loads(open(os.path.join(ROOT, path), "rb").read().decode("utf-8"))
    return {"face": path, "ts_key": ko, "ours_ts": to, "theirs_ts": tt,
            "pick": pick}


def resolve_md_twin(md_path, json_pick):
    """Twin-locked: md follows its json twin's pick (single generator, one
    ts). Validation = marker-free + non-empty."""
    data = git_bytes("HEAD" if json_pick == "ours" else "MERGE_HEAD", md_path)
    raw = write_resolved(md_path, data)
    assert len(raw) > 0
    for ln in raw.decode("utf-8", errors="replace").splitlines():
        assert not ln.startswith("<<<<<<<") and not ln.startswith(">>>>>>>"), \
            f"marker line in {md_path}"
    return {"face": md_path, "pick": json_pick + " (twin-locked)"}


def resolve_token():
    """r456/r466 canon: machines per-key union (own rows canonical, side-pick
    count asserted >0), rest = whole-face ts freshness fallback."""
    ours_b = git_bytes("HEAD", TOKEN_FACE)
    theirs_b = git_bytes("MERGE_HEAD", TOKEN_FACE)
    ours = json.loads(ours_b.decode("utf-8"))
    theirs = json.loads(theirs_b.decode("utf-8"))
    side_pick = 0
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
        # r456 fallback: whole-face freshness key
        ko, to = face_ts(ours)
        kt, tt = face_ts(theirs)
        assert ko == kt, f"token ts key mismatch {ko}/{kt}"
        base = ours if to >= tt else theirs
        pick = f"whole-face-freshness({'ours' if to >= tt else 'theirs'})"
    out = (json.dumps(base, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    raw = write_resolved(TOKEN_FACE, out)
    json.loads(raw.decode("utf-8"))
    return {"face": TOKEN_FACE, "pick": pick, "side_pick": side_pick}


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
    for md_path, json_path in MD_TWINS:
        table.append(resolve_md_twin(md_path, picks[json_path]))
    table.append(resolve_token())
    receipt = {
        "resolver": "r692 bm-b merge (14 UU S6 shared-regen faces vs bm-c r494)",
        "law": "r440 per-face newer-wins + r484 no-blind-side + r456/r466 token union+fallback + md-twin lock",
        "table": table,
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    open(RECEIPT, "wb").write((json.dumps(
        receipt, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(json.dumps(table, ensure_ascii=False, indent=1))
    print("RECEIPT ->", os.path.relpath(RECEIPT, ROOT))


if __name__ == "__main__":
    main()
