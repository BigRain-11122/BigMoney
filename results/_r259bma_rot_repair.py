# -*- coding: utf-8 -*-
"""R259 bm-a: repair check-ROT on T-73-CN-DIV-LOWVOL-ROT-P1 (R256 law
family, second instance): legacy depth-less git_log_file slid out of the -5
window as the hot ticket file kept receiving progress_r25x appends. Fact
first verified in deep history: e43bc613 (round 252) carries
'CN-DIV-LOWVOL-ROT-P1 harvested NEGATIVE 0/4 G1'v2'. Re-encode the SAME
frozen fact durably with depth=30 (git_log_file optional 3rd arg, R256
addition) + _reconciled note. No criteria invented, no rows deleted."""
import io
import json
import subprocess

P = "results/post_review_criteria.json"
raw = io.open(P, "rb").read()
had_bom = raw.startswith(b"\xef\xbb\xbf")
d = json.loads(raw.decode("utf-8-sig"))

# fact verification (deep history, before any edit)
log = subprocess.run(
    ["git", "log", "--oneline", "-40", "--all", "--",
     "fleet/tasks/T-2026-09-26-73-P1.json"],
    capture_output=True, check=True).stdout.decode("utf-8", "replace")
hits = [ln for ln in log.splitlines() if "CN-DIV-LOWVOL-ROT" in ln]
assert hits and "e43bc613" in hits[0], f"fact not verified: {hits}"

for it in d["items"]:
    if it["id"] == "T-73-CN-DIV-LOWVOL-ROT-P1":
        for c in it["checks"]:
            if c["kind"] == "git_log_file" and len(c["args"]) == 2:
                c["args"] = [c["args"][0], c["args"][1], 30]
                it["_reconciled"] = (
                    "R259 bm-a: git_log_file depth-less check rotted "
                    "(2nd R256-family instance): harvest commit e43bc613 "
                    "(round 252, CN-DIV-LOWVOL-ROT-P1 harvested NEGATIVE "
                    "0/4 G1'v2) slid out of legacy -5 window under "
                    "progress_r253..259 appends to the hot ticket file; "
                    "fact re-verified in deep history then re-encoded "
                    "SAME criterion with depth=30 (R256 durable-encoding "
                    "law; no criteria invented, no rows deleted)")
                print("re-encoded with depth=30")

out = json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
io.open(P, "wb").write(out)
print("written")
