"""r320 bm-a P0 fix: T-90-V1-E2E-FINALIZE post_review criteria path reconciliation.

Root cause: bm-b r319 (commit 5e667f10) registered the frozen-value check with a
dotted path 'verdict.ring_table.base.ring2_routing.bull.mean_a1_minus_d_12m', but
the LANDED product results/decision_chain_e2e.json keeps ring_table at TOP level
(parallel to verdict), per bm-b's own r318 finalize structure + r319 deliverable-4
wiring claim ("consuming results/decision_chain_e2e.json
(verdict/ring_table/seat_vacancy/trials_ledger)") + monthly_briefing sec-6 consumer.
Registration-side path typo => reviewer derives a false NO
("json_field:key absent: 'ring_table'").

Fix policy (r223 bm-a reconciliation precedent + r270 bm-b criteria re-anchor
precedent): correct the check path to the product's true structure, verify the
frozen value resolves IDENTICALLY on both sides BEFORE editing, append a
_reconciled trace row, then re-derive via Tools/post_review.py (ledger verdict
comes from the reviewer, never hand-flipped). Science values zero-change.
Idempotent: if the bad path is already absent, no-op with status report.
"""
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "results" / "post_review_criteria.json"
PROD = ROOT / "results" / "decision_chain_e2e.json"

BAD = "verdict.ring_table.base.ring2_routing.bull.mean_a1_minus_d_12m"
GOOD = "ring_table.base.ring2_routing.bull.mean_a1_minus_d_12m"
EXPECT = "-0.0528"
ITEM_ID = "T-90-V1-E2E-FINALIZE"

raw = REG.read_bytes()
has_bom = raw[:3] == b"\xef\xbb\xbf"
nl = b"\r\n" if b"\r\n" in raw else b"\n"
reg = json.loads(raw.decode("utf-8-sig"))

item = None
for it in reg["items"]:
    if it.get("id") == ITEM_ID:
        item = it
        break
assert item is not None, f"criteria item {ITEM_ID} not found"

bad_checks = [c for c in item["checks"]
              if c.get("kind") == "json_field" and len(c.get("args", [])) > 1 and c["args"][1] == BAD]

if not bad_checks:
    print(f"NO-OP: check path {BAD!r} already absent from {ITEM_ID}")
    raise SystemExit(0)

# --- fact self-verification BEFORE any edit
prod = json.loads(PROD.read_text(encoding="utf-8-sig"))
node = prod
for seg in GOOD.split("."):
    node = node[seg]
prod_val = str(node)
assert prod_val == EXPECT, f"product value {prod_val!r} != frozen expect {EXPECT!r}"

node_bad = prod
bad_resolves = True
try:
    for seg in BAD.split("."):
        node_bad = node_bad[seg]
except (KeyError, TypeError):
    bad_resolves = False
assert not bad_resolves, "BAD path unexpectedly resolves in product -- abort, not a path typo"

# --- edit: path correction only (value untouched)
for c in bad_checks:
    c["args"][1] = GOOD

ts = time.strftime("%Y-%m-%d %H:%M")
trace = (
    f" | {ts} r320 bm-a: {ITEM_ID} check-path reconciliation -- json_field path "
    f"'{BAD}' -> '{GOOD}' (registration-side path typo: product keeps ring_table at "
    f"top level parallel to verdict per bm-b r318 finalize structure + r319 D4 wiring "
    f"claim + monthly_briefing sec-6 consumer; frozen value {EXPECT} verified equal "
    f"both sides pre-edit; science values zero-change; ledger verdict re-derived by "
    f"reviewer, not hand-flipped)"
)
reg["_reconciled"] = (reg.get("_reconciled") or "") + trace

text = json.dumps(reg, ensure_ascii=False, indent=1)
if has_bom:
    text = "\ufeff" + text
out = text.replace("\r\n", "\n").replace("\n", nl.decode())
REG.write_bytes(out.encode("utf-8"))

# --- post-edit verification: reload, resolve corrected check against product
reg2 = json.loads(REG.read_text(encoding="utf-8-sig"))
item2 = next(it for it in reg2["items"] if it.get("id") == ITEM_ID)
fixed = [c for c in item2["checks"] if c.get("kind") == "json_field" and c["args"][1] == GOOD]
assert len(fixed) == len(bad_checks), "fixed check count mismatch after write-back"
assert not any(len(c.get("args", [])) > 1 and c["args"][1] == BAD
               for c in item2["checks"]), "bad path still present"
print(f"FIXED: {len(bad_checks)} check path corrected {BAD!r} -> {GOOD!r}; "
      f"value {prod_val!r} verified pre/post; _reconciled trace appended; bom={has_bom} nl={'CRLF' if nl==b'\r\n' else 'LF'}")
