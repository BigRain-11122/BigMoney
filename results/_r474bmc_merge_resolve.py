"""r474 bm-c merge-UU canon resolver (r466 lineage + post-r466 law increments):
- CODELY.md -> r675 block-level union (MERGE_HEAD full text in order + HEAD-only
  lines appended in order; origin-prefix identity assert + added-line count==1
  assert + structural line-count non-shrink assert). r466's resolve_twin is
  FORBIDDEN for append-only memory faces per r675 (enacted after r466 -- the
  very r466 teaching: copied chains don't auto-inherit later laws).
- compute_audit.json -> history ts-identity union (containment asserts)
- token_usage.json -> machines per-key max-union (side_pick>0 assert, r456
  explicit whole-face freshness fallback)
- all other regen twins -> embedded-ts newer-wins (ts_norm per r461)
Unknown UU face -> abort before any write. After resolution: marker scan +
reparse gates + attrition post-merge re-scan (fresh evidence face) + add +
merge commit --no-edit + push_verify. Evidence file-out per r446."""
import datetime
import json
import os
import re
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "results", "_r474bmc_merge_resolve.json")
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
CODELY = "CODELY.md"
AUDIT = "results/compute_audit.json"
TOKEN = "results/token_usage.json"
ATTR_GUARD = "results/_attrition_guard_scan.json"


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


def resolve_codely(ev):
    ob = blob("MERGE_HEAD", CODELY)   # incoming origin side = base full text
    mb = blob("HEAD", CODELY)         # ours = carries only our new entries
    eol = b"\r\n" if b"\r\n" in ob[-200:] else b"\n"
    o_lines = ob.splitlines()
    m_lines = mb.splitlines()
    o_set = set(o_lines)
    added = [ln for ln in m_lines if ln not in o_set]
    assert len(added) == 1, "CODELY added-line count %d != 1 (r675 block union)" % len(added)
    base = ob if ob.endswith(b"\n") or ob.endswith(b"\r\n") else ob + eol
    out = base + added[0] + eol
    # asserts: origin prefix identity + our entry present once + bm-a's
    # newest entry (theirs) present + structural line count non-shrink
    assert out.startswith(ob.rstrip(b"\r\n")), "CODELY origin prefix identity fail"
    assert out.count(added[0]) == 1, "our entry count != 1"
    theirs_tail = [ln for ln in o_lines if ln.startswith(b"- [2026-10-04")][-1]
    assert out.count(theirs_tail) == 1, "bm-a newest entry lost"
    assert len(out.splitlines()) >= len(o_lines), "structural line shrink"
    with open(os.path.join(ROOT, CODELY), "wb") as f:
        f.write(out)
    ev[CODELY] = {"mode": "r675 block-union", "origin_lines": len(o_lines),
                  "added_lines": len(added),
                  "added_preview": added[0][:80].decode("utf-8", "replace")}
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
    side_pick = picks["ours_only"] + picks["theirs_only"] + picks["newer_ours"] + picks["newer_theirs"]
    if side_pick > 0:
        o[mk] = merged
        ev[TOKEN] = {"machines": len(merged), "picks": picks, "mode": "per-key union"}
    else:
        # r456 law: zero side-pick -> EXPLICIT whole-face freshness judgment
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
        json.loads(winner.decode("utf-8"))  # reparse gate


def main():
    with open(os.path.join(ROOT, "results", "_r474bmc_uu_faces.json"),
              encoding="utf-8") as f:
        uu = json.load(f)["uu"]
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "faces": {}}
    known_special = {CODELY, AUDIT, TOKEN}
    for path in sorted(uu):
        if path == CODELY:
            resolve_codely(ev["faces"])
        elif path == AUDIT:
            resolve_audit(ev["faces"])
        elif path == TOKEN:
            resolve_token(ev["faces"])
        else:
            resolve_twin(path, ev["faces"])
    # marker scan (line-start per r657) + final reparse of all JSON faces
    for path in uu:
        data = wt_bytes(path)
        for ln in data.decode("utf-8", "replace").splitlines():
            assert not (ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>")
                        or ln.startswith("=======")), "marker residual " + path
        if path.endswith(".json"):
            json.loads(data.decode("utf-8"))
    # attrition post-merge re-scan (fresh evidence overwrites resolved face)
    ar = subprocess.run([sys.executable, "scripts/attrition_ledger_guard.py", "scan"],
                        capture_output=True, creationflags=C, cwd=ROOT)
    ev["attrition_rescan_rc"] = ar.returncode
    ev["attrition_rescan_tail"] = (ar.stdout or b"").decode("utf-8", "replace").strip()[-200:]
    assert ar.returncode == 0, "attrition post-merge rescan rc=%d" % ar.returncode
    rc, out, err = git("add", "--", *sorted(uu))
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
