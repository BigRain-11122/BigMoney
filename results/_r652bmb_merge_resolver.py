# -*- coding: utf-8 -*-
# r652 bm-b merge resolver: intersecting S6 regen twin faces, my-worktree vs origin/main blob,
# ts-field honest compare (r640/r661 take-new-by-ts recipe). Zero judgment on non-ts faces:
# those default to origin-wins (regenerable same-day snapshots).
import json, subprocess, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def load_face(spec):
    # spec: ("file", path) -> read from worktree; ("blob", path) -> git show origin/main:path raw bytes
    kind, path = spec
    if kind == "file":
        try:
            with open(path, "rb") as f:
                return json.loads(f.read().decode("utf-8"))
        except Exception as e:
            return {"__err__": str(e)[:120]}
    else:
        p = subprocess.run(["git", "show", "origin/main:" + path],
                           capture_output=True, timeout=30)
        if p.returncode != 0:
            return {"__err__": "git show rc=%d" % p.returncode}
        try:
            return json.loads(p.stdout.decode("utf-8"))
        except Exception as e:
            return {"__err__": str(e)[:120]}

def find_ts(d):
    """Best-effort ts extraction: common keys at top level."""
    if not isinstance(d, dict):
        return None
    for k in ("ts", "updated", "updated_at", "generated_at", "asof", "asof_ts",
              "cutoff", "last_burn", "scan_ts", "epoch"):
        v = d.get(k)
        if isinstance(v, (int, float)) and v > 1e9:
            return ("epoch", v)
        if isinstance(v, str) and len(v) >= 10:
            return (k, v)
    return None

rows = []
for face in FACES:
    mine = load_face(("file", face))
    theirs = load_face(("blob", face))
    mts = find_ts(mine)
    tts = find_ts(theirs)
    # decide
    if "__err__" in mine and "__err__" in theirs:
        verdict = "BOTH-ERR skip"
    elif "__err__" in theirs:
        verdict = "ORIGIN-ERR keep-mine"
    elif "__err__" in mine:
        verdict = "MINE-ERR take-origin"
    else:
        if mts and tts:
            mk, mv = mts; tk, tv = tts
            if mk == tk and isinstance(mv, str) and isinstance(tv, str):
                verdict = "mine-newer" if mv > tv else ("origin-newer" if tv > mv else "EQUAL take-origin")
            elif mk == tk and isinstance(mv, (int, float)) and isinstance(tv, (int, float)):
                verdict = "mine-newer" if mv > tv else ("origin-newer" if tv > mv else "EQUAL take-origin")
            else:
                verdict = "ts-key-mismatch(%s vs %s) manual" % (mk, tk)
        else:
            verdict = "no-ts regen-twin take-origin"
    rows.append((face, mts, tts, verdict))
    print("%-52s mine=%s origin=%s -> %s" % (face, str(mts)[:40], str(tts)[:40], verdict))

take_origin = [r[0] for r in rows if r[3] in ("take-origin", "EQUAL take-origin", "origin-newer", "no-ts regen-twin take-origin", "MINE-ERR take-origin")]
keep_mine = [r[0] for r in rows if r[3] in ("mine-newer", "ORIGIN-ERR keep-mine")]
manual = [r[0] for r in rows if "manual" in r[3] or "BOTH-ERR" in r[3]]
print("---")
print("TAKE-ORIGIN faces:", len(take_origin))
print("KEEP-MINE faces:", len(keep_mine))
print("MANUAL faces:", len(manual), manual)
with open("results/_r652bmb_merge_resolver.json", "w", encoding="utf-8") as f:
    json.dump({"take_origin": take_origin, "keep_mine": keep_mine, "manual": manual,
               "rows": [{"face": r[0], "mine_ts": r[1], "origin_ts": r[2], "verdict": r[3]} for r in rows]},
              f, ensure_ascii=False, indent=1)
print("resolver evidence -> results/_r652bmb_merge_resolver.json")
