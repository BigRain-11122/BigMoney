# -*- coding: utf-8 -*-
"""r744 bm-a W139: extract the W138 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w138_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written)."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T141 = "    # --- T-141 s2 lane face"
i_t141 = n1.index(T141)
seg = n1[:i_t141]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W138 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(138)" in face and face.lstrip().startswith("# --- W138 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w138_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w138 = face.count("W138"); n_w137 = face.count("W137"); n_w136 = face.count("W136")
f2 = face.replace("W138", "W139").replace("W137", "W138").replace("W136", "W137")
assert f2.count("W139") == n_w138 and f2.count("W138") == n_w137 and f2.count("W137") == n_w136 and f2.count("W136") == 0
f2 = f2.replace("== 319_004 == 319_003 + 1", "== 321_004 == 321_003 + 1")
f2 = f2.replace("set(range(319_004, 321_004))", "set(range(321_004, 323_004))")
f2 = f2.replace("set(range(94_201, 94_401))", "set(range(94_401, 94_601))")
f2 = f2.replace("arith_a138", "arith_a139")
f2 = f2.replace("arith_b138", "arith_b139")
counts = {}
needles = ["_r743bma_w138_band_gate.py", "MSG-2026-10-05-211x-bma-w138-seat",
 "bm-a r742 freeze f9e4ec5d2", "0bf01ef64", "7e1fc08d0",
 "pre-freeze push raced origin forward", "behind-signal",
 "576b22603", "W138 finalize one-pass bm-a r743",
 "= W138 bm-a r743 one-pass", "net chain head 697,411", "K=299,320",
 "ONE HUNDRED-AND-TWENTY-EIGHTH", "fifty-fourth", "wave 138 = first free number",
 "rows 53 + candidate", "rows 127 + candidate", "below 138 composes",
 "WAVE_CONFIGS[138]", "pf.N1_BANDS[138]", "_set_wave(138)", "if w < 138",
 "range(17, 138)", "range(16, 138)", "w138_a", "w138_b",
 "n3r1_used138", "n1w138", "n1_w138",
 "== 94_201 == 94_200 + 1",
 "the W138 honest 12-hop forward walk",
 "r742 W138 gate-tail", "MSG-202x tail",
 "(law sec.4 W139 row, r743)",
 "(r743 bm-a freeze",
 "registered W137 row parity drift (r307; bm-a r742)",
 "registered W138 row parity drift (r307; bm-a r742)",
 "registered W135 row parity drift (r307; bm-a r740)",
 "94_201 == 94_200 + 1", "PERPETUAL-N1-W138", "W138 path drift",
 "W138 A band drift", "W138 B band drift", "W138 engine_owner drift",
 "W138 A/B band overlap", "W138 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used138", "W138 bands hit the N3-R1",
 "W138 bands must clear",
 "W138 A hits W", "W138 B hits W", "shard dir collides",
 "W138 finalize cumulative dep", "W138 per-wave prereg missing",
 "W138 prior-wave set must derive"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[134]", "N1_BANDS[135]", "N1_BANDS[136]", "N1_BANDS[137]", "N1_BANDS[138]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[135]")
print("---- parity [135..137] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[137]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "pre-freeze push raced origin forward",
               "band facts (law sec.4", "the W138 honest 12-hop",
               "r742 W138 gate-tail projection",
               "== 94_201 == 94_200 + 1", "W139 B window must be CLEAN",
               "ONE HUNDRED-AND-TWENTY-EIGHTH", "fifty-fourth",
               "wave 138 = first free", "W138 finalize one-pass",
               "= W138 bm-a r743 one-pass"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 380]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W138 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w138"')
print(repr(n1[k:k + 130]))
print("---- n1 prose anchor ----")
p = n1.find("W137 row, r742 bm-a] ")
print(repr(n1[p - 60:p + 90]))
