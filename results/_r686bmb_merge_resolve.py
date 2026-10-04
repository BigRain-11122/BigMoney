# -*- coding: utf-8 -*-
"""r686 bm-b merge-UU canon resolver (r679 lineage copy-adapted per r461 law;
post-r679 laws re-checked: none beyond canon set. This window's incoming =
bm-c r483 wave (W3 screen finalize + S6 close). S6 timing: MY S6 ran
16:22-16:29, bm-c r483 close S6 ran ~16:31+ -> expected THEIRS-newer for
most regen twins; resolver takes embedded-ts newer regardless of side.
Routing:
- CODELY.md -> memory-union: merge-base prefix-identity BOTH sides asserted,
  direct-concat suffixes, order = base + theirs + ours (r675 chronology);
  extra r479 containment pre-check: identical line in both suffixes -> abort
  for manual dedupe (keep-first) instead of double-recording.
- compute_audit.json -> history ts-identity union (containment asserts);
- token_usage.json -> machines per-key max-union (side_pick>0 assert, r456;
  zero side-pick -> EXPLICIT whole-face freshness per r466);
- results/x2_watch_log.jsonl -> line-level union zero-loss (r656 law);
- results/_attrition_guard_scan.json -> whole-face take-new ts (per-run
  scan receipt re-derived whole each scan);
- all other regen twins -> embedded-ts newer-wins (r461 ts_norm; equal->ours).
NO COMMIT here: resolve + verify + single git add; merge commit happens after
the post-merge attrition_ledger_guard scan so fresh evidence rides it.
pool_w3_post_assert per r482 + trio owner_since freshness regression check."""
import datetime
import json
import os
import re
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "results", "_r686bmb_merge_resolve.json")
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
CODELY = "CODELY.md"
AUDIT = "results/compute_audit.json"
TOKEN = "results/token_usage.json"
X2LOG = "results/x2_watch_log.jsonl"
ATTR = "results/_attrition_guard_scan.json"
POOL = "results/runnable_pool.json"
TRIO_IDS = ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS",
            "FUND-DIVLOWVOL-P1-NULLS")
W3_PREF = "MASS-TRIAL-W3-SCREEN-SHARD"


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def blob(ref, path):
    rc, out, err = git("show", ref + ":" + path)
    assert rc == 0, "blob read fail %s:%s %s" % (ref, path, err[:120])
    return out.encode("utf-8", "surrogateescape")


def ts_norm(v):
    if not isinstance(v, str):
        return ""
    return v.replace("T", " ")[:19]


def uu_faces():
    rc, out, err = git("status", "--porcelain")
    assert rc == 0, "status fail " + err[:120]
    faces = []
    for ln in out.splitlines():
        if ln.startswith("UU ") or ln.startswith("AA ") or ln.startswith("DU ") or ln.startswith("UD "):
            faces.append(ln[3:].strip().strip('"'))
    return sorted(faces)


def resolve_codely(ev):
    rc, base_sha, _ = git("merge-base", "HEAD", "MERGE_HEAD")
    assert rc == 0, "merge-base fail"
    base = blob(base_sha.strip(), CODELY)
    ours = blob("HEAD", CODELY)
    theirs = blob("MERGE_HEAD", CODELY)
    assert ours.startswith(base), "CODELY ours NOT pure append -- manual review"
    assert theirs.startswith(base), "CODELY theirs NOT pure append -- manual review"
    o_suf, t_suf = ours[len(base):], theirs[len(base):]
    assert o_suf and t_suf, "empty suffix"
    o_lines = {ln for ln in o_suf.decode("utf-8", "replace").splitlines() if ln.strip()}
    t_lines = {ln for ln in t_suf.decode("utf-8", "replace").splitlines() if ln.strip()}
    dup = o_lines & t_lines
    assert not dup, ("r479 containment: identical suffix lines both sides -- "
                     "manual keep-first dedupe needed: %r" % list(dup)[:2])
    new = base + t_suf + o_suf
    assert len(new) == len(base) + len(t_suf) + len(o_suf), "concat byte math fail"
    assert new.count(o_suf) == 1 and new.count(t_suf) == 1, "suffix count fail"
    for ln in new.decode("utf-8", "replace").splitlines():
        assert not (ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>")
                    or ln.startswith("=======")), "CODELY marker residue"
    with open(os.path.join(ROOT, CODELY), "wb") as f:
        f.write(new)
    ev[CODELY] = {"mode": "memory-union direct-concat (base+theirs+ours)",
                  "base": len(base), "ours_suf": len(o_suf),
                  "theirs_suf": len(t_suf), "new": len(new)}
    return CODELY


