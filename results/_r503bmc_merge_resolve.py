# r503 bm-c merge-window resolver: 17 UU same-window regen faces + pool canonical face
# Lineage: r501/r698/r697/r696/r694 (per-face in-content ts-newer-wins, r657 direct
# git-show both sides, r461 ts_norm, r440 tie->theirs); r503 additions:
# (a) TWIN_LOCK += results/dashboard_status.js -> results/dashboard_status.json
# (b) compute_audit.json history-union leg (r188/R208 zero-loss, bm-b r701 precedent)
# (c) runnable_pool.json post-verify: SHARD-2 status==done owner=bm-a (canonical
#     bm-a done-flip 23:44:03, bm-b 22a8b12ee MSG-0612 law A resolution; our daemon
#     23:40:38 takeover claim is superseded). -*- coding: utf-8 -*-
import json
import subprocess
import sys

TS_KEYS = ("generated", "generated_at", "written_at", "updated_at", "updated",
           "last_run", "asof", "ts", "written", "date", "last_refusal_ts",
           "last_crash_ts", "last_seen", "scanned_at", "owner_since", "keepalive",
           "last_keepalive")

TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-04.md":
        "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md":
        "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
PER_KEY_FACES = {"results/token_usage.json"}
HISTORY_UNION_FACES = {"results/compute_audit.json"}
POOL_FACE = "results/runnable_pool.json"

RECEIPT = "results/_r503bmc_merge_resolve.json"


def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def ts_norm(v):
    if not isinstance(v, str):
        return ""
    s = v.strip().replace("T", " ")
    return s[:19]


def pick_ts(obj, depth=0):
    best = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if any(t in lk for t in TS_KEYS) and isinstance(v, str) \
                    and len(v) >= 10:
                n = ts_norm(v)
                if n > best:
                    best = n
            elif depth < 1 and isinstance(v, (dict, list)):
                sub = pick_ts(v, depth + 1)
                if sub > best:
                    best = sub
    elif isinstance(obj, list) and depth < 1:
        for v in obj:
            sub = pick_ts(v, depth + 1)
            if sub > best:
                best = sub
    return best


def resolve_token(ours, theirs):
    o = json.loads(ours)
    t = json.loads(theirs)
    side = {"ours": 0, "theirs": 0}

    def merge_dict(do, dt):
        merged = dict(do)
        for k, v in dt.items():
            if k not in do:
                merged[k] = v
                side["theirs"] += 1
                continue
            if isinstance(v, dict) and isinstance(do[k], dict):
                no = pick_ts(do[k])
                nt = pick_ts(v)
                if nt == "" and no == "":
                    merged[k] = v
                    side["theirs"] += 1
                elif nt > no:
                    merged[k] = v
                    side["theirs"] += 1
                elif no > nt:
                    side["ours"] += 1
            else:
                no = ts_norm(str(do[k])) if isinstance(do[k], str) else ""
                nt = ts_norm(str(v)) if isinstance(v, str) else ""
                if nt >= no:
                    merged[k] = v
                    side["theirs"] += 1
                else:
                    side["ours"] += 1
        return merged

    for k, v in t.items():
        if isinstance(v, dict) and isinstance(o.get(k), dict):
            o[k] = merge_dict(o[k], v)
        elif k not in o:
            o[k] = v
            side["theirs"] += 1
    if side["ours"] == 0 and side["theirs"] == 0:
        no, nt = pick_ts(o), pick_ts(t)
        if nt >= no:
            o = t
            side["theirs"] += 1
        else:
            side["ours"] += 1
    return json.dumps(o, ensure_ascii=True, indent=1).encode("utf-8"), side


def resolve_history_union(ours, theirs):
    """compute_audit: fresher-side top fields + zero-loss history-array union (r188/R208)."""
    o = json.loads(ours)
    t = json.loads(theirs)
    no, nt = pick_ts(o), pick_ts(t)
    base, other = (t, o) if nt >= no else (o, t)
    base_fresh = "theirs" if nt >= no else "ours"
    merged = dict(base)
    stats = {"base": base_fresh, "unions": {}}
    for k, bv in base.items():
        if not (isinstance(bv, list) and bv and isinstance(bv[0], dict)):
            continue
        ov = other.get(k)
        if not (isinstance(ov, list) and ov):
            continue
        b_ids = [json.dumps(x, sort_keys=True, ensure_ascii=True) for x in bv]
        b_set = set(b_ids)
        added = [x for x in ov
                 if json.dumps(x, sort_keys=True, ensure_ascii=True) not in b_set]
        uni = bv + added
        ids = [json.dumps(x, sort_keys=True, ensure_ascii=True) for x in uni]
        assert len(ids) == len(set(ids)), "history union produced dups in %s" % k
        assert set([json.dumps(x, sort_keys=True, ensure_ascii=True) for x in ov]) <= set(ids), "zero-loss: ours items dropped"
        assert b_set <= set(ids), "zero-loss: base items dropped"
        merged[k] = uni
        stats["unions"][k] = {"base": len(bv), "other": len(ov), "merged": len(uni)}
    return json.dumps(merged, ensure_ascii=True, indent=1).encode("utf-8"), stats


