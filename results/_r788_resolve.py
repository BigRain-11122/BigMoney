# r788 bm-b S0 rebase resolver v2 (2026-10-07)
# Conflict face: 10 UU files replaying 9ec7e688d (r787 unlanded absorb) onto origin/main 482cbd01a
# Empirically verified semantic diff paths (walk above, recorded 2026-10-07):
#   - 6x paper/*_paper.json : only /updated + /forward_guard/as_of (same run wall-clock, payload identical)
#   - 2x prospect_*/_summary.json : only /generated
#   - token_usage.json : generated newer on :3 (23:55:08 > 22:57:59) -> R216 take-new by generated ts
#   - x2_watch_log.jsonl : append-log line-level union zero loss (r188/r217)
# Recipes: take-new = write :3 bytes; union = dedup line-ordered merge.
import json
import subprocess
import sys

ALLOWED_DIFF_PATHS = {
    "/updated",
    "/forward_guard/as_of",
    "/generated",
}
WALLCLOCK_KEYS = {"updated", "generated", "as_of"}


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read :{n}:{path}")
    return r.stdout


def collect_diff_paths(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                out.add(path + "/" + k + " (only-one-side)")
            else:
                collect_diff_paths(a[k], b[k], path + "/" + k, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.add(path + " (len)")
        for i, (x, y) in enumerate(zip(a, b)):
            collect_diff_paths(x, y, f"{path}[{i}]", out)
    else:
        if a != b:
            out.add(path)


WALLCLOCK_ONLY = [
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
TAKE_NEW_BY_TS = "results/token_usage.json"
APPEND_LOG = "results/x2_watch_log.jsonl"

report = []
for p in WALLCLOCK_ONLY:
    a2, a3 = stage(2, p), stage(3, p)
    d2, d3 = json.loads(a2.decode("utf-8")), json.loads(a3.decode("utf-8"))
    diffs = set()
    collect_diff_paths(d2, d3, "", diffs)
    bad = diffs - ALLOWED_DIFF_PATHS
    if bad:
        report.append(f"RED unexpected-diff {p}: {sorted(bad)}")
        print("\n".join(report))
        sys.exit(2)
    open(p, "wb").write(a3)
    report.append(f"OK wallclock-verified take-new {p} (diffs={sorted(diffs)})")

# token_usage: R216 take-new by generated ts
p = TAKE_NEW_BY_TS
a2, a3 = stage(2, p), stage(3, p)
g2 = json.loads(a2.decode("utf-8")).get("generated", "")
g3 = json.loads(a3.decode("utf-8")).get("generated", "")
if g3 > g2:
    open(p, "wb").write(a3)
    report.append(f"OK snapshot take-new-by-ts {p} ({g3} > {g2})")
else:
    report.append(f"RED take-new ts not newer {p}: {g2} vs {g3}")
    print("\n".join(report))
    sys.exit(2)

p = APPEND_LOG
a2, a3 = stage(2, p), stage(3, p)
lines2 = a2.decode("utf-8").splitlines()
lines3 = a3.decode("utf-8").splitlines()
seen = set()
union = []
for ln in lines2 + lines3:
    if ln not in seen:
        seen.add(ln)
        union.append(ln)
assert len(union) == len(set(lines2) | set(lines3)), "union zero-loss assertion failed"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(union) + "\n")
report.append(
    f"OK append-union {p}: |:2|={len(lines2)} |:3|={len(lines3)} union={len(union)}"
)

print("\n".join(report))
# post-write parse validation (r185 law)
for q in WALLCLOCK_ONLY + [TAKE_NEW_BY_TS]:
    json.load(open(q, encoding="utf-8"))
print("PARSE-OK 9/9 snapshots")
print("RESOLVE-OK all files written")
