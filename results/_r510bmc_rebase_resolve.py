# r510 bm-c rebase-window resolver: 13 UU faces (pull --rebase vs origin 14-commit wave).
# Lineage: r509 strategies receipt + r506 v2 three laws (pan-label marker anchor /
# sides from explicit commit blobs, no index-stage reads / line-anchored residual
# assertion) + r503 canon (twin-lock, history-union, per-key token union).
# This window's marker style = "<<<<<<< HEAD" + diff3 base "||||||| parent of"
# (side1=HEAD=rebase base=origin+daemon side, side2=my round commit 77fc1e146).
# crash_fuse face = canonical merge_lane_views.merge_crash_fuse import (D-03(2)
# tombstone semantics, zero-loss sigs union) -- reuse canon, no rewrite.
# -*- coding: utf-8 -*-
import json
import subprocess
import sys

sys.path.insert(0, "scripts")
from merge_lane_views import merge_crash_fuse  # canonical (r390/r465 lineage)

MY_COMMIT = "77fc1e146"          # the round commit being replayed (conflicted pick)
RECEIPT = "results/_r510bmc_rebase_resolve.json"

TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-05.md": "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md": "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
JSON_TWIN_FACES = set(TWIN_LOCK.values())
PER_KEY_FACES = {"results/token_usage.json"}
HISTORY_UNION_FACES = {"results/compute_audit.json"}
FUSE_FACES = {"results/crash_fuse.json"}

TS_KEYS = ("generated", "generated_at", "written_at", "updated_at", "updated",
           "last_run", "asof", "ts", "written", "date", "last_refusal_ts",
           "last_crash_ts", "last_seen", "scanned_at", "owner_since", "keepalive",
           "last_keepalive")


def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
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
            if any(t in lk for t in TS_KEYS) and isinstance(v, str) and len(v) >= 10:
                n = ts_norm(v)
                if n > best:
                    best = n
            elif depth < 2 and isinstance(v, (dict, list)):
                sub = pick_ts(v, depth + 1)
                if sub > best:
                    best = sub
    elif isinstance(obj, list) and depth < 2:
        for v in obj:
            sub = pick_ts(v, depth + 1)
            if sub > best:
                best = sub
    return best


def resolve_token(mine, origin):
    m = json.loads(mine)
    o = json.loads(origin)
    side = {"mine": 0, "origin": 0}

    def merge_dict(dm, do):
        merged = dict(dm)
        for k, v in do.items():
            if k not in dm:
                merged[k] = v
                side["origin"] += 1
                continue
            if isinstance(v, dict) and isinstance(dm[k], dict):
                nm, no = pick_ts(dm[k]), pick_ts(v)
                if no == "" and nm == "":
                    merged[k] = v
                    side["origin"] += 1
                elif no > nm:
                    merged[k] = v
                    side["origin"] += 1
                elif nm > no:
                    side["mine"] += 1
            else:
                nm = ts_norm(str(dm[k])) if isinstance(dm[k], str) else ""
                no = ts_norm(str(v)) if isinstance(v, str) else ""
                if no >= nm:
                    merged[k] = v
                    side["origin"] += 1
                else:
                    side["mine"] += 1
        return merged

    for k, v in o.items():
        if isinstance(v, dict) and isinstance(m.get(k), dict):
            m[k] = merge_dict(m[k], v)
        elif k not in m:
            m[k] = v
            side["origin"] += 1
    return json.dumps(m, ensure_ascii=True, indent=1).encode("utf-8"), side


def resolve_history_union(mine, origin):
    m = json.loads(mine)
    o = json.loads(origin)
    nm, no = pick_ts(m), pick_ts(o)
    base, other = (m, o) if nm >= no else (o, m)
    base_side = "mine" if nm >= no else "origin"
    merged = dict(base)
    stats = {"base": base_side, "unions": {}}
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
        assert len(ids) == len(set(ids)), "history union dup in %s" % k
        o_set = set([json.dumps(x, sort_keys=True, ensure_ascii=True) for x in ov])
        assert o_set <= set(ids), "zero-loss: other items dropped in %s" % k
        assert b_set <= set(ids), "zero-loss: base items dropped in %s" % k
        merged[k] = uni
        stats["unions"][k] = {"base": len(bv), "other": len(ov), "merged": len(uni)}
    return json.dumps(merged, ensure_ascii=True, indent=1).encode("utf-8"), stats


def resolve_fuse(mine, origin):
    m = json.loads(mine)
    o = json.loads(origin)
    out, notes = merge_crash_fuse([("mine", m), ("origin", o)])
    return json.dumps(out, ensure_ascii=True, indent=1).encode("utf-8"), notes


