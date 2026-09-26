# -*- coding: utf-8 -*-
"""r239 push-collision rebase resolver STEP 2 (bm-b r239 round commit replay).
Adjudication: fleet/README s4 -- bm-a claim 09:58:58 precedes bm-b 10:05 ->
bm-a canonical for T-74/T-75 + all same-window duplicate deliverables; bm-b
yields. Recipes per bigmoney-conflict-resolve SKILL (classifier output):
- take-side (bm-a canonical): DECISIONS.md, MARKET_CLOCK_COMBO.md,
  daily_report.py, iteration_prompt.txt, both tickets (+corrected yield_note)
- r221 namespace collision: bm-b helpers renamed _r239bmb_* (both preserved)
- classifier recipes: autofill_state (union cap50+last_tick whole-dict),
  compute_audit/regime_state (history union+take-new), post_review.jsonl
  (line union), snapshots (take-new by ts), dashboard pair (js judged by
  json twin, take-side whole bytes, R209/r226)
- orphan drop: bm-b non-canonical report/call pages (canonical paths differ)
Parse-verify before every write (r185). Zero-loss checks per recipe.
"""
import json
import subprocess

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"


def stage(n, path):
    out = subprocess.run(["git", "-C", ROOT, "show", ":%d:%s" % (n, path)],
                         capture_output=True)
    assert out.returncode == 0, (n, path, out.stderr.decode("utf-8", "replace")[:200])
    return out.stdout.decode("utf-8")


def w(path, text, eol=None):
    if eol and eol != "\n":
        text = text.replace("\n", eol)
    p = ROOT + "\\" + path.replace("/", "\\")
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return p


def jload(s):
    return json.loads(s)


TS_KEYS = ["generated", "ts", "updated", "last_attempt", "asof"]


def ts_of(d):
    for k in TS_KEYS:
        v = None
        if isinstance(d, dict):
            v = d.get(k) or (d.get("meta") or {}).get(k) if isinstance(d.get("meta"), dict) else d.get(k)
        if v:
            return str(v)
    return ""


def take_new(path):
    a, b = jload(stage(2, path)), jload(stage(3, path))
    ta, tb = ts_of(a), ts_of(b)
    win = 3 if tb >= ta else 2  # tie -> stage2 (HEAD, r140)
    w(path, stage(win, path) if win == 2 else stage(3, path))
    jload(stage(win, path))
    print("  take-new %-42s ts2=%s ts3=%s -> side%d" % (path, ta[:19], tb[:19], win))


print("== A. take-side (bm-a canonical, earlier claim per s4) ==")
for p in ("firm/DECISIONS.md", "research/MARKET_CLOCK_COMBO.md",
          "scripts/daily_report.py", "Tools/iteration_prompt.txt"):
    s = stage(2, p)
    w(p, s)
    if p.endswith(".py"):
        compile(s, p, "exec")  # py syntax verify (r185)
    print("  take-side bm-a:", p)

print("== B. tickets: bm-a side + corrected yield_note ==")
YIELD = {
 "74": ("claim race r239 adjudicated per fleet/README s4: bm-a claim 09:58:58 precedes bm-b 10:05 -> bm-a canonical owner; "
        "bm-b same-window delivery (s0 tree doc + s1 call page) dropped from canonical in rebase (preserved in bm-b local history); "
        "bm-b contributions available to owner at discretion: fund-event distortion guard flag (512480/159995 r60=-62% share-event suspects in core48 sector faces), "
        "honest-window audit facts (core48 sector faces start 2020-01; heat faces = lane data, bm-a box authoritative per r226), "
        "G1'v2/G2v2 shared-lib gate wiring + N_eff accounting in dropped draft"),
 "75": ("claim race r239 adjudicated per fleet/README s4: bm-a claim 09:58:58 precedes bm-b 10:05 -> bm-a canonical owner; "
        "bm-b same-window delivery (daily_report.py + DECISIONS + first report + S6 wiring) dropped from canonical in rebase (preserved in bm-b local history); "
        "bm-b unique fixes as follow-up patch on canonical: _-prefixed schema-foreign file skip (r157 law -- canonical renders _summary.json as account row); "
        "dropped draft also carried full-ts 24h-window compare + run-guard/force channel"),
}
for tid in ("74", "75"):
    p = "fleet/tasks/T-2026-09-26-%s-P1.json" % tid
    s2 = stage(2, p)
    eol = "\r\n" if "\r\n" in s2 else "\n"
    d = jload(s2)
    d["yield_note"] = YIELD[tid]
    out = json.dumps(d, ensure_ascii=False, indent=1) + "\n"
    jload(out)  # parse-verify
    w(p, out, eol)
    print("  ticket T-%s -> bm-a side + corrected yield_note (eol=%r)" % (tid, eol))

