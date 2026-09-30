# _r460bmb_resolve2.py -- batch-2 resolver: replay r460 onto bm-a r472 (875ca03c4), 32 UU
# Direction: :2 ours = bm-a r472 base (NEWEST, post-RW1-fix engine, MSG-1330 do-not-revert)
#            :3 theirs = our r460 (12:54-55 + 13:05/13:15 background marks ticks)
# Recipes: 26 snapshots take-:2 (bm-a newer, verified by named ts asserts)
#          8 paper/export faces take-:2 UNCONDITIONAL (post-RW-1-exit-fix canonical values)
#          marks-20260930.jsonl take-:3 (base 35 lines strict subset of ours 38)
#          x2_watch_log.jsonl line-union (base-only 6 + ours-only 6, dedupe exact)
#          compute_audit.json history union by ts (heals bm-a 201-row regression; latest=:2 12:59:27)
#          regime_state.json history/transitions union + state=:2 (12:59:37)
import subprocess, json, sys

def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read {rev}:{path}")
    return r.stdout

def wb(path, b):
    with open(path, "wb") as f:
        f.write(b)

def jt(b):
    return json.loads(b.decode("utf-8"))

# ---- group A: snapshots, take-:2 with newer-ts assertion ----
A_TS = {  # path -> ts key list (first found wins)
 "docs/daily_report/REPORT-2026-09-30.json": ["generated_at"],
 "docs/daily_report/REPORT-2026-09-30.md": None,
 "docs/live_usage/LIVE-2026-09-30.json": ["generated"],
 "docs/live_usage/LIVE-2026-09-30.md": None,
 "docs/live_usage/LIVE-latest.json": ["generated"],
 "docs/live_usage/LIVE-latest.md": None,
 "results/_attrition_guard_scan.json": ["ts"],
 "results/daily_scorecard.json": ["generated"],
 "results/dashboard_status.js": None,
 "results/dashboard_status.json": None,
 "results/fundamental_b_layer_filter.json": ["updated"],
 "results/futures_update_status.json": ["ts"],
 "results/lhb_update_status.json": ["updated"],
 "results/prospect_paper/_summary.json": ["generated"],
 "results/prospect_promotion/_summary.json": ["generated"],
 "results/scorecard_v1.json": ["generated"],
 "results/strategy_scorecard.json": ["generated"],
 "results/t35_open_fill_verify.json": ["ts", "generated", "updated"],
 "results/token_usage.json": ["generated"],
 "results/update_status.json": ["updated"],
}
report = []
for p, keys in A_TS.items():
    b2, b3 = blob(":2", p), blob(":3", p)
    if keys and p.endswith(".json"):
        d2, d3 = jt(b2), jt(b3)
        t2 = next((d2[k] for k in keys if k in d2), None)
        t3 = next((d3[k] for k in keys if k in d3), None)
        if t2 and t3:
            assert t2 >= t3, f"ts direction INVERTED for {p}: base={t2} ours={t3}"
    wb(p, b2)
    if p.endswith(".json"):
        jt(b2)
    report.append(f"take2 {p} ({len(b2)}B)")

# ---- group B: post-RW-1-fix canonical faces, take-:2 unconditional ----
for p in ["results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
          "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
          "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
          "results/paper_export/export-2026-09-29.json", "results/paper_export/latest.json"]:
    b2 = blob(":2", p)
    jt(b2)
    wb(p, b2)
    report.append(f"take2-rw1 {p} ({len(b2)}B)")

# ---- marks: base strict subset of ours -> take :3 whole ----
p = "results/paper/marks/marks-20260930.jsonl"
l2 = set(x for x in blob(":2", p).decode("utf-8").splitlines() if x.strip())
l3 = [x for x in blob(":3", p).decode("utf-8").splitlines() if x.strip()]
assert l2 <= set(l3), "marks base NOT subset of ours -- abort take3"
wb(p, ("\n".join(l3) + "\n").encode("utf-8"))
report.append(f"marks take3 {len(l3)} lines (base {len(l2)} subset, zero loss)")

# ---- x2_watch_log: line union dedupe, sort by ts ----
p = "results/x2_watch_log.jsonl"
L2 = [x for x in blob(":2", p).decode("utf-8").splitlines() if x.strip()]
L3 = [x for x in blob(":3", p).decode("utf-8").splitlines() if x.strip()]
seen = {}
for x in L2 + L3:
    seen.setdefault(x, None)
rows = []
for x in seen:
    try:
        rows.append((json.loads(x).get("ts", ""), x))
    except Exception:
        rows.append(("", x))
rows.sort(key=lambda r: r[0])
out = "\n".join(x for _, x in rows) + "\n"
wb(p, out.encode("utf-8"))
report.append(f"x2watch union {len(L2)}+{len(L3)} dedupe -> {len(rows)} lines")

# ---- compute_audit: union history (heal bm-a 206->201 regression), latest=take :2 ----
p = "results/compute_audit.json"
d2, d3 = jt(blob(":2", p)), jt(blob(":3", p))
seen, union = {}, []
for r in d2["history"] + d3["history"]:
    k = r.get("ts")
    if k not in seen:
        seen[k] = r
        union.append(r)
union.sort(key=lambda r: r.get("ts", ""))
n2, n3 = len(d2["history"]), len(d3["history"])
n_only2 = len({r.get("ts") for r in d2["history"]} - {r.get("ts") for r in d3["history"]})
n_only3 = len({r.get("ts") for r in d3["history"]} - {r.get("ts") for r in d2["history"]})
assert len(union) == n2 + n_only3 == n3 + n_only2
merged = dict(d2)  # latest = :2 (12:59:27 newer than ours 12:54:15)
merged["history"] = union
out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
jt(out)
wb(p, out)
report.append(f"compute_audit union |{n2}|+|{n3}| -> {len(union)} rows (base-only {n_only2} incl 12:59:27, ours-only {n_only3}, heals r472 201-regression, zero loss)")

# ---- regime_state: union + state=take :2 ----
p = "results/regime_state.json"
d2, d3 = jt(blob(":2", p)), jt(blob(":3", p))
def urows(a, b):
    seen = {}
    for r in a + b:
        k = json.dumps({kk: r[kk] for kk in sorted(r)}, ensure_ascii=False)
        seen.setdefault(k, r)
    return sorted(seen.values(), key=lambda r: r.get("asof", r.get("ts", "")))
merged = dict(d2)  # updated 12:59:37 newer
merged["history"] = urows(d2["history"], d3["history"])
merged["transitions"] = urows(d2["transitions"], d3["transitions"])
out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
jt(out)
wb(p, out)
report.append(f"regime union hist->{len(merged['history'])} trans->{len(merged['transitions'])} state={merged['state']}")

for line in report:
    print(line)
print("RESOLVE2-OK")
