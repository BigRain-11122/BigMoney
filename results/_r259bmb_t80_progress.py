import json

P = "fleet/tasks/T-2026-09-26-80-P1.json"
raw = open(P, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and b"\r\n" not in raw  # byte face probe
t = json.loads(raw.decode("utf-8"))
assert "progress_r259" not in t
t["progress_r259"] = (
    "R259 bm-b slice-4 CAPACITY FACE DELIVERED (disclosure leg, zero re-judge): "
    "(1) prereg research/AGGR_CAPACITY_FACE_P1.md FROZEN pre-run (commit "
    "precedes run, R99) -- 20 frozen battery variants at representative-weight "
    "scale, engine-native D5 cost_v2 ADV20 1% participation cap (V2 face), "
    "zero judgment cells (ledger +0, canon re-anchor precedent). "
    "(2) runner scripts/aggr_capacity_probe.py: 267 dedup (tid,scale) units "
    "consumed verbatim from frozen battery weights_representative (census "
    "gates 291 pairs/267 units fail-closed), caliber snapshot manifest sha "
    "gate 29/29 (R253 double door), selftest 8/8 (F1 known-refusal matrix "
    "with tier-sum==num_entries identity, F2 zero-ADV drop, F3 determinism, "
    "F4 scale boundary, F5 battery census, F6 manifest gate, F7 core48 "
    "integration, F8 ADV yearly). "
    "(3) RUN: 267/267 units 37.6s 12 workers; labels 9 unconstrained / 11 "
    "constrained; all constrained = concentrated CE-sleeve weights (CONC-TOP2 "
    "24 caps 2.72% ... TOP2-MON 3 caps 0.03%); dropped_zero_adv=0 and "
    "missing_adv=0 all 20 (core48 shares calendar, no union gaps); structural "
    "location inference (labeled): only 513520 2020-2022 has cap1pct_median "
    "(37-64k CNY) below max CE demand 95k -- 2023+ no binding face. "
    "(4) products: results/aggr_capacity_face/p1_results.json (evidence_cutoff "
    "2026-09-24 top-level, prereg sha embedded, 267 unit detail, per-year ADV "
    "table) + gate_attrition entries row (cells_ledger_delta 0, "
    "ledger_total_after 186592 unchanged) + prereg s7/s8 backfilled; battery "
    "product byte-frozen untouched; six-face capacity coverage = probe "
    "product six_face_capacity block = authoritative successor face. "
    "NEXT: canon B_MAXDIV full-pool deep-member capacity = separate bm-a "
    "lane face (not started); constrained-label consumption = GM/month "
    "boundary tournament face (dual-track law)."
)
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("progress_r259 written; keys:", len(t))
