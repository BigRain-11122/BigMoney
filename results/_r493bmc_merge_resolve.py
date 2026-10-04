"""r493 bm-c merge resolver: 13 UU shared S6-regen faces (both machines ran
the same canon S6 chain this window -- classic r484 bm-a r693 shape).
Per-face whole-file newer-wins on top-level ts (r440 S6-regen face law,
r484 no-blind-side law): dual-side raw bytes via git show HEAD:/MERGE_HEAD:
(r657-2 -- add never preceded, MERGE_HEAD alive), ts_norm compare (r461
T->space [:19]), md twins follow json, token_usage per-key union with
side_pick>0 assert + whole-face ts fallback (r456/r466 lineage).
Gates: reparse every resolved face + marker scan + receipt table.
Fail-closed: any gate failure -> exception BEFORE any add (r657-3)."""
import datetime
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_KEYS = ["ts", "generated", "generated_at", "updated", "updated_at",
           "probe_ts", "scan_ts", "asof"]

# face -> ts key override (after inspection of both sides, printed in table)
FACES = {
    "docs/daily_report/REPORT-2026-10-04.json": None,      # auto-detect
    "docs/live_usage/LIVE-2026-10-04.json": None,
    "docs/live_usage/LIVE-latest.json": None,
    "results/_attrition_guard_scan.json": None,
    "results/compute_audit.json": None,
    "results/fundamental_b_layer_filter.json": None,
    "results/futures_update_status.json": None,
    "results/lhb_update_status.json": None,
    "results/regime_state.json": None,
    "results/update_status.json": None,
    "results/token_usage.json": "SPECIAL_TOKEN",
}
MD_TWINS = {
    "docs/daily_report/REPORT-2026-10-04.md":
        "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md":
        "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md":
        "docs/live_usage/LIVE-latest.json",
}
RECEIPT = os.path.join(ROOT, "results", "_r493bmc_merge_resolve.json")


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
    # nested holder fallback (compute_audit.json shape: {"latest": {...}})
    for holder in ("latest", "status", "state"):
        sub = obj.get(holder)
        if isinstance(sub, dict):
            for k in TS_KEYS:
                if k in sub and isinstance(sub[k], (str, int, float)):
                    return f"{holder}.{k}", ts_norm(sub[k])
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
    # gate: reparse + marker scan
    raw = open(os.path.join(ROOT, path), "rb").read()
    json.loads(raw.decode("utf-8"))
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw
    return {"face": path, "ts_key": ko, "ours_ts": to, "theirs_ts": tt,
            "pick": pick}


