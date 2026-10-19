# r1080 bm-a UU resolver (rebase replay onto f8f1502e57; r1078 resolver family verbatim + 4-face extension)
# Rebase semantics: ours=HEAD(origin tip f8f1502e57: bm-c r1119/r1120/addendum + bm-b r1025), theirs=MINE (24c43926fa, my r1080 commit).
# Faces (r1078 law mapping):
#  - REPORT/LIVE twins + latest twins : newer generated side, md+latest same side (r1071 generator-face law)
#  - compute_audit / regime_state     : history union + latest newer-wins (r965 recipe)
#  - update_status / attrition / b_layer_filter / d19_check / d19_watermark / token_usage : newer ts/updated (transient receipt faces)
#  - _r686bmb_orders_fresh.md         : newer embedded-ts side (shared D-19 cache snapshot; tie->HEAD, bm-c watermark 11c172b3 > mine 690cd830)
#  - dashboard_status json+js / strategy_scorecard / scorecard_v1 : newer generated (r378 host=bm-a operative face)
#  - marks-20261019.jsonl             : append-only line union, exact-dedupe, ts-sort, all-valid-JSON (r419 law)
#  - research/HANDOVER.md            : row-union (HEAD rows + MINE-only rows appended; exact-dedupe)
import json
import re
import subprocess
import sys

MINE = "24c43926fa"  # my r1080 commit being replayed

