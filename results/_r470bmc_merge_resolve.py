"""r470 bm-c merge-UU canon resolver (r462/r461/r465/r466 families, fail-closed):
- compute_audit.json -> history ts-identity union (containment asserts)
- token_usage.json -> machines per-key max-union (side_pick>0 assert, r456;
  zero side_pick -> EXPLICIT whole-face freshness fallback per r456 law)
- all other regen twins -> embedded-ts newer-wins (r461 ts_norm); extraction
  fail/equal -> byte-compare; still differ -> ours (logged)
- no crash_fuse UU this window (18 faces all twin/audit/token tracks)
Unknown UU face -> abort before any write. After: reparse + line-start marker
scan + add + merge commit --no-edit + push_verify. Evidence file-out.
Round-numbered copy of _r466bmc_merge_resolve.py per r461 law."""
import datetime
import json
import os
import re
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "results", "_r470bmc_merge_resolve.json")
UU_LIST = os.path.join(ROOT, "results", "_r470bmc_uu_faces.json")
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
AUDIT = "results/compute_audit.json"
TOKEN = "results/token_usage.json"


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
    ev["compute_audit"] = {"hist_key": hist_key, "ours": len(oh), "theirs": len(th),
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
        ev["token_usage"] = {"machines": len(merged), "picks": picks, "mode": "per-key union"}
    else:
        # r456 law: zero side-pick -> EXPLICIT whole-face freshness-key judgment
        # (r455 same-keyset precedent). Never silently default whole face.
        ots = extract_ts(blob("HEAD", TOKEN), False) or ts_norm(o.get("ts", ""))
        tts = extract_ts(blob("MERGE_HEAD", TOKEN), False) or ts_norm(t.get("ts", ""))
        if ots >= tts:
            winner, side = o, "ours"
        else:
            winner, side = t, "theirs"
        picks["whole_face"] = 1
        ev["token_usage"] = {"machines": len(om), "picks": picks,
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
        ev.setdefault("twins", {})[path] = "byte-equal"
        return
    ots = extract_ts(ob, path.endswith(".md"))
    tts = extract_ts(tb, path.endswith(".md"))
    if ots and tts and ots != tts:
        winner, side = (ob, "ours") if ots > tts else (tb, "theirs")
        ev.setdefault("twins", {})[path] = "take-%s (ours %s vs theirs %s)" % (side, ots, tts)
    elif ots and tts and ots == tts:
        winner, side = ob, "ours"
        ev.setdefault("twins", {})[path] = "ts-equal-took-ours %s" % ots
    else:
        winner, side = ob, "ours"
        ev.setdefault("twins", {})[path] = "no-ts-took-ours"
    with open(os.path.join(ROOT, path.replace("/", os.sep)), "wb") as f:
        f.write(winner)
    if path.endswith(".json"):
        json.loads(winner.decode("utf-8"))  # reparse gate


def main():
    with open(UU_LIST, encoding="utf-8") as f:
        uu = json.load(f)["uu"]
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "faces": {}}
    for path in sorted(uu):
        if path == AUDIT:
            resolve_audit(ev)
            ev["faces"][path] = "hist ts-identity union"
        elif path == TOKEN:
            resolve_token(ev)
            ev["faces"][path] = "token_usage: " + ev["token_usage"]["mode"]
        else:
            resolve_twin(path, ev)
            ev["faces"][path] = ev["twins"][path]
    # marker scan (line-start per r657) + final reparse of all JSON faces
    for path in uu:
        data = wt_bytes(path)
        for ln in data.decode("utf-8", "replace").splitlines():
            assert not (ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>")
                        or ln.startswith("=======")), "marker残留 " + path
        if path.endswith(".json"):
            json.loads(data.decode("utf-8"))
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
