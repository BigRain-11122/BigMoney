# -*- coding: utf-8 -*-
"""r753 bm-a W145: extract the W144 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w144_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written).
Bloodline: r752 _r752bma_w144_extract.py verbatim + W145 facts."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T = "    # --- T-141 s2 lane face"
i_t = n1.index(T)
seg = n1[:i_t]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W144 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(144)" in face and face.lstrip().startswith("# --- W144 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w144_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w144 = face.count("W144"); n_w143 = face.count("W143"); n_w142 = face.count("W142"); n_w141 = face.count("W141")
f2 = face.replace("W144", "W145").replace("W143", "W144").replace("W142", "W143").replace("W141", "W142")
assert f2.count("W145") == n_w144 and f2.count("W144") == n_w143 and f2.count("W143") == n_w142 and f2.count("W142") == n_w141 and f2.count("W141") == 0
f2 = f2.replace("set(range(331_604, 333_604))", "set(range(333_804, 335_804))")
f2 = f2.replace("set(range(333_604, 333_804))", "set(range(335_804, 336_004))")
f2 = f2.replace("arith_a144", "arith_a145")
f2 = f2.replace("arith_b144", "arith_b145")
counts = {}
needles = ["_r752bma_w144_band_gate.py", "MSG-2026-10-06-011x-bma-w144-seat",
 "bm-a r752 freeze ff6d2f918", "2ba4a613f",
 "W144 finalize one-pass bm-a r753",
 "= W144 bm-a r753 one-pass", "net chain head 712,811", "K=314,720",
 "ONE HUNDRED-AND-THIRTY-FOURTH", "sixtieth",
 "wave 144 = first free number",
 "rows 59 + candidate", "rows 133 + candidate", "below 144 composes",
 "WAVE_CONFIGS[144]", "pf.N1_BANDS[144]", "_set_wave(144)",
 "if w < 144", "range(17, 144)", "range(16, 144)", "w144_a", "w144_b",
 "n3r1_used144", "n1w144", "n1_w144",
 "== 331_604 == 331_603 + 1",
 "247e53cf8", "247e53cf8,",
 "the W143 zero-hop", "the W141 zero-hop",
 "r752 W143 gate-tail", "MSG-011x tail",
 "(law sec.4 W145 row, r753)",
 "(r752 bm-a freeze",
 "registered W142 row parity drift (r307; bm-a r748)",
 "registered W143 row parity drift (r307; bm-a r752)",
 "331_604 == 331_603 + 1", "PERPETUAL-N1-W145", "W145 path drift",
 "W145 A band drift", "W145 B band drift", "W145 engine_owner drift",
 "W145 A/B band overlap", "W145 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used145", "W145 bands hit the N3-R1",
 "W145 bands must clear",
 "W145 A hits W", "W145 B hits W", "shard dir collides",
 "W145 finalize cumulative dep", "W145 per-wave prereg missing",
 "W145 prior-wave set must derive",
 "set(range(335_804, 336_004))",
 "set(range(333_804, 335_804))",
 "must be the first-clean window past the registered",
 "must be the first-clean window past the own-wave",
 "A window must be CLEAN", "B window must be CLEAN",
 "same-freeze mutual exclusion (B hops past own A)",
 "first-clean ADMIT face past prior-wave B",
 "W145 A/B same-freeze mutual exclusion"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[139]", "N1_BANDS[140]", "N1_BANDS[141]", "N1_BANDS[142]", "N1_BANDS[143]", "N1_BANDS[144]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[139]")
print("---- parity [139..143] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[144]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "deletion-set EMPTY",
               "band facts (law sec.4", "must be the first-clean window past the registered",
               "must be the first-clean window past the own-wave", "A window must be CLEAN",
               "B window must be CLEAN", "same-freeze mutual exclusion",
               "W144 finalize one-pass", "= W144 bm-a r753 one-pass",
               "arith_a145", "set(range(333_804, 335_804))",
               "B = FIRST-CLEAN past the own-wave A window (the arithmetic",
               "W146+ projection", "ONE HUNDRED-AND-THIRTY-FOURTH",
               "sixtieth", "wave 144 = first free",
               "the re-derive-MANDATORY note"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 460]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W144 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w144"')
print(repr(n1[k - 60:k + 90]))
print("---- n1 prose anchor ----")
p = n1.find("W144 row, r752 bm-a] ")
print(repr(n1[p - 60:p + 90]))
print("---- n1 face insertion anchor ----")
fa = n1.find("assert pickle.dumps(_worker_init)")
print(repr(n1[fa:fa + 200]))
