# -*- coding: utf-8 -*-
"""r755 bm-a W146: extract the W145 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w145_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written).
Bloodline: r753 _r753bma_w145_extract.py verbatim + W146 facts."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T = "    # --- T-141 s2 lane face"
i_t = n1.index(T)
seg = n1[:i_t]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W145 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(145)" in face and face.lstrip().startswith("# --- W145 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w145_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w145 = face.count("W145"); n_w144 = face.count("W144"); n_w143 = face.count("W143"); n_w142 = face.count("W142"); n_w141 = face.count("W141")
# W146 0a key set = W145/W144/W143/W142 ONLY (W141 = precedent refs, stays; the
# W145 face carries W141=3 all inside 0d-replaced blocks, zero outside-prose risk)
f2 = face.replace("W145", "W146").replace("W144", "W145").replace("W143", "W144").replace("W142", "W143")
assert f2.count("W146") == n_w145 and f2.count("W145") == n_w144 and f2.count("W144") == n_w143 \
    and f2.count("W143") == n_w142 and f2.count("W141") == n_w141, \
    "blanket count check (W141 preserved: precedent refs)"
f2 = f2.replace("set(range(333_804, 335_804))", "set(range(336_004, 338_004))")
f2 = f2.replace("set(range(335_804, 336_004))", "set(range(338_004, 338_204))")
f2 = f2.replace("arith_a145", "arith_a146")
f2 = f2.replace("arith_b145", "arith_b146")
counts = {}
needles = ["_r753bma_w145_band_gate.py", "MSG-2026-10-06-023x-bma-w145-seat",
 "bm-a r754 freeze", "55c2a1715", "d5fdbb317",
 "W145 finalize one-pass bm-a r755",
 "= W145 bm-a r755 one-pass", "net chain head 712,811", "K=314,720",
 "ONE HUNDRED-AND-THIRTY-FIFTH", "sixty-first",
 "wave 145 = first free number",
 "rows 60 + candidate", "rows 134 + candidate", "below 145 composes",
 "WAVE_CONFIGS[145]", "pf.N1_BANDS[145]", "_set_wave(145)",
 "if w < 145", "range(17, 145)", "range(16, 145)", "w145_a", "w145_b",
 "n3r1_used145", "n1w145", "n1_w145",
 "== 333_804 == 333_803 + 1",
 "must be the first-clean window past the registered",
 "must be the first-clean window past the own-wave",
 "A window must be CLEAN", "B window must be CLEAN",
 "same-freeze mutual exclusion (B hops past own A)",
 "first-clean ADMIT face past prior-wave B",
 "band facts (law sec.4",
 "the W144 zero-hop", "the W142 zero-hop",
 "r752 W144 gate-tail", "MSG-023x tail",
 "(law sec.4 W146 row, r755)",
 "(r754 bm-a freeze",
 "registered W143 row parity drift (r307; bm-a r747)",
 "registered W144 row parity drift (r307; bm-a r752)",
 "registered W145 row parity drift (r307; bm-a r753)",
 "335_804 == 335_803 + 1", "PERPETUAL-N1-W146", "W146 path drift",
 "W146 A band drift", "W146 B band drift", "W146 engine_owner drift",
 "W146 A/B band overlap", "W146 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used146", "W146 bands hit the N3-R1",
 "W146 bands must clear",
 "W146 A hits W", "W146 B hits W", "shard dir collides",
 "W146 finalize cumulative dep", "W146 per-wave prereg missing",
 "W146 prior-wave set must derive",
 "set(range(338_004, 338_204))",
 "set(range(336_004, 338_004))",
 "B = FIRST-CLEAN past the own-wave A window (the arithmetic",
 "W147+ projection", "the re-derive-MANDATORY note",
 "ff6d2f918", "247e53cf8",
 "MSG-2026-10-06-023x", "n1_w145", "n1_w146",
]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[140]", "N1_BANDS[141]", "N1_BANDS[142]", "N1_BANDS[143]", "N1_BANDS[144]", "N1_BANDS[145]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[140]")
print("---- parity [140..145] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[145]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "deletion-set EMPTY",
               "band facts (law sec.4", "must be the first-clean window past the registered",
               "must be the first-clean window past the own-wave", "A window must be CLEAN",
               "B window must be CLEAN", "same-freeze mutual exclusion",
               "W145 finalize one-pass", "= W145 bm-a r755 one-pass",
               "arith_a146", "set(range(336_004, 338_004))",
               "B = FIRST-CLEAN past the own-wave A window (the arithmetic",
               "W147+ projection", "ONE HUNDRED-AND-THIRTY-FIFTH",
               "sixty-first", "wave 145 = first free",
               "the re-derive-MANDATORY note"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 460]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W145 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w145"')
print(repr(n1[k - 60:k + 90]))
print("---- n1 prose anchor ----")
p = n1.find("W145 row, r753 bm-a] ")
print(repr(n1[p - 60:p + 90]))
print("---- n1 face insertion anchor ----")
fa = n1.find("assert pickle.dumps(_worker_init)")
print(repr(n1[fa:fa + 200]))
