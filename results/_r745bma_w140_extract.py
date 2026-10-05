# -*- coding: utf-8 -*-
"""r745 bm-a W140: extract the W139 materializer face from
scripts/perpetual_faces_n1.py -> .codely-cli/scratch_w139_face_source.txt,
then MEASURE every planned transform needle (r735 measurement-pass law:
counts printed verbatim before the insert script is written)."""
import io, json

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
TAIL = "    finally:\n        _set_wave(2)\n"
T141 = "    # --- T-141 s2 lane face"
i_t141 = n1.index(T141)
seg = n1[:i_t141]
first = seg.rindex(TAIL, 0, seg.rindex(TAIL) - 1)  # second-to-last face end
second = seg.rindex(TAIL)                            # last face end = W139 face end
face = n1[first + len(TAIL):second + len(TAIL)]
assert "_set_wave(139)" in face and face.lstrip().startswith("# --- W139 materializer face"), "face extraction sanity"
io.open(r".codely-cli\scratch_w139_face_source.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face bytes:", len(face), "| lines:", face.count(chr(10)))

# --- measurement pass: simulate 0a/0b then count the specific needles ---
n_w139 = face.count("W139"); n_w138 = face.count("W138"); n_w137 = face.count("W137")
f2 = face.replace("W139", "W140").replace("W138", "W139").replace("W137", "W138")
assert f2.count("W140") == n_w139 and f2.count("W139") == n_w138 and f2.count("W138") == n_w137 and f2.count("W137") == 0
f2 = f2.replace("== 321_004 == 321_003 + 1", "== 323_004 == 323_003 + 1")
f2 = f2.replace("set(range(321_004, 323_004))", "set(range(323_004, 325_004))")
f2 = f2.replace("set(range(94_401, 94_601))", "set(range(94_601, 94_801))")
f2 = f2.replace("arith_a139", "arith_a140")
f2 = f2.replace("arith_b139", "arith_b140")
counts = {}
needles = ["_r744bma_w139_band_gate.py", "MSG-2026-10-05-213x-bma-w139-seat",
 "bm-a r743 freeze 6798a1e5f", "7e1fc08d0", "08710e2d0",
 "pre-freeze push raced origin forward", "behind-signal",
 "39ec08fa0", "W139 finalize one-pass bm-a r744",
 "= W139 bm-a r744 one-pass", "net chain head 699,611", "K=301,520",
 "ONE HUNDRED-AND-TWENTY-NINTH", "fifty-fifth", "wave 139 = first free number",
 "rows 54 + candidate", "rows 128 + candidate", "below 139 composes",
 "WAVE_CONFIGS[139]", "pf.N1_BANDS[139]", "_set_wave(139)", "if w < 139",
 "range(17, 139)", "range(16, 139)", "w139_a", "w139_b",
 "n3r1_used139", "n1w139", "n1_w139",
 "== 94_401 == 94_400 + 1",
 "the W139 honest 12-hop forward walk",
 "r744 W139 gate-tail", "MSG-202x tail",
 "(law sec.4 W140 row, r744)",
 "(r744 bm-a freeze",
 "registered W136 row parity drift (r307; bm-a r741)",
 "registered W137 row parity drift (r307; bm-a r742)",
 "registered W138 row parity drift (r307; bm-a r743)",
 "94_401 == 94_400 + 1", "PERPETUAL-N1-W139", "W139 path drift",
 "W139 A band drift", "W139 B band drift", "W139 engine_owner drift",
 "W139 A/B band overlap", "W139 hits SEED_REGISTRY", "hits v1", "hits W1",
 "hits probe seeds", "n3r1_used139", "W139 bands hit the N3-R1",
 "W139 bands must clear",
 "W139 A hits W", "W139 B hits W", "shard dir collides",
 "W139 finalize cumulative dep", "W139 per-wave prereg missing",
 "W139 prior-wave set must derive"]
for nd in needles:
    counts[nd] = f2.count(nd)
print(json.dumps(counts, indent=1))
# parity block presence check
for probe in ["N1_BANDS[135]", "N1_BANDS[136]", "N1_BANDS[137]", "N1_BANDS[138]", "N1_BANDS[139]"]:
    print("parity probe", probe, "count:", f2.count("pf." + probe))
# dump the current parity block tail verbatim for the insert script needle
i = f2.find("assert pf.N1_BANDS[136]")
print("---- parity [136..138] block verbatim (post-0a form) ----")
print(repr(f2[i:f2.find('}', f2.find("pf.N1_BANDS[138]")) + 1]))
# dump key segments verbatim for needle construction
for marker in ["pushed to origin", "pre-freeze push raced origin forward",
               "band facts (law sec.4", "the W139 honest 12-hop",
               "r744 W139 gate-tail projection",
               "== 94_401 == 94_400 + 1", "W140 B window must be CLEAN",
               "ONE HUNDRED-AND-TWENTY-NINTH", "fifty-fifth",
               "wave 139 = first free", "W139 finalize one-pass",
               "= W139 bm-a r744 one-pass"]:
    j = f2.find(marker)
    print(f"---- segment @ {marker!r} (count={f2.count(marker)}) ----")
    print(repr(f2[max(0, j - 120):j + 380]) if j >= 0 else "ABSENT")
# n1-side anchors for part 2
print("---- n1 WAVE_CONFIGS W139 tail anchor ----")
k = n1.find('"shard_subdir": "n1_w139"')
print(repr(n1[k:k + 130]))
print("---- n1 prose anchor ----")
p = n1.find("W138 row, r743 bm-a] ")
print(repr(n1[p - 60:p + 90]))
