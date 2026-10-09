# -*- coding: utf-8 -*-
"""r796 bm-c merge UU resolver (6 faces, deep-ts r738 canon):
ts-duel take-newer-by-embedded-timestamp for 5 regen faces
(REPORT json/md, attrition scan, compute_audit, lhb_update_status);
append-only union for x2_watch_log.jsonl (r742 union canon).
Facts receipt -> results/_r796bmc_merge_resolver.json"""
import json, re, subprocess, sys, os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout, p.stderr

TS_RE = re.compile(r"(20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d)")

def newest_ts(text):
    tss = TS_RE.findall(text)
    return max(tss) if tss else ""

DUEL = [
    "docs/daily_report/REPORT-2026-10-09.json",
    "docs/daily_report/REPORT-2026-10-09.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/lhb_update_status.json",
]
UNION = ["results/x2_watch_log.jsonl"]

receipt = {"round": 796, "duel": {}, "union": {}}
for f in DUEL:
    rc, ours, _ = git(["show", "HEAD:%s" % f])
    rc, theirs, _ = git(["show", "origin/main:%s" % f])
    o_ts, t_ts = newest_ts(ours.decode("utf-8", "replace")), newest_ts(theirs.decode("utf-8", "replace"))
    side = "ours" if o_ts >= t_ts else "theirs"
    receipt["duel"][f] = {"ours_ts": o_ts, "theirs_ts": t_ts, "take": side}
    git(["checkout", "--%s" % side, "--", f])
    git(["add", "--", f])
    print("DUEL %s ours=%s theirs=%s -> %s" % (f, o_ts, t_ts, side))

for f in UNION:
    rc, ours, _ = git(["show", "HEAD:%s" % f])
    rc, theirs, _ = git(["show", "origin/main:%s" % f])
    o_lines = ours.decode("utf-8", "replace").splitlines()
    t_lines = theirs.decode("utf-8", "replace").splitlines()
    seen, merged = set(), []
    for ln in o_lines + t_lines:
        if ln not in seen:
            seen.add(ln)
            merged.append(ln)
    with open(os.path.join(REPO, f), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(merged) + ("\n" if merged else ""))
    git(["add", "--", f])
    receipt["union"][f] = {"ours_lines": len(o_lines), "theirs_lines": len(t_lines),
                           "union_lines": len(merged)}

# verify zero UU remain
rc, out, _ = git(["diff", "--name-only", "--diff-filter=U"])
remaining = out.decode("utf-8", "replace").split()
receipt["remaining_uu"] = remaining
with open(os.path.join(REPO, "results", "_r796bmc_merge_resolver.json"), "w",
          encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print(json.dumps(receipt, indent=1, ensure_ascii=False))
sys.exit(0 if not remaining else 3)
