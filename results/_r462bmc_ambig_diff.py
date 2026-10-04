"""r462 bm-c ambiguous-face diff probe: paper_export/latest.json +
daily_scorecard.json + dashboard_status.json -- both sides' bytes, find first
differing lines + ts fields (meta.generated_at / generated_from).
File-out per r446 law."""
import difflib
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = ROOT + r"\results\_r462bmc_ambig_diff.txt"

FACES = [
    "results/paper_export/latest.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
]


def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       cwd=ROOT, creationflags=0x08000000)
    return r.stdout or b""


lines_out = []
for path in FACES:
    lines_out.append("=" * 30 + " " + path)
    ours = git_show("HEAD", path).decode("utf-8", "replace")
    theirs = git_show("MERGE_HEAD", path).decode("utf-8", "replace")
    jo = json.loads(ours)
    jt = json.loads(theirs)
    # ts probe
    for tag, j in (("ours", jo), ("theirs", jt)):
        hits = {}
        meta = j.get("meta") if isinstance(j, dict) else None
        if isinstance(meta, dict) and "generated_at" in meta:
            hits["meta.generated_at"] = meta["generated_at"]
        for k in ("generated_from", "generated", "updated", "ts", "generated_at"):
            if isinstance(j, dict) and isinstance(j.get(k), str):
                hits[k] = j[k]
        lines_out.append(f"  {tag} ts-fields: {hits}")
    # first differing lines
    o_l = ours.splitlines()
    t_l = theirs.splitlines()
    diff = list(difflib.unified_diff(o_l, t_l, "ours", "theirs", lineterm="", n=0))
    shown = 0
    for d in diff[2:]:
        if d.startswith(("+", "-")) and not d.startswith(("+++", "---")):
            lines_out.append("    " + d[:220])
            shown += 1
            if shown >= 10:
                lines_out.append("    ...(more)")
                break
    if shown == 0:
        lines_out.append("  (no unified diff hunks?? byte-equal)")
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines_out))
print("AMBIG_DIFF_DONE", len(FACES))