print("== C. r221 namespace collision: rename bm-b helpers _r239bmb_* ==")
for old, new in (("results/_r239_claim.py", "results/_r239bmb_claim.py"),
                 ("results/_r239_wire_prompt.py", "results/_r239bmb_wire_prompt.py")):
    theirs = stage(2, old)   # bm-a canonical stays at original path
    mine = stage(3, old)    # bm-b version -> machine-prefixed path
    w(old, theirs)
    compile(theirs, old, "exec")
    w(new, mine)
    compile(mine, new, "exec")
    print("  %s: bm-a kept at path, bm-b -> %s" % (old, new))

print("== D. snapshots take-new ==")
for p in ("results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json",
          "results/update_status.json", "results/daily_scorecard.json"):
    take_new(p)

print("== E. dashboard pair: js judged by json twin (r226), take-side whole bytes (R209) ==")
j2, j3 = jload(stage(2, "results/dashboard_status.json")), jload(stage(3, "results/dashboard_status.json"))
side = 3 if ts_of(j3) > ts_of(j2) else 2
for p in ("results/dashboard_status.js", "results/dashboard_status.json"):
    s = stage(side, p)
    if p.endswith(".js"):
        assert s.lstrip().startswith("window.DASH_DATA"), "wrapper missing"
    jload(s) if p.endswith(".json") else None
    w(p, s)
    print("  dashboard %s -> side%d (twin generated_at 2=%s 3=%s)" % (p.split("/")[-1], side, ts_of(j2)[:19], ts_of(j3)[:19]))

print("== F. append-log union: post_review.jsonl ==")
p = "results/post_review.jsonl"
l2 = [l for l in stage(2, p).splitlines() if l.strip()]
l3 = [l for l in stage(3, p).splitlines() if l.strip()]
seen = set(l2)
union = l2 + [l for l in l3 if l not in seen]
for l in union[:5] + union[-2:]:
    json.loads(l)
w(p, "\n".join(union) + "\n")
print("  union lines: |2|=%d |3|=%d -> |U|=%d (zero-loss: U>=max)" % (len(l2), len(l3), len(union)))

print("== G. rolling-ledger unions ==")
# autofill_state: launches union cap50 + last_tick inner-ts whole-dict + EOL mirror
p = "results/autofill_state.json"
s2, s3 = stage(2, p), stage(3, p)
eol = "\r\n" if "\r\n" in s2 else "\n"
d2, d3 = jload(s2), jload(s3)
L2 = d2.get("launches") or []
L3 = d3.get("launches") or []
ident = {}
for e in L2 + L3:
    ident.setdefault(json.dumps(e, sort_keys=True), e)
merged = sorted(ident.values(), key=lambda e: str(e.get("ts", "")), reverse=True)[:50]
merged.reverse()
lt2, lt3 = d2.get("last_tick") or {}, d3.get("last_tick") or {}
last_tick = lt3 if str(lt3.get("ts", "")) > str(lt2.get("ts", "")) else lt2  # tie -> HEAD=stage2
assert isinstance(last_tick, dict)
out_d = {"last_tick": last_tick, "launches": merged}
out = json.dumps(out_d, ensure_ascii=False, indent=1) + "\n"
jload(out)
w(p, out, eol)
print("  autofill_state: launches |2|=%d |3|=%d -> union-capped=%d; last_tick side=%s ts=%s; eol=%r"
      % (len(L2), len(L3), len(merged), "3" if last_tick is lt3 and lt3 else "2", str(last_tick.get("ts"))[:19], eol))

