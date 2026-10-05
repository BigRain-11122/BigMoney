# -*- coding: utf-8 -*-
import io
face = io.open(r".codely-cli\scratch_w131_face_source.txt", encoding="utf-8").read()
face = face.replace("W131", "W132"); face = face.replace("W130", "W131"); face = face.replace("W129", "W130")
for nd in ["wave 129 = first free number", "W131 finalize one-pass bm-a r736",
           "= W131 bm-a r736 one-pass", "(r736 bm-a freeze", "r735 W131 gate-tail",
           "law sec.4 W132 row, r736", "(bm-c r559 same-window", "past the W131 ",
           "rows 46 + candidate", "rows 120 + candidate", "ONE HUNDRED-AND-TWENTY-FIRST",
           "forty-seventh", "WAVE_CONFIGS[131]", "pf.N1_BANDS[131]", "_set_wave(131)",
           "if w < 131", "range(17, 131)", "range(16, 131)", "w131_a", "w131_b",
           "n3r1_used131", "n1w131", "n1_w131", "682,011", "K=283,920",
           "net chain head 682,011", "W1..W131", "W2..W131", "below 131 composes",
           "_r736bma_w131_band_gate.py", "MSG-2026-10-05-1726-bma-w131-seat",
           "bm-a r735 freeze 0b8b308db", "fde20e3a1", "d09d5fe6a"]:
    print(f"count({nd!r}) = {face.count(nd)}")

print("--- n1 anchors ---")
n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
a1 = 'W131 row, r736 bm-a] "\n          "+ T-141 s2 "'
print("prose anchor:", n1.count(a1))
a2 = '"shard_subdir": "n1_w131", "out_name": "n1_w131_results.json",\n                            "engine_owner": "bm-a"},\n                       }'
print("wc anchor:", n1.count(a2))
a3 = 'assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"\n    finally:\n        _set_wave(2)\n    # --- T-141 s2 lane face'
print("face anchor:", n1.count(a3))
print("--- pf anchor ---")
pf = io.open(r"scripts\perpetual_faces.py", encoding="utf-8").read()
a4 = '131: {"a": (305_004, 307_003), "b_exit": (68_702, 68_901),\n         "engine_owner": "bm-a"},\n}'
print("pf anchor:", pf.count(a4))