def resolve_token(path):
    ours_b = git_bytes("HEAD", path)
    theirs_b = git_bytes("MERGE_HEAD", path)
    ours = json.loads(ours_b.decode("utf-8"))
    theirs = json.loads(theirs_b.decode("utf-8"))
    assert set(ours.keys()) == set(theirs.keys()), "token top keys differ"
    # r678 roundtrip gate: only rewrite via load-dump if BOTH sides
    # roundtrip byte-identical with our writer format; else fall back to
    # whole-face newer-wins by generated (no rewrite, zero pseudo-diff).
    rt_ok = True
    for side_b in (ours_b, theirs_b):
        obj = json.loads(side_b.decode("utf-8"))
        if (json.dumps(obj, ensure_ascii=False, indent=1)
                + "\n").encode("utf-8") != side_b:
            rt_ok = False
            break
    o_gen = str(ours.get("generated", ""))
    t_gen = str(theirs.get("generated", ""))
    if not rt_ok:
        pick = "ours" if o_gen >= t_gen else "theirs"
        data = ours_b if pick == "ours" else theirs_b
        open(os.path.join(ROOT, path), "wb").write(data)
        raw = open(os.path.join(ROOT, path), "rb").read()
        json.loads(raw.decode("utf-8"))
        assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw
        return {"face": path, "mode": "WHOLE-FACE FALLBACK (roundtrip "
                "non-identity, r678)", "ours_generated": o_gen,
                "theirs_generated": t_gen, "pick": pick}
    side_pick = 0
    merged = {}
    machine_owner_pick = {}
    for k in ours:
        o, t = ours[k], theirs[k]
        if k == "machines" and isinstance(o, dict) and isinstance(t, dict):
            mm = {}
            for mk in sorted(set(o) | set(t)):
                if mk == "-bm-c":      # ours owns our row
                    mm[mk] = o.get(mk, t.get(mk))
                    side_pick += 1
                elif mk == "-bm-b":   # theirs owns their row
                    mm[mk] = t.get(mk, o.get(mk))
                    side_pick += 1
                else:                 # third-party rows: newer observation wins
                    ro, rt = o.get(mk), t.get(mk)
                    if ro is None:
                        mm[mk] = rt
                    elif rt is None:
                        mm[mk] = ro
                    else:
                        mm[mk] = t if (t_gen >= o_gen) else o
                    if ro != t.get(mk):
                        side_pick += 1
                machine_owner_pick[mk] = "ours" if mm[mk] is o.get(mk) else "theirs"
            merged[k] = mm
        elif k in ("generated",):
            merged[k] = max(str(o), str(t))       # wall-clock newer wins
        elif k == "delta_vs_prev":
            merged[k] = ours[k]                   # ours regenerated last
        elif o == t:
            merged[k] = o
        else:
            # scalar drift: take side with newer generated
            merged[k] = theirs[k] if t_gen > o_gen else ours[k]
            side_pick += 1
    assert side_pick > 0, ("per-key side-pick zero -> r456 explicit "
                           "fallback required")
    data = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
    open(os.path.join(ROOT, path), "wb").write(data + b"\n")
    raw = open(os.path.join(ROOT, path), "rb").read()
    json.loads(raw.decode("utf-8"))
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw
    return {"face": path, "mode": "per-key union (owner-row + ts newer-wins)",
            "side_pick": side_pick,
            "ours_generated": o_gen,
            "theirs_generated": t_gen,
            "pick": "union"}


def main():
    assert subprocess.run(["git", "rev-parse", "--verify", "MERGE_HEAD"],
                          cwd=ROOT, capture_output=True).returncode == 0, \
        "MERGE_HEAD absent"
    table = []
    for path, mode in FACES.items():
        if mode == "SPECIAL_TOKEN":
            table.append(resolve_token(path))
        else:
            table.append(resolve_whole(path))
    for md, js in MD_TWINS.items():
        dec = next(r for r in table if r["face"] == js)
        pick = dec["pick"]
        src = "HEAD" if pick == "ours" else (
            "MERGE_HEAD" if pick == "theirs" else None)
        # token union / whole picks: md twin follows the json decision bytes
        if pick == "union":
            ours_md = git_bytes("HEAD", md)
            theirs_md = git_bytes("MERGE_HEAD", md)
            # md twin of a union face: regenerate not possible -> take side
            # with newer matching json (ours regenerated last in this window
            # if table says ours_generated >= theirs_generated)
            src = "HEAD" if (dec.get("ours_generated", "") >=
                             dec.get("theirs_generated", "")) else "MERGE_HEAD"
            pick = "ours" if src == "HEAD" else "theirs"
        data = git_bytes(src, md)
        open(os.path.join(ROOT, md), "wb").write(data)
        raw = open(os.path.join(ROOT, md), "rb").read()
        assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw
        table.append({"face": md, "pick": pick, "follows": js})

    receipt = {
        "resolver": "r493 bm-c merge (13 UU S6-regen faces)",
        "law": "r440 S6-regen per-face newer-wins + r484 no-blind-side + "
               "r456/r466 token per-key union + md twins follow json",
        "table": table,
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    open(RECEIPT, "wb").write((json.dumps(
        receipt, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(json.dumps(table, ensure_ascii=False, indent=1))
    print("RECEIPT ->", os.path.relpath(RECEIPT, ROOT))


if __name__ == "__main__":
    main()
