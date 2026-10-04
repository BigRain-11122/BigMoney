"""r493 bm-c merge resolver WAVE-2: 22 UU faces from bm-a r694 integration
(third push-race wave this window). Same law family as wave-1 (r440 per-face
newer-wins / r484 no-blind-side / r678 roundtrip gate / r656 line-union
zero-loss). Dual-side raw bytes via git show HEAD:/MERGE_HEAD: (r657-2).
Face map:
  - ts whole-face: 15 json faces (auto-detect top-level + latest./meta.
    holders + generated_from_state_updated)
  - dashboard_status.js: own embedded generated_at regex newer-wins
  - daily_scorecard.json: whole-face ours on derived-input coherence (only
    top-level diff = traders rows; all upstream faces resolved ours this
    wave -- probe receipt _r493bmc_noTts_probe)
  - token_usage.json: per-key union w/ r678 roundtrip gate fallback
  - x2_watch_log.jsonl: structured tail-union (shared-prefix assert +
    chronological theirs-tail then ours-tail) w/ zero-loss containment
Gates: reparse + marker scan on every resolved face. Fail-closed before
any add (r657-3). Receipt -> results/_r493bmc_merge_resolve2.json"""
import datetime
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_KEYS = ["ts", "generated", "generated_at", "generated_from_state_updated",
           "updated", "updated_at", "probe_ts", "scan_ts", "asof"]
HOLDERS = ("latest", "status", "state", "meta")

