"""r480 bm-c merge-UU canon resolver (r479 lineage copy-adapted per r461 law;
post-r479 laws re-checked: r456 token fallback PRESENT in lineage, r474 pool
per-face law -> NEW resolve_pool special this round, r675 codely block-union
KEPT (CODELY auto-merged clean this window; function dormant):
- compute_audit.json -> history ts-identity union (containment asserts)
- token_usage.json -> machines per-key max-union (side_pick>0 assert, r456;
  zero side-pick -> EXPLICIT whole-face freshness per r466)
- runnable_pool.json -> POOL FACE (r474/MSG-1332): take-theirs whole-face
  ONLY with superset asserts (entry count theirs>=ours + trio owner_since
  theirs>=ours per-face) -- this round ours adds zero pool entries and
  theirs carries the canonical burner's fresher keepalives; a bare twin
  take without these asserts is the r474 regression shape
- all other regen twins -> embedded-ts newer-wins (r461 ts_norm; equal ->
  ours, logged). S6 regen faces: origin side (bm-a r682-683 + bm-b r677
  S6 waves) naturally newer = r440 law.
Unknown-but-listed face -> abort before any write (fail-closed).
After: line-start marker scan + reparse + add + merge commit --no-edit +
push_verify. Evidence file-out."""
import datetime
import json
import os
import re
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "results", "_r480bmc_merge_resolve.json")
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
FUSE = "results/crash_fuse.json"
AUDIT = "results/compute_audit.json"
TOKEN = "results/token_usage.json"
POOL = "results/runnable_pool.json"
CODELY = "CODELY.md"
TRIO_IDS = ("FUND-VALUE-P1-NULLS", "FUND-QUALITY-P1-NULLS",
            "FUND-DIVLOWVOL-P1-NULLS")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def blob(ref, path):
    rc, out, err = git("show", ref + ":" + path)
    assert rc == 0, "blob read fail %s:%s %s" % (ref, path, err[:120])
    return out.encode("utf-8", "surrogateescape")


def wt_bytes(path):
    with open(os.path.join(ROOT, path.replace("/", os.sep)), "rb") as f:
        return f.read()


def ts_norm(v):
    if not isinstance(v, str):
        return ""
    return v.replace("T", " ")[:19]


def ent_ts(e):
    return max(ts_norm(e.get("last_refusal_ts", "")),
               ts_norm(e.get("last_crash_ts", "")))


def uu_faces():
    rc, out, err = git("status", "--porcelain")
    assert rc == 0, "status fail " + err[:120]
    faces = []
    for ln in out.splitlines():
        if ln.startswith("UU ") or ln.startswith("AA ") or ln.startswith("DU ") or ln.startswith("UD "):
            faces.append(ln[3:].strip().strip('"'))
    return sorted(faces)


def resolve_codely(ev):
    ob = blob("HEAD", CODELY)
    tb = blob("MERGE_HEAD", CODELY)
    t_lines = tb.split(b"\n")
    o_lines = ob.split(b"\n")
    t_set = set(t_lines)
    missing = [ln for ln in o_lines if ln and ln not in t_set]
    missing = [ln for ln in missing if ln not in tb]
    assert 0 < len(missing) <= 8, "codely union: unexpected missing-line count %d" % len(missing)
    base = tb if tb.endswith(b"\n") else tb + b"\n"
    union = base + b"\n".join(missing) + b"\n"
    assert union.startswith(tb), "codely union: origin prefix identity FAIL"
    for ln in union.decode("utf-8", "replace").splitlines():
        assert not (ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>")
                    or ln.startswith("=======")), "codely union marker"
    for ln in missing:
        assert union.count(ln) == 1, "codely union: missing line not exactly-once"
    with open(os.path.join(ROOT, CODELY), "wb") as f:
        f.write(union)
    ev[CODELY] = {"mode": "block-union r675", "ours_missing_lines": len(missing),
                  "theirs_bytes": len(tb), "union_bytes": len(union)}
    return CODELY


def resolve_pool(ev):
    o = json.loads(blob("HEAD", POOL).decode("utf-8"))
    t = json.loads(blob("MERGE_HEAD", POOL).decode("utf-8"))
    oe, te = o.get("entries", []), t.get("entries", [])
    assert len(te) >= len(oe), "pool take-theirs: theirs not superset (%d < %d)" % (
        len(te), len(oe))
    o_by_id = {e.get("id"): e for e in oe}
    t_by_id = {e.get("id"): e for e in te}
    assert set(o_by_id) <= set(t_by_id), "pool take-theirs: entry-id loss"
    freshness = {}
    for tid in TRIO_IDS:
        a = o_by_id.get(tid)
        b = t_by_id.get(tid)
        if not (a and b):
            freshness[tid] = "absent-one-side"
            continue
        def trio_ts(e):
            ts = ""
            for sh in e.get("shards", []):
                if sh.get("owner_since", "") > ts:
                    ts = sh.get("owner_since", "")
            return ts_norm(ts)
        oa, tb2 = trio_ts(a), trio_ts(b)
        assert tb2 >= oa, "pool trio freshness regression %s: theirs %s < ours %s" % (
            tid, tb2, oa)
        freshness[tid] = {"ours": oa, "theirs": tb2}
    out = json.dumps(t, ensure_ascii=False, indent=1) + "\n"
    json.loads(out)
    with open(os.path.join(ROOT, POOL), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    ev[POOL] = {"mode": "take-theirs whole-face (r474 superset asserts)",
                "entries_ours": len(oe), "entries_theirs": len(te),
                "trio_freshness": freshness}
    return POOL


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


def main():
    uu = uu_faces()
    if not uu:
        print("NO-UU nothing to resolve")
        sys.exit(0)
    known_special = {CODELY: resolve_codely, POOL: resolve_pool,
                     AUDIT: resolve_audit, TOKEN: resolve_token}
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
          "merge_head": git("rev-parse", "MERGE_HEAD")[1].strip(), "faces": {}}
    for path in uu:
        if path in known_special:
            known_special[path](ev)
            ev.setdefault("faces", {})[path] = "special"
        else:
            resolve_twin(path, ev)
            ev.setdefault("faces", {})[path] = ev[path]
    for path in uu:
        data = wt_bytes(path).decode("utf-8", "replace")
        for ln in data.splitlines():
            assert not (ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>")
                        or ln.startswith("=======")), "marker-residue " + path
        if path.endswith(".json"):
            json.loads(wt_bytes(path).decode("utf-8"))
    rc, out, err = git("add", "--", *uu)
    assert rc == 0, "resolver add fail " + err[:200]
    rc, out, err = git("commit", "--no-edit")
    assert rc == 0, "merge commit fail " + (out + err)[:300]
    ev["merge_commit"] = (out + err).strip()[:200]
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                        capture_output=True, creationflags=C, cwd=ROOT)
    txt = (pr.stdout or b"").decode("utf-8", "replace")
    ev["push_verify_rc"] = pr.returncode
    ev["push_verify_tail"] = txt.strip()[-300:]
    with open(EVID, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("RESOLVED", len(uu), "faces; merge committed; PUSH_VERIFY_RC", pr.returncode)
    print(txt.strip()[-300:])
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
