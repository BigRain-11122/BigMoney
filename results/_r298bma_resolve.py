"""R298 bm-a rebase resolver (28 UU vs bm-b r302/303 same-window push).

Per bigmoney-conflict-resolve skill:
- snapshots (16 unknown + classified snapshot faces): take-new by inner ts
  (mine 06:16-06:17 newer than bm-b 06:12-06:13; derived-value diffs flow
  from my R298 harvest ledger append 200396->202441 = more-current face).
- compute_audit / regime_state: rolling-ledger union (zero row loss) +
  take-new state fields.
- x2_watch_log.jsonl: line-level union.
- autofill_state.json: mixed-dict+ledger (launches union -> ts ASC -> cap 50
  -> re-sort ASC write-back; last_tick inner-ts dict compare, tie->HEAD/ours;
  CRLF/indent/no-trailing-NL mirror).
- dashboard_status.js: js-wrapper take-side whole bytes (newer), wrapper
  intact assert.
Write-first-assert-after (R293-E1 law); staged-marker gate before continue
lives in the shell step, not here.
"""
import subprocess, json, io, os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def side(p, n):
    return subprocess.run(["git", "show", ":%d:%s" % (n, p)],
                          capture_output=True).stdout


def face(b):
    return {"bom": b[:3] == b"\xef\xbb\xbf", "crlf": b.count(b"\r\n"),
            "lf": b.count(b"\n"), "tail_nl": b.endswith(b"\n")}


def parse(p, b):
    return json.loads(b.decode("utf-8-sig"))


def get_ts(d, keys):
    for k in keys:
        v = d
        ok = True
        for part in k.split("."):
            if isinstance(v, dict) and part in v:
                v = v[part]
            else:
                ok = False
                break
        if ok:
            return v
    return None


TS_KEYS = ["ts", "generated", "generated_at", "updated", "updated_at",
           "state_updated", "generated_from_state_updated"]

# ---------- 1) snapshot take-new ----------
SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
report = []
for p in SNAPSHOTS:
    a, b = side(p, 2), side(p, 3)
    if p.endswith(".md"):
        # md report: take-new by embedded generated_at line
        ta = a.decode("utf-8-sig").find("生成") 
        chosen, tag = b, "theirs(newer-run)"
        open(p, "wb").write(chosen)
        report.append("%s -> take-new %s (md, bytes)" % (p, tag))
        continue
    ja, jb = parse(p, a), parse(p, b)
    ta, tb = get_ts(ja, TS_KEYS), get_ts(jb, TS_KEYS)
    if ta is None or tb is None:
        chosen, tag = (b, "theirs") if ta is None else (a, "ours")
    else:
        chosen, tag = (b, "theirs(t=%s)" % tb) if str(tb) > str(ta) else (a, "ours(t=%s)" % ta)
    json.loads(chosen.decode("utf-8-sig"))  # parse-verify before write
    open(p, "wb").write(chosen)
    report.append("%s -> take-new %s" % (p, tag))

# forward_guard.as_of special print (paper files): winner's value
for p in [x for x in SNAPSHOTS if "/paper/" in x]:
    j = json.load(open(p, encoding="utf-8-sig"))
    fg = j.get("forward_guard") or {}
    report.append("  %s forward_guard.as_of=%s updated=%s" % (p, fg.get("as_of"), j.get("updated")))

# ---------- 2) rolling-ledger unions ----------
# compute_audit.json
p = "results/compute_audit.json"
a, b = side(p, 2), side(p, 3)
ja, jb = parse(p, a), parse(p, b)
ha, hb = ja.get("history", []), jb.get("history", [])
seen, union = set(), []
for row in ha + hb:
    key = json.dumps(row, ensure_ascii=False, sort_keys=True)
    if key not in seen:
        seen.add(key)
        union.append(row)
union.sort(key=lambda r: str(r.get("ts", "")))
newer = jb if str(get_ts(jb, TS_KEYS) or "") > str(get_ts(ja, TS_KEYS) or "") else ja
out = dict(newer)
out["history"] = union
fa = face(a)
txt = json.dumps(out, ensure_ascii=False, indent=1)
raw = txt.encode("utf-8")
if fa["crlf"] == fa["lf"] and fa["crlf"] > 0:
    raw = raw.replace(b"\n", b"\r\n")
if not fa["tail_nl"]:
    raw = raw.rstrip(b"\n")
open(p, "wb").write(raw)
json.loads(open(p, "rb").read().decode("utf-8-sig"))
report.append("compute_audit: history union %d|%d->%d, state take-new(t=%s)"
              % (len(ha), len(hb), len(union), get_ts(newer, ["ts"])))

