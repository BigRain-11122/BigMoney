# r264 bm-b S7 push-collision resolver (rebase onto bm-a 5206d901 r261 closeout).
# Skill recipes: snapshot take-new by ts probe (r242 law: real ts keys only),
# rolling-ledger union zero-loss (r188/R208), mixed-dict+ledger autofill
# (union cap50 desc -> write-back asc, inner-ts last_tick, r245/r140 laws),
# append-log line union, memory-union CODELY, criteria items union by id.
# Parse-verify every json before write-back+add (r185 law). No PS redirection.
import json
import subprocess


def stage(s, path):
    return subprocess.run(["git", "show", f":{s}:{path}"], capture_output=True).stdout


def w(path, data):
    with open(path, "wb") as f:
        f.write(data)
    print("  wrote", path, len(data), "bytes")


def faces(b):
    return dict(bom=b.startswith(b"\xef\xbb\xbf"), crlf=b"\r\n" in b, tail=b.endswith(b"\n"))


RESOLVED = []

# ---------- 1. whole-take-mine snapshots (ts probed newer) ----------
for p in [
    "results/update_status.json",
    "results/token_usage.json",
    "results/fundamental_b_layer_filter.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",
]:
    w(p, stage(3, p))
    RESOLVED.append(p)

# ---------- 2. whole-take-theirs: post_review REPORT (their 17:53:14 run > my 17:52:55) ----------
w("results/post_review/REPORT-20260926.md", stage(2, "results/post_review/REPORT-20260926.md"))
RESOLVED.append("results/post_review/REPORT-20260926.md")

# ---------- 3. regime_state: union any list-ledger keys, else take-mine whole ----------
p = "results/regime_state.json"
a, b = json.loads(stage(2, p).decode("utf-8-sig")), json.loads(stage(3, p).decode("utf-8-sig"))
union_needed = False
for k in a:
    if isinstance(a[k], list) and a[k] != b.get(k):
        seen = {json.dumps(x, sort_keys=True) for x in a[k]}
        merged = list(a[k]) + [x for x in b[k] if json.dumps(x, sort_keys=True) not in seen]
        print(f"  regime ledger '{k}': |{len(a[k])}| + |{len(b[k])}| -> |{len(merged)}| union")
        a[k] = merged
        union_needed = True
if not union_needed:
    w(p, stage(3, p))  # no divergent ledger keys -> take newer ts whole
else:
    base = faces(stage(2, p))
    out = json.dumps(a, ensure_ascii=False, indent=1).replace("\n", "\r\n" if base["crlf"] else "\n")
    if base["tail"]:
        out += "\n" if not base["crlf"] else "\r\n"
    w(p, out.encode("utf-8"))
RESOLVED.append(p)

# ---------- 4. compute_audit: history union by ts, state fields take-new ----------
p = "results/compute_audit.json"
a, b = json.loads(stage(2, p).decode("utf-8-sig")), json.loads(stage(3, p).decode("utf-8-sig"))
ha, hb = a.get("history", []), b.get("history", [])
tsa = {h.get("ts") for h in ha}
merged = ha + [h for h in hb if h.get("ts") not in tsa]
merged.sort(key=lambda h: h.get("ts", ""))
print(f"  audit history: |{len(ha)}| + |{len(hb)}| -> |{len(merged)}| (zero-loss union)")
a["history"] = merged
for k, v in b.items():
    if k != "history" and not isinstance(v, list):
        a[k] = v  # take-mine state fields (ts 17:54:16 newer)
base = faces(stage(2, p))
out = json.dumps(a, ensure_ascii=False, indent=1).replace("\n", "\r\n" if base["crlf"] else "\n")
if base["tail"]:
    out += "\r\n" if base["crlf"] else "\n"
w(p, out.encode("utf-8"))
RESOLVED.append(p)

