"""r494 bm-c merge resolver: 2 UU trio-probe faces (both machines ran the
trio watch / ETA probes this window -- bm-b r691 trio closeout vs bm-c r494
watch). Per-face whole-file newer-wins on top-level ts (r440 S6-regen face
law, r484 no-blind-side): dual-side raw bytes via git show HEAD:/MERGE_HEAD:
(r657-2 -- add never preceded, MERGE_HEAD alive), ts_norm compare (r461
T->space [:19]). Gates: reparse every resolved face + marker scan + receipt
table. Fail-closed: any gate failure -> exception BEFORE any add (r657-3).
Lineage: _r493bmc_merge_resolve.py verbatim adaptation (read per r461),
face set replaced with the actual r494 UU set, md-twin/token legs dropped
(not in this UU set)."""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_KEYS = ["ts", "generated", "generated_at", "updated", "updated_at",
           "probe_ts", "scan_ts", "asof"]

FACES = [
    "results/_r675bmb_trio_watch.json",
    "results/trio_burn_eta.json",
]
RECEIPT = os.path.join(ROOT, "results", "_r494bmc_merge_resolve.json")


def git_bytes(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git show {rev}:{path} rc={r.returncode} "
                           f"{r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


def ts_norm(v):
    return str(v).replace("T", " ")[:19]


DEEP_KEYS = set(TS_KEYS) | {"owner_since", "claimed_at", "ts_probe"}


def deep_max_ts(obj):
    """Recursive walk: collect all timestamp-ish values, return the max
    (norm form). For deeply nested probe faces (trio_watch shape:
    pool_trio.<fam>.shards[].owner_since at depth 3)."""
    best = ""
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if k in DEEP_KEYS and isinstance(v, (str, int, float)):
                    n = ts_norm(v)
                    if len(n) >= 10 and n > best:
                        best = n
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            for it in cur:
                if isinstance(it, (dict, list)):
                    stack.append(it)
    return best


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
    # deep walk fallback (r494 live extension: trio_watch depth-3 shape)
    m = deep_max_ts(obj)
    if m:
        return "deep_max_ts", m
    return None, None


def resolve_whole(path):
    ours_b = git_bytes("HEAD", path)
    theirs_b = git_bytes("MERGE_HEAD", path)
    ours = json.loads(ours_b.decode("utf-8"))
    theirs = json.loads(theirs_b.decode("utf-8"))
    ko, to = face_ts(ours)
    kt, tt = face_ts(theirs)
    if ko is None or kt is None:
        raise RuntimeError(f"{path}: no ts key found ours={ko} theirs={kt}")
    if ko != kt:
        raise RuntimeError(f"{path}: ts key mismatch ours={ko} theirs={kt}")
    pick = "ours" if to >= tt else "theirs"
    data = ours_b if pick == "ours" else theirs_b
    open(os.path.join(ROOT, path), "wb").write(data)
    raw = open(os.path.join(ROOT, path), "rb").read()
    json.loads(raw.decode("utf-8"))
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw
    return {"face": path, "ts_key": ko, "ours_ts": to, "theirs_ts": tt,
            "pick": pick}


def main():
    assert subprocess.run(["git", "rev-parse", "--verify", "MERGE_HEAD"],
                          cwd=ROOT, capture_output=True).returncode == 0, \
        "MERGE_HEAD absent"
    table = []
    for path in FACES:
        table.append(resolve_whole(path))
    receipt = {
        "resolver": "r494 bm-c merge (2 UU trio-probe faces)",
        "law": "r440 S6-regen per-face newer-wins + r484 no-blind-side",
        "table": table,
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    open(RECEIPT, "wb").write((json.dumps(
        receipt, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(json.dumps(table, ensure_ascii=False, indent=1))
    print("RECEIPT ->", os.path.relpath(RECEIPT, ROOT))


if __name__ == "__main__":
    main()