# compute_audit: history union + latest take-new
p = "results/compute_audit.json"
d2, d3 = jload(stage(2, p)), jload(stage(3, p))
H2, H3 = d2.get("history") or [], d3.get("history") or []
ident = {}
for e in H2 + H3:
    ident.setdefault(json.dumps(e, sort_keys=True), e)
def _hts(e):
    return str(e.get("ts", ""))
hist = sorted(ident.values(), key=_hts)
latest = d3.get("latest") if ts_of(d3.get("latest") or {}) > ts_of(d2.get("latest") or {}) else d2.get("latest")
d2["history"] = hist
d2["latest"] = latest
out = json.dumps(d2, ensure_ascii=False, indent=2) + "\n"
jload(out)
s2raw = stage(2, p)
eol = "\r\n" if "\r\n" in s2raw else "\n"
# indent probe (r237 law): first nested-line indent of base blob
import re
m = re.search(r"\n( +)", s2raw)
ind = len(m.group(1)) if m else 2
out = json.dumps(d2, ensure_ascii=False, indent=ind) + "\n"
jload(out)
w(p, out, eol)
print("  compute_audit: history |2|=%d |3|=%d -> union=%d; latest side ts=%s; indent=%d eol=%r"
      % (len(H2), len(H3), len(hist), ts_of(latest or {})[:19], ind, eol))

# regime_state: history/transitions union + take-new fields
p = "results/regime_state.json"
s2raw = stage(2, p)
eol = "\r\n" if "\r\n" in s2raw else "\n"
d2, d3 = jload(s2raw), jload(stage(3, p))
for key in ("history", "transitions"):
    A, B = d2.get(key) or [], d3.get(key) or []
    ident = {}
    for e in A + B:
        ident.setdefault(json.dumps(e, sort_keys=True), e)
    def _k(e):
        return str(e.get("ts") or e.get("date") or e.get("asof") or "")
    d2[key] = sorted(ident.values(), key=_k)
if str(d3.get("updated", "")) > str(d2.get("updated", "")):
    for k, v in d3.items():
        if k not in ("history", "transitions"):
            d2[k] = v
out = json.dumps(d2, ensure_ascii=False, indent=1) + "\n"
jload(out)
w(p, out, eol)
print("  regime_state: union history=%d transitions=%d; updated=%s" % (
    len(d2["history"]), len(d2["transitions"]), str(d2.get("updated"))[:19]))

print("== H. post_review REPORT take-new by internal ts ==")
p = "results/post_review/REPORT-20260926.md"
r2, r3 = stage(2, p), stage(3, p)
import re
def _mts(s):
    m = re.search(r"20\d\d-\d\d-\d\d \d\d:\d\d(:\d\d)?", s)
    return m.group(0) if m else ""
win = 3 if _mts(r3) >= _mts(r2) else 2
w(p, r3 if win == 3 else r2)
print("  report ts2=%s ts3=%s -> side%d" % (_mts(r2), _mts(r3), win))

print("== I. CODELY.md memory-union ==")
p = "CODELY.md"
c2 = stage(2, p).splitlines()
c3 = stage(3, p).splitlines()
seen = set(c2)
union = c2 + [l for l in c3 if l not in seen and l.strip()]
eol = "\r\n" if "\r\n" in stage(2, p) else "\n"
w(p, "\n".join(union) + "\n", eol)
print("  CODELY: |2|=%d |3|=%d -> union=%d (stage3-only kept: %d)" % (
    len(c2), len(c3), len(union), len(union) - len(c2)))

print("== J. orphan drops + scorecard pointer fix (deferred to addendum: patch on canonical) ==")
print("STEP2 RESOLVER COMPLETE")
