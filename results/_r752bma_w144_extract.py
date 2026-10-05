# -*- coding: utf-8 -*-
"""r752 bm-a W144: extract the W143 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w143_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written).
Bloodline: r750 _r750bma_w143_extract.py verbatim + W144 facts."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T = "    # --- T-141 s2 lane face"
i_t = n1.index(T)
seg = n1[:i_t]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W143 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(143)" in face and face.lstrip().startswith("# --- W143 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w143_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w143 = face.count("W143"); n_w142 = face.count("W142"); n_w141 = face.count("W141")
f2 = face.replace("W143", "W144").replace("W142", "W143").replace("W141", "W142")
assert f2.count("W144") == n_w143 and f2.count("W143") == n_w142 and f2.count("W142") == n_w141 and f2.count("W141") == 0
f2 = f2.replace("set(range(329_404, 331_404))", "set(range(331_604, 333_604))")
f2 = f2.replace("set(range(331_404, 331_604))", "set(range(333_604, 333_804))")
f2 = f2.replace("arith_a143", "arith_a144")
f2 = f2.replace("arith_b143", "arith_b144")
counts = {}
needles = ["_r750bma_w143_band_gate.py", "MSG-2026-10-06-002x-bma-w143-seat",
 "bm-a r748 freeze 16baa2a7b", "3a7640311",
 "W143 finalize one-pass bm-a r749",
 "= W143 bm-a r749 one-pass", "net chain head 708,411", "K=310,320",
 "ONE HUNDRED-AND-THIRTY-THIRD", "fifty-ninth",
 "wave 143 = first free number",
 "rows 58 + candidate", "rows 132 + candidate", "below 143 composes",
 "WAVE_CONFIGS[143]", "pf.N1_BANDS[143]", "_set_wave(143)",
 "if w < 143", "range(17, 143)", "range(16, 143)", "w143_a", "w143_b",
 "n3r1_used143", "n1w143", "n1_w143",
 "== 329_404 == 329_403 + 1",
 "fec2adb73", "fec2adb73,",
 "the W142 zero-hop", "the W140 zero-hop",
 "r749 W142 gate-tail", "MSG-002x tail",
 "(law sec.4 W144 row, r752)",
 "(r750 bm-a freeze",
 "registered W141 row parity drift (r307; bm-a r745)",
 "registered W142 row parity drift (r307; bm-a r748)",
 "329_404 == 329_403 + 1", "PERPETUAL-N1-W144", "W144 path drift",
 "W144 A band drift", "W144 B band drift", "W144 engine_owner drift",
 "W144 A/B band overlap", "W144 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used144", "W144 bands hit the N3-R1",
 "W144 bands must clear",
 "W144 A hits W", "W144 B hits W", "shard dir collides",
 "W144 finalize cumulative dep", "W144 per-wave prereg missing",
 "W144 prior-wave set must derive",
 "set(range(333_604, 333_804))",
 "set(range(331_604, 333_604))",
 "must be the first-clean window past the registered",
 "must be the first-clean window past the own-wave",
 "A window must be CLEAN", "B window must be CLEAN",
 "same-freeze mutual exclusion (B hops past own A)",
 "first-clean ADMIT face past prior-wave B",
 "W144 A/B same-freeze mutual exclusion"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[138]", "N1_BANDS[139]", "N1_BANDS[140]", "N1_BANDS[141]", "N1_BANDS[142]", "N1_BANDS[143]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[138]")
print("---- parity [138..142] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[143]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "deletion-set EMPTY",
               "band facts (law sec.4", "must be the first-clean window past the registered",
               "must be the first-clean window past the own-wave", "A window must be CLEAN",
               "B window must be CLEAN", "same-freeze mutual exclusion",
               "W143 finalize one-pass", "= W143 bm-a r749 one-pass",
               "arith_a144", "set(range(331_604, 333_604))",
               "B = FIRST-CLEAN past the own-wave A window (the arithmetic",
               "W145+ projection", "ONE HUNDRED-AND-THIRTY-THIRD",
               "fifty-ninth", "wave 143 = first free",
               "the re-derive-MANDATORY note"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 460]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W143 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w143"')
print(repr(n1[k - 60:k + 90]))
print("---- n1 prose anchor ----")
p = n1.find("W143 row, r750 bm-a] ")
print(repr(n1[p - 60:p + 90]))
print("---- n1 face insertion anchor ----")
fa = n1.find("assert pickle.dumps(_worker_init)")
print(repr(n1[fa:fa + 200]))
