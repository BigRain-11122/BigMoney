# -*- coding: utf-8 -*-
# r704 bm-b merge-window resolver: 19 UU (r703 closeout push rejected ->
# merge-mode pull mid-flight session death; ours=bm-b r703 S6 faces
# 01:17-01:20 vs theirs=bm-a r705 S6 01:08-01:10 + bm-a r705 N2-W15
# judge enrollment). Blood-line: r701/r698/r697/r696/r657/r461/r440.
# r704 deltas vs r701:
#   (a) runnable_pool.json carved OUT of generic handling -> canonical
#       scripts/merge_lane_views.py resolve with EXPLICIT SWAPPED stage
#       files (merge-mode: git :2:=ours/:3:=theirs, r351 mapping is
#       rebase-only; pass --stage2=theirs --stage3=ours so same-second
#       tie resolves to origin per r140 canon) + r704 readback law
#       (resolved must carry theirs-newer fields, 403-entry union,
#       JUDGE-PREP done-flip adopted, zero ours-only loss);
#   (b) TWIN_LOCK retargeted to 2026-10-05 faces;
#   (c) bm-b r703 CEO-face writes = C_HOST_STALE_MIN legal takeover
#       (lane_io.py O-2100 s2.4), ours-fresh take-new is the designed
#       near-identical add/add pick.
import json
import subprocess
import sys
import datetime

TS_KEYS = ("generated", "generated_at", "written_at", "updated_at", "updated",
           "last_run", "asof", "as_of", "ts", "written", "date",
           "last_refusal_ts", "last_crash_ts", "last_seen", "scanned_at")

TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-05.md":
        "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md":
        "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
PER_KEY_FACES = {"results/token_usage.json"}
LEDGER_FACES = {
    "results/compute_audit.json": ("history",),
    "results/regime_state.json": ("transitions", "history"),
}
POOL_FACE = "results/runnable_pool.json"
RECEIPT = "results/_r704bmb_merge_resolve.json"
GOV_FIELDS = ("owner_since", "cleared_ts", "status", "owner")


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


def _dump_crlf(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2).encode(
        "utf-8").replace(b"\n", b"\r\n")


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
                no = ts_norm(do[k]) if isinstance(do[k], str) else ""
                nt = ts_norm(v) if isinstance(v, str) else ""
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
    return _dump_crlf(o), side


def resolve_ledger(ours, theirs, ledger_keys):
    o = json.loads(ours)
    t = json.loads(theirs)
    no, nt = pick_ts(o), pick_ts(t)
    top = "ours" if no >= nt else "theirs"
    out = dict(o if top == "ours" else t)
    rows_note = {}
    for k in ledger_keys:
        lo = o.get(k, [])
        lt = t.get(k, [])
        assert isinstance(lo, list) and isinstance(lt, list)
        seen = {}
        for r in lo:
            seen.setdefault(json.dumps(r, sort_keys=True), r)
        for r in lt:
            seen.setdefault(json.dumps(r, sort_keys=True), r)
        rows = sorted(seen.values(),
                      key=lambda r: ts_norm(str(r.get("ts")
                                                 or r.get("asof") or "")))
        so = {json.dumps(r, sort_keys=True) for r in lo}
        st = {json.dumps(r, sort_keys=True) for r in lt}
        su = {json.dumps(r, sort_keys=True) for r in rows}
        assert so <= su and st <= su, "ledger union lost rows: %s" % k
        out[k] = rows
        rows_note[k] = {"ours": len(lo), "theirs": len(lt),
                        "union": len(rows),
                        "only_ours": len(so - st),
                        "only_theirs": len(st - so)}
    return _dump_crlf(out), {"pick": "ledger-union top=%s (%s>=%s)" % (
        top, no, nt), "rows": rows_note}


