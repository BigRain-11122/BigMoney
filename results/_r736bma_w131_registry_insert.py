# -*- coding: utf-8 -*-
"""r736 bm-a W131 registry insertion: N1_BANDS row 131 (perpetual_faces.py)
+ WAVE_CONFIGS[131] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r735 _r735bma_w130_registry_insert.py verbatim + W131 facts
(double-CLEAN window: A = arithmetic continuation from the registered W130
A tail 305_003+1, CLEAN hops=0; B = arithmetic continuation from the
registered W130 B tail 68_701+1, CLEAN hops=0).
r735 codegen pit laws enforced: (1) all new-block assert messages
single-line or parenthesized; (2) rep() expects measured on
post-prior-replacement text (measurement pass _r736bma_w131_measure.py
+ _r736bma_print_blocks.py printed every count verbatim before this
script was written)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W130 face -> W131 face ============
face = io.open(r".codely-cli\scratch_w130_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w130 = face.count("W130"); n_w129 = face.count("W129"); n_w128 = face.count("W128")
face = face.replace("W130", "W131")
face = face.replace("W129", "W130")
face = face.replace("W128", "W129")
assert face.count("W131") == n_w130 and face.count("W130") == n_w129 \
    and face.count("W129") == n_w128 and face.count("W128") == 0, \
    "blanket count check"

# --- 0b. B-block: past-hit restart -> plain arithmetic (W131 B hops=0 CLEAN) ---
old_b = '''assert WAVE_CONFIGS[130]["b_exit_seed_base"] == 68_502, (
            "W131 B must be the first-clean past-hit restart window "
            "after the REFUSED arithmetic continuation 68_401..68_600 "
            "from the W130 registered B band tail (refusal facts "
            "SEED_REGISTRY 68_500 t19_phantom_p1 + 68_501 "
            "perpetual_n4_b1, D-20261002-05 pin past-hit restart "
            "semantics, hops=1)")
        _arith_b130_refused = set(range(68_401, 68_601))
        assert _arith_b130_refused & reg_ints == {68_500, 68_501}, \\
            "W131 B refusal face: exactly t19_phantom_p1 + perpetual_n4_b1"
        arith_b130 = set(range(68_502, 68_702))
        assert not (arith_b130 & reg_ints), \\
            "W131 B first-clean window must be CLEAN (hops=1 ADMIT face)"'''
new_b = '''assert WAVE_CONFIGS[131]["b_exit_seed_base"] == 68_702 == 68_701 + 1, (
            "W131 B must be the arithmetic continuation past the W130 "
            "registered B band tail (CLEAN hops=0 at both the pre-seat "
            "probe and the freeze-window gate; double-CLEAN window)")
        arith_b131 = set(range(68_702, 68_902))
        assert not (arith_b131 & reg_ints), \\
            "W131 B window must be CLEAN (arithmetic ADMIT face, hops=0)"'''
assert face.count(old_b) == 1, "face: B-block needle"
face = face.replace(old_b, new_b)
assert face.count("arith_b130") == 0, "face: arith_b130 residue after B-block replace"

# --- 0c. band facts comment: past-hit restart -> double-CLEAN (W131 facts) ---
old_facts = '''# band facts (law sec.4 W131 row, r735): A = the arithmetic
        # continuation from the registered W130 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the first-clean past-hit restart window after the
        # REFUSED arithmetic continuation 68_401..68_600 from the
        # registered W130 B tail (refusal facts SEED_REGISTRY
        # 68_500 t19_phantom_p1 + 68_501 perpetual_n4_b1, hops=1,
        # D-20261002-05 pin past-hit restart semantics;
        # cross-window convergence with the r734 W130 gate-tail
        # W131+ projection).'''
new_facts = '''# band facts (law sec.4 W131 row, r736): A = the arithmetic
        # continuation from the registered W130 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the arithmetic continuation from the registered W130
        # B tail (CLEAN hops=0 at both windows; double-CLEAN window;
        # cross-window convergence with the r735 W130 gate-tail
        # W131+ projection).'''
assert face.count(old_facts) == 1, "face: band-facts comment needle"
face = face.replace(old_facts, new_facts)

# --- 0d. specific needles (counts measured post-0a/0b/0c by the measurement
#     pass; the band-gate receipt needle runs FIRST because it carries a
#     w130_b substring, consuming the 9th raw hit -- substring-order law;
#     the parity block runs LAST because its added rows carry W-numbers) ---
specific = [
    # receipt/seat needles FIRST (substring-order law)
    ("_r735bma_w130_band_gate.py", "_r736bma_w131_band_gate.py", 1),
    ("MSG-2026-10-05-1658-bma-w130-seat", "MSG-2026-10-05-1726-bma-w131-seat", 1),
    ("bm-a r734 freeze 5e8d140ef", "bm-a r735 freeze 0b8b308db", 1),
    ("to origin 02e151b0a BEFORE this freeze, r565 law (payload\n"
     "    #     = seat MSG + pre-seat probe + probe receipt;\n"
     "    #     deletion-set EMPTY; zero-UU clean push, behind 0 at\n"
     "    #     fetch -- no race this window)",
     "to origin fde20e3a1 BEFORE this freeze, r565 law (payload\n"
     "    #     = seat MSG + pre-seat probe + probe receipt;\n"
     "    #     deletion-set EMPTY; first push raced origin forward 3\n"
     "    #     commits = r524 behind-signal (bm-c r559 same-window\n"
     "    #     wave), merge-mode zero-UU canonical closeout,\n"
     "    #     delivery d09d5fe6a)", 1),
    ("W130 finalize one-pass bm-a r735", "W130 finalize one-pass bm-a r736", 1),
    ("= W130 bm-a r735 one-pass", "= W130 bm-a r736 one-pass", 1),
    ("net chain head 679,811", "net chain head 682,011", 2),
    ("K=281,720", "K=283,920", 1),
    ("ONE HUNDRED-AND-TWENTIETH", "ONE HUNDRED-AND-TWENTY-FIRST", 1),
    ("forty-sixth", "forty-seventh", 1),
    ("rows 45 + candidate", "rows 46 + candidate", 1),
    ("rows 119 + candidate", "rows 120 + candidate", 1),
    ("(r735 bm-a freeze", "(r736 bm-a freeze", 1),
    ("below 130 composes", "below 131 composes", 1),
    ("== 303_004 == 303_003 + 1", "== 305_004 == 305_003 + 1", 1),
    ("set(range(303_004, 305_004))", "set(range(305_004, 307_004))", 1),
    ("WAVE_CONFIGS[130]", "WAVE_CONFIGS[131]", 4),  # 5 raw minus 1 consumed by the 0b B-block replace
    ("pf.N1_BANDS[130]", "pf.N1_BANDS[131]", 3),
    ("_set_wave(130)", "_set_wave(131)", 1),
    ("if w < 130", "if w < 131", 3),
    ("range(17, 130)", "range(17, 131)", 1),
    ("range(16, 130)", "range(16, 131)", 1),
    ("w130_a", "w131_a", 8), ("w130_b", "w131_b", 8),  # 9th raw hit = "_r735bma_w130_band_gate.py" substring, consumed by the receipt needle above (substring-order law)
    ("arith_a130", "arith_a131", 2),  # arith_b131 handled inside the B-block replacement
    ("n3r1_used130", "n3r1_used131", 3),
    ("n1w130", "n1w131", 2), ("n1_w130", "n1_w131", 2),
]
face = rep(face, specific, "face")

# --- 0e. registered row parity block shift LAST (W126..W129 -> W127..W130) ---
old_parity = '''assert pf.N1_BANDS[126] == {"a": (295_004, 297_003),
                                    "b_exit": (67_401, 67_600),
                                    "engine_owner": "bm-a"}, \\
            "registered W126 row parity drift (r307; bm-a r731)"
        assert pf.N1_BANDS[127] == {"a": (297_004, 299_003),
                                    "b_exit": (67_601, 67_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W127 row parity drift (r307; bm-a r732)"
        assert pf.N1_BANDS[128] == {"a": (299_004, 301_003),
                                    "b_exit": (68_001, 68_200),
                                    "engine_owner": "bm-a"}, \\
            "registered W129 row parity drift (r307; bm-a r733)"
        assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),
                                    "b_exit": (68_201, 68_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W130 row parity drift (r307; bm-a r734)"'''
new_parity = '''assert pf.N1_BANDS[127] == {"a": (297_004, 299_003),
                                    "b_exit": (67_601, 67_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W127 row parity drift (r307; bm-a r732)"
        assert pf.N1_BANDS[128] == {"a": (299_004, 301_003),
                                    "b_exit": (68_001, 68_200),
                                    "engine_owner": "bm-a"}, \\
            "registered W128 row parity drift (r307; bm-a r733)"
        assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),
                                    "b_exit": (68_201, 68_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W129 row parity drift (r307; bm-a r734)"
        assert pf.N1_BANDS[130] == {"a": (303_004, 305_003),
                                    "b_exit": (68_502, 68_701),
                                    "engine_owner": "bm-a"}, \\
            "registered W130 row parity drift (r307; bm-a r735)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w131_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W131 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 131 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '131: {"a": (305_004, 307_003)' in pf_src:
    print("pf: row 131 already present (idempotent skip)")
else:
    w130_row = '''    130: {"a": (303_004, 305_003), "b_exit": (68_502, 68_701),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w130_row) == 1, "pf: W130 row + closing brace needle"
    w131_block = '''    130: {"a": (303_004, 305_003), "b_exit": (68_502, 68_701),
         "engine_owner": "bm-a"},
    # W131 (bm-a r736 freeze, seat MSG-2026-10-05-1726-bma-w131-seat
    # pushed to origin fde20e3a1 pre-freeze r565 law; band gate ADMIT
    # results/_r736bma_w131_band_gate.json: double-CLEAN window --
    # A arithmetic continuation 305_003+1 -> 305_004..307_003
    # CLEAN hops=0; B arithmetic continuation 68_701+1 ->
    # 68_702..68_901 CLEAN hops=0; dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W132+ projection (gate-derived r736): A 307_004..309_003
    # CLEAN hops=0; B 68_902..69_101 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W131 bands were never assigned).
    131: {"a": (305_004, 307_003), "b_exit": (68_702, 68_901),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w130_row, w131_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 131 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[131] after entry 130 ---
if '"batch": "PERPETUAL-N1-W131"' in n1:
    print("n1: WAVE_CONFIGS[131] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w130", "out_name": "n1_w130_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W130 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w130", "out_name": "n1_w130_results.json",
                            "engine_owner": "bm-a"},
                       131: {"batch": "PERPETUAL-N1-W131",
                            "prereg": ("research/PERPETUAL_N1_W131_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTY-FIRST ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 120 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W130 row bm-a r735 freeze "
                                       "0b8b308db, SINGLE STATE zero seat gap W2..W130 all "
                                       "registered; W130 finalize landed same-window r736, ledger "
                                       "head 682,011, merged pool K=283,920; seat published=reserved "
                                       "MSG-2026-10-05-1726-bma-w131-seat PUSHED to origin fde20e3a1 "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "first push raced origin forward 3 commits = r524 behind-signal "
                                       "(bm-c r559 same-window wave), merge-mode zero-UU canonical "
                                       "closeout, delivery d09d5fe6a); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 131: "
                                       "A = arithmetic continuation from the registered W130 A tail "
                                       "(305_004..307_003 CLEAN hops=0) + B = arithmetic continuation "
                                       "from the registered W130 B tail (68_702..68_901 CLEAN hops=0 "
                                       "double-CLEAN window; cross-window convergence with the r735 "
                                       "W130 gate-tail W131+ projection re-derived; ADMIT receipt "
                                       "results/_r736bma_w131_band_gate.py; W132+ projection per this "
                                       "window gate: A 307_004..309_003 CLEAN / B 68_902..69_101 "
                                       "CLEAN both hops=0; W1..W130 finalize ALL LANDED (W130 "
                                       "finalize one-pass bm-a r736, §7 backfill same commit; net "
                                       "chain head 682,011, merged pool K=283,920) -- ZERO in-flight "
                                       "upstream seats, clean finalize chain precondition -- finalize "
                                       "merge loop still derives the wave set from registry keys at "
                                       "run time, FAIL-CLOSED r307 always on)"),
                            "a_seed_base": 305_004,        # law sec.4 W131 A: 305_004..307_003 (arithmetic continuation from the registered W130 A tail)
                            "b_exit_seed_base": 68_702,   # law sec.4 W131 B: 68_702..68_901 (arithmetic continuation from the registered W130 B tail, CLEAN hops=0 double-CLEAN window)
                            "shard_subdir": "n1_w131", "out_name": "n1_w131_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[131] inserted")

# --- 2b. materializer face insertion after the W130 face end ---
if "_set_wave(131)" in n1:
    print("n1: W131 materializer face already present (idempotent skip)")
else:
    face_anchor = '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'''
    assert n1.count(face_anchor) == 1, "n1: face insertion anchor"
    n1 = n1.replace(face_anchor,
        '''        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
''' + face + '''    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim''')
    print("n1: W131 materializer face inserted")

# --- 2c. selftest prose face after the W130 prose ---
if 'law sec.4 W131 row, r736 bm-a] ' in n1:
    print("n1: W131 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W130 row, r735 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W130 row, r735 bm-a] "
          "+ W131 materializer face [same guard set, dep=W17..W130 outputs "
          "ALL PRESENT (landed net chain head 682,011 = W130 bm-a r736 "
          "one-pass, §7 backfill same commit; K=283,920 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTY-FIRST ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 120 + candidate) bm-a's forty-seventh owned "
          "claim per machine-derive (engine_owner==bm-a rows 46 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 131 = first "
          "FREE number after the REGISTERED W130 row bm-a r735 freeze "
          "0b8b308db, SINGLE STATE zero seat gap W2..W130 all registered; "
          "seat published=reserved MSG-2026-10-05-1726-bma-w131-seat "
          "pushed to origin fde20e3a1 BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; first push raced origin forward 3 commits "
          "= r524 behind-signal (bm-c r559 same-window wave), merge-mode "
          "zero-UU canonical closeout, delivery d09d5fe6a), A = "
          "ARITHMETIC CONTINUATION from the registered W130 A tail "
          "(305_004..307_003 CLEAN hops=0) + B = ARITHMETIC CONTINUATION "
          "from the registered W130 B tail (68_702..68_901 CLEAN hops=0 "
          "double-CLEAN window; cross-window convergence with the r735 "
          "W130 gate-tail W131+ projection re-derived; ADMIT receipt "
          "results/_r736bma_w131_band_gate.py; W132+ projection per "
          "this window gate: A 307_004..309_003 CLEAN / B 68_902..69_101 "
          "CLEAN both hops=0) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W131 row, r736 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W131 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