def blob(rev, path):
    r = subprocess.run(["git", "show", rev + ":" + path], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return None
    return r.stdout

def jload(rev, path):
    try:
        return json.loads(blob(rev, path))
    except Exception:
        return None

def jwrite(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    json.load(open(path, encoding="utf-8"))
    print("resolved", path)

def bwrite(path, rev):
    r = subprocess.run(["git", "show", rev + ":" + path], capture_output=True)
    with open(path, "wb") as f:
        f.write(r.stdout)
    txt = open(path, encoding="utf-8").read()
    assert ">>>>>>>" not in txt and "<<<<<<<" not in txt, "marker in " + path
    print("resolved", path, "(side", rev[:8] + ")")

def ts_of(d, *keys):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return str(d[k])
    return ""

bad = 0

# 1) REPORT twins: newer generated_at
o = jload("HEAD", "docs/daily_report/REPORT-2026-10-19.json")
m = jload(MINE, "docs/daily_report/REPORT-2026-10-19.json")
mine_wins = ts_of(m, "generated_at", "generated", "ts") >= ts_of(o, "generated_at", "generated", "ts")
side = m if mine_wins else o
print("report twins: mine_wins=%s gen=%s" % (mine_wins, ts_of(side, "generated_at", "generated", "ts")))
jwrite("docs/daily_report/REPORT-2026-10-19.json", side)
bwrite("docs/daily_report/REPORT-2026-10-19.md", MINE if mine_wins else "HEAD")

# 2) LIVE dated + latest twins: same-side law
o = jload("HEAD", "docs/live_usage/LIVE-2026-10-19.json")
m = jload(MINE, "docs/live_usage/LIVE-2026-10-19.json")
lmw = ts_of(m, "generated_at", "generated", "updated", "ts") >= ts_of(o, "generated_at", "generated", "updated", "ts")
print("live twins: mine_wins=%s" % lmw)
lv_side = MINE if lmw else "HEAD"
for p in ("docs/live_usage/LIVE-2026-10-19.json", "docs/live_usage/LIVE-2026-10-19.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"):
    bwrite(p, lv_side)

# 3) compute_audit: history union + latest newer-wins (r965 recipe)
o = jload("HEAD", "results/compute_audit.json")
m = jload(MINE, "results/compute_audit.json")
hist = {json.dumps(h, sort_keys=True, ensure_ascii=False): h for h in (o.get("history") or [])}
for h in (m.get("history") or []):
    hist.setdefault(json.dumps(h, sort_keys=True, ensure_ascii=False), h)
merged_hist = sorted(hist.values(), key=lambda h: str(h.get("ts", h.get("time", ""))))
latest = m.get("latest") if str((m.get("latest") or {}).get("ts", "")) >= str((o.get("latest") or {}).get("ts", "")) else o.get("latest")
jwrite("results/compute_audit.json", {"latest": latest, "history": merged_hist})

# 4) regime_state: latest newer + history union
o = jload("HEAD", "results/regime_state.json")
m = jload(MINE, "results/regime_state.json")
newer = m if str(m.get("updated", "")) >= str(o.get("updated", "")) else o
oh = {json.dumps(h, sort_keys=True, ensure_ascii=False): h for h in (o.get("history") or [])}
for h in (m.get("history") or []):
    oh.setdefault(json.dumps(h, sort_keys=True, ensure_ascii=False), h)
newer = dict(newer)
newer["history"] = sorted(oh.values(), key=lambda h: str(h.get("asof", h.get("ts", ""))))
jwrite("results/regime_state.json", newer)

# 5) transient receipt faces: newer ts/updated (token_usage added this round)
for path, keys in (
    ("results/update_status.json", ("updated", "ts")),
    ("results/_attrition_guard_scan.json", ("ts",)),
    ("results/fundamental_b_layer_filter.json", ("updated", "ts")),
    ("results/_r686bmb_d19_check.json", ("ts",)),
    ("results/d19_watermark.json", ("ts",)),
    ("results/token_usage.json", ("updated", "ts", "generated")),
):
    o = jload("HEAD", path)
    m = jload(MINE, path)
    win = m if ts_of(m, *keys) >= ts_of(o, *keys) else o
    print(path, "winner=%s ts=%s/%s" % ("MINE" if win is m else "HEAD", ts_of(m, *keys), ts_of(o, *keys)))
    jwrite(path, win)

# 6) _r686bmb_orders_fresh.md: newer embedded-ISO-ts side, tie->HEAD (shared D-19 cache snapshot)
ISO = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?")
def md_ts(txt):
    found = ISO.findall(txt)
    return max(found) if found else ""
o_txt = blob("HEAD", "results/_r686bmb_orders_fresh.md") or ""
m_txt = blob(MINE, "results/_r686bmb_orders_fresh.md") or ""
ow_side = "HEAD" if md_ts(o_txt) >= md_ts(m_txt) else MINE
print("orders_fresh.md winner=%s ts=%s/%s" % (ow_side[:8], md_ts(o_txt), md_ts(m_txt)))
bwrite("results/_r686bmb_orders_fresh.md", ow_side)

# 7) dashboard twins json+js: newer meta/generated; SAME side for both (r378 host=bm-a operative)
o = jload("HEAD", "results/dashboard_status.json")
m = jload(MINE, "results/dashboard_status.json")
dmw = ts_of((m or {}).get("meta", {}), "generated", "generated_at", "ts") >= ts_of((o or {}).get("meta", {}), "generated", "generated_at", "ts")
print("dashboard: mine_wins=%s" % dmw)
dash_side = MINE if dmw else "HEAD"
bwrite("results/dashboard_status.json", dash_side)
bwrite("results/dashboard_status.js", dash_side)

# 8) scorecard faces: newer generated (r378 host=bm-a operative)
for path in ("results/strategy_scorecard.json", "results/scorecard_v1.json"):
    o = jload("HEAD", path)
    m = jload(MINE, path)
    win = m if ts_of(m, "generated", "generated_at", "ts", "updated") >= ts_of(o, "generated", "generated_at", "ts", "updated") else o
    print(path, "winner=%s" % ("MINE" if win is m else "HEAD"))
    jwrite(path, win)

# 9) marks-20261019.jsonl: append-only line union (r419)
MP = "results/paper/marks/marks-20261019.jsonl"
o_txt = blob("HEAD", MP) or ""
m_txt = blob(MINE, MP) or ""
o_lines = [l for l in o_txt.splitlines() if l.strip()]
m_lines = [l for l in m_txt.splitlines() if l.strip()]
seen, rows = set(), []
for l in o_lines + m_lines:
    if l in seen:
        continue
    seen.add(l)
    rows.append(l)

def row_ts(l):
    try:
        j = json.loads(l)
        return str(j.get("ts", j.get("time", "")))
    except Exception:
        return "9999"
rows.sort(key=row_ts)
ok = 0
for l in rows:
    json.loads(l)
    ok += 1
with open(MP, "w", encoding="utf-8", newline="\n") as f:
    for l in rows:
        f.write(l + "\n")
print("marks union: ours=%d theirs=%d merged=%d all_valid=%d" % (len(o_lines), len(m_lines), len(rows), ok))

# 10) research/HANDOVER.md: row-union (HEAD rows first, MINE-only rows appended; exact-dedupe)
HP = "research/HANDOVER.md"
o_txt = blob("HEAD", HP) or ""
m_txt = blob(MINE, HP) or ""
o_lines = o_txt.splitlines()
m_lines = m_txt.splitlines()
o_set = set(o_lines)
seen_h, out = set(), []
for l in o_lines:
    if l in seen_h:
        continue
    seen_h.add(l)
    out.append(l)
added = 0
for l in m_lines:
    if l in o_set or (not l.strip()):
        continue
    if l in seen_h:
        continue
    seen_h.add(l)
    out.append(l)
    added += 1
with open(HP, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
chk = open(HP, encoding="utf-8").read()
assert "<<<<<<<" not in chk and ">>>>>>>" not in chk, "marker in HANDOVER"
print("HANDOVER union: HEAD=%d MINE=%d out=%d mine_only_added=%d" % (len(o_lines), len(m_lines), len(out), added))

# stage all
files = [
    "docs/daily_report/REPORT-2026-10-19.json", "docs/daily_report/REPORT-2026-10-19.md",
    "docs/live_usage/LIVE-2026-10-19.json", "docs/live_usage/LIVE-2026-10-19.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json", "results/regime_state.json", "results/update_status.json",
    "results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
    "results/_r686bmb_d19_check.json", "results/d19_watermark.json", "results/token_usage.json",
    "results/_r686bmb_orders_fresh.md",
    "results/dashboard_status.json", "results/dashboard_status.js",
    "results/strategy_scorecard.json", "results/scorecard_v1.json",
    "results/paper/marks/marks-20261019.jsonl",
    "research/HANDOVER.md",
]
for p in files:
    r = subprocess.run(["git", "add", "--", p], capture_output=True, text=True)
    if r.returncode != 0:
        print("ADD-FAIL", p, r.stderr[:200])
        bad += 1
print("STAGED-OK" if bad == 0 else "BAD=%d" % bad)
sys.exit(1 if bad else 0)
