# -*- coding: utf-8 -*-
"""r743 bm-a W138: extract the W137 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w137_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written)."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T141 = "    # --- T-141 s2 lane face"
i_t141 = n1.index(T141)
seg = n1[:i_t141]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W137 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(137)" in face and face.lstrip().startswith("# --- W137 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w137_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b/B-block then count the specific needles ---
n_w137 = face.count("W137"); n_w136 = face.count("W136"); n_w135 = face.count("W135")
f2 = face.replace("W137", "W138").replace("W136", "W137").replace("W135", "W136")
assert f2.count("W138") == n_w137 and f2.count("W137") == n_w136 and f2.count("W136") == n_w135 and f2.count("W135") == 0
f2 = f2.replace("== 317_004 == 317_003 + 1", "== 319_004 == 319_003 + 1")
f2 = f2.replace("set(range(317_004, 319_004))", "set(range(319_004, 321_004))")
f2 = f2.replace("set(range(94_001, 94_201))", "set(range(94_201, 94_401))")
f2 = f2.replace("arith_a137", "arith_a138")
f2 = f2.replace("arith_b137", "arith_b138")
counts = {}
needles = ["_r742bma_w137_band_gate.py", "MSG-2026-10-05-202x-bma-w137-seat",
 "bm-a r741 freeze 7cafbc7ab", "af1c3c267", "0bf01ef64", "576b22603",
 "pre-freeze push raced origin forward", "behind-signal",
 "d28d392ce", "W137 finalize one-pass bm-a r742",
 "= W137 bm-a r742 one-pass", "net chain head 695,211", "K=297,120",
 "ONE HUNDRED-AND-TWENTY-SEVENTH", "fifty-third", "wave 137 = first free number",
 "rows 52 + candidate", "rows 126 + candidate", "below 137 composes",
 "WAVE_CONFIGS[137]", "pf.N1_BANDS[137]", "_set_wave(137)", "if w < 137",
 "range(17, 137)", "range(16, 137)", "w137_a", "w137_b",
 "n3r1_used137", "n1w137", "n1_w137",
 "FIRST-CLEAN window after the honest", "12-hop forward walk",
 "arithmetic continuation from the registered W137",
 "double-CLEAN", "69_702..69_901", "94_001..94_200",
 "(r742 bm-a freeze", "(law sec.4 W138 row, r742)",
 "r741 W137 gate-tail"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[133]", "N1_BANDS[134]", "N1_BANDS[135]", "N1_BANDS[136]", "N1_BANDS[137]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[133]")
print("---- parity block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[136]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "pre-freeze push raced origin forward",
               "r741 freeze", "W137 finalize one-pass", "= W137 bm-a r742",
               "net chain head", "K=297,120", "FIRST-CLEAN window after the honest",
               "B = the FIRST-CLEAN", "b_exit_seed_base\"] == 94_001",
               "W138 B window must be CLEAN"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 150):j + 420]) if j >= 0 else "ABSENT")