def resolve_audit(ev):
    o = json.loads(blob("HEAD", AUDIT).decode("utf-8"))
    t = json.loads(blob("MERGE_HEAD", AUDIT).decode("utf-8"))
    hist_key = None
    for k in o:
        if isinstance(o[k], list) and (len(o[k]) > 20 or k == "history"):
            hist_key = k
            break
    assert hist_key, "compute_audit history key not found"
    oh, th = o[hist_key], t[hist_key]
    union = list(oh)
    seen = {json.dumps(e, sort_keys=True, ensure_ascii=False) for e in oh}
    added = 0
    for e in th:
        key = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            union.append(e)
            seen.add(key)
            added += 1
    for e in oh:
        assert json.dumps(e, sort_keys=True, ensure_ascii=False) in seen
    for e in th:
        assert json.dumps(e, sort_keys=True, ensure_ascii=False) in seen
    o[hist_key] = union
    out = json.dumps(o, ensure_ascii=False, indent=1) + "\n"
    with open(os.path.join(ROOT, AUDIT), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    json.loads(out)
    ev[AUDIT] = {"hist_key": hist_key, "ours": len(oh), "theirs": len(th),
                 "union": len(union), "theirs_only_added": added}
    return AUDIT


def resolve_token(ev):
    o = json.loads(blob("HEAD", TOKEN).decode("utf-8"))
    t = json.loads(blob("MERGE_HEAD", TOKEN).decode("utf-8"))
    mk = "machines" if "machines" in o else None
    assert mk, "token_usage machines key not found"
    om, tm = o[mk], t[mk]
    picks = {"ours_only": 0, "theirs_only": 0, "newer_ours": 0, "newer_theirs": 0}
    merged = {}
    for k in sorted(set(om) | set(tm)):
        a, b = om.get(k), tm.get(k)
        if a and not b:
            merged[k] = a
            picks["ours_only"] += 1
        elif b and not a:
            merged[k] = b
            picks["theirs_only"] += 1
        elif a == b:
            merged[k] = a
        else:
            ta = ts_norm(a.get("ts", a.get("updated", "")))
            tb = ts_norm(b.get("ts", b.get("updated", "")))
            if ta >= tb:
                merged[k] = a
                picks["newer_ours"] += 1
            else:
                merged[k] = b
                picks["newer_theirs"] += 1
    side_pick = (picks["ours_only"] + picks["theirs_only"]
                 + picks["newer_ours"] + picks["newer_theirs"])
    if side_pick > 0:
        o[mk] = merged
        ev[TOKEN] = {"machines": len(merged), "picks": picks, "mode": "per-key union"}
    else:
        ots = extract_ts(blob("HEAD", TOKEN), False) or ts_norm(o.get("ts", ""))
        tts = extract_ts(blob("MERGE_HEAD", TOKEN), False) or ts_norm(t.get("ts", ""))
        if ots >= tts:
            winner, side = o, "ours"
        else:
            winner, side = t, "theirs"
        picks["whole_face"] = 1
        ev[TOKEN] = {"machines": len(om), "picks": picks,
                     "mode": "whole-face freshness (r456 explicit fallback)",
                     "ours_ts": ots, "theirs_ts": tts, "took": side}
        o = winner
    out = json.dumps(o, ensure_ascii=False, indent=1) + "\n"
    with open(os.path.join(ROOT, TOKEN), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    json.loads(out)
    return TOKEN


def line_union(path, ev, tag):
    ob = blob("HEAD", path)
    tb = blob("MERGE_HEAD", path)
    o_lines = [ln for ln in ob.split(b"\n") if ln.strip()]
    t_lines = [ln for ln in tb.split(b"\n") if ln.strip()]
    o_set, t_set = set(o_lines), set(t_lines)
    theirs_only = [ln for ln in t_lines if ln not in o_set]
    base = ob if ob.endswith(b"\n") else ob + b"\n"
    union = base
    if theirs_only:
        union = base + b"\n".join(theirs_only) + b"\n"
    u_lines = [ln for ln in union.split(b"\n") if ln.strip()]
    u_set = set(u_lines)
    assert o_set <= u_set, "%s union lost OURS lines" % tag
    assert t_set <= u_set, "%s union lost THEIRS lines" % tag
    assert len(u_lines) == len(u_set), "%s union has dup lines" % tag
    for ln in u_lines:
        s = ln.decode("utf-8", "replace")
        assert not (s.startswith("<<<<<<<") or s.startswith(">>>>>>>")
                    or s.startswith("=======")), "%s marker" % tag
        if s.startswith("{"):
            json.loads(s)
    with open(os.path.join(ROOT, path.replace("/", os.sep)), "wb") as f:
        f.write(union)
    ev[path] = {"mode": "line-union r656", "ours": len(o_lines),
                "theirs": len(t_lines), "union": len(u_lines),
                "theirs_only_added": len(theirs_only)}
    return path


def extract_ts(data, is_md):
    head = data[:800].decode("utf-8", "replace")
    m = TS_RE.search(head)
    if m:
        return ts_norm(m.group(0))
    try:
        j = json.loads(data.decode("utf-8"))
        for k in ("ts", "generated", "generated_at", "updated", "updated_at", "asof"):
            if isinstance(j.get(k), str):
                return ts_norm(j[k])
        for v in j.values():
            if isinstance(v, dict):
                for k in ("ts", "generated", "updated"):
                    if isinstance(v.get(k), str):
                        return ts_norm(v[k])
    except ValueError:
        pass
    return ""


def resolve_twin(path, ev):
    ob = blob("HEAD", path)
    tb = blob("MERGE_HEAD", path)
    if ob == tb:
        with open(os.path.join(ROOT, path.replace("/", os.sep)), "wb") as f:
            f.write(ob)
        ev[path] = "byte-equal"
        return
    ots = extract_ts(ob, path.endswith(".md"))
    tts = extract_ts(tb, path.endswith(".md"))
    if ots and tts and ots != tts:
        winner, side = (ob, "ours") if ots > tts else (tb, "theirs")
        ev[path] = "take-%s (ours %s vs theirs %s)" % (side, ots, tts)
    elif ots and tts and ots == tts:
        winner, side = ob, "ours"
        ev[path] = "ts-equal-took-ours %s" % ots
    else:
        winner, side = ob, "ours"
        ev[path] = "no-ts-took-ours"
    with open(os.path.join(ROOT, path.replace("/", os.sep)), "wb") as f:
        f.write(winner)
    if path.endswith(".json"):
        json.loads(winner.decode("utf-8"))


def pool_w3_post_assert(ev):
    merged = json.load(open(os.path.join(ROOT, POOL), encoding="utf-8"))
    head = json.loads(blob("HEAD", POOL).decode("utf-8"))
    theirs = json.loads(blob("MERGE_HEAD", POOL).decode("utf-8"))

    def w3map(pool):
        m = {}
        for e in pool.get("entries", []):
            if str(e.get("id", "")).startswith(W3_PREF):
                s = e["shards"][0]
                m[e["id"]] = (e.get("status"), s.get("status"),
                             s.get("owner"), ts_norm(s.get("owner_since") or ""))
        return m
    hm, tm, mm = w3map(head), w3map(theirs), w3map(merged)
    for k in sorted(set(hm) | set(tm)):
        h, t, m = hm.get(k), tm.get(k), mm.get(k)
        assert m, "merged pool lost W3 entry %s" % k
        for side, tag in ((h, "HEAD"), (t, "MERGE_HEAD")):
            if side and side[1] == "done":
                assert m[1] == "done", "W3 done regression %s vs %s" % (k, tag)
        if h and t:
            best = max(h[3], t[3])
            assert m[3] >= best, "W3 owner_since regression %s: %s < %s" % (
                k, m[3], best)
        ev.setdefault("pool_w3_post", {})[k] = {"merged": m, "head": h, "theirs": t}
    for e in merged.get("entries", []):
        if e.get("id") in TRIO_IDS:
            s = e["shards"][0]
            for other in (head, theirs):
                for e2 in other.get("entries", []):
                    if e2.get("id") == e.get("id"):
                        s2 = e2["shards"][0]
                        assert ts_norm(s.get("owner_since") or "") >= \
                            ts_norm(s2.get("owner_since") or ""), \
                            "trio freshness regression %s" % e["id"]


def main():
    uu = uu_faces()
    if not uu:
        print("NO-UU nothing to resolve")
        sys.exit(0)
    special = {CODELY: resolve_codely, AUDIT: resolve_audit, TOKEN: resolve_token,
               X2LOG: lambda ev: line_union(X2LOG, ev, "x2watch"),
               ATTR: lambda ev: resolve_twin(ATTR, ev)}
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
          "merge_head": git("rev-parse", "MERGE_HEAD")[1].strip(), "faces": {}}
    for path in uu:
        if path in special:
            special[path](ev)
            ev.setdefault("faces", {})[path] = "special"
        else:
            resolve_twin(path, ev)
            ev.setdefault("faces", {})[path] = ev[path]
    pool_w3_post_assert(ev)
    for path in uu:
        with open(os.path.join(ROOT, path.replace("/", os.sep)), "rb") as f:
            data = f.read().decode("utf-8", "replace")
        for ln in data.splitlines():
            assert not (ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>")
                        or ln.startswith("=======")), "marker-residue " + path
        if path.endswith(".json"):
            with open(os.path.join(ROOT, path.replace("/", os.sep)), "rb") as f:
                json.loads(f.read().decode("utf-8"))
    rc, out, err = git("add", "--", *uu)
    assert rc == 0, "resolver add fail " + err[:200]
    ev["added_faces"] = len(uu)
    ev["committed"] = False
    with open(EVID, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("RESOLVED", len(uu), "faces (added, NOT committed -- attrition scan next)")
    sys.exit(0)


if __name__ == "__main__":
    main()
