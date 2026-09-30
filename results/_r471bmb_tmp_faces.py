import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
f = json.load(open(r"results/_r470bmb_vsumd_resi_w14_probe_facts.json", encoding="utf-8"))
s = json.load(open(r"results/_r471bmb_cntn20_w14_supplement_facts.json", encoding="utf-8"))

def pick(d, *keys):
    for k in keys:
        v = d[k]
        print(k, "->", json.dumps(v, ensure_ascii=False)[:260])

print("== resi60 adjacency ==")
pick(f["adjacency_resi60"], "resi60_vs_rsqr20", "resi60_vs_rsqr20_closed", "resi60_vs_rsv60",
     "resi60_vs_rsv60_highside_notlow", "resi60_vs_mom", "resi60_vs_sumn20", "resi60_vs_upstreak",
     "resi60_vs_bull", "resi60_vs_bear", "resi60_vs_calm", "resi60_vs_wild")
print("== cntd5 adjacency ==")
pick(f["adjacency_cntd5"], "cntd5_vs_sumn20", "cntd5_vs_upstreak", "cntd5_vs_rsqr20",
     "cntd5_vs_mom", "cntd5_vs_resi60", "cntd5_vs_yang", "cntd5_vs_surge")
print("== cntn20 adjacency (supp) ==")
pick(s["adjacency_cntn20"], "cntn20_vs_sumn20", "cntn20_vs_upstreak", "cntn20_vs_cntd5",
     "cntn20_vs_resi60", "cntn20_vs_mad60", "cntn20_vs_rsv60", "cntn20_vs_mom")
print("== open-rate inside gates ==")
print("resi60:", json.dumps(f["resi60_open_rate_inside_pct"], ensure_ascii=False))
print("cntd5:", json.dumps(f["cntd5_open_rate_inside_pct"], ensure_ascii=False))
print("cntn20(r470):", json.dumps(f["cntn20_open_rate_inside_pct"], ensure_ascii=False))
print("== vsumd20 demote face ==")
pick(f["distinct_space_increment_vsumd20"])
print("== extreme days ==")
print(json.dumps(f["extreme_day_states"], ensure_ascii=False)[:1500])
print("== resi60 slope ==")
pick(f["resi60_open_slope_sign_split"])
print("== resi60 fwd5d ==")
pick(f["resi60_forward_5d"], f["cntd5_forward_5d"], f["cntn20_forward_5d"])
print("== grind resi60/cntd5 ==")
pick(f["resi60_grind_face_forward_20d"], f["cntd5_grind_face_forward_20d"])
print("== dirsplit resi60/cntd5 ==")
pick(f["resi60_direction_split_forward_20d"], f["cntd5_direction_split_forward_20d"])
