# -*- coding: utf-8 -*-
"""r327 bm-a rebase resolver v2 -- 11-UU second push-collision batch
(replay c923368f onto dd34727b; origin moved mid-resolve: bm-c r83 pair
30d392ef/78465909 + bm-b r327 pair 80a57a54/dd34727b landed).

Recipes per bigmoney-conflict-resolve skill (canonical Tools copy, post r83
L28 fix) + hand-adjudication:

  CODELY.md                   : in-place-archival adjudication (origin side
                                = bm-b r327 14th-batch hot-cold archival,
                                prefix assertion intentionally fails) ->
                                origin archived face + my 871B r326 asi8
                                suffix direct-concat (suffix not in origin,
                                zero loss both sides; archived entries live
                                in research/memory-archive/202609.md)
  results/autofill_state.json : launches composite-key (ts,machine,pid,
                                runner_sha256,entry,shard) dedup FIRST
                                (field-union merge same-key, no silent
                                double-store), ts-asc write-back, cap50
                                (post-r83 L28 recipe); last_tick tie 13:40:02
                                -> HEAD/origin (r140)
  results/compute_audit.json  : history union (ts,machine) composite key,
                                content-identity on collisions (r322);
                                latest take-new S2 13:45:27 > S3 13:43:46
  results/regime_state.json   : history union by asof + content check;
                                state take-new S2 13:45:36 > S3 13:43:55
  7 snapshot/daily faces      : deep ts probe -> take newer whole bytes
                                (all S2 newer this batch)
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def sh(*args):
    return subprocess.run(list(args), capture_output=True, cwd=REPO).stdout


def stage_bytes(path, n):
    return sh("git", "show", ":%d:%s" % (n, path))


def deep_ts(doc):
    best = ""
    stack = [doc]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
        elif isinstance(x, str):
            m = re.search(r"2026-09-2\d[ T]\d{2}:\d{2}(:\d{2})?", x)
            if m and m.group(0) > best:
                best = m.group(0)
    return best


def w(path, b):
    with open(path.replace("/", "\\"), "wb") as fh:
        fh.write(b)


rep = []

# ---------- 1. CODELY.md in-place-archival adjudication ----------
p = "CODELY.md"
s1 = stage_bytes(p, 1).rstrip(b"\r\n")
s2 = stage_bytes(p, 2).rstrip(b"\r\n")
s3 = stage_bytes(p, 3).rstrip(b"\r\n")
assert s3.startswith(s1), "MINE side lost prefix (unexpected)"
assert not s2.startswith(s1), "origin side unexpectedly plain-append"
suf3 = s3[len(s1):]
assert suf3.startswith(b"\n- [2026-09-27 13:4x r326 bm-a]"), "my suffix shape changed"
# my suffix entries must not already exist on origin side
for probe in (b"asi8", b"r326 bm-a"):
    assert probe not in s2, "suffix entry already on origin side"
crlf = b"\r\n" in stage_bytes(p, 2)
merged = s2 + suf3 + (b"\r\n" if crlf else b"\n")
txt = merged.decode("utf-8")  # strict gate
for probe in ("asi8", "r83 bm-c", "town", "r326 bm-a"):
    assert probe in txt, "merged CODELY missing %r" % probe
w(p, merged)
sh("git", "add", p)
rep.append("CODELY.md in-place-archival: origin %dB + my r326 suffix %dB + nl = %dB (CRLF=%s); r83+town+asi8 all present" % (len(s2), len(suf3), len(merged), crlf))

# ---------- 2. autofill_state.json composite-key union (post-r83 recipe) ----------
p = "results/autofill_state.json"
b2, b3 = stage_bytes(p, 2), stage_bytes(p, 3)
crlf = b"\r\n" in b2 or b"\r\n" in b3
d2, d3 = json.loads(b2.decode("utf-8")), json.loads(b3.decode("utf-8"))
l2, l3 = d2.get("launches") or [], d3.get("launches") or []
KEYF = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")


def ckey(e):
    return tuple(e.get(k) for k in KEYF)


union = {}
flagged = []
for e in l2 + l3:
    k = ckey(e)
    if k in union:
        if json.dumps(union[k], sort_keys=True) != json.dumps(e, sort_keys=True):
            # field-union merge: keep one entry, union fields, no double-store
            m = dict(union[k])
            for fk, fv in e.items():
                if fk not in m:
                    m[fk] = fv
                elif m[fk] != fv:
                    if isinstance(fv, (int, float)) and isinstance(m[fk], (int, float)):
                        m[fk] = max(m[fk], fv)  # counter fields: conservative max
                        flagged.append((k, fk))
                    else:
                        m[fk] = union[k][fk]   # keep canonical origin value
            union[k] = m
    else:
        union[k] = e
launches = sorted(union.values(), key=lambda e: str(e.get("ts") or ""))
if len(launches) > 50:
    launches = sorted(union.values(), key=lambda e: str(e.get("ts") or ""), reverse=True)[:50]
    launches.sort(key=lambda e: str(e.get("ts") or ""))
doc = dict(d2)  # HEAD/origin face for non-launches fields
doc["launches"] = launches
lt2, lt3 = d2.get("last_tick"), d3.get("last_tick")
t2 = str((lt2 or {}).get("ts") or "")
t3 = str((lt3 or {}).get("ts") or "")
doc["last_tick"] = lt2 if t2 >= t3 else lt3  # tie -> HEAD(origin) r140
assert isinstance(doc["last_tick"], dict)
s = json.dumps(doc, ensure_ascii=False, indent=1)
json.loads(s)
w(p, (s + ("\r\n" if crlf else "\n")).encode("utf-8"))
sh("git", "add", p)
rep.append("autofill_state.json composite-key union %d+%d -> %d (dedup-first, field-union merges=%d flagged-counter-merges); last_tick %s vs %s tie->HEAD" % (len(l2), len(l3), len(launches), len(flagged), t2, t3))

# ---------- 3. compute_audit.json composite-key history union ----------
p = "results/compute_audit.json"
d2 = json.loads(stage_bytes(p, 2).decode("utf-8"))
d3 = json.loads(stage_bytes(p, 3).decode("utf-8"))
h2, h3 = d2["history"], d3["history"]
un, col = {}, 0
for e in h2 + h3:
    k = (e.get("ts"), e.get("machine"))
    if k in un:
        col += 1
        assert json.dumps(un[k], sort_keys=True) == json.dumps(e, sort_keys=True), "content-diff %r (r322 escalate)" % (k,)
    else:
        un[k] = e
merged_h = sorted(un.values(), key=lambda e: e.get("ts") or "")
newer = d2 if deep_ts(d2) >= deep_ts(d3) else d3
doc = dict(newer)
doc["history"] = merged_h
s = json.dumps(doc, ensure_ascii=False, indent=1)
json.loads(s)
w(p, s.encode("utf-8"))
sh("git", "add", p)
rep.append("compute_audit.json history union %d+%d -> %d (collisions %d content-identical); latest take-new %s vs %s" % (len(h2), len(h3), len(merged_h), col, deep_ts(d2), deep_ts(d3)))

# ---------- 4. regime_state.json asof union + take-new ----------
p = "results/regime_state.json"
d2 = json.loads(stage_bytes(p, 2).decode("utf-8"))
d3 = json.loads(stage_bytes(p, 3).decode("utf-8"))
h2, h3 = d2.get("history") or [], d3.get("history") or []
un = {}
for e in h2 + h3:
    k = e.get("asof")
    if k in un:
        assert json.dumps(un[k], sort_keys=True) == json.dumps(e, sort_keys=True), "asof content-diff %r" % (k,)
    else:
        un[k] = e
merged_h = sorted(un.values(), key=lambda e: str(e.get("asof") or ""))
newer = d2 if deep_ts(d2) >= deep_ts(d3) else d3
doc = dict(newer)
if merged_h:
    doc["history"] = merged_h
s = json.dumps(doc, ensure_ascii=False, indent=1)
json.loads(s)
w(p, s.encode("utf-8"))
sh("git", "add", p)
rep.append("regime_state.json history union %d+%d -> %d by asof; state take-new %s" % (len(h2), len(h3), len(merged_h), deep_ts(d2)))

# ---------- 5. take-newer snapshot/daily faces ----------
SNAPS = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/dashboard_status.json",
    "results/futures_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]
for p in SNAPS:
    b2, b3 = stage_bytes(p, 2), stage_bytes(p, 3)
    if b2 == b3:
        w(p, b3); sh("git", "add", p)
        rep.append("%s identical bytes" % p)
        continue
    try:
        t2 = deep_ts(json.loads(b2.decode("utf-8")))
        t3 = deep_ts(json.loads(b3.decode("utf-8")))
    except Exception:
        t2 = t3 = ""
    if t3 and (not t2 or t3 > t2):
        w(p, b3); sh("git", "add", p); side = "S3(mine)"
    elif t2 and (not t3 or t2 > t3):
        w(p, b2); sh("git", "add", p); side = "S2(origin)"
    else:
        w(p, b2); sh("git", "add", p); side = "HEAD-side(tie/no-ts)"
    if p.endswith(".json"):
        json.loads(open(p.replace("/", "\\"), "rb").read().decode("utf-8"))
    rep.append("%-46s ts-diffpick %s vs %s -> %s" % (p, t2, t3, side))

uu = sh("git", "diff", "--name-only", "--diff-filter=U").decode().splitlines()
assert not uu, "still unmerged: %r" % uu
for line in rep:
    print(line)
print("RESOLVER-V2 OK: 11/11 resolved, rebase ready for --continue")
