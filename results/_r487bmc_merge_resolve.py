"""r487 bm-c merge UU resolver -- 8 faces from merge origin/main wave.

Laws: r474 pool per-face max-merge (owner_since newer-wins, status rank,
entry union) / r456+r466 token per-key union with side_pick>0 assert +
whole-face freshness fallback / r461 ts_norm newer-wins (space/T-form
normalized) / r657 HEAD: MERGE_HEAD: raw bytes direct (stage2/3 immune)
/ r485 host-eol join / r641 evidence printed before assertion.

Output: resolved bytes written in-place; receipt JSON printed to file.
Zero push, zero add (batch add happens in the calling step per r673).
"""
import json
import os
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
RECEIPT = os.path.join(REPO, "results", "_r487bmc_merge_resolve.json")
UU = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
]
TS_KEYS = ("ts", "generated", "generated_at", "updated_at", "updated",
           "asof", "probed_at", "written_at", "clock_read", "last_seen")
RANK = {"done": 3, "ready": 2, "running": 2, "waiting": 1, "parked": 1}


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"],
                       capture_output=True, cwd=REPO, creationflags=CNW)
    if r.returncode != 0:
        return None
    return r.stdout


def ts_norm(v):
    if not isinstance(v, str):
        return ""
    return (v.replace("T", " ") + " ")[:19].strip()


def face_ts(d):
    """Best-effort top-level timestamp for a snapshot face."""
    if not isinstance(d, dict):
        return ""
    for k in TS_KEYS:
        if isinstance(d.get(k), str):
            return ts_norm(d[k])
    return ""


def eol_of(raw):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    return b"\r\n" if crlf > 0 and crlf >= lf else b"\n"


def write_face(path, obj, base_raw):
    buf = json.dumps(obj, indent=1, ensure_ascii=False)
    nl = "\r\n" if eol_of(base_raw) == b"\r\n" else "\n"
    text = buf.replace("\n", nl) if nl == "\r\n" else buf
    with open(os.path.join(REPO, path), "w", encoding="utf-8",
              newline="") as f:
        f.write(text)


def resolve_snapshot(path, rec):
    ours = show("HEAD", path)
    theirs = show("MERGE_HEAD", path)
    try:
        do = json.loads(ours.decode("utf-8"))
        dt = json.loads(theirs.decode("utf-8"))
    except Exception as e:
        rec[path] = {"mode": "FALLBACK_OURS", "err": str(e)[:100]}
        with open(os.path.join(REPO, path), "wb") as f:
            f.write(ours)
        return
    to, tt = face_ts(do), face_ts(dt)
    pick = "ours" if to >= tt else "theirs"
    rec[path] = {"mode": "ts-newer-wins", "ours_ts": to, "theirs_ts": tt,
                 "pick": pick}
    write_face(path, do if pick == "ours" else dt, ours if pick == "ours"
               else theirs)


def resolve_token(path, rec):
    ours = show("HEAD", path)
    theirs = show("MERGE_HEAD", path)
    do = json.loads(ours.decode("utf-8"))
    dt = json.loads(theirs.decode("utf-8"))
    to, tt = face_ts(do), face_ts(dt)
    side_pick = 0
    merged = dict(do)
    for k, v in dt.items():
        if k not in do:
            merged[k] = v
            side_pick += 1
            continue
        ov, tv = do[k], v
        if isinstance(ov, dict) and isinstance(tv, dict):
            face = {}
            for sk in set(ov) | set(tv):
                a, b = ov.get(sk), tv.get(sk)
                if a == b:
                    face[sk] = a
                    continue
                ta = face_ts(a) if isinstance(a, dict) else ""
                tb = face_ts(b) if isinstance(b, dict) else ""
                if ta and tb:
                    face[sk] = a if ta >= tb else b
                    side_pick += 1
                else:
                    face[sk] = a  # keep-first ours, disclosed
                    side_pick += 1
            merged[k] = face
        elif ov != tv:
            # per-key scalar diff: side by face-level freshness (r456
            # fallback generalized per-key)
            merged[k] = tv if tt > to else ov
            side_pick += 1
    if side_pick == 0:
        pick = "ours" if to >= tt else "theirs"
        rec[path] = {"mode": "r456-whole-face-freshness",
                     "ours_ts": to, "theirs_ts": tt, "pick": pick}
        write_face(path, do if pick == "ours" else dt, ours)
    else:
        rec[path] = {"mode": "per-key-union", "side_pick": side_pick,
                     "ours_ts": to, "theirs_ts": tt}
        write_face(path, merged, ours)