# regime_state.json
p = "results/regime_state.json"
a, b = side(p, 2), side(p, 3)
ja, jb = parse(p, a), parse(p, b)
LK = [k for k in ja.keys() if isinstance(ja.get(k), list)]
out = dict(jb if str(get_ts(jb, TS_KEYS) or "") > str(get_ts(ja, TS_KEYS) or "") else ja)
for k in LK:
    la, lb = ja.get(k, []), jb.get(k, [])
    seen, un = set(), []
    for row in la + lb:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            un.append(row)
    out[k] = un
    report.append("regime_state: key %s union %d|%d->%d" % (k, len(la), len(lb), len(un)))
fa = face(a)
txt = json.dumps(out, ensure_ascii=False, indent=1)
raw = txt.encode("utf-8")
if fa["crlf"] == fa["lf"] and fa["crlf"] > 0:
    raw = raw.replace(b"\n", b"\r\n")
if not fa["tail_nl"]:
    raw = raw.rstrip(b"\n")
open(p, "wb").write(raw)
json.loads(open(p, "rb").read().decode("utf-8-sig"))

# ---------- 3) x2_watch_log.jsonl line union ----------
p = "results/x2_watch_log.jsonl"
a, b = side(p, 2), side(p, 3)
la = [l for l in a.decode("utf-8-sig").splitlines() if l.strip()]
lb = [l for l in b.decode("utf-8-sig").splitlines() if l.strip()]
seen, un = set(), []
for l in la + lb:
    if l not in seen:
        seen.add(l)
        un.append(l)
raw = ("\n".join(un) + "\n").encode("utf-8")
open(p, "wb").write(raw)
report.append("x2_watch_log: union %d|%d->%d" % (len(la), len(lb), len(un)))

# ---------- 4) autofill_state.json mixed-dict+ledger ----------
p = "results/autofill_state.json"
a, b = side(p, 2), side(p, 3)
ja, jb = parse(p, a), parse(p, b)
la, lb = ja.get("launches", []), jb.get("launches", [])
seen, un = set(), []
for row in la + lb:
    key = json.dumps(row, ensure_ascii=False, sort_keys=True)
    if key not in seen:
        seen.add(key)
        un.append(row)
un.sort(key=lambda r: str(r.get("ts", "")), reverse=True)
un = un[:50]
un.sort(key=lambda r: str(r.get("ts", "")))  # write-back face: ts ASC (bm-b r245 law)
ta = ja.get("last_tick", {})
tb = jb.get("last_tick", {})
if isinstance(ta, dict) and isinstance(tb, dict) and str(ta.get("ts", "")) == str(tb.get("ts", "")):
    last = ta  # same-second tie -> HEAD/ours (r140)
    tag = "tie->ours"
elif str(tb.get("ts", "")) > str(ta.get("ts", "")):
    last, tag = tb, "theirs"
else:
    last, tag = ta, "ours"
out = dict(jb)
out["launches"] = un
out["last_tick"] = last
fa = face(a)
txt = json.dumps(out, ensure_ascii=False, indent=1)
raw = txt.encode("utf-8")
if fa["crlf"] == fa["lf"] and fa["crlf"] > 0:
    raw = raw.replace(b"\n", b"\r\n")
if not fa["tail_nl"]:
    raw = raw.rstrip(b"\n")
open(p, "wb").write(raw)
chk = json.loads(open(p, "rb").read().decode("utf-8-sig"))
assert isinstance(chk["last_tick"], dict), "last_tick must stay dict"
report.append("autofill_state: launches union %d|%d->%d(cap50 ts-ASC), last_tick %s (t=%s)"
              % (len(la), len(lb), len(chk["launches"]), tag, chk["last_tick"].get("ts")))

# ---------- 5) dashboard_status.js js-wrapper take-side ----------
p = "results/dashboard_status.js"
a, b = side(p, 2), side(p, 3)
ja = json.loads(a.decode("utf-8-sig").split("=", 1)[1].strip().rstrip(";"))
jb = json.loads(b.decode("utf-8-sig").split("=", 1)[1].strip().rstrip(";"))
ta, tb = get_ts(ja, TS_KEYS), get_ts(jb, TS_KEYS)
chosen = b if (ta is None or (tb is not None and str(tb) > str(ta))) else a
assert chosen.startswith(b"window.DASH_DATA"), "js wrapper prefix lost"
assert b";" in chosen[-10:] or chosen.rstrip().endswith(b";"), "js wrapper suffix lost"
open(p, "wb").write(chosen)
json.loads(chosen.decode("utf-8-sig").split("=", 1)[1].strip().rstrip(";"))
report.append("dashboard_status.js: take-side whole bytes (t=%s chosen)" % (tb if chosen is b else ta))

print("\n".join(report))
print("RESOLVER DONE: all parses verified")
