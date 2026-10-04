# -*- coding: utf-8 -*-
# r701 bm-b merge-window resolver: 19 UU (r700 push-race: bm-b r700 vs
# bm-c r502-close + bm-a r701 W119-seat same window, merge-mode pull).
# Policy blood-line r698/r697/r696: per-face in-content ts-newer-wins
# (r657 direct git-show both sides, r461 ts_norm, r440 regen tie->theirs);
# md/js twins locked to json twin side; token_usage per-key union
# (r456/r466 side_pick>0 fallback whole-face freshness).
# r701 deltas vs r698:
#   (a) rolling-ledger union leg (r188/R208): compute_audit.json history
#       row-union zero-loss (202=|A u B|, dedup canonical, ts-asc to keep
#       producer append-at-tail order; producer trims [-200:] on next run)
#       + regime_state.json transitions/history union, top-level state
#       fields newest-wins;
#   (b) TS_KEYS += "as_of" (daily_scorecard.json deep wall-clock lives at
#       traders[*].forward_guard.as_of -- underscore variant missed by
#       "asof"; theirs-fresh 23:22 > ours 23:01, rest byte-identical);
#   (c) token union serialization matched to producer (token_meter.py
#       indent=2 ensure_ascii=False CRLF) to kill format churn.
# -*- coding: utf-8 -*-
import json
import subprocess
import sys
import datetime

TS_KEYS = ("generated", "generated_at", "written_at", "updated_at", "updated",
           "last_run", "asof", "as_of", "ts", "written", "date",
           "last_refusal_ts", "last_crash_ts", "last_seen", "scanned_at")

TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-04.md":
        "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md":
        "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
PER_KEY_FACES = {"results/token_usage.json", "results/crash_fuse.json"}
LEDGER_FACES = {
    "results/compute_audit.json": ("history",),
    "results/regime_state.json": ("transitions", "history"),
}
RECEIPT = "results/_r701bmb_merge_resolve.json"


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
    """Producer-matched JSON face emit: indent=2, ensure_ascii=False, CRLF,
    no trailing newline (compute_audit.py/market_regime.py writer shape)."""
    return json.dumps(obj, ensure_ascii=False, indent=2).encode(
        "utf-8").replace(b"\n", b"\r\n")


def resolve_token(ours, theirs):
    """Per-key union (token_usage machines map / crash_fuse sigs+active);
    serialize per token_meter.py producer format (r701 delta (c))."""
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
        # r456/r466: per-key zero side-pick -> whole-face freshness
        no, nt = pick_ts(o), pick_ts(t)
        if nt >= no:
            o = t
            side["theirs"] += 1
        else:
            side["ours"] += 1
    return _dump_crlf(o), side


def resolve_ledger(ours, theirs, ledger_keys):
    """r188/R208 rolling-ledger law: union ledger rows zero-loss (dedup
    canonical, ts-asc append-at-tail producer order), top-level state
    fields newest-wins."""
    o = json.loads(ours)
    t = json.loads(theirs)
    no, nt = pick_ts(o), pick_ts(t)
    top = "ours" if no >= nt else "theirs"
    out = dict(o if top == "ours" else t)
    rows_note = {}
    for k in ledger_keys:
        lo = o.get(k, [])
        lt = t.get(k, [])
        assert isinstance(lo, list) and isinstance(lt, list), \
            "%s: ledger key %s not list" % (k,)
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
                        "only_ours": len(so - st), "only_theirs": len(st - so)}
    data = _dump_crlf(out)
    return data, {"pick": "ledger-union top=%s (%s>=%s)" % (top, no, nt),
                  "rows": rows_note}


def resolve_jsonl(ours, theirs):
    """Line-level block union (r675) + r479 containment filter + r656
    zero-loss proof (r698 verbatim)."""
    eol = b"\r\n" if b"\r\n" in theirs else b"\n"
    to = [ln.rstrip(b"\r") for ln in theirs.split(b"\n") if ln.strip()]
    tset = set(to)
    added = []
    for ln in ours.split(b"\n"):
        base = ln.rstrip(b"\r")
        if not base.strip():
            continue
        if base in tset:
            continue
        if base in theirs:
            continue
        added.append(base)
    blob = eol.join(to + added) + eol if to or added else b""
    outset = {ln.rstrip(b"\r") for ln in blob.split(b"\n") if ln.strip()}
    assert tset <= outset, "zero-loss violation: theirs lines dropped"
    return blob, {"theirs_lines": len(tset), "ours_added": len(added)}


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
    receipt = {"resolver": "r701 bm-b merge (19 UU push-race: 12 json regen "
                           "ts-newer-wins + 2 rolling-ledger union + token "
                           "per-key union + 4 md/js twins locked)",
               "law": "r440 per-face newer-wins + r456/r466 token union+"
                      "fallback + md/js-twin lock + r188/R208 ledger union",
               "n_uu": len(uu), "faces": {}, "ts": datetime.datetime.now(
                   ).isoformat(timespec="seconds")}
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
        elif path in LEDGER_FACES:
            data, side = resolve_ledger(ours, theirs, LEDGER_FACES[path])
            note = "ledger union %s" % side
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
