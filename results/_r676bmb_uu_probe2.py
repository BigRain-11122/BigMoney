import subprocess, json, io, os, difflib

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
faces = [
 "docs/live_usage/LIVE-2026-10-04.json",
 "docs/live_usage/LIVE-2026-10-04.md",
 "results/compute_audit.json",
 "results/dashboard_status.json",
 "results/scorecard_v1.json",
 "results/strategy_scorecard.json",
 "results/regime_state.json",
 "results/update_status.json",
 "results/token_usage.json",
]

def blob(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", rev + ":" + path],
                       capture_output=True, timeout=30)
    return r.stdout

lines = []
for f in faces:
    ours = blob("HEAD", f)
    theirs = blob("MERGE_HEAD", f)
    ol = ours.decode("utf-8", "replace").splitlines()
    tl = theirs.decode("utf-8", "replace").splitlines()
    diff = list(difflib.unified_diff(tl, ol, "theirs", "ours", lineterm="", n=0))
    ndiff = sum(1 for d in diff if d[:1] in "+-" and d[:3] not in ("---", "+++"))
    lines.append("=== %s diff_lines=%d" % (f, ndiff))
    # show up to 14 diff lines, each truncated to 160 chars
    shown = 0
    for d in diff:
        if d[:3] in ("---", "+++") or d[:1] in ("@",):
            continue
        if d[:1] in "+-":
            lines.append("  " + d[:160])
            shown += 1
            if shown >= 14:
                lines.append("  ...truncated")
                break

out = os.path.join(ROOT, "results", "_r676bmb_uu_probe2.txt")
with io.open(out, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("OK " + out)
