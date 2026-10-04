"""r474 bm-c merge-UU canon resolver WAVE 3 (bm-b r673 closeout top):
- x2_watch_log.jsonl -> line-level union per r656/r453 (keep-first exact-line
  dedup, BOTH-side containment asserts, zero-loss line canon sets) -- jsonl
  append faces NEVER take one whole side (r474bmc wave-2 lesson family).
- all other regen twins -> embedded-ts newer-wins (ts_norm per r461; ours side
  carries bm-a@13:33 versions from wave-2 resolve, theirs carries bm-a@13:26-29
  via bm-b's closeout -- ts compare preserves the newer regen regardless of
  carrier machine).
After: marker scan + reparse + token_usage auto-merge containment verify
(machines keys of both sides present) + attrition post-merge re-scan + add +
merge commit --no-edit + push_verify. Evidence file-out per r446."""
import datetime
import json
import os
import re
import subprocess
import sys

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(ROOT, "results", "_r474bmc_merge_resolve3.json")
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
X2 = "results/x2_watch_log.jsonl"
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


def resolve_x2(ev):
    ob = blob("HEAD", X2)
    tb = blob("MERGE_HEAD", X2)
    # line canon split on \n (r656: mixed-EOL block counting trap -- count LINES)
    o_lines = ob.split(b"\n")
    t_lines = tb.split(b"\n")

    def canon(lines):
        return [ln.rstrip(b"\r") for ln in lines if ln.strip()]

    o_canon, t_canon = canon(o_lines), canon(t_lines)
    o_set, t_set = set(o_canon), set(t_canon)
    union = list(o_canon)
    seen = set(o_canon)
    added = 0
    for ln in t_canon:
        if ln not in seen:
            union.append(ln)
            seen.add(ln)
            added += 1
    # zero-loss containment asserts (canon set level per r656)
    assert o_set <= set(union), "ours line loss in x2 union"
    assert t_set <= set(union), "theirs line loss in x2 union"
    eol = b"\r\n" if b"\r\n" in ob[:4000] else b"\n"
    out = eol.join(union) + eol
    with open(os.path.join(ROOT, X2.replace("/", os.sep)), "wb") as f:
        f.write(out)
    ev[X2] = {"mode": "line-union r656", "ours": len(o_canon),
              "theirs": len(t_canon), "union": len(union), "theirs_only_added": added}
    return X2


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


def verify_token_automerge(ev):
    """token_usage.json auto-merged (no UU) -- verify machines keys of BOTH
    sides are present in the working tree (auto-merge loss check)."""
    ob = json.loads(blob("HEAD", TOKEN).decode("utf-8"))
    tb = json.loads(blob("MERGE_HEAD", TOKEN).decode("utf-8"))
    wt = json.loads(wt_bytes(TOKEN).decode("utf-8"))
    om, tm, wm = ob.get("machines", {}), tb.get("machines", {}), wt.get("machines", {})
    assert set(om) <= set(wm), "token automerge lost ours machine keys: %s" % (set(om) - set(wm))
    assert set(tm) <= set(wm), "token automerge lost theirs machine keys: %s" % (set(tm) - set(wm))
    ev[TOKEN] = {"mode": "auto-merge verify", "machines_ours": sorted(om),
                 "machines_theirs": sorted(tm), "machines_wt": sorted(wm)}


def main():
    with open(os.path.join(ROOT, "results", "_r474bmc_uu_faces3.json"),
              encoding="utf-8") as f:
        uu = json.load(f)["uu"]
    ev = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "faces": {}}
    for path in sorted(uu):
        if path == X2:
            resolve_x2(ev["faces"])
        else:
            resolve_twin(path, ev["faces"])
    verify_token_automerge(ev["faces"])
    # marker scan + reparse gates
    for path in uu:
        data = wt_bytes(path)
        for ln in data.decode("utf-8", "replace").splitlines():
            assert not (ln.startswith("<<<<<<<") or ln.startswith(">>>>>>>")
                        or ln.startswith("=======")), "marker residual " + path
        if path.endswith(".json"):
            json.loads(data.decode("utf-8"))
    # attrition post-merge re-scan (fresh evidence face)
    ar = subprocess.run([sys.executable, "scripts/attrition_ledger_guard.py", "scan"],
                        capture_output=True, creationflags=C, cwd=ROOT)
    ev["attrition_rescan_rc"] = ar.returncode
    ev["attrition_rescan_tail"] = (ar.stdout or b"").decode("utf-8", "replace").strip()[-200:]
    assert ar.returncode == 0, "attrition post-merge rescan rc=%d" % ar.returncode
    # absorb own 2 satengine treadmill lane faces + fresh attrition evidence
    # face into the merge close (r437 ③ absorb pattern)
    lane = ["results/saturation_engine/face_bm-c.json",
            "results/saturation_engine_state.bm-c.json",
            "results/_attrition_guard_scan.json"]
    add_list = sorted(uu) + lane
    rc, out, err = git("add", "--", *add_list)
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
    print("RESOLVED", len(uu), "faces (wave3); merge committed; PUSH_VERIFY_RC", pr.returncode)
    print(txt.strip()[-300:])
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
