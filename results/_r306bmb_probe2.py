# -*- coding: utf-8 -*-
"""r306 bm-b: detail probe for resolver2 qualification (2nd collision batch).
ours=a4c0e3d4 (bm-a r300), theirs=448a972f (bm-b r305'). Read-only."""
import subprocess, json, difflib

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("blob fail %d %s" % (stage, path))
    return r.stdout

def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((".".join(path + [k]), "ONLY-B", None))
            elif k not in b:
                out.append((".".join(path + [k]), "ONLY-A", None))
            else:
                walk(a[k], b[k], path + [k], out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((".".join(path), "LEN %d vs %d" % (len(a), len(b)), None))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, path + [str(i)], out)
    else:
        if a != b:
            out.append((".".join(map(str, path)), repr(a)[:60], repr(b)[:60]))

# 1. full leaf diffs for the small files
for p in ("docs/daily_report/REPORT-2026-09-27.json", "results/token_usage.json",
          "results/lhb_update_status.json", "results/update_status.json",
          "results/futures_update_status.json"):
    o = json.loads(blob(2, p).decode("utf-8-sig"))
    t = json.loads(blob(3, p).decode("utf-8-sig"))
    out = []
    walk(o, t, [], out)
    print("=" * 8, p, "=> %d paths" % len(out))
    for pa, va, vb in out:
        print("   %s | A=%s | B=%s" % (pa, va, vb))

# 2. runnable_pool structure
p = "results/runnable_pool.json"
o = json.loads(blob(2, p).decode("utf-8-sig"))
t = json.loads(blob(3, p).decode("utf-8-sig"))
print("=" * 8, p, "top-keys A=%s B=%s" % (sorted(o), sorted(t)))
oe, te = o.get("entries", []), t.get("entries", [])
ok = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in oe}
tk = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in te}
print("  entries A=%d B=%d | A-only=%d B-only=%d shared=%d" % (
    len(oe), len(te), len(ok - tk), len(tk - ok), len(ok & tk)))
for r in oe:
    k = json.dumps(r, sort_keys=True, ensure_ascii=False)
    if k not in tk:
        print("  A-only entry:", json.dumps(r, ensure_ascii=False)[:400])
for r in te:
    k = json.dumps(r, sort_keys=True, ensure_ascii=False)
    if k not in ok:
        print("  B-only entry:", json.dumps(r, ensure_ascii=False)[:400])
for kk in sorted(set(o) | set(t)):
    if kk != "entries" and o.get(kk) != t.get(kk):
        print("  meta %s: A=%r B=%r" % (kk, o.get(kk), t.get(kk)))

# 3. compute_audit union preview
p = "results/compute_audit.json"
o = json.loads(blob(2, p).decode("utf-8-sig"))
t = json.loads(blob(3, p).decode("utf-8-sig"))
oh, th = o.get("history", []), t.get("history", [])
um = {}
for r in oh + th:
    um.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
print("=" * 8, p, "history A=%d B=%d union=%d" % (len(oh), len(th), len(um)))
print("  latest A ts=%s | B ts=%s" % (o.get("latest", {}).get("ts"), t.get("latest", {}).get("ts")))
print("  A last row ts=%s | B last row ts=%s" % (oh[-1].get("ts"), th[-1].get("ts")))

# 4. autofill_state preview
p = "results/autofill_state.json"
o = json.loads(blob(2, p).decode("utf-8-sig"))
t = json.loads(blob(3, p).decode("utf-8-sig"))
ol, tl = o.get("launches", []), t.get("launches", [])
oum = {}
for r in ol + tl:
    oum.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
print("=" * 8, p, "launches A=%d B=%d union=%d" % (len(ol), len(tl), len(oum)))
print("  last_tick A=%s | B=%s" % (o.get("last_tick", {}).get("ts"), t.get("last_tick", {}).get("ts")))
print("  A last ts=%s | B last ts=%s" % (ol[-1].get("ts"), tl[-1].get("ts")))
print("  top-keys equal:", sorted(o) == sorted(t))

# 5. x2_watch_log diff
p = "results/x2_watch_log.jsonl"
o_l = [l for l in blob(2, p).decode("utf-8", "replace").replace("\r\n", "\n").split("\n") if l.strip()]
t_l = [l for l in blob(3, p).decode("utf-8", "replace").replace("\r\n", "\n").split("\n") if l.strip()]
dl = list(difflib.unified_diff(o_l, t_l, lineterm="", n=0))
print("=" * 8, p, "A=%d B=%d difflines=%d" % (len(o_l), len(t_l), len(dl)))
for d in dl[:6]:
    print("   ", d[:120])

# 6. dashboard_status.js wrapper check + autofill face both sides
p = "results/dashboard_status.js"
o_raw, t_raw = blob(2, p), blob(3, p)
print("=" * 8, p, "A=%dB B=%dB | A head=%r | B head=%r" % (
    len(o_raw), len(t_raw), o_raw[:40], t_raw[:40]))
oj = json.loads(o_raw.decode("utf-8-sig").replace("window.DASH_DATA = ", "").rstrip().rstrip(";"))
tj = json.loads(t_raw.decode("utf-8-sig").replace("window.DASH_DATA = ", "").rstrip().rstrip(";"))
for side, d in (("A", oj), ("B", tj)):
    print("  %s meta.generated_at=%s autofill=%s" % (side, d.get("meta", {}).get("generated_at"),
          json.dumps(d.get("data", {}).get("autofill", {}), ensure_ascii=False)[:200]))

# 7. HANDOVER.md conflict hunks (raw from worktree)
print("=" * 8, "research/HANDOVER.md conflict region (worktree markers)")
raw = open("research/HANDOVER.md", "rb").read().decode("utf-8", "replace")
lines = raw.splitlines()
for i, l in enumerate(lines):
    if l.startswith(("<<<<<<<", "=======", ">>>>>>>")):
        lo = max(0, i - 4)
        hi = min(len(lines), i + 6)
        print("  --- hunk around line %d ---" % (i + 1))
        for j in range(lo, hi):
            print("  %4d| %s" % (j + 1, lines[j][:110]))
        i = hi
print("DETAIL-PROBE-DONE")