TS_FACES = [
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.json",
    "results/futures_update_status.json",
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
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
JS_FACE = "results/dashboard_status.js"
COHERENCE_FACES = {"results/daily_scorecard.json":
                   "whole-face ours (derived-input coherence: only top-level "
                   "diff = traders rows; all upstream picks ours this wave)"}
TOKEN_FACE = "results/token_usage.json"
JSONL_FACE = "results/x2_watch_log.jsonl"
RECEIPT = os.path.join(ROOT, "results", "_r493bmc_merge_resolve2.json")


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
    for h in HOLDERS:
        sub = obj.get(h)
        if isinstance(sub, dict):
            for k in TS_KEYS:
                if k in sub and isinstance(sub[k], (str, int, float)):
                    return f"{h}.{k}", ts_norm(sub[k])
    return None, None


def write_and_gate(path, data):
    open(os.path.join(ROOT, path), "wb").write(data)
    raw = open(os.path.join(ROOT, path), "rb").read()
    if path.endswith(".json"):
        json.loads(raw.decode("utf-8"))
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, f"markers {path}"


def resolve_whole(path):
    ours_b, theirs_b = git_bytes("HEAD", path), git_bytes("MERGE_HEAD", path)
    ko, to = face_ts(json.loads(ours_b.decode("utf-8")))
    kt, tt = face_ts(json.loads(theirs_b.decode("utf-8")))
    if ko is None or kt is None or ko != kt:
        raise RuntimeError(f"{path}: ts detect fail ours={ko} theirs={kt}")
    pick = "ours" if to >= tt else "theirs"
    write_and_gate(path, ours_b if pick == "ours" else theirs_b)
    return {"face": path, "ts_key": ko, "ours_ts": to, "theirs_ts": tt,
            "pick": pick}


def resolve_js(path):
    ours_b, theirs_b = git_bytes("HEAD", path), git_bytes("MERGE_HEAD", path)
    pat = re.compile(r'"generated_at":\s*"([^"]+)"')
    mo, mt = pat.search(ours_b.decode("utf-8")), pat.search(
        theirs_b.decode("utf-8"))
    assert mo and mt, "generated_at not found in dashboard_status.js"
    to, tt = ts_norm(mo.group(1)), ts_norm(mt.group(1))
    pick = "ours" if to >= tt else "theirs"
    write_and_gate(path, ours_b if pick == "ours" else theirs_b)
    return {"face": path, "ts_key": "embedded generated_at",
            "ours_ts": to, "theirs_ts": tt, "pick": pick}


def resolve_coherence(path, note):
    ours_b = git_bytes("HEAD", path)
    o = json.loads(ours_b.decode("utf-8"))
    t = json.loads(git_bytes("MERGE_HEAD", path).decode("utf-8"))
    assert set(o) == set(t), "coherence face top keys differ"
    diff = [k for k in o if o[k] != t[k]]
    assert diff == ["traders"], ("unexpected diff scope", diff)
    write_and_gate(path, ours_b)
    return {"face": path, "mode": note, "diff_scope": diff, "pick": "ours"}


def resolve_token(path):
    ours_b, theirs_b = git_bytes("HEAD", path), git_bytes("MERGE_HEAD", path)
    o_gen = ts_norm(json.loads(ours_b.decode("utf-8")).get("generated", ""))
    t_gen = ts_norm(json.loads(theirs_b.decode("utf-8")).get("generated", ""))
    rt_ok = all(
        (json.dumps(json.loads(b.decode("utf-8")), ensure_ascii=False,
                    indent=1) + "\n").encode("utf-8") == b
        for b in (ours_b, theirs_b))
    pick = "ours" if o_gen >= t_gen else "theirs"
    mode = "per-key union"
    if not rt_ok:
        mode = f"WHOLE-FACE FALLBACK (roundtrip non-identity, r678)"
        write_and_gate(path, ours_b if pick == "ours" else theirs_b)
    else:
        o = json.loads(ours_b.decode("utf-8"))
        t = json.loads(theirs_b.decode("utf-8"))
        merged, side_pick = {}, 0
        for k in o:
            a, b = o[k], t[k]
            if k == "machines" and isinstance(a, dict) and isinstance(b, dict):
                # owner-map: -bm-c row authoritative in OURS (our regen);
                # -bm-a row authoritative in THEIRS (bm-a r694 regen);
                # -bm-b row: OURS side carries bm-b's authoritative row
                # (inherited via wave-1 merge of bm-b r690 closeout).
                own = {"-bm-c": "o", "-bm-a": "t", "-bm-b": "o"}
                mm = {}
                for mk in sorted(set(a) | set(b)):
                    src = own.get(mk, "o")
                    if src == "o":
                        mm[mk] = a.get(mk, b.get(mk))
                    else:
                        mm[mk] = b.get(mk, a.get(mk))
                    side_pick += 1
                merged[k] = mm
            elif k == "generated":
                merged[k] = max(str(a), str(b))
            else:
                merged[k] = a if a == b else (
                    b if t_gen > o_gen else a)
                if a != b:
                    side_pick += 1
        assert side_pick > 0, "per-key side-pick zero"
        data = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
        write_and_gate(path, data + b"\n")
    return {"face": path, "mode": mode, "ours_generated": o_gen,
            "theirs_generated": t_gen, "pick": pick}


def resolve_jsonl(path):
    ours_b, theirs_b = git_bytes("HEAD", path), git_bytes("MERGE_HEAD", path)
    # byte-level line canon (r656): split on b"\n"; CRLF lines keep their
    # embedded b"\r"; join with b"\n" only (join-with-CRLF would double \r)
    o_lines = ours_b.split(b"\n")
    t_lines = theirs_b.split(b"\n")
    o_nz = [l for l in o_lines if l.strip()]
    t_nz = [l for l in t_lines if l.strip()]
    o_set, t_set = set(o_nz), set(t_nz)
    o_only = [l for l in o_nz if l not in t_set]
    t_only = [l for l in t_nz if l not in o_set]
    shared_n = len(o_nz) - len(o_only)
    # structural asserts: shared block is identical prefix in BOTH files
    assert o_nz[:shared_n] == t_nz[:shared_n], "shared prefix mismatch"
    assert o_nz[shared_n:] == o_only, "ours tail not pure ours-only"
    assert t_nz[shared_n:] == t_only, "theirs tail not pure theirs-only"

    def ts_of(line):
        s = line.decode("utf-8", "replace").strip()
        if not s:
            return ""
        return ts_norm(json.loads(s).get("ts", ""))

    if t_only and o_only:
        assert max(ts_of(l) for l in t_only) < min(ts_of(l) for l in o_only), \
            "tails not chronologically disjoint"
    merged = o_nz[:shared_n] + t_only + o_only
    # zero-loss containment proof (r656)
    m_set = set(merged)
    assert o_set <= m_set and t_set <= m_set, "union lost lines"
    assert len(merged) == len(m_set), "union produced dup lines"
    data = b"\n".join(merged)
    if ours_b.endswith(b"\n"):
        data += b"\n"
    write_and_gate(path, data)
    return {"face": path, "mode": "structured tail-union (r656 zero-loss)",
            "shared": shared_n, "ours_only": len(o_only),
            "theirs_only": len(t_only), "merged_lines": len(merged),
            "pick": "union"}


def main():
    assert subprocess.run(["git", "rev-parse", "--verify", "MERGE_HEAD"],
                          cwd=ROOT, capture_output=True).returncode == 0, \
        "MERGE_HEAD absent"
    table = []
    for p in TS_FACES:
        table.append(resolve_whole(p))
    table.append(resolve_js(JS_FACE))
    for p, note in COHERENCE_FACES.items():
        table.append(resolve_coherence(p, note))
    table.append(resolve_token(TOKEN_FACE))
    table.append(resolve_jsonl(JSONL_FACE))
    receipt = {"resolver": "r493 bm-c merge WAVE-2 (22 UU, bm-a r694 wave)",
               "table": table,
               "ts": datetime.datetime.now().isoformat(timespec="seconds")}
    open(RECEIPT, "wb").write((json.dumps(
        receipt, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(json.dumps(table, ensure_ascii=False, indent=1))
    print("RECEIPT ->", os.path.relpath(RECEIPT, ROOT))


if __name__ == "__main__":
    main()
