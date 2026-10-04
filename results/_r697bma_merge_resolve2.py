"""r697 bm-a merge resolver wave-2: 16 UU regen-twin faces from bm-b r694
+ bm-c r497 wave. Canon:
- 15 whole-face ts-newer-wins: ours S6 chain ran 21:03-21:10 vs theirs
  21:02-21:03 (probe receipts in round log). daily_scorecard ts lives in
  traders[].forward_guard.as_of (nested list) -- probed explicitly.
- crash_fuse.json: per-sig max-merge (r696 canon). 4 leaf diffs only,
  all ours-max/newer (refusals 13>8, last_refusal 21:00:04>20:46:04,
  cleared_ts 21:02:04>21:00:22). Structural deep-merge with numeric max
  for counters, string ts lex-compare newer-wins, keyset union.
Fail-closed: abort without write on any assertion failure.
"""
import json
import subprocess

WHOLE_FACE = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def side(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"],
                           capture_output=True).stdout


def scorecard_ts(d):
    try:
        return d["traders"][0]["forward_guard"]["as_of"]
    except Exception:
        return ""


def resolve_whole(path):
    a = side("HEAD", path)
    if path.endswith(".json"):
        ja = json.loads(a.decode("utf-8"))
        jb = json.loads(side("MERGE_HEAD", path).decode("utf-8"))
        ta = scorecard_ts(ja) if "scorecard" in path else None
        tb = scorecard_ts(jb) if "scorecard" in path else None
        if ta is not None:
            assert ta >= tb, f"{path}: theirs newer ({ta} vs {tb})"
            print(f"[ours-wins] {path} (as_of {ta} >= {tb})")
    with open(path, "wb") as fh:
        fh.write(a)
    if path.endswith(".json"):
        json.loads(open(path, "rb").read().decode("utf-8"))


def merge_sig(a, b):
    """recursive per-sig max-merge: numbers -> max, strings -> lex newer,
    dicts -> keyset union recurse, else ours."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in set(a) | set(b):
            if k in a and k in b:
                out[k] = merge_sig(a[k], b[k])
            else:
                out[k] = a.get(k, b.get(k))
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) \
            and not isinstance(a, bool) and not isinstance(b, bool):
        return a if a >= b else b
    if isinstance(a, str) and isinstance(b, str):
        return a if a >= b else b
    return a if a is not None else b


def resolve_fuse():
    path = "results/crash_fuse.json"
    ja = json.loads(side("HEAD", path).decode("utf-8"))
    jb = json.loads(side("MERGE_HEAD", path).decode("utf-8"))
    m = merge_sig(ja, jb)
    # prove: only the 4 known leaf diffs, product carries ours on all 4
    fa, fb = _flat(ja), _flat(jb)
    fm = _flat(m)
    diffs = [k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k)]
    assert sorted(diffs) == sorted([
        "/cleared/scripts/contest_ytd_legs.py|revcensus/cleared_by",
        "/cleared/scripts/contest_ytd_legs.py|revcensus/cleared_ts",
        "/sigs/scripts/perpetual_faces_n2.py|generate/last_refusal_ts",
        "/sigs/scripts/perpetual_faces_n2.py|generate/refusals"]), diffs
    for k in diffs:
        va, vb = fa.get(k), fb.get(k)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) \
                and not isinstance(va, bool) and not isinstance(vb, bool):
            expect = va if va >= vb else vb          # numeric max
        else:
            expect = va if str(va) >= str(vb) else vb  # string lex-newer
        assert fm[k] == expect, (k, fm[k], expect)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1)
    json.loads(open(path, "rb").read().decode("utf-8"))
    print(f"[per-sig max-merge] {path}: 4 known leaf diffs -> "
          f"ours (13>8 refusals, ts 21:00:04>20:46:04, "
          f"cleared 21:02:04>21:00:22)")


def _flat(d, p=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (int, str, float)) and not isinstance(v, bool):
                out[p + "/" + k] = v
            else:
                out.update(_flat(v, p + "/" + k))
    return out


def main():
    for p in WHOLE_FACE:
        resolve_whole(p)
    resolve_fuse()
    print("RESOLVE OK 16/16")


if __name__ == "__main__":
    main()