def resolve_pool():
    """Canonical merge_lane_views resolve with SWAPPED explicit stages
    (merge-mode r701-pit-3 law) + r704 readback assertions."""
    tmp = {}
    for s, tag in ((1, "base"), (2, "ours"), (3, "theirs")):
        b = show(":%d" % s, POOL_FACE)
        assert b is not None, "pool stage :%s: missing" % s
        fn = "results/_r704bmb_stage/pool_%s.blob" % tag
        open(fn, "wb").write(b)
        tmp[tag] = json.loads(b.decode("utf-8"))
    r = subprocess.run(
        [sys.executable, "scripts/merge_lane_views.py", "resolve",
         POOL_FACE,
         "--stage2", "results/_r704bmb_stage/pool_theirs.blob",
         "--stage3", "results/_r704bmb_stage/pool_ours.blob",
         "--stage1", "results/_r704bmb_stage/pool_base.blob"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, "merge_lane_views resolve failed:\n%s\n%s" % (
        r.stdout, r.stderr)
    # r704 readback law: parse resolved + adopt-theirs-newer assertions
    res = json.load(open(POOL_FACE, encoding="utf-8"))
    re_ids = {e.get("id"): e for e in res["entries"]}
    th_ids = {e.get("id"): e for e in tmp["theirs"]["entries"]}
    ou_ids = {e.get("id"): e for e in tmp["ours"]["entries"]}
    diffs = 0
    for k, te in th_ids.items():
        assert k in re_ids, "pool union LOST theirs entry %s" % k
        for f in GOV_FIELDS:
            rv, tv = re_ids[k].get(f), te.get(f)
            if rv != tv:
                ov = ou_ids.get(k, {}).get(f)
                # allowed only when ours side was strictly newer for f
                assert rv == ov and ov is not None, (
                    "pool gov regression %s.%s resolved=%r theirs=%r" % (
                        k, f, rv, tv))
                diffs += 1
    n_shards = sum(1 for i in re_ids
                   if i.startswith("PERPETUAL-N2-W15-JUDGE-SHARD-"))
    jp = re_ids.get("PERPETUAL-N2-W15-JUDGE-PREP", {})
    note = {"entries": len(re_ids), "theirs": len(th_ids),
            "ours": len(ou_ids), "judge_shards": n_shards,
            "judge_prep_status": jp.get("status"),
            "updated_at": res.get("updated_at"),
            "theirs_updated_at": tmp["theirs"].get("updated_at"),
            "ours_only_lost": sorted(set(ou_ids) - set(re_ids)),
            "gov_regression_fixed_by_ours_newer": diffs}
    assert len(re_ids) >= len(th_ids), "pool shrank vs theirs"
    assert n_shards == 12, "expected 12 judge shards, got %d" % n_shards
    assert jp.get("status") == "done", (
        "JUDGE-PREP done-flip not adopted: %r" % jp.get("status"))
    assert not note["ours_only_lost"], "ours-only entries lost"
    return "canon mlv-resolve swapped-stages " + json.dumps(note), r.stdout


def main():
    assert subprocess.run(["git", "rev-parse", "--verify", "MERGE_HEAD"],
                          capture_output=True).returncode == 0, \
        "MERGE_HEAD absent (no merge in progress)"
    st = subprocess.run(["git", "status", "--porcelain"],
                        capture_output=True, text=True,
                        encoding="utf-8", errors="replace").stdout
    uu = [ln[3:].strip().strip('"') for ln in st.splitlines()
          if ln.startswith("UU ")]
    assert uu, "no UU faces found"
    receipt = {"resolver": "r704 bm-b merge closeout (19 UU: r703 "
               "push-race vs bm-a r705 judge enrollment; 10 json regen "
               "ts-newer-wins + 2 rolling-ledger union + token per-key "
               "union + pool canon-swapped + 4 md/js twins locked)",
               "n_uu": len(uu), "faces": {},
               "ts": datetime.datetime.now().isoformat(timespec="seconds")}
    for path in uu:
        if path == POOL_FACE:
            note, mlv_out = resolve_pool()
            receipt["faces"][path] = note
            receipt["mlv_resolve_stdout"] = mlv_out[-1500:]
            continue
        ours = show("HEAD", path)
        theirs = show("MERGE_HEAD", path)
        if ours is None or theirs is None:
            receipt["faces"][path] = "MISSING-SIDE"
            continue
        if ours == theirs:
            data, note = theirs, "identical"
        elif path.endswith(".jsonl"):
            eol = b"\r\n" if b"\r\n" in theirs else b"\n"
            to = [ln.rstrip(b"\r") for ln in theirs.split(b"\n")
                  if ln.strip()]
            tset = set(to)
            added = []
            for ln in ours.split(b"\n"):
                base = ln.rstrip(b"\r")
                if base.strip() and base not in tset and base not in theirs:
                    added.append(base)
            blob = eol.join(to + added) + eol if (to or added) else b""
            outset = {ln.rstrip(b"\r") for ln in blob.split(b"\n")
                      if ln.strip()}
            assert tset <= outset, "zero-loss violation"
            data, note = blob, "line-union +%d" % len(added)
        elif path in PER_KEY_FACES:
            data, side = resolve_token(ours, theirs)
            note = "per-key union side_pick=%s" % side
        elif path in LEDGER_FACES:
            data, side = resolve_ledger(ours, theirs, LEDGER_FACES[path])
            note = "ledger union %s" % side
        elif path in TWIN_LOCK:
            data = None
            receipt["faces"][path] = "TWIN-PENDING"
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
                json.loads(data)
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

    json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"),
              ensure_ascii=True, indent=1)
    n_ok = sum(1 for v in receipt["faces"].values()
               if v not in ("MISSING-SIDE", "TWIN-PENDING"))
    print("RESOLVED %d/%d faces (receipt -> %s)" % (n_ok, receipt["n_uu"],
                                                    RECEIPT))
    for k, v in receipt["faces"].items():
        print("  %s -> %s" % (k, v))
    pending = [k for k, v in receipt["faces"].items()
               if v in ("MISSING-SIDE", "TWIN-PENDING")]
    if pending:
        print("PENDING (unresolved): %s" % pending)
        return 2
    # targeted add: the 19 resolved faces + own receipt only
    add = uu + [RECEIPT, "results/_r704bmb_merge_probe.py",
                "results/_r704bmb_uu_report.json"]
    r = subprocess.run(["git", "add"] + add, capture_output=True, text=True)
    assert r.returncode == 0, "git add failed: %s" % r.stderr
    print("TARGETED-ADD ok: %d paths" % len(add))
    return 0


if __name__ == "__main__":
    sys.exit(main())
