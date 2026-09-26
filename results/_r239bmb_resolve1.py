# -*- coding: utf-8 -*-
"""r239 push-collision rebase resolver STEP 1: T-74/T-75 claim race.
Adjudication: bm-a claim 09:58:58 (origin, canonical) precedes bm-b claim
10:05 (commit 2fab3637) per fleet/README s4 -> bm-b yields.
Recipe: take stage2 (bm-a side) whole + append yield_note line (text-level
insert before ticket_lineage anchor, EOL+indent mirrored from base blob).
Parse-verify before write (r185 law)."""
import json
import subprocess

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"

YIELD = {
    "74": ("claim race r239 adjudicated per fleet/README s4: bm-a claim 09:58:58 precedes bm-b 10:05 -> bm-a canonical owner; "
            "bm-b same-window delivery (s0 tree doc + s1 call page) dropped from canonical in rebase; bm-b unique contributions "
            "to follow-up as patches on canonical: fund-event distortion guard flag (512480/159995 r60=-62% share-event suspects), "
            "honest-window audit facts (core48 sector faces start 2020-01, popularity 3 snapshots)"),
    "75": ("claim race r239 adjudicated per fleet/README s4: bm-a claim 09:58:58 precedes bm-b 10:05 -> bm-a canonical owner; "
            "bm-b same-window delivery (daily_report.py + DECISIONS + first report + wiring) dropped from canonical in rebase; "
            "bm-b unique fixes to follow-up as patches on canonical if absent: _-prefixed schema-foreign file skip (r157), "
            "24h-window full-timestamp compare, heat-composite unfreeze ruling (D-04 in bm-b DECISIONS draft)"),
}

for tid in ("74", "75"):
    p = "fleet/tasks/T-2026-09-26-%s-P1.json" % tid
    out = subprocess.run(["git", "-C", ROOT, "show", ":2:%s" % p], capture_output=True)
    assert out.returncode == 0
    raw = out.stdout.decode("utf-8")
    json.loads(raw)  # parse-verify base side
    eol = "\r\n" if "\r\n" in raw else "\n"
    anchor = ' "ticket_lineage":'
    assert anchor in raw, "anchor missing " + p
    assert '"yield_note"' not in raw
    note = ' "yield_note": "%s",' % YIELD[tid] + eol
    new = raw.replace(anchor, note + anchor, 1)
    json.loads(new)  # parse-verify resolved side (r185 law)
    with open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print("resolved", p, "-> bm-a side + yield_note (eol=%r)" % eol)