def marker_audit(path):
    """diff3 block sanity on the conflicted working-tree file (r506 v2 law #1)."""
    raw = open(path, "rb").read().decode("utf-8", "replace")
    n_open = n_base = n_mid = n_close = 0
    for ln in raw.split("\n"):
        if ln.startswith("<<<<<<< "):
            n_open += 1
        elif ln.startswith("||||||| "):
            n_base += 1
        elif ln.startswith("======="):
            n_mid += 1
        elif ln.startswith(">>>>>>> "):
            n_close += 1
    assert n_open == n_close, "unpaired conflict markers in %s" % path
    assert n_open == n_mid, "mid marker mismatch in %s" % path
    assert n_open == n_base, "diff3 base section missing in %s" % path
    return n_open


def main():
    st = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                        text=True, encoding="utf-8", errors="replace").stdout
    uu = [ln[3:].strip().strip('"') for ln in st.splitlines()
          if ln.startswith("UU ")]
    assert uu, "no UU faces found"
    receipt = {"round": "r510", "n_uu": len(uu), "strategies": {},
               "sides": {}, "gates": {}}
    for path in uu:
        marker_audit(path)
        mine = show(MY_COMMIT, path)      # side2 = my round commit
        origin = show("HEAD", path)       # side1 = rebase base (origin + daemon)
        assert mine is not None and origin is not None, "missing side %s" % path
        if mine == origin:
            data, note = origin, "identical"
        elif path in FUSE_FACES:
            data, notes = resolve_fuse(mine, origin)
            note = "canonical merge_crash_fuse sigs-union notes=%s" % (notes,)
        elif path in PER_KEY_FACES:
            data, side = resolve_token(mine, origin)
            note = "per-key union side_pick=%s" % side
        elif path in HISTORY_UNION_FACES:
            data, stats = resolve_history_union(mine, origin)
            note = "history-union zero-loss %s" % stats
        elif path in JSON_TWIN_FACES:
            receipt["strategies"][path] = "TWIN-PENDING"
            continue
        else:
            try:
                jm, jo = json.loads(mine), json.loads(origin)
            except Exception:
                data, note = origin, "unparseable -> origin side"
            else:
                nm, no = pick_ts(jm), pick_ts(jo)
                if nm == "" and no == "":
                    data, note = origin, "no-ts-both -> origin (r440)"
                elif nm >= no:
                    data, note = mine, "ts-newer-wins mine %s>=%s" % (nm, no)
                else:
                    data, note = origin, "ts-newer-wins origin %s>%s" % (no, nm)
        if data is not None:
            assert not any(l.startswith("<<<<<<< ") for l in
                           data.decode("utf-8", "replace").split("\n")), \
                "residual marker in resolved %s" % path
            if path.endswith(".json"):
                json.loads(data)          # reparse gate (fail-closed)
            with open(path, "wb") as f:
                f.write(data)
            receipt["strategies"][path] = note
            receipt["sides"][path] = ("mine" if data == mine else
                                      "origin" if data == origin else "merged")

    def twin_json_side(jp):
        jm = json.loads(show(MY_COMMIT, jp))
        jo = json.loads(show("HEAD", jp))
        nm, no = pick_ts(jm), pick_ts(jo)
        return ("mine" if nm >= no else "origin"), nm, no

    for mdp, jp in TWIN_LOCK.items():
        if receipt["strategies"].get(mdp) == "TWIN-PENDING":
            side, nm, no = twin_json_side(jp)
            data = show(MY_COMMIT if side == "mine" else "HEAD", mdp)
            assert data is not None
            assert not any(l.startswith("<<<<<<< ") for l in
                           data.decode("utf-8", "replace").split("\n"))
            with open(mdp, "wb") as f:
                f.write(data)
            jdata = json.loads(open(jp, "rb").read())
            jside, jnm, jno = twin_json_side(jp)
            assert jside == side, "twin side drift %s" % mdp
            receipt["strategies"][jp] = "ts-newer-wins %s %s vs %s" % (side, jnm, jno)
            receipt["strategies"][mdp] = "twin-locked-to-json %s" % side
            receipt["sides"][mdp] = side
            receipt["sides"][jp] = side

    json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"),
              ensure_ascii=True, indent=1)
    n_ok = sum(1 for v in receipt["strategies"].values() if v != "TWIN-PENDING")
    print("RESOLVED %d/%d faces (receipt -> %s)" % (n_ok, len(uu), RECEIPT))
    for k, v in receipt["strategies"].items():
        print("  %s -> %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
