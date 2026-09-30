import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
f = json.load(open(r"results/_r470bmb_vsumd_resi_w14_probe_facts.json", encoding="utf-8"))
for k in ("resi60_open_slope_sign_split", "cntd5_open_slope_sign_split",
          "resi60_forward_5d", "cntd5_forward_5d", "cntn20_forward_5d",
          "resi60_grind_face_forward_20d", "cntd5_grind_face_forward_20d",
          "resi60_direction_split_forward_20d", "cntd5_direction_split_forward_20d",
          "distinct_space_increment_vsumd20",
          "resi60_nine_gate_512_cells_empty_count", "cntd5_nine_gate_512_cells_empty_count",
          "vsumd20_open_days", "vsumd20_open_rate_on_decidable",
          "core48_vsumd20_open_rate", "core48_cntd5_open_rate"):
    print(k, "=>", json.dumps(f[k], ensure_ascii=False)[:300])
est = f["extreme_day_states"]
for d in ("2025-04-07", "2026-01-19"):
    print(d, "=>", json.dumps(est[d], ensure_ascii=False)[:400])
