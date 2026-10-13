# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
t = open(r"results\_w233bmc_prereg_derive_tpl.py", encoding="utf-8").read()
markers = [
    'SUB32 = extract_lit',
    'OLD32 = lvl(OLD31',
    'blob("a3a7aa632", "research/PERPETUAL_N1_W232_PREREG.md")',
    '"A": "527404_529403"',
    '"B": "529404_529603"',
    'leg0["bmc_ordinal"] == 63',
    'w232 = json.load',
    'n1_w232_results.json',
    'r972 {WIN_LABEL}',
    '@@SUB_BLOCK@@',
    'SEVENTEEN-LEVEL replay chain',
    'W233 per-wave prereg derivation',
    'RAM_FACE_232 = ram_face(t)',
    'WIN_LABEL_232 = win_label(t)',
    'leg4["W233p_A"] == "529404..531403"',
    'assert se_mu == 0.000344',
    'fmt8(w232only["mu"]) == "\\u2212" + "0.10490950"',
]
for m in markers:
    print(t.count(m), "|", m[:70])