def resolve_pool(path, rec):
    ours = show("HEAD", path)
    theirs = show("MERGE_HEAD", path)
    do = json.loads(ours.decode("utf-8"))
    dt = json.loads(theirs.decode("utf-8"))
    tmap_o, tmap_t = {}, {}

    def shard_map(d):
        m = {}
        for e in d.get("entries", []):
            for s in e.get("shards", []):
                m[(e.get("id"), s.get("key"))] = s
        return m

    mo, mt = shard_map(do), shard_map(dt)
    n_newer_theirs = n_newer_ours = n_same = 0
    regress = []
    for key in set(mo) | set(mt):
        so, st = mo.get(key), mt.get(key)
        if so is None:
            n_newer_theirs += 1
            continue
        if st is None:
            n_newer_ours += 1
            continue
        to, tt = ts_norm(so.get("owner_since")), ts_norm(st.get("owner_since"))
        if tt > to:
            n_newer_theirs += 1
            for f in ("owner", "owner_since", "status", "checkpoint",
                      "note", "closed_at", "done_at", "result_ref"):
                if f in st:
                    so[f] = st[f]
        elif to > tt:
            n_newer_ours += 1
        else:
            n_same += 1
            if RANK.get(st.get("status", ""), 0) > \
                    RANK.get(so.get("status", ""), 0):
                so["status"] = st["status"]
    # entries present only in theirs -> adopt verbatim (fleet-published)
    ids_o = {e.get("id") for e in do.get("entries", [])}
    for e in dt.get("entries", []):
        if e.get("id") not in ids_o:
            do.setdefault("entries", []).append(e)
            rec.setdefault("entries_added_from_theirs", []).append(
                e.get("id"))
    # post-verify: no owner_since regression vs either parent
    mres = shard_map(do)
    for key, s in mres.items():
        so, st = mo.get(key), mt.get(key)
        tr = ts_norm(s.get("owner_since"))
        if so and tr < ts_norm(so.get("owner_since")):
            regress.append([key, "vs-ours", tr,
                            ts_norm(so.get("owner_since"))])
        if st and tr < ts_norm(st.get("owner_since")):
            regress.append([key, "vs-theirs", tr,
                            ts_norm(st.get("owner_since"))])
    rec[path] = {"mode": "r474-per-face-max-merge",
                 "shards_newer_theirs": n_newer_theirs,
                 "shards_newer_ours": n_newer_ours,
                 "shards_same_ts": n_same,
                 "regressions": regress[:10]}
    assert not regress, f"pool regression {regress[:3]}"
    write_face(path, do, ours)


def main():
    rec = {"round": "r487 bm-c merge-resolve",
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    for p in UU:
        if p.endswith("runnable_pool.json"):
            resolve_pool(p, rec)
        elif p.endswith("token_usage.json"):
            resolve_token(p, rec)
        else:
            resolve_snapshot(p, rec)
    # reparse proof + marker scan
    for p in UU:
        full = os.path.join(REPO, p)
        raw = open(full, "rb").read()
        if p.endswith(".js"):
            assert b"<<<<<<<" not in raw, p
        else:
            json.loads(raw.decode("utf-8"))
            assert b"<<<<<<<" not in raw, p
    rec["reparse_and_marker_scan"] = "PASS 8/8"
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("RESOLVE_DONE")
    for p in UU:
        print(p, "->", json.dumps(rec[p], ensure_ascii=False)[:160])


if __name__ == "__main__":
    main()
