# -*- coding: utf-8 -*-
"""r750 bm-a W143: extract the W142 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w142_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written).
Bloodline: r748 _r748bma_w142_extract.py verbatim + W143 facts."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T = "    # --- T-141 s2 lane face"
i_t = n1.index(T)
seg = n1[:i_t]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W142 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(142)" in face and face.lstrip().startswith("# --- W142 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w142_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w142 = face.count("W142"); n_w141 = face.count("W141"); n_w140 = face.count("W140")
f2 = face.replace("W142", "W143").replace("W141", "W142").replace("W140", "W141")
assert f2.count("W143") == n_w142 and f2.count("W142") == n_w141 and f2.count("W141") == n_w140 and f2.count("W140") == 0
f2 = f2.replace("set(range(327_204, 329_204))", "set(range(329_404, 331_404))")
f2 = f2.replace("set(range(329_204, 329_404))", "set(range(331_404, 331_604))")
f2 = f2.replace("arith_a142", "arith_a143")
f2 = f2.replace("arith_b142", "arith_b143")
counts = {}
needles = ["_r748bma_w142_band_gate.py", "MSG-2026-10-05-233x-bma-w142-seat",
 "bm-a r747 freeze 7ffadab65", "94dee2c36",
 "W142 finalize one-pass bm-a r748",
 "= W142 bm-a r748 one-pass", "net chain head 706,211", "K=308,120",
 "ONE HUNDRED-AND-THIRTY-SECOND", "fifty-eighth",
 "wave 142 = first free number",
 "rows 57 + candidate", "rows 131 + candidate", "below 142 composes",
 "WAVE_CONFIGS[142]", "pf.N1_BANDS[142]", "_set_wave(142)",
 "if w < 142", "range(17, 142)", "range(16, 142)", "w142_a", "w142_b",
 "n3r1_used142", "n1w142", "n1_w142",
 "== 327_204 == 327_203 + 1",
 "the W141 zero-hop", "the W139 zero-hop",
 "r747 W141 gate-tail", "MSG-233x tail",
 "(law sec.4 W143 row, r748)",
 "(r748 bm-a freeze",
 "registered W136 row parity drift (r307; bm-a r741)",
 "registered W137 row parity drift (r307; bm-a r742)",
 "registered W138 row parity drift (r307; bm-a r743)",
 "registered W139 row parity drift (r307; bm-a r744)",
 "registered W141 row parity drift (r307; bm-a r745)",
 "registered W142 row parity drift (r307; bm-a r747)",
 "327_204 == 327_203 + 1", "PERPETUAL-N1-W143", "W143 path drift",
 "W143 A band drift", "W143 B band drift", "W143 engine_owner drift",
 "W143 A/B band overlap", "W143 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used143", "W143 bands hit the N3-R1",
 "W143 bands must clear",
 "W143 A hits W", "W143 B hits W", "shard dir collides",
 "W143 finalize cumulative dep", "W143 per-wave prereg missing",
 "W143 prior-wave set must derive",
 "set(range(331_404, 331_604))",
 "set(range(329_404, 331_404))",
 "must be the first-clean window past the registered",
 "must be the first-clean window past the own-wave A",
 "A window must be CLEAN", "B window must be CLEAN",
 "same-freeze mutual exclusion (B hops past own A)",
 "first-clean ADMIT face past prior-wave B",
 "W143 A/B same-freeze mutual exclusion"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[138]", "N1_BANDS[139]", "N1_BANDS[140]", "N1_BANDS[141]", "N1_BANDS[142]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[138]")
print("---- parity [138..141] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[141]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "deletion-set EMPTY",
               "band facts (law sec.4", "must be the first-clean window past the registered",
               "must be the first-clean window past the own-wave", "A window must be CLEAN",
               "B window must be CLEAN", "same-freeze mutual exclusion",
               "W142 finalize one-pass", "= W142 bm-a r748 one-pass",
               "arith_a143", "set(range(331_404, 331_604))",
               "B = FIRST-CLEAN past the own-wave A window (the arithmetic",
               "W144+ projection", "ONE HUNDRED-AND-THIRTY-SECOND",
               "fifty-eighth", "wave 142 = first free",
               "the re-derive-MANDATORY note"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 460]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W142 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w142"')
print(repr(n1[k - 60:k + 90]))
print("---- n1 prose anchor ----")
p = n1.find("W142 row, r748 bm-a] ")
print(repr(n1[p - 60:p + 90]))
print("---- n1 face insertion anchor ----")
fa = n1.find("assert pickle.dumps(_worker_init)")
print(repr(n1[fa:fa + 200]))
