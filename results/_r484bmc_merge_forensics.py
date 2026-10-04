"""r484 bm-c merge-window forensics: theirs-freshness probe (r440 two-way
classification) + token_usage.json structure + CODELY missing-list (r479)."""
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(REPO, "results", "_r484bmc_merge_forensics_out.txt")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
lines = []


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       cwd=REPO, creationflags=CNW)
    return r.stdout if r.returncode == 0 else None


# 1. theirs-freshness probe on S6 regenerable faces (ts fields)
probes = ["results/regime_state.json", "results/update_status.json",
          "results/compute_audit.json", "docs/daily_report/REPORT-2026-10-04.json"]
for p in probes:
    for tag, ref in (("ours", "HEAD"), ("theirs", "MERGE_HEAD")):
        raw = show(ref, p)
        if raw is None:
            lines.append(f"{p} {tag}: READ_FAIL")
            continue
        try:
            d = json.loads(raw)
            ts = d.get("ts") or d.get("generated") or d.get("updated") or "?"
            lines.append(f"{p} {tag}: ts={ts}")
        except Exception as e:
            lines.append(f"{p} {tag}: PARSE_FAIL {e}")

# 2. token_usage.json structure (ours vs theirs)
for tag, ref in (("ours", "HEAD"), ("theirs", "MERGE_HEAD")):
    raw = show(ref, "results/token_usage.json")
    if raw:
        d = json.loads(raw)
        keys = list(d.keys())
        lines.append(f"token_usage {tag}: top_keys={keys[:8]}")
        if "machines" in d and isinstance(d["machines"], dict):
            mk = {k: (v.get("ts") if isinstance(v, dict) else v)
                  for k, v in d["machines"].items()}
            lines.append(f"token_usage {tag}: machines={json.dumps(mk, ensure_ascii=False)[:400]}")

# 3. CODELY missing-list (r479): my lines not in theirs, with containment filter
ours_raw = show("HEAD", "CODELY.md")
theirs_raw = show("MERGE_HEAD", "CODELY.md")
if ours_raw and theirs_raw:
    ours_lines = ours_raw.decode("utf-8").splitlines()
    theirs_text = theirs_raw.decode("utf-8")
    missing, contained = [], []
    for ln in ours_lines:
        if ln.strip() and ln not in theirs_text:
            if ln in theirs_text:
                contained.append(ln)
            else:
                missing.append(ln)
    lines.append(f"CODELY: ours_lines={len(ours_lines)} missing_in_theirs={len(missing)} substring_contained={len(contained)}")
    for ln in missing:
        lines.append(f"CODELY_MISSING: {ln[:160]}")

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("PROBE_DONE")
