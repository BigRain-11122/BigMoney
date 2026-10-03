"""r634 bm-b: inspect union-file keys and x2 line-tail diff between stages."""
import json
import subprocess

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"


def side(path, stage):
    p = subprocess.run(
        ["git", "show", f":{stage}:{path}"], cwd=ROOT, capture_output=True
    )
    return p.stdout if p.returncode == 0 else None


# JSON ledger keys
for path in ("results/compute_audit.json", "results/regime_state.json"):
    d2 = json.loads(side(path, 2))
    d3 = json.loads(side(path, 3))
    print("===", path)
    print(" S2 keys:", list(d2.keys()), "| list-type keys:", [k for k, v in d2.items() if isinstance(v, list)])
    print(" S3 keys:", list(d3.keys()), "| list-type keys:", [k for k, v in d3.items() if isinstance(v, list)])
    for k in d2:
        if isinstance(d2[k], list):
            print(
                f"  {k}: S2 len={len(d2[k])} S3 len={len(d3[k])}",
                "row_keys=" + str(list(d2[k][-1].keys())[:8]) if d2[k] and isinstance(d2[k][-1], dict) else "",
            )

# x2_watch_log line-level diff
l2 = side("results/x2_watch_log.jsonl", 2).decode("utf-8").splitlines()
l3 = side("results/x2_watch_log.jsonl", 3).decode("utf-8").splitlines()
s2, s3 = set(l2), set(l3)
print("=== x2_watch_log.jsonl S2 lines=", len(l2), "S3 lines=", len(l3))
print(" S2-only:", sorted(s2 - s3)[:4])
print(" S3-only:", sorted(s3 - s2)[:4])
print(" common:", len(s2 & s3))

# paper account file structure
p2 = side("results/paper/COMPOSITE-CE-01_paper.json", 2)
p3 = side("results/paper/COMPOSITE-CE-01_paper.json", 3)
d2 = json.loads(p2)
d3 = json.loads(p3)
print("=== paper/COMPOSITE-CE-01 keys:", list(d2.keys())[:12])
for k in d2:
    if isinstance(d2[k], list):
        print(f"  {k}: S2={len(d2[k])} S3={len(d3[k])}")

# paper_export ts presence
e2 = json.loads(side("results/paper_export/export-2026-09-30.json", 2))
e3 = json.loads(side("results/paper_export/export-2026-09-30.json", 3))
print("=== paper_export keys:", list(e2.keys())[:10])
ts2 = {k: v for k, v in e2.items() if "ts" in k.lower() or "time" in k.lower() or "date" in k.lower() or "generated" in k.lower()}
print(" ts-ish top-level:", ts2)
print(" bytes equal:", p2 == p3 if False else side("results/paper_export/export-2026-09-30.json", 2) == side("results/paper_export/export-2026-09-30.json", 3))
