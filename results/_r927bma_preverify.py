import ast, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

n1 = open(ROOT + r"\scripts\perpetual_faces_n1.py", encoding="utf-8",
          newline="").read().replace("\r\n", "\n")
pf = open(ROOT + r"\scripts\perpetual_faces.py", encoding="utf-8",
          newline="").read().replace("\r\n", "\n")

# 1) cfg row indent
for ln in n1.split("\n"):
    if '"batch": "PERPETUAL-N1-W20' in ln and '201: {' in ln:
        print("CFG201 LINE repr:", repr(ln[:40]))
    if '"batch": "PERPETUAL-N1-W200"' in ln:
        print("CFG200 LINE repr:", repr(ln[:40]))

# 2) claim anchor form
i = n1.find('"r922 bm-a] "')
print("CLAIM TAIL:", repr(n1[i:i+120]))

# 3) T-141 marker after mat201
i = n1.find("    # --- W201 materializer face")
j = n1.find("    # --- T-141 s2 lane face", i)
print("T141 after mat201:", j > i, "gap:", j - i)

# 4) r921 STALE dict
src = open(ROOT + r"\results\_r921bma_w200_freeze_edits.py",
           encoding="utf-8").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "STALE"):
        d = ast.literal_eval(node.value)
        for k, v in d.items():
            print("STALE key:", k, "| n_entries:", len(v), "| first3:",
                  [e[:60] for e in v[:3]])

# 5) t915 DROP_IF
src2 = open(ROOT + r"\results\_r915bma_w197_freeze_edits.py",
            encoding="utf-8").read()
for node in ast.walk(ast.parse(src2)):
    if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "DROP_IF"):
        print("DROP_IF:", ast.literal_eval(node.value))

# 6) pf201 chunk start
print("PF201 START OK:", "    # W201 (bm-a r922 freeze, seat MSG-2026-10-09-1812-bma-w201-seat" in pf)

# 7) seat MSG archive state
import os
print("SEAT inbox:", os.path.exists(ROOT + r"\fleet\inbox\MSG-2026-10-09-1935-bma-w202-seat.md"))
print("SEAT processed:", os.path.exists(ROOT + r"\fleet\inbox\processed\MSG-2026-10-09-1935-bma-w202-seat.md"))

# 8) mat201 PENDING block exact text check
pend = ("    #     --no-verify; self-ack inbox->processed archive PENDING WITH\n"
        "    #     THIS freeze window -- bm-a r922 freeze-closeout archive move\n"
        "    #     (the W201 seat MSG sits in fleet/inbox/ at freeze time,\n"
        "    #     moves to processed/ with this window closeout, honest per\n"
        "    #     frozen prereg sec.0).")
print("MAT PENDING count:", n1.count(pend))
pend_pf = ("    # zero merge, zero --no-verify; self-ack inbox->processed\n"
           "    # archive PENDING WITH THIS freeze window -- bm-a r922 freeze\n"
           "    # closeout archive move (the W201 seat MSG sits in\n"
           "    # fleet/inbox/ at freeze time, moves to processed/ with this\n"
           "    # window closeout, honest per frozen prereg sec.0);")
print("PF PENDING count:", pf.count(pend_pf))

# 9) n1_w201 occurrences / misc counts for G9 pre-planning
print("n1_w201 count:", n1.count("n1_w201"))
print("PREREG201 count:", n1.count("PERPETUAL_N1_W201_PREREG.md"))
print("w<201 loop count:", n1.count("sorted(w for w in WAVE_CONFIGS if w < 201)"))
print("set_wave(201):", n1.count("_set_wave(201)"))
print("range(17, 201):", n1.count("range(17, 201):"))
print("94_201 in n1:", n1.count("94_201"))
print("e2187e483 seat sha in n1/pf:", n1.count("e2187e483"), pf.count("e2187e483"))
