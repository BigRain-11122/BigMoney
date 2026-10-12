# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts")
import perpetual_faces as pf
W224 = dict(pf.N1_BANDS.get(224) or {})
print("W224 row:", W224)
owners = [w for w, c in pf.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc = [w for w, c in pf.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
print("owner_rows:", len(owners), "| bmc_rows:", len(bmc))
n1 = open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts\perpetual_faces_n1.py", encoding="utf-8").read()
print("W224 block marker:", n1.count("    # --- W224 materializer face"),
      "| T141 marker:", n1.count("    # --- T-141 s2 lane face"))
print("leg223 count:", n1.count("assert pf.N1_BANDS[223] =="),
      "| leg222 count:", n1.count("assert pf.N1_BANDS[222] =="))
print("w<224 loops:", n1.count("if w < 224)"), "| w<223 stale:", n1.count("if w < 223)"))
print("range(16, 224):", n1.count("range(16, 224)"), "| range(17, 224):", n1.count("range(17, 224)"))
print("below-224 comment:", n1.count("registered wave below 224 composes"),
      "| below-223 stale comment:", n1.count("registered wave below 223 composes"))
pfb = open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts\perpetual_faces.py", "rb").read().decode("utf-8")
print("pf 224 row:", pfb.count('    224: {"a"'), "| pf 223 row:", pfb.count('    223: {"a"'))
print("n1 cfg 224:", n1.count('224: {"batch": "PERPETUAL-N1-W224"'))
print("W224 materializer face print:", n1.count('"+ W224 materializer face'))
# block span + parity row census inside the W224 block
a15 = "    # --- W224 materializer face"
a_t141 = "    # --- T-141 s2 lane face"
s = n1.find(a15); e = n1.find(a_t141)
blk = n1[s:e]
import re
rows = [int(w) for w in re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", blk)]
print("W224 block parity rows:", len(rows), "| head:", rows[:3], "| tail:", rows[-3:])
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
print("disjoint marker:", bool(m_disj), m_disj.group(0) if m_disj else "")
print("W223 cfg a_seed_base line:", n1.count('"a_seed_base": 507604'))
print("W224 cfg a_seed_base line:", n1.count('"a_seed_base": 509604'))
