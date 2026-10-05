# -*- coding: utf-8 -*-
"""r748 bm-a W142: extract the W141 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w141_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written).
Bloodline: r747 _r747bma_w141_extract.py verbatim + W142 facts."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T141 = "    # --- T-141 s2 lane face"
i_t141 = n1.index(T141)
seg = n1[:i_t141]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W141 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(141)" in face and face.lstrip().startswith("# --- W141 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w141_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w141 = face.count("W141"); n_w140 = face.count("W140"); n_w139 = face.count("W139")
f2 = face.replace("W141", "W142").replace("W140", "W141").replace("W139", "W140")
assert f2.count("W142") == n_w141 and f2.count("W141") == n_w140 and f2.count("W140") == n_w139 and f2.count("W139") == 0
f2 = f2.replace("== 325_004 == 325_003 + 1", "== 327_204 == 327_203 + 1")
f2 = f2.replace("set(range(325_004, 327_004))", "set(range(327_204, 329_204))")
f2 = f2.replace("set(range(327_004, 327_204))", "set(range(329_204, 329_404))")
f2 = f2.replace("arith_a141", "arith_a142")
f2 = f2.replace("arith_b141", "arith_b142")
counts = {}
needles = ["_r747bma_w141_band_gate.py", "MSG-2026-10-05-231x-bma-w141-seat",
 "bm-a r745 freeze 5e3984200", "aaa4d9be8",
 "pre-freeze push plain fast-forward delivery", "zero race this window",
 "W141 finalize one-pass bm-a r746",
 "= W141 bm-a r746 one-pass", "net chain head 704,011", "K=305,920",
 "ONE HUNDRED-AND-THIRTY-FIRST", "fifty-seventh",
 "wave 141 = first free number",
 "rows 56 + candidate", "rows 130 + candidate", "below 142 composes",
 "WAVE_CONFIGS[142]", "pf.N1_BANDS[142]", "_set_wave(142)",
 "if w < 142", "range(17, 142)", "range(16, 142)", "w142_a", "w142_b",
 "n3r1_used142", "n1w142", "n1_w142",
 "== 327_004 == 327_003 + 1",
 "the W141 zero-hop", "the W139 zero-hop",
 "r747 W141 gate-tail", "MSG-231x tail",
 "(law sec.4 W142 row, r747)",
 "(r747 bm-a freeze",
 "registered W136 row parity drift (r307; bm-a r741)",
 "registered W137 row parity drift (r307; bm-a r742)",
 "registered W139 row parity drift (r307; bm-a r743)",
 "registered W140 row parity drift (r307; bm-a r744)",
 "registered W141 row parity drift (r307; bm-a r745)",
 "325_004 == 325_003 + 1", "PERPETUAL-N1-W142", "W142 path drift",
 "W142 A band drift", "W142 B band drift", "W142 engine_owner drift",
 "W142 A/B band overlap", "W142 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used142", "W142 bands hit the N3-R1",
 "W142 bands must clear",
 "W142 A hits W", "W142 B hits W", "shard dir collides",
 "W142 finalize cumulative dep", "W142 per-wave prereg missing",
 "W142 prior-wave set must derive",
 "set(range(327_004, 327_204))",
 "set(range(325_004, 327_004))",
 "must be the arithmetic continuation past the W141",
 "must be the first-clean window past the own-wave A",
 "A window must be CLEAN", "B window must be CLEAN",
 "same-freeze mutual exclusion (B hops past own A)"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[137]", "N1_BANDS[138]", "N1_BANDS[139]", "N1_BANDS[140]", "N1_BANDS[141]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[137]")
print("---- parity [137..141] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[141]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "pre-freeze push plain fast-forward",
               "band facts (law sec.4", "must be the arithmetic continuation",
               "must be the first-clean window", "A window must be CLEAN",
               "B window must be CLEAN", "same-freeze mutual exclusion",
               "W141 finalize one-pass", "= W141 bm-a r746 one-pass",
               "arith_a142", "set(range(329_204, 329_404))",
               "B = the arithmetic continuation from the registered W141",
               "W143+ projection", "ONE HUNDRED-AND-THIRTY-FIRST",
               "fifty-seventh", "wave 141 = first free",
               "the re-derive-MANDATORY note"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 460]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W141 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w141"')
print(repr(n1[k - 60:k + 90]))
print("---- n1 prose anchor ----")
p = n1.find("W141 row, r747 bm-a] ")
print(repr(n1[p - 60:p + 90]))
