# r698 bm-b merge-window resolver: 32 UU same-window dual-S6 regen faces
# (bm-c r500 S6 38/38 + bm-b r698 S6 38/38 same window).
# Policy blood-line r697/r696/r694: per-face in-content ts-newer-wins
# (r657 direct git-show both sides, r461 ts_norm, r440 S6-regen
# origin-newer-wins on tie/missing); md/js twins locked to json twin side;
# token_usage + crash_fuse per-key union (r456/r466 side_pick>0 fallback);
# x2_watch_log.jsonl line-level union (r675 block-union + r479 containment
# filter + r656 zero-loss containment proof). -*- coding: utf-8 -*-
import json
import subprocess
import sys

TS_KEYS = ("generated", "generated_at", "written_at", "updated_at", "updated",
           "last_run", "asof", "ts", "written", "date", "last_refusal_ts",
           "last_crash_ts", "last_seen", "scanned_at")

TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-04.md":
        "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md":
        "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
PER_KEY_FACES = {"results/token_usage.json", "results/crash_fuse.json"}


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
    """Per-key union (token_usage machines map / crash_fuse sigs+active)."""
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
                    merged[k] = v          # tie / no-ts -> theirs (r440)
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
        # r456/r466: per-key zero side-pick -> whole-face freshness
        no, nt = pick_ts(o), pick_ts(t)
        if nt >= no:
            o = t
            side["theirs"] += 1
        else:
            side["ours"] += 1
    return json.dumps(o, ensure_ascii=True, indent=1).encode("utf-8"), side


def resolve_jsonl(ours, theirs):
    """Line-level block union: theirs full text + our lines missing from
    theirs (r675 block-union law, NOT whole-file line dedup); r479
    substring containment filter; r656 zero-loss containment proof."""
    eol = b"\r\n" if b"\r\n" in theirs else b"\n"
    to = [ln.rstrip(b"\r") for ln in theirs.split(b"\n") if ln.strip()]
    # note: split on \n leaves trailing \r on CRLF lines; rstrip canon face
    tset = set(to)
    added = []
    for ln in ours.split(b"\n"):
        base = ln.rstrip(b"\r")
        if not base.strip():
            continue
        if base in tset:
            continue
        if base in theirs:           # r479: substring containment filter
            continue
        added.append(base)
    blob = eol.join(to + added) + eol if to or added else b""
    # zero-loss proof: every theirs canon line present in output
    outset = {ln.rstrip(b"\r") for ln in blob.split(b"\n") if ln.strip()}
    assert tset <= outset, "zero-loss violation: theirs lines dropped"
    return blob, {"theirs_lines": len(tset), "ours_added": len(added)}


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
        elif path.endswith(".jsonl"):
            data, m = resolve_jsonl(ours, theirs)
            note = "line-union %s" % m
        elif path in PER_KEY_FACES:
            data, side = resolve_token(ours, theirs)
            note = "per-key union side_pick=%s" % side
        elif path in TWIN_LOCK:
            data = None
            receipt["faces"][path] = "TWIN-PENDING"   # set BEFORE data check
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

    json.dump(receipt, open("results/_r698bmb_merge_resolve.json", "w",
                            encoding="utf-8"), ensure_ascii=True, indent=1)
    n_ok = sum(1 for v in receipt["faces"].values()
               if v not in ("MISSING-SIDE", "TWIN-PENDING"))
    print("RESOLVED %d/%d faces (receipt -> results/"
          "_r698bmb_merge_resolve.json)" % (n_ok, receipt["n_uu"]))
    for k, v in receipt["faces"].items():
        print("  %s -> %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
