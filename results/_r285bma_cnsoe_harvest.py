"""R285 bm-a: CN_SOE_ETF_P1 same-round harvest -- pool flip done (r244 law)
+ post_review criteria row T-87-CN-SOE-P1 registration (stable-product
anchors only, D-20260927-04 law). Byte faces probed before every write-back
(r255 five-face law): pool JSON and criteria JSON probed, LF-normalized
json.dump face, zero trailing-newline inventions.
"""
import io
import json

# ---------- probe faces ----------
def faces(path):
    raw = open(path, "rb").read()
    import re
    m = re.search(rb"\n(\s+)\"", raw)
    return {
        "bom": raw[:3] == b"\xef\xbb\xbf",
        "crlf": raw.count(b"\r\n"),
        "lf": raw.count(b"\n"),
        "tail_nl": raw.endswith(b"\n"),
        "indent": (m.group(1) if m else b"").decode(),
        "ensure_ascii_escapes": bool(re.search(rb"\\u", raw)),
    }

POOL = "results/runnable_pool.json"
CRIT = "results/post_review_criteria.json"
fp_, fc_ = faces(POOL), faces(CRIT)
print("pool faces:", fp_)
print("criteria faces:", fc_)

# ---------- pool flip (harvest face, r244 law) ----------
pool = json.load(io.open(POOL, encoding="utf-8-sig"))
entry = [e for e in pool["entries"] if e.get("id") == "CN_SOE_ETF_P1"]
assert len(entry) == 1, "pool entry not found"
e = entry[0]
shard = e["shards"][0]
assert shard["owner"] == "bm-a" and shard["status"] in ("ready", "running"), \
    "unexpected shard state: %s" % shard
shard["status"] = "done"
e["status"] = "done"
e["harvest_note"] = (
    "R285 bm-a same-round harvest: finalize ok 02:06:19 (elapsed 371.7s, "
    "workers 4, units 2005) -> judged-negative 0/5 G1'v2 (line 0.4792 "
    "core48-passive-dominated; SOE_REPAIR line_ok+CI pass but F6 entries "
    "13<30 structural block) + G2 0/5 (DSR 0.0, family PBO 0.3714 "
    "observe) -> slot closed per O-20260926-0926 queue order, no paper "
    "account; prereg s7/s8 backfilled single-finalization same round; "
    "post_review row T-87-CN-SOE-P1 registered same round; cross-family "
    "leg vs CN_TREND_ETF_P1 stays open (in flight, bm-b lane)")
with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
print("pool: CN_SOE_ETF_P1 flipped done with harvest_note")

# ---------- criteria row registration ----------
c = json.load(io.open(CRIT, encoding="utf-8"))
new_row = {
    "id": "T-87-CN-SOE-P1",
    "claim": "T-87 s2 queue #2 CN_SOE_ETF_P1 (zhongtegu SOE sleeve, "
             "SCHOOL_SUPPLY_S1 sec.2 zero-invention order) full arc: "
             "prereg frozen commit ba54b43f BEFORE runner build BEFORE "
             "any run (R99 law; sha256_lf_normalized 57390c85 pinned in "
             "product meta) + runner selftest 34/34 (r286 family legs: "
             "np-native coercion + _compute_cells glue + div-cross "
             "dated reconstruction) + real-data gate probe (T=2445 N=8, "
             "probe 0.2s, SOE_HOLD x2 0.3915, SOE_REPAIR 13 entries 3 "
             "episodes in prereg band) -> pool entry 01:50:09 -> tick "
             "claim 02:00:07 owner=bm-a (latency 9.9min) -> finalize ok "
             "02:06:19 (371.7s, 2005 units, ledger 189859+2005=191864, "
             "attrition row 51) -> verdict NEGATIVE per frozen s4: "
             "G1'v2 0/5 (line 0.4792 core48-passive-dominated; "
             "SOE_REPAIR 0.7077 line_ok TRUE + bootstrap CI lower "
             "+0.1257>0 but F6 entries 13<30 structural block = "
             "sample-insufficiency-type negative; SOE_HOLD entries 8<30 "
             "same F6 face; MA200/LowVOL3 below-line type) + G2 0/5 "
             "(DSR 0.0, family PBO 0.3714 observe band) + D6 0.2755 "
             "max vs registered CE members no reject + cross-family "
             "disclosure leg vs CN-DIV-LOWVOL-ROT W63_bare corr 0.7133 "
             "vs SOE_HOLD (>0.7 style-overlap honesty face, both "
             "families negative) -> CN_SOE-ETF judged negative, slot "
             "closed, no paper account; SOE_REPAIR forward pointer: "
             "2023+ pure-zhongtegu cohort or cumulative events >=30 "
             "warrants a NEW prereg (reopen-law positive face); "
             "cross-family leg vs CN_TREND_ETF_P1 open until that "
             "batch lands",
    "claim_source": "research/CN_SOE_ETF_PREREG.md (frozen ba54b43f, "
                    "s7/s8 backfilled R285 single-finalization) + "
                    "results/cn_soe_ETF/p1_results.json product + "
                    "results/gate_attrition.json row 51 + logs/"
                    "autofill_CN_SOE_ETF_P1.log finalize trail",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["scripts/cn_soe_etf_p1.py"]},
        {"kind": "file_exists",
         "args": ["results/cn_soe_ETF/p1_results.json"]},
        {"kind": "file_exists",
         "args": ["research/CN_SOE_ETF_PREREG.md"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "evidence_cutoff", "2026-09-22"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "trials_ledger.total", "191864"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "n_trials", "2005"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "gates.SOE_REPAIR.g1_prime_v2.line_ok", "True"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "gates.SOE_REPAIR.g1_prime_v2.pass_v2", "False"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "gates.SOE_REPAIR.g1_prime_v2.trade_gate.n_entries",
                  "13"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "gates.SOE_HOLD.g1_prime_v2.pass_v2", "False"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "family_pbo.pbo", "0.3714"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "nulls.coverage.n_values", "2000"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "virtual_starts.n_starts", "2119"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "panel_face.universe_n", "8"]},
        {"kind": "json_field",
         "args": ["results/cn_soe_ETF/p1_results.json",
                  "cross_family_advisory.cn_div_lowvol_rot.cells."
                  "W63_bare.corr_vs_our_cells.SOE_HOLD.corr",
                  "0.7133"]},
        {"kind": "file_contains",
         "args": ["research/CN_SOE_ETF_PREREG.md",
                  "CN_SOE-ETF 判负收线"]},
        {"kind": "file_contains",
         "args": ["results/gate_attrition.json",
                  "CN_SOE_ETF_P1"]},
    ],
}
assert not any(x["id"] == new_row["id"] for x in c["items"])
c["items"].append(new_row)
with io.open(CRIT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(c, fh, ensure_ascii=False, indent=1)
print("registered T-87-CN-SOE-P1 claim row (items=%d)" % len(c["items"]))
