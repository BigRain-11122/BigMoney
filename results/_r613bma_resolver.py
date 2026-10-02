# r613 bm-a adoption resolver: finalize r612's dead-session rebase (final pick UU batch)
# Recipes per bigmoney-conflict-resolve skill:
#  - fundamental_b_layer_filter.json / _attrition_guard_scan.json: snapshot deep-ts probe take-new (tie -> :2: origin side, r140)
#  - docs/daily_report/REPORT-2026-10-03.{json,md}: twin-side coupling (json face decides side by deep ts; md copies same-side blob bytes)
#  - docs/live_usage/LIVE-2026-10-03.* + LIVE-latest.*: same twin law, one side for all 4 (same producer run)
#  - research/pit-git.md: append-only ledger byte-prefix union (base + HEAD suffix + replay suffix)
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
TS_KEYS = ("updated", "generated", "generated_at", "ts", "scanned_at", "asof", "run_at", "last_scan")


def stage_bytes(stage: int, path: str) -> bytes:
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {path} :{stage}: {r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kk = k.lower().replace("_", "").replace("-", "")
            if isinstance(v, str) and TS_RE.match(v) and any(kk.startswith(t.replace("_", "").replace("-", "")) for t in TS_KEYS):
                if v > best:
                    best = v
            nb = deep_ts(v, best)
            if nb > best:
                best = nb
    elif isinstance(obj, list):
        for it in obj:
            nb = deep_ts(it, best)
            if nb > best:
                best = nb
    return best


def write_bytes(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)
    print(f"  wrote {path} ({len(data)}B)")


def snapshot_take_new(path: str):
    ours, theirs = stage_bytes(2, path), stage_bytes(3, path)
    jo, jt = json.loads(ours), json.loads(theirs)
    to, tt = deep_ts(jo), deep_ts(jt)
    side = 3 if tt > to else 2  # tie (==) -> :2: origin/HEAD (r140)
    why = f"ours={to or 'NONE'} theirs={tt or 'NONE'} -> :{side}:" + (" (tie->HEAD)" if tt == to else "")
    print(f"[snapshot] {path}: {why}")
    write_bytes(path, theirs if side == 3 else ours)
    json.loads(open(path, "rb").read())  # parse-verify


def twin_pair(json_path: str, md_path: str, extra: list = None):
    ours, theirs = stage_bytes(2, json_path), stage_bytes(3, json_path)
    jo, jt = json.loads(ours), json.loads(theirs)
    to, tt = deep_ts(jo), deep_ts(jt)
    side = 3 if tt > to else 2
    print(f"[twin] {json_path}: ours={to} theirs={tt} -> :{side}:" + (" (tie->HEAD)" if tt == to else ""))
    write_bytes(json_path, theirs if side == 3 else ours)
    json.loads(open(json_path, "rb").read())
    if md_path:
        write_bytes(md_path, stage_bytes(side, md_path))
    for p in (extra or []):
        write_bytes(p, stage_bytes(side, p))


def union_append_md(path: str):
    base, ours, theirs = stage_bytes(1, path), stage_bytes(2, path), stage_bytes(3, path)
    assert theirs.startswith(base), f"{path}: :3: not byte-prefix of base"
    theirs_tail = theirs[len(base):]
    assert theirs_tail.strip(), f"{path}: empty :3: suffix"
    if ours.startswith(base):
        ours_tail = ours[len(base):]
        assert ours_tail.strip(), f"{path}: empty :2: suffix"
        merged = base + ours_tail
    else:
        # origin side edited mid-file too (r401 header 对账行): take :2: wholesale, append :3:'s unique tail
        merged = ours
        print(f"[union-md] {path}: :2: non-prefix (mid-file edits) -> take :2: wholesale + :3: tail")
    if not merged.endswith(b"\n") and not theirs_tail.startswith(b"\n"):
        merged += b"\n"
    merged += theirs_tail
    _CMBEG = bytes([0x3C] * 7)  # conflict marker literals are constructed, not embedded (pre-commit claw safety)
    _CMEND = bytes([0x3E] * 7)
    assert _CMBEG not in merged and _CMEND not in merged
    assert b"06:1x r605 bm-b" in merged and b"07:0x r612 bm-a" in merged, "union lost a side's row"
    write_bytes(path, merged)
    print(f"[union-md] {path}: base={len(base)}B ours={len(ours)}B theirs={len(theirs)}B -> merged={len(merged)}B (r605+r612 rows both kept)")


union_append_md("research/pit-git.md")
snapshot_take_new("results/fundamental_b_layer_filter.json")
snapshot_take_new("results/_attrition_guard_scan.json")
twin_pair("docs/daily_report/REPORT-2026-10-03.json", "docs/daily_report/REPORT-2026-10-03.md")
twin_pair("docs/live_usage/LIVE-2026-10-03.json", "docs/live_usage/LIVE-2026-10-03.md",
          extra=["docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"])
print("RESOLVER DONE rc=0")
