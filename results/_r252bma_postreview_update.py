# -*- coding: utf-8 -*-
"""R252 bm-a: post_review registry updates (byte-mirror producer, r254 law).

1. Surgical text updates inside existing rows (path/value re-anchored to
   the R252 chain repair):
   - t33 row check path "ledger.total" -> "trials_ledger.total" (value
     58110 unchanged: t33 arithmetic was true-correct, only the key
     renamed);
   - CN-REV row check path -> "trials_ledger.total", value 185852 ->
     186138 (true-chain re-anchor).
2. Append two new claim rows (r246 law: claimed deliveries registered the
   same round):
   - T-73-CN-DIV-LOWVOL-ROT-P1 (full arc delivery);
   - R252-BMA-LEDGER-CHAIN-REPAIR (chain repair + verdict-impact).
"""
import io
import json

P = "results/post_review_criteria.json"
raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
crlf = b"\r\n" in raw
text = raw.decode("utf-8-sig")

subs = [
    ('"results/t33_attack_wave.json",\n      "ledger.total",',
     '"results/t33_attack_wave.json",\n      "trials_ledger.total",'),
    ('"results/cn_rev_tilt/p1_results.json",\n      "ledger.total",\n      "185852"',
     '"results/cn_rev_tilt/p1_results.json",\n      "trials_ledger.total",\n      "186138"'),
]
for old, new in subs:
    assert text.count(old) == 1, f"target not unique: {old[:60]!r}"
    text = text.replace(old, new)

d = json.loads(text)
ids = {it.get("id") for it in d["items"]}
assert "T-73-CN-DIV-LOWVOL-ROT-P1" not in ids
assert "R252-BMA-LEDGER-CHAIN-REPAIR" not in ids

d["items"].append({
    "id": "T-73-CN-DIV-LOWVOL-ROT-P1",
    "claim": "T-73 s3 slice-2 CN-DIV-LOWVOL-ROT full arc: prereg frozen R250 + R251 zero-run amendment -> pool entry 14:39:04 starved by fused T80 head until r252 autofill anti-starvation fix -> autofill launch 14:50:27 (bm-a pid 43612) -> landed 14:50:53 (18.4s, 65 units fresh) -> deterministic harvest _r252bma_rot_harvest.py PASS (10-face re-derive) flipped pool entry+shard done + harvest_note (r244 law) -> verdict NEGATIVE 0/4 cells G1'v2 (best W252_bare x2 0.7371 < skill line 0.9527, CI95 [0.0139,1.4851] low positive but line unmet) -> G2 ineligible -> model judged negative per prereg s4 (no paper account); prereg s7/s8 backfilled run numbers only; ledger 185798+54=185852 as recorded at landing, re-chained same round to true head 186192 by R252-BMA-LEDGER-CHAIN-REPAIR (judgment faces untouched)",
    "claim_source": "research/CN_DIV_LOWVOL_ROT_PREREG.md (frozen R250 + R251 zero-run amendment af368f8e; R99 law: post-run s7/s8 backfill only) + results/_r252bma_rot_harvest.py (deterministic harvest gate, exit 0) + results/cn_div_lowvol_rot/p1_results.json product + results/runnable_pool.json harvest_note + T-73 progress_r252",
    "status": "pending",
    "checks": [
        {"kind": "file_exists", "args": ["scripts/cn_div_lowvol_rot_p1.py"]},
        {"kind": "file_exists", "args": ["results/cn_div_lowvol_rot/p1_results.json"]},
        {"kind": "file_exists", "args": ["results/_r252bma_rot_harvest.py"]},
        {"kind": "json_field", "args": ["results/cn_div_lowvol_rot/p1_results.json", "evidence_cutoff", "2026-09-22"]},
        {"kind": "json_field", "args": ["results/cn_div_lowvol_rot/p1_results.json", "trials_ledger.total", "186192"]},
        {"kind": "json_field", "args": ["results/cn_div_lowvol_rot/p1_results.json", "n_trials", "54"]},
        {"kind": "json_field", "args": ["results/cn_div_lowvol_rot/p1_results.json", "g1_prime_v2.W252_bare.pass_v2", "False"]},
        {"kind": "json_field", "args": ["results/cn_div_lowvol_rot/p1_results.json", "g1_prime_v2.W63_gate.pass_v2", "False"]},
        {"kind": "file_contains", "args": ["results/runnable_pool.json", "harvested bm-a r252 2026-09-26"]},
        {"kind": "file_contains", "args": ["research/CN_DIV_LOWVOL_ROT_PREREG.md", "R252 收割轮回填"]},
        {"kind": "git_log_file", "args": ["fleet/tasks/T-2026-09-26-73-P1.json", "CN-DIV-LOWVOL-ROT"]},
    ],
})

