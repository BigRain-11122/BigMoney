# -*- coding: utf-8 -*-
"""r740 bm-a W135: extract the W134 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w134_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written)."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T141 = "    # --- T-141 s2 lane face"
i_t141 = n1.index(T141)
# last two face-end markers before the T-141 comment
seg = n1[:i_t141]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W134 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(134)" in face and face.lstrip().startswith("# --- W134 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w134_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w134 = face.count("W134"); n_w133 = face.count("W133"); n_w132 = face.count("W132")
f2 = face.replace("W134", "W135").replace("W133", "W134").replace("W132", "W133")
assert f2.count("W135") == n_w134 and f2.count("W134") == n_w133 and f2.count("W133") == n_w132 and f2.count("W132") == 0
f2 = f2.replace("== 311_004 == 311_003 + 1", "== 313_004 == 313_003 + 1")
f2 = f2.replace("set(range(311_004, 313_004))", "set(range(313_004, 315_004))")
f2 = f2.replace("== 69_302 == 69_301 + 1", "== 69_502 == 69_501 + 1")
f2 = f2.replace("set(range(69_302, 69_502))", "set(range(69_502, 69_702))")
f2 = f2.replace("arith_a134", "arith_a135")
f2 = f2.replace("arith_b134", "arith_b135")
counts = {}
needles = ["_r739bma_w134_band_gate.py", "MSG-2026-10-05-1857-bma-w134-seat",
 "bm-a r738 freeze a869ad2ee", "5f3d9fcfc", "ad07612e7",
 "first push raced origin forward 4", "(bm-c r565 same-window",
 "r738 W133 seat MSG-1824 tail", "W134 finalize one-pass bm-a r739",
 "= W134 bm-a r739 one-pass", "net chain head 688,611", "K=290,520",
 "ONE HUNDRED-AND-TWENTY-FOURTH", "fiftieth", "wave 135 = first free number",
 "rows 50 + candidate", "rows 124 + candidate", "below 135 composes",
 "WAVE_CONFIGS[134]", "pf.N1_BANDS[134]", "_set_wave(134)", "if w < 134",
 "range(17, 134)", "range(16, 134)", "w134_a", "w134_b",
 "n3r1_used134", "n1w134", "n1_w134"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[130]", "N1_BANDS[131]", "N1_BANDS[132]", "N1_BANDS[133]", "N1_BANDS[134]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[130]")
print("---- parity block verbatim ----")
print(f2[i:f2.find('}', f2.find("N1_BANDS[133]")) + 1])
