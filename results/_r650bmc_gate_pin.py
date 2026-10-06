# -*- coding: utf-8 -*-
"""r650 bm-c: delivery verify (fetch + rev-parse origin/main == HEAD, N=0
undelivered) + codely gate-pin receipt (post-commit blob face, r646 law:
git cat-file -s HEAD:CODELY.md is the sole authority for main-file size)."""
import json, os, subprocess, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True, text=True, encoding="utf-8")

git("fetch", "origin")
head = git("rev-parse", "HEAD").stdout.strip()
origin = git("rev-parse", "origin/main").stdout.strip()
behind = git("rev-list", "--count", "HEAD..origin/main").stdout.strip()
ahead = git("rev-list", "--count", "origin/main..HEAD").stdout.strip()
blob_size = git("cat-file", "-s", "HEAD:CODELY.md").stdout.strip()
blob_sha = git("rev-parse", "HEAD:CODELY.md").stdout.strip()

out = {
    "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "round": "r650 bm-c",
    "head": head,
    "origin_main": origin,
    "delivered": head == origin,
    "undelivered_count": int(behind),
    "ahead_count": int(ahead),
    "codely_blob_size_bytes": int(blob_size),
    "codely_blob_sha": blob_sha,
    "gate": 30720,
    "gate_ok": int(blob_size) <= 30720,
    "headroom_bytes": 30720 - int(blob_size),
    "note": ("post-commit blob face per r646 law (receipt-vs-commit mismatch pit); "
             "tail commit 0335e4a7d after rebase closeout vs bm-a r806 wave; "
             "15 UU faces resolved per ts-law + unions; delivery verified same window"),
}
assert out["delivered"], "NOT DELIVERED: head != origin/main"
assert out["undelivered_count"] == 0
path = os.path.join(ROOT, "results", "_r650bmc_codely_gate_pin.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False))