d["items"].append({
    "id": "R252-BMA-LEDGER-CHAIN-REPAIR",
    "claim": "R252 bm-a trials-ledger chain repair: five family-runner products embedded append_ledger blocks under non-canonical key 'ledger' (scanner sees only trials_ledger) + two correct-key lineage gaps (p1e_zoo narrow-scanner 157, market_clock run1 concurrent skip of exit_overlay 30) + t33 legacy skip 40 by xstock_synth prev=58070 -> recorded head 185798 short by 394. Repair (results/_r252bma_ledger_chain_repair.py, exit 0): key rename on t33/div_lowvol/cny_window/cn_rev_tilt/cn_div_lowvol_rot products with true-chain re-anchor (head -> 186192; cn_rev 186138, cny 185082, div 183028, t33 58110) + six runner code sites fixed to write/resume trials_ledger (cn_div_lowvol_rot_p1/cn_rev_tilt_p1/div_lowvol_backtest/cny_window_p1/mf_ic_p1/t33_attack_wave). Judgment faces byte-untouched; 4dp skill lines unchanged (rot true line 0.95273 -> 0.9527, cn_rev +4e-5 -> 0.6147); verdicts unaffected (all margins >= 0.1). Intermediate correct-key files keep recorded derivations = superseded historical records; shortline_p1_factor.json left as accepted legacy (239 self-healed via p2_synth prev=1312, pre-cutoff-law, not C2-renamed)",
    "claim_source": "results/_r252bma_ledger_census.py (read-only census evidence) + results/_r252bma_ledger_chain_repair.py (deterministic repair gate, exit 0, head 186192 verified) + git diff (5 products field-level only) + scripts science_gates.ledger_head() re-derive",
    "status": "pending",
    "checks": [
        {"kind": "file_exists", "args": ["results/_r252bma_ledger_census.py"]},
        {"kind": "file_exists", "args": ["results/_r252bma_ledger_chain_repair.py"]},
        {"kind": "json_field", "args": ["results/t33_attack_wave.json", "trials_ledger.total", "58110"]},
        {"kind": "json_field", "args": ["results/div_lowvol_p1.json", "trials_ledger.total", "183028"]},
        {"kind": "json_field", "args": ["results/cny_window_p1.json", "trials_ledger.total", "185082"]},
        {"kind": "json_field", "args": ["results/cn_rev_tilt/p1_results.json", "trials_ledger.total", "186138"]},
        {"kind": "json_field", "args": ["results/cn_div_lowvol_rot/p1_results.json", "trials_ledger.total", "186192"]},
        {"kind": "json_field", "args": ["results/cn_div_lowvol_rot/p1_results.json", "skill_line.line", "0.9527"]},
        {"kind": "json_field", "args": ["results/cn_rev_tilt/p1_results.json", "trials_ledger.prev_total", "186084"]},
        {"kind": "file_contains", "args": ["scripts/cn_div_lowvol_rot_p1.py", "\"trials_ledger\": led,"]},
        {"kind": "file_contains", "args": ["scripts/t33_attack_wave.py", "\"trials_ledger\": led,"]},
        {"kind": "file_contains", "args": ["scripts/cny_window_p1.py", "\"trials_ledger\": append_ledger("]},
        {"kind": "file_contains", "args": ["scripts/mf_ic_p1.py", "out[\"trials_ledger\"] = led"]},
    ],
})

out = json.dumps(d, ensure_ascii=False, indent=1)
data = out.encode("utf-8")
if crlf:
    data = data.replace(b"\n", b"\r\n")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as fh:
    fh.write(data)
print("post_review registry: 2 rows appended, 2 rows re-anchored; bytes:", len(data))
