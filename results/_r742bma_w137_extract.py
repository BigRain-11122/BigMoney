# -*- coding: utf-8 -*-
"""r742 bm-a W137: extract the W136 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w136_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written)."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T141 = "    # --- T-141 s2 lane face"
i_t141 = n1.index(T141)
seg = n1[:i_t141]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W136 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(136)" in face and face.lstrip().startswith("# --- W136 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w136_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w136 = face.count("W136"); n_w135 = face.count("W135"); n_w134 = face.count("W134")
f2 = face.replace("W136", "W137").replace("W135", "W136").replace("W134", "W135")
assert f2.count("W137") == n_w136 and f2.count("W136") == n_w135 and f2.count("W135") == n_w134 and f2.count("W134") == 0
f2 = f2.replace("== 315_004 == 315_003 + 1", "== 317_004 == 317_003 + 1")
f2 = f2.replace("set(range(315_004, 317_004))", "set(range(317_004, 319_004))")
f2 = f2.replace("== 69_702 == 69_701 + 1", "== 94_001 == 69_901 + 1  # first-clean after honest 12-hop forward walk (NOT arithmetic)")
f2 = f2.replace("set(range(69_702, 69_902))", "set(range(94_001, 94_201))")
f2 = f2.replace("arith_a136", "arith_a137")
f2 = f2.replace("arith_b136", "arith_b137")
counts = {}
needles = ["_r741bma_w136_band_gate.py", "MSG-2026-10-05-1952-bma-w136-seat",
 "bm-a r740 freeze bc921896a", "20d0036dc", "af1c3c267", "d28d392ce",
 "pre-freeze push raced origin forward", "behind-signal",
 "r740 W135 seat MSG-1933 tail", "W135 finalize one-pass bm-a r741",
 "= W135 bm-a r741 one-pass", "net chain head 693,011", "K=294,920",
 "ONE HUNDRED-AND-TWENTY-SIXTH", "fifty-second", "wave 136 = first free number",
 "rows 51 + candidate", "rows 125 + candidate", "below 136 composes",
 "WAVE_CONFIGS[136]", "pf.N1_BANDS[136]", "_set_wave(136)", "if w < 136",
 "range(17, 136)", "range(16, 136)", "w136_a", "w136_b",
 "n3r1_used136", "n1w136", "n1_w136", "arithmetic continuation from the registered W135 B tail",
 "69_702..69_901 CLEAN hops=0", "double-CLEAN"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[132]", "N1_BANDS[133]", "N1_BANDS[134]", "N1_BANDS[135]", "N1_BANDS[136]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[132]")
print("---- parity block verbatim (post-0a form) ----")
print(f2[i:f2.find('}', f2.find("pf.N1_BANDS[136]")) + 1])
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "delivery", "r740 freeze", "W135 finalize one-pass", "net chain head", "K=294,920", "arithmetic continuation from the registered W135 B tail", "69_702..69_901 CLEAN hops=0"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(f2[max(0, j - 120):j + 300])