# ---------- 5. autofill_state: launches union (desc cap50 -> asc write-back) + inner-ts last_tick ----------
p = "results/autofill_state.json"
a, b = json.loads(stage(2, p).decode("utf-8-sig")), json.loads(stage(3, p).decode("utf-8-sig"))
la, lb = a.get("launches", []), b.get("launches", [])
key = lambda x: x.get("ts", "")
seen = {json.dumps(x, sort_keys=True) for x in la}
merged = la + [x for x in lb if json.dumps(x, sort_keys=True) not in seen]
merged.sort(key=key, reverse=True)
merged = merged[:50]
merged.sort(key=key)  # r245 law: write-back = producer append order (ts asc)
print(f"  launches: |{la}| + |{lb}| -> |{len(merged)}| (cap50 desc, written asc)")
a["launches"] = merged
ltb, lta = (b.get("last_tick") or {}).get("ts", ""), (a.get("last_tick") or {}).get("ts", "")
if ltb > lta:
    a["last_tick"] = b["last_tick"]
    print(f"  last_tick: took mine(st3) {ltb} > theirs {lta}")
else:
    print(f"  last_tick: kept theirs(st2 base) {lta} >= {ltb}")
assert isinstance(a.get("last_tick"), dict), "last_tick must be dict"
base = faces(stage(2, p))
out = json.dumps(a, ensure_ascii=False, indent=1).replace("\n", "\r\n" if base["crlf"] else "\n")
if base["tail"]:
    out += "\r\n" if base["crlf"] else "\n"
w(p, out.encode("utf-8"))
RESOLVED.append(p)

# ---------- 6. post_review.jsonl: line-level union (append-log) ----------
p = "results/post_review.jsonl"
ba, bb = stage(2, p), stage(3, p)
sa = [l for l in ba.decode("utf-8-sig").splitlines() if l.strip()]
sb = [l for l in bb.decode("utf-8-sig").splitlines() if l.strip()]
seen = set(sa)
merged = sa + [l for l in sb if l not in seen]
print(f"  jsonl: |{len(sa)}| + |{len(sb)}| -> |{len(merged)}| line union, +{len(merged) - len(sa)} mine-only")
eol = "\r\n" if b"\r\n" in ba else "\n"
tail = eol if ba.endswith(b"\n") or ba.endswith(b"\r\n") else ""
w(p, (eol.join(merged) + tail).encode("utf-8"))
for l in merged:
    json.loads(l)
print("  jsonl parse-verify: ALL rows valid")
RESOLVED.append(p)

# ---------- 7. post_review_criteria: items union by id (my re-anchored T-73 rows + their new row) ----------
p = "results/post_review_criteria.json"
mine = json.loads(stage(3, p).decode("utf-8-sig"))
theirs = json.loads(stage(2, p).decode("utf-8-sig"))
mi = {i["id"]: i for i in mine["items"]}
added = 0
for it in theirs["items"]:
    if it["id"] not in mi:
        mine["items"].append(it)
        added += 1
        print(f"  criteria +their item: {it['id']}")
assert mine["_reconciled"].startswith(theirs["_reconciled"]), "reconciled prefix law violated"
print(f"  criteria: {added} their items added, mine kept for T-73 re-anchors, _reconciled=mine (superset)")
out = json.dumps(mine, ensure_ascii=False, indent=1)
w(p, out.encode("utf-8"))
RESOLVED.append(p)

# ---------- 8. CODELY.md: line-level memory union ----------
p = "CODELY.md"
ta = stage(2, p).decode("utf-8-sig")
tb = stage(3, p).decode("utf-8-sig")
la = [l for l in ta.split("\n")]
lb = [l for l in tb.split("\n")]
seen = set(la)
newl = [l for l in lb if l not in seen and l.strip()]
print(f"  CODELY: theirs |{len(la)}| lines + {len(newl)} mine-only lines")
merged = ta
if newl:
    if not merged.endswith("\n"):
        merged += "\n"
    merged += "\n".join(newl) + "\n"
w(p, merged.encode("utf-8"))
RESOLVED.append(p)

print("RESOLVED:", len(RESOLVED), "files")
for p in RESOLVED:
    if p.endswith(".json") or p.endswith(".jsonl"):
        raw = open(p, "rb").read()
        txt = raw.decode("utf-8-sig")
        if p.endswith(".jsonl"):
            for l in txt.splitlines():
                if l.strip():
                    json.loads(l)
        else:
            json.loads(txt)
print("final parse-verify: ALL PASS")
