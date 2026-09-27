# -*- coding: utf-8 -*-
"""R313 bm-a push-collision final resolver (rebase replay 3788209f onto 7ce3e12e).
Recipes per bigmoney-conflict-resolve SKILL.md: R208/R209/R216 snapshots take-new-by-ts,
r188 rolling-ledger union, r140 same-ts tie->ours, memory-union line dedupe.
Fail-closed assertions throughout; byte-exact copies for take-new faces.
"""
import json, os, subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("blob fail %s st%d" % (path, stage))
    return r.stdout

def wb(path, data):
    with open(path, "wb") as f:
        f.write(data)

# ---- 1) take-new-theirs (all verified newer ts in pass 1/2) ----
TAKE_THEIRS = [
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in TAKE_THEIRS:
    b = blob(3, p)
    if p.endswith(".json"):
        json.loads(b.decode("utf-8"))  # parse gate before write
    wb(p, b)
    print("take-new-theirs %s (%dB)" % (p, len(b)))

# ---- 2) compute_audit.json rolling-ledger union ----
do = json.loads(blob(2, "results/compute_audit.json").decode("utf-8"))
dt = json.loads(blob(3, "results/compute_audit.json").decode("utf-8"))
bya = {h["ts"]: h for h in do["history"]}
byb = {h["ts"]: h for h in dt["history"]}
assert len(bya) == len(do["history"]) and len(byb) == len(dt["history"]), "ts dupes in history"
union = [bya[ts] if ts in bya else byb[ts] for ts in sorted(set(bya) | set(byb))]
assert len(union) == len(set(bya) | set(byb))
latest = do["latest"] if do["latest"]["ts"] >= dt["latest"]["ts"] else dt["latest"]
assert latest["ts"] == union[-1]["ts"], "latest must equal newest history row"
out = {"history": union, "latest": latest}
assert isinstance(out["history"], list) and isinstance(out["latest"], dict)
src = blob(2, "results/compute_audit.json").decode("utf-8")
nl = "\r\n" if "\r\n" in src[:2000] else "\n"
text = json.dumps(out, ensure_ascii=False, indent=1) + nl
with open("results/compute_audit.json", "w", encoding="utf-8", newline="") as f:
    f.write(text)
print("compute_audit union: %d+%d -> %d rows, latest ts=%s" % (
    len(bya), len(byb), len(union), latest["ts"]))

# ---- 3) memory-archive/202609.md section union ----
pa = "research/memory-archive/202609.md"
ta = blob(2, pa).decode("utf-8")
tb = blob(3, pa).decode("utf-8")
nl = "\r\n" if "\r\n" in ta[:5000] else "\n"
la, lb = ta.splitlines(), tb.splitlines()
i = 0
while i < min(len(la), len(lb)) and la[i] == lb[i]:
    i += 1
j = 0
while j < min(len(la), len(lb)) - i and la[len(la)-1-j] == lb[len(lb)-1-j]:
    j += 1
mid_a, mid_b = la[i:len(la)-j], lb[i:len(lb)-j]
strip_a = set(l.strip() for l in mid_a if l.strip())
dropped = [l for l in mid_b if l.strip() and l.strip() in strip_a]
extra_b = [l for l in mid_b if not (l.strip() and l.strip() in strip_a)]
assert len(dropped) == 4, "expected exactly 4 byte-identical dup entries, got %d" % len(dropped)
assert all(l.strip().startswith("- [") for l in dropped), "dropped lines must be entry lines"
union_lines = la[:i] + mid_a + [""] + extra_b
tail = nl if ta.endswith(nl) else ""
with open(pa, "w", encoding="utf-8", newline="") as f:
    f.write(nl.join(union_lines) + tail)
print("archive union: prefix=%d mid_a=%d mid_b=%d (dropped %d dupes, kept %d) -> total %d lines" % (
    i, len(mid_a), len(mid_b), len(dropped), len(extra_b), len(union_lines)))

# ---- 4) CODELY.md memory-union ----
ca = blob(2, "CODELY.md").decode("utf-8")
cb = blob(3, "CODELY.md").decode("utf-8")
nl = "\r\n" if "\r\n" in ca[:2000] else "\n"
la = ca.splitlines()
arch_idx = [n for n, l in enumerate(la) if "坑律正典全量归档" in l]
assert len(arch_idx) == 1
arch_ours = la[arch_idx[0]]
lb = cb.splitlines()
arch_idx_b = [n for n, l in enumerate(lb) if "坑律正典全量归档" in l]
assert len(arch_idx_b) == 1
arch_theirs = lb[arch_idx_b[0]]
marker = "归档五批节。"
pa_, pb_ = arch_ours.find(marker), arch_theirs.find(marker)
assert pa_ != -1 and pb_ != -1
shared = arch_ours[:pa_ + len(marker)]
assert arch_theirs[:pb_ + len(marker)] == shared, "arch entry shared head diverged"
union_arch = shared + arch_ours[pa_ + len(marker):] + arch_theirs[pb_ + len(marker):]
la[arch_idx[0]] = union_arch
strip_set = set(l.strip() for l in la)
new_entries = [l for l in lb if l.strip() and l.strip() not in strip_set
               and l.strip().startswith("- [") and "坑律正典全字归档" not in l
               and "坑律正典全量归档" not in l]
assert len(new_entries) == 1, "expected exactly 1 unique entry from theirs, got %d" % len(new_entries)
out_lines = la + new_entries
tail = nl if ca.endswith(nl) else ""
codely_text = nl.join(out_lines) + tail
size = len(codely_text.encode("utf-8"))
assert size < 10240, "CODELY union exceeds 10KB hard line: %d" % size
for probe in ["r310 bm-b", "r312 bm-b", "r316 bm-b", "r312 bm-a", "八批（r316 bm-b）", "八批外迁索引（R312 bm-a）"]:
    assert probe in codely_text, "union missing probe: " + probe
with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
    f.write(codely_text)
print("CODELY union: %d lines, %dB <10KB, +1 entry %s" % (
    len(out_lines), size, new_entries[0][:60]))

# ---- 5) verify all 16 + stage ----
RESOLVED = TAKE_THEIRS + ["results/compute_audit.json", pa, "CODELY.md"]
assert len(RESOLVED) == 16
for p in RESOLVED:
    if p.endswith(".json"):
        with open(p, "rb") as f:
            json.loads(f.read().decode("utf-8"))  # final parse gate on written bytes
r = subprocess.run(["git", "add"] + RESOLVED, capture_output=True)
print("git add rc=%d %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:200]))
print("RESOLVED OK")
