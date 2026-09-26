"""R267 bm-a replay-2 resolver (17-UU vs bm-b r272 20:07-08 chain).

Facts probed: bm-b chain newer (:2) on every snapshot face -> take :2 whole;
post_review REPORT md :3 newer (20:03:01 > 20:02:10) -> take :3;
post_review.jsonl both 1331 lines -> line union (both run rows zero-loss);
compute_audit history union + latest take-new; autofill launches union + last_tick
inner-ts compare; scorecards asserted volatile-only diff before take-new.
"""
import subprocess, json, re

def blob(stage, f):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, f)], capture_output=True)
    assert r.returncode == 0, (stage, f, r.stderr[:200])
    return r.stdout

def probe_face(b):
    lines = b.split(b"\n")
    indent = 0
    for ln in lines[1:6]:
        m = re.match(rb"^( +)", ln)
        if m:
            indent = len(m.group(1)); break
    return {"indent": indent, "ensure_ascii": (not any(c >= 0x80 for c in b)) and (b"\\u" in b),
            "tail_nl": b.endswith(b"\n"), "crlf": b"\r\n" in b}

def emit(obj, face):
    s = json.dumps(obj, indent=face["indent"], ensure_ascii=face["ensure_ascii"])
    b = s.encode("utf-8")
    if face["crlf"]: b = b.replace(b"\n", b"\r\n")
    if face["tail_nl"] and not b.endswith(b"\n"): b += b"\n"
    if not face["tail_nl"] and b.endswith(b"\n"): b = b[:-1]
    return b

def deepdiff(a, b, path=""):
    out = []
    if type(a) != type(b): return [(path, "TYPE")]
    if isinstance(a, dict):
        for k in set(a) | set(b):
            if k not in a: out.append((path + "/" + str(k), "ONLY_B"))
            elif k not in b: out.append((path + "/" + str(k), "ONLY_A"))
            else: out += deepdiff(a[k], b[k], path + "/" + str(k))
    elif isinstance(a, list):
        if len(a) != len(b): out.append((path, "LEN", len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)): out += deepdiff(x, y, path + "[%d]" % i)
    else:
        if a != b: out.append((path, "VAL", repr(a)[:50], repr(b)[:50]))
    return out

VOLATILE = re.compile(r"generated|elapsed|stamp|asof|/ts$|updated", re.I)

# ---- 1. whole-byte take-:2 (bm-b newer chain) --------------------------------
TAKE2 = [
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/heat_update_status.json", "results/lhb_update_status.json",
    "results/token_usage.json", "results/update_status.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "docs/daily_report/REPORT-2026-09-26.json", "docs/daily_report/REPORT-2026-09-26.md",
]
for f in TAKE2:
    b2 = blob(2, f)
    if f.endswith(".json"):
        json.loads(b2.decode("utf-8-sig"))
    open(f, "wb").write(b2)
    print("take2 whole:", f, len(b2))

# scorecard volatile-only assertion (determinism evidence)
for f in ["results/scorecard_v1.json", "results/strategy_scorecard.json"]:
    d2 = json.loads(blob(2, f).decode("utf-8-sig")); d3 = json.loads(blob(3, f).decode("utf-8-sig"))
    real = [d for d in deepdiff(d2, d3) if not VOLATILE.search(d[0])]
    print(f, "non-volatile diffs:", len(real), real[:3])
    assert len(real) == 0, (f, real[:5])

# ---- 2. post_review REPORT md: take :3 (newer) ---------------------------------
b3 = blob(3, "results/post_review/REPORT-20260926.md")
open("results/post_review/REPORT-20260926.md", "wb").write(b3)
print("take3 whole: results/post_review/REPORT-20260926.md", len(b3))

# ---- 3. post_review.jsonl: line union zero-loss ----------------------------------
f = "results/post_review.jsonl"
l2 = blob(2, f).decode("utf-8-sig").splitlines()
l3 = blob(3, f).decode("utf-8-sig").splitlines()
set2 = set(l2)
extra3 = [l for l in l3 if l not in set2]
union = l2 + extra3
face2 = blob(2, f)
nl = b"\r\n" if b"\r\n" in face2 else b"\n"
open(f, "wb").write(nl.join(l.encode("utf-8") for l in union) + (nl if face2.endswith(b"\n") else b""))
for l in union:
    json.loads(l)
print("post_review.jsonl union:", len(l2), "|", len(l3), "->", len(union), "(extra3 =", len(extra3), ")")

# ---- 4. compute_audit: history union + latest take-new (:2) ----------------------
f = "results/compute_audit.json"
b2, b3 = blob(2, f), blob(3, f)
d2, d3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
seen, rows = set(), []
for r in d2["history"] + d3["history"]:
    k = json.dumps(r, sort_keys=True)
    if k not in seen: seen.add(k); rows.append(r)
rows.sort(key=lambda r: r.get("ts", ""))
out = {"latest": d2["latest"], "history": rows}
open(f, "wb").write(emit(out, probe_face(b2)))
json.loads(open(f, "rb").read().decode("utf-8-sig"))
print("compute_audit history union:", len(d2["history"]), "|", len(d3["history"]), "->", len(rows))

# ---- 5. autofill_state: launches union cap50 + last_tick inner-ts ------------------
f = "results/autofill_state.json"
b2, b3 = blob(2, f), blob(3, f)
d2, d3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
seen, rows = set(), []
for r in d2["launches"] + d3["launches"]:
    k = json.dumps(r, sort_keys=True)
    if k not in seen: seen.add(k); rows.append(r)
rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
rows = rows[:50]
rows.sort(key=lambda r: r.get("ts", ""))
lt2, lt3 = d2["last_tick"], d3["last_tick"]
last_tick = lt2 if lt2.get("ts", "") >= lt3.get("ts", "") else lt3   # tie -> HEAD(:2, r140)
open(f, "wb").write(emit({"launches": rows, "last_tick": last_tick}, probe_face(b2)))
chk = json.loads(open(f, "rb").read().decode("utf-8-sig"))
assert isinstance(chk["last_tick"], dict)
print("autofill resolved: launches", len(chk["launches"]), "last_tick", chk["last_tick"]["ts"], chk["last_tick"]["machine"])

# ---- 6. regime_state: union history + fields take-new (:2 newer) ---------------------
f = "results/regime_state.json"
b2, b3 = blob(2, f), blob(3, f)
d2, d3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
for key in ("transitions", "history"):
    seen, rows = set(), []
    for r in d2.get(key, []) + d3.get(key, []):
        k = json.dumps(r, sort_keys=True)
        if k not in seen: seen.add(k); rows.append(r)
    d2[key] = rows
    print("regime_state", key, "union ->", len(rows))
open(f, "wb").write(emit(d2, probe_face(b2)))
json.loads(open(f, "rb").read().decode("utf-8-sig"))
print("ALL RESOLVED FILES PARSE-VERIFIED")