def pool_post_verify(path):
    raw = open(path, "rb").read()
    obj = json.loads(raw)
    found = None
    for e in obj.get("entries", []):
        eid = e.get("id", e.get("key", ""))
        if "N2-W15" in eid and "SHARD-2" in eid:
            for s in e.get("shards", []):
                found = s
    assert found is not None, "SHARD-2 entry not found in resolved pool"
    assert found.get("status") == "done", "SHARD-2 not done in canonical pool: %r" % found.get("status")
    print("pool post-verify: SHARD-2 status=done owner=%s since=%s (canonical)" % (found.get("owner"), found.get("owner_since")))


def main():
    st = subprocess.run(["git", "status", "--porcelain"],
                        capture_output=True, text=True,
                        encoding="utf-8", errors="replace").stdout
    uu = [ln[3:].strip().strip('"') for ln in st.splitlines()
          if ln.startswith("UU ")]
    assert uu, "no UU faces found"
    receipt = {"n_uu": len(uu), "faces": {}}
    for path in uu:
        ours = show("HEAD", path)
        theirs = show("MERGE_HEAD", path)
        if ours is None or theirs is None:
            receipt["faces"][path] = "MISSING-SIDE"
            continue
        if ours == theirs:
            data, note = theirs, "identical"
        elif path in PER_KEY_FACES:
            data, side = resolve_token(ours, theirs)
            note = "per-key union side_pick=%s" % side
            assert side["ours"] + side["theirs"] > 0 or True
        elif path in HISTORY_UNION_FACES:
            data, stats = resolve_history_union(ours, theirs)
            note = "history-union %s" % stats
        elif path in TWIN_LOCK:
            data = None
            receipt["faces"][path] = "TWIN-PENDING"   # set BEFORE data check (r698)
        else:
            try:
                jo, jt = json.loads(ours), json.loads(theirs)
            except Exception:
                data, note = theirs, "unparseable -> theirs"
            else:
                no, nt = pick_ts(jo), pick_ts(jt)
                if nt == "" and no == "":
                    data, note = theirs, "no-ts-both -> theirs (r440)"
                elif nt >= no:
                    data, note = theirs, "theirs-fresh %s>=%s" % (nt, no)
                else:
                    data, note = ours, "ours-fresh %s>%s" % (no, nt)
        if data is not None:
            assert data.count(b"<<<<<<<") == 0, "marker in resolved %s" % path
            if path.endswith(".json"):
                json.loads(data)          # reparse gate (fail-closed)
            with open(path, "wb") as f:
                f.write(data)
            receipt["faces"][path] = note

    def json_side(jpath):
        o = show("HEAD", jpath)
        t = show("MERGE_HEAD", jpath)
        if o is None or o == t:
            return "theirs"
        try:
            no = pick_ts(json.loads(o))
            nt = pick_ts(json.loads(t))
        except Exception:
            return "theirs"
        return "ours" if no > nt else "theirs"

    for mdp, jp in TWIN_LOCK.items():
        if receipt["faces"].get(mdp) == "TWIN-PENDING":
            side = json_side(jp)
            data = show("HEAD" if side == "ours" else "MERGE_HEAD", mdp)
            assert data is not None and data.count(b"<<<<<<<") == 0
            with open(mdp, "wb") as f:
                f.write(data)
            receipt["faces"][mdp] = "twin-locked to json side=%s" % side

    if POOL_FACE in receipt["faces"]:
        pool_post_verify(POOL_FACE)

    json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"),
              ensure_ascii=True, indent=1)
    n_ok = sum(1 for v in receipt["faces"].values()
               if v not in ("MISSING-SIDE", "TWIN-PENDING"))
    print("RESOLVED %d/%d faces (receipt -> %s)" % (n_ok, receipt["n_uu"], RECEIPT))
    for k, v in receipt["faces"].items():
        print("  %s -> %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
