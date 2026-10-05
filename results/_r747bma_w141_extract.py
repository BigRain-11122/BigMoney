# -*- coding: utf-8 -*-
"""r747 bm-a W141: extract the W140 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w140_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written).
Bloodline: r745 _r745bma_w140_extract.py verbatim + W141 facts."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T141 = "    # --- T-141 s2 lane face"
i_t141 = n1.index(T141)
seg = n1[:i_t141]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W140 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(140)" in face and face.lstrip().startswith("# --- W140 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w140_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w140 = face.count("W140"); n_w139 = face.count("W139"); n_w138 = face.count("W138")
f2 = face.replace("W140", "W141").replace("W139", "W140").replace("W138", "W139")
assert f2.count("W141") == n_w140 and f2.count("W140") == n_w139 and f2.count("W139") == n_w138 and f2.count("W138") == 0
f2 = f2.replace("== 323_004 == 323_003 + 1", "== 325_004 == 325_003 + 1")
f2 = f2.replace("set(range(323_004, 325_004))", "set(range(325_004, 327_004))")
f2 = f2.replace("arith_a140", "arith_a141")
f2 = f2.replace("arith_b140", "arith_b141")
counts = {}
needles = ["_r745bma_w140_band_gate.py", "MSG-2026-10-05-215x-bma-w140-seat",
 "bm-a r744 freeze 4e3a018c7", "08710e2d0",
 "pre-freeze push plain fast-forward delivery", "zero race this window",
 "W140 finalize one-pass bm-a r746",
 "= W140 bm-a r746 one-pass", "net chain head 701,811", "K=303,720",
 "ONE HUNDRED-AND-THIRTIETH", "fifty-sixth", "wave 140 = first free number",
 "rows 55 + candidate", "rows 129 + candidate", "below 140 composes",
 "WAVE_CONFIGS[140]", "pf.N1_BANDS[140]", "_set_wave(140)", "if w < 140",
 "range(17, 140)", "range(16, 140)", "w140_a", "w140_b",
 "n3r1_used140", "n1w140", "n1_w140",
 "== 94_601 == 94_600 + 1",
 "the W139 zero-hop double-CLEAN",
 "r745 W140 gate-tail", "MSG-215x tail",
 "(law sec.4 W140 row, r745)",
 "(r745 bm-a freeze",
 "registered W137 row parity drift (r307; bm-a r742)",
 "registered W138 row parity drift (r307; bm-a r743)",
 "registered W139 row parity drift (r307; bm-a r744)",
 "94_601 == 94_600 + 1", "PERPETUAL-N1-W140", "W140 path drift",
 "W140 A band drift", "W140 B band drift", "W140 engine_owner drift",
 "W140 A/B band overlap", "W140 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used140", "W140 bands hit the N3-R1",
 "W140 bands must clear",
 "W140 A hits W", "W140 B hits W", "shard dir collides",
 "W140 finalize cumulative dep", "W140 per-wave prereg missing",
 "W140 prior-wave set must derive",
 "set(range(94_601, 94_801))"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[136]", "N1_BANDS[137]", "N1_BANDS[138]", "N1_BANDS[139]", "N1_BANDS[140]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[137]")
print("---- parity [137..139] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[139]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "pre-freeze push plain fast-forward",
               "band facts (law sec.4", "the W139 zero-hop double-CLEAN",
               "r745 W140 gate-tail projection",
               "== 94_601 == 94_600 + 1", "W141 B window must be CLEAN",
               "ONE HUNDRED-AND-THIRTIETH", "fifty-sixth",
               "wave 140 = first free", "W140 finalize one-pass",
               "= W140 bm-a r746 one-pass",
               "arith_b140", "set(range(94_601, 94_801))",
               "B = the arithmetic continuation from the registered W139",
               "W141+ projection"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 420]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W140 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w140"')
print(repr(n1[k:k + 130]))
print("---- n1 prose anchor ----")
p = n1.find("W139 row, r744 bm-a] ")
print(repr(n1[p - 60:p + 90]))
