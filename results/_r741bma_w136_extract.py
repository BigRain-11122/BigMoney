# -*- coding: utf-8 -*-
"""r741 bm-a W136: extract the W135 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w135_face_source.txt,
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
second = seg.rindex(TAIL)                            # last face end = W135 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(135)" in face and face.lstrip().startswith("# --- W135 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w135_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w135 = face.count("W135"); n_w134 = face.count("W134"); n_w133 = face.count("W133")
f2 = face.replace("W135", "W136").replace("W134", "W135").replace("W133", "W134")
assert f2.count("W136") == n_w135 and f2.count("W135") == n_w134 and f2.count("W134") == n_w133 and f2.count("W133") == 0
f2 = f2.replace("== 313_004 == 313_003 + 1", "== 315_004 == 315_003 + 1")
f2 = f2.replace("set(range(313_004, 315_004))", "set(range(315_004, 317_004))")
f2 = f2.replace("== 69_502 == 69_501 + 1", "== 69_702 == 69_701 + 1")
f2 = f2.replace("set(range(69_502, 69_702))", "set(range(69_702, 69_902))")
f2 = f2.replace("arith_a135", "arith_a136")
f2 = f2.replace("arith_b135", "arith_b136")
counts = {}
needles = ["_r740bma_w135_band_gate.py", "MSG-2026-10-05-1933-bma-w135-seat",
 "bm-a r739 freeze d6b64dddd", "98712a0e3", "20d0036dc", "2564ba798",
 "direct clean fast-forward push this", "zero race, zero merge window",
 "r739 W135 seat MSG-1933 tail", "W135 finalize one-pass bm-a r740",
 "= W135 bm-a r740 one-pass", "net chain head 690,811", "K=292,720",
 "ONE HUNDRED-AND-TWENTY-FIFTH", "fifty-first", "wave 135 = first free number",
 "rows 51 + candidate", "rows 125 + candidate", "below 136 composes",
 "WAVE_CONFIGS[135]", "pf.N1_BANDS[135]", "_set_wave(135)", "if w < 135",
 "range(17, 135)", "range(16, 135)", "w135_a", "w135_b",
 "n3r1_used135", "n1w135", "n1_w135"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[131]", "N1_BANDS[132]", "N1_BANDS[133]", "N1_BANDS[134]", "N1_BANDS[135]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[131]")
print("---- parity block verbatim (post-0a form) ----")
print(f2[i:f2.find('}', f2.find("pf.N1_BANDS[134]")) + 1])
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "delivery", "r739 freeze", "W135 finalize one-pass", "net chain head", "K=292,720"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} ----")
    print(f2[max(0, j - 120):j + 260])
