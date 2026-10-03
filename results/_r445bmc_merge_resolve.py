"""r445 bm-c merge UU resolver: 18 shared faces, r440 two-法 + cross-machine
union law (bm-a r660 precedent).

- 15 S6 regen faces + token_usage.json -> --theirs (origin newer: bm-a/bm-b
  05:07-05:23 derives vs bm-c 05:06; token_usage machines entries identical
  both sides, newer generated wins)
- results/_attrition_guard_scan.json -> --ours (bm-c 05:26 scan > bm-b 05:15;
  r644 latest-scan precedent)
- results/compute_audit.json -> programmatic union: history rows merged
  (dedup by ts+cores+py_cpu_pct, sort by ts, tail cap 201) + latest =
  newer-wins (theirs 05:12:43 > ours 05:06:08)
Post: marker scan on all 18 + git add. All git children CREATE_NO_WINDOW.
"""
import json
import subprocess

CREATE = 0x08000000
R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(*a):
    p = subprocess.run(["git", "-C", R] + list(a), capture_output=True,
                       creationflags=CREATE)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


THEIRS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
    "results/token_usage.json",
]
OURS = ["results/_attrition_guard_scan.json"]
UNION = ["results/compute_audit.json"]
ALL = THEIRS + OURS + UNION
assert len(ALL) == 18 and len(set(ALL)) == 18

for f in THEIRS:
    rc, _, err = git("checkout", "--theirs", "--", f)
    assert rc == 0, (f, err)
    rc, _, err = git("add", "--", f)
    assert rc == 0, (f, err)
print("THEIRS-RESOLVED", len(THEIRS))

for f in OURS:
    rc, _, err = git("checkout", "--ours", "--", f)
    assert rc == 0, (f, err)
    rc, _, err = git("add", "--", f)
    assert rc == 0, (f, err)
print("OURS-RESOLVED", len(OURS))

# ---- compute_audit union
f = UNION[0]
rc, o, _ = git("show", ":2:" + f)
assert rc == 0
ours = json.loads(o)
rc, o, _ = git("show", ":3:" + f)
assert rc == 0
theirs = json.loads(o)


def rowkey(r):
    return (r["ts"], r.get("cores"), r.get("py_cpu_pct"), r.get("cpu_total_pct"))


merged = {}
for r in ours["history"] + theirs["history"]:
    merged[rowkey(r)] = r
hist = sorted(merged.values(), key=lambda r: r["ts"])[-201:]
assert len(hist) >= 201, len(hist)
assert hist[-1]["ts"] == theirs["history"][-1]["ts"], "newest row must be theirs head"
ours_rows = sum(1 for r in hist if rowkey(r) in {rowkey(x) for x in ours["history"]})
theirs_rows = sum(1 for r in hist if rowkey(r) in {rowkey(x) for x in theirs["history"]})
latest = theirs["latest"]  # newer (05:12:43 > 05:06:08)
out = {"latest": latest, "history": hist}
with open(R + "\\" + f, "w", encoding="utf-8", newline="") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
re_d = json.load(open(R + "\\" + f, encoding="utf-8"))
assert len(re_d["history"]) == len(hist) and re_d["latest"]["ts"] == theirs["latest"]["ts"]
rc, _, err = git("add", "--", f)
assert rc == 0, err
print("UNION-RESOLVED compute_audit rows=%d (ours-side %d / theirs-side %d) latest=%s"
      % (len(hist), ours_rows, theirs_rows, latest["ts"]))

# ---- marker scan on all 18 (r644/r657 law: content check, not rc)
bad = []
for f in ALL:
    with open(R + "\\" + f, "rb") as fh:
        b = fh.read()
    if b"<<<<<<<" in b or b">>>>>>>" in b:
        bad.append(f)
assert not bad, ("marker residue", bad)
print("MARKER-SCAN-CLEAN 18/18")

# ---- final staged sanity
rc, o, _ = git("diff", "--name-only", "--diff-filter=U")
assert rc == 0
assert o.strip() == "", ("unresolved left", o)
print("UU-CLEARED-ALL-18")
print("RESOLVE-OK")
