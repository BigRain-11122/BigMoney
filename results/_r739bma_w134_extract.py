# -*- coding: utf-8 -*-
"""r739 bm-a W134: extract the W133 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w133_face_source.txt,
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
second = seg.rindex(TAIL)                            # last face end = W133 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(133)" in face and face.lstrip().startswith("# --- W133 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w133_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w133 = face.count("W133"); n_w132 = face.count("W132"); n_w131 = face.count("W131")
f2 = face.replace("W133", "W134").replace("W132", "W133").replace("W131", "W132")
assert f2.count("W134") == n_w133 and f2.count("W133") == n_w132 and f2.count("W132") == n_w131 and f2.count("W131") == 0
f2 = f2.replace("== 309_004 == 309_003 + 1", "== 311_004 == 311_003 + 1")
f2 = f2.replace("set(range(309_004, 311_004))", "set(range(311_004, 313_004))")
f2 = f2.replace("== 69_102 == 69_101 + 1", "== 69_302 == 69_301 + 1")
f2 = f2.replace("set(range(69_102, 69_302))", "set(range(69_302, 69_502))")
f2 = f2.replace("arith_a133", "arith_a134")
f2 = f2.replace("arith_b133", "arith_b134")
counts = {}
needles = ["_r738bma_w133_band_gate.py", "MSG-2026-10-05-1824-bma-w133-seat",
 "bm-a r737 freeze 37c3925ad", "2d717cc03", "1ea4ff938",
 "first push raced origin forward 8", "(bm-c r563 same-window",
 "r737 W132 seat MSG-1755 tail", "W132 finalize one-pass bm-a r738",
 "= W132 bm-a r738 one-pass", "net chain head 686,411", "K=288,320",
 "ONE HUNDRED-AND-TWENTY-THIRD", "forty-ninth", "wave 133 = first free number",
 "rows 48 + candidate", "rows 122 + candidate", "below 133 composes",
 "WAVE_CONFIGS[133]", "pf.N1_BANDS[133]", "_set_wave(133)", "if w < 133",
 "range(17, 133)", "range(16, 133)", "w133_a", "w133_b",
 "n3r1_used133", "n1w133", "n1_w133"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[129]", "N1_BANDS[130]", "N1_BANDS[131]", "N1_BANDS[132]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
