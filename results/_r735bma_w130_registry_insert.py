# -*- coding: utf-8 -*-
"""r735 bm-a W130 registry insertion: N1_BANDS row 130 (perpetual_faces.py)
+ WAVE_CONFIGS[130] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r734 _r734bma_w129_registry_insert.py verbatim + W130 facts
(A = arithmetic continuation CLEAN hops=0; B = first-clean past-hit restart
window after the REFUSED arithmetic continuation 68_401..68_600, refusal
identity SEED_REGISTRY 68_500 t19_phantom_p1 + 68_501 perpetual_n4_b1,
hops=1)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W129 face -> W130 face ============
face = io.open(r".codely-cli\scratch_w129_face_source.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w129 = face.count("W129"); n_w128 = face.count("W128")
face = face.replace("W129", "W130")
face = face.replace("W128", "W129")
assert face.count("W130") == n_w129 and face.count("W129") == n_w128, \
    "blanket count check"

# --- 0b. B-block: plain arithmetic -> past-hit restart (W130 B hops=1) ---
old_b = '''assert WAVE_CONFIGS[129]["b_exit_seed_base"] == 68_201 == 68_200 + 1, (
            "W130 B must be the arithmetic continuation past the W129 "
            "registered B band tail")
        arith_b129 = set(range(68_201, 68_401))
        assert not (arith_b129 & reg_ints), \\
            "W130 B window must be CLEAN (arithmetic ADMIT face, hops=0)"'''
new_b = '''assert WAVE_CONFIGS[130]["b_exit_seed_base"] == 68_502, (
            "W130 B must be the first-clean past-hit restart window "
            "after the REFUSED arithmetic continuation 68_401..68_600 "
            "from the W129 registered B band tail (refusal facts "
            "SEED_REGISTRY 68_500 t19_phantom_p1 + 68_501 "
            "perpetual_n4_b1, D-20261002-05 pin past-hit restart "
            "semantics, hops=1)")
        _arith_b130_refused = set(range(68_401, 68_601))
        assert _arith_b130_refused & reg_ints == {68_500, 68_501}, \\
            "W130 B refusal face: exactly t19_phantom_p1 + perpetual_n4_b1"
        arith_b130 = set(range(68_502, 68_702))
        assert not (arith_b130 & reg_ints), \\
            "W130 B first-clean window must be CLEAN (hops=1 ADMIT face)"'''
assert face.count(old_b) == 1, "face: B refusal block needle"
face = face.replace(old_b, new_b)

# --- 0c. band facts comment: plain arithmetic -> past-hit restart (W130 facts) ---
old_facts = '''# band facts (law sec.4 W130 row, r734): A = the arithmetic
        # continuation from the registered W129 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the arithmetic continuation from the registered W129
        # B tail (CLEAN hops=0 both windows; B side already past
        # the cny_window_p1=68_000 refusal point of the W129 window
        # family; cross-window convergence with the r733 W129
        # gate-tail W130+ projection).'''
new_facts = '''# band facts (law sec.4 W130 row, r735): A = the arithmetic
        # continuation from the registered W129 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the first-clean past-hit restart window after the
        # REFUSED arithmetic continuation 68_401..68_600 from the
        # registered W129 B tail (refusal facts SEED_REGISTRY
        # 68_500 t19_phantom_p1 + 68_501 perpetual_n4_b1, hops=1,
        # D-20261002-05 pin past-hit restart semantics;
        # cross-window convergence with the r734 W129 gate-tail
        # W130+ projection).'''
assert face.count(old_facts) == 1, "face: band-facts comment needle"
face = face.replace(old_facts, new_facts)

# --- 0d. specific needles FIRST (counts verified against the W129 face text;
#     the parity block added-row reference pf.N1_BANDS[129] must NOT be
#     touched by the wave-config drift needle, so parity runs LAST) ---
specific = [
    # long receipt/seat needles FIRST (substring-order law)
    ("_r734bma_w129_band_gate.py", "_r735bma_w130_band_gate.py", 1),
    ("MSG-2026-10-05-1627-bma-w129-seat", "MSG-2026-10-05-1658-bma-w130-seat", 1),
    ("bm-a r733 freeze 26ce3f5d6", "bm-a r734 freeze 5e8d140ef", 1),
    ("to origin 3575842b2 BEFORE this freeze, r565 law (payload\n"
     "    #     = seat MSG + W129 finalize products + probe + probe\n"
     "    #     receipt; deletion-set EMPTY; first push raced origin\n"
     "    #     forward 10 commits = r524 behind-signal (bm-b r735 +\n"
     "    #     bm-c r555 same-window wave), merge-mode 18-UU canonical\n"
     "    #     resolver closeout, delivery 735eaa0ac)",
     "to origin 02e151b0a BEFORE this freeze, r565 law (payload\n"
     "    #     = seat MSG + pre-seat probe + probe receipt;\n"
     "    #     deletion-set EMPTY; zero-UU clean push, behind 0 at\n"
     "    #     fetch -- no race this window)", 1),
    ("W129 finalize one-pass bm-a r734", "W129 finalize one-pass bm-a r735", 1),
    ("= W129 bm-a r734 one-pass", "= W129 bm-a r735 one-pass", 1),
    ("net chain head 677,611", "net chain head 679,811", 2),
    ("K=279,520", "K=281,720", 1),
    ("ONE HUNDRED-AND-NINETEENTH", "ONE HUNDRED-AND-TWENTIETH", 1),
    ("forty-fifth", "forty-sixth", 1),
    ("rows 44 + candidate", "rows 45 + candidate", 1),
    ("rows 118 + candidate", "rows 119 + candidate", 1),
    ("(r734 bm-a freeze", "(r735 bm-a freeze", 1),
    ("below 129 composes", "below 130 composes", 1),
    ("== 301_004 == 301_003 + 1", "== 303_004 == 303_003 + 1", 1),
    ("set(range(301_004, 303_004))", "set(range(303_004, 305_004))", 1),
    ("WAVE_CONFIGS[129]", "WAVE_CONFIGS[130]", 4),
    ("pf.N1_BANDS[129]", "pf.N1_BANDS[130]", 3),
    ("_set_wave(129)", "_set_wave(130)", 1),
    ("if w < 129", "if w < 130", 3),
    ("range(17, 129)", "range(17, 130)", 1),
    ("range(16, 129)", "range(16, 130)", 1),
    ("w129_a", "w130_a", 8), ("w129_b", "w130_b", 8),  # 9th raw hit = "_r734bma_w129_band_gate.py" substring, consumed by the receipt needle above (substring-order law),
    ("arith_a129", "arith_a130", 2),  # arith_b130 handled inside the B-block replacement
    ("n3r1_used129", "n3r1_used130", 3),
    ("n1w129", "n1w130", 2), ("n1_w129", "n1_w130", 2),
]
face = rep(face, specific, "face")

# --- 0e-2. registered row parity block shift LAST (W125..W128 -> W126..W129) ---
# NOTE post-0a blanket: rows 125/126/127 comments unchanged (W125/W126/W127
# not in the shift set); the row-128 comment shifted W128->W129 (r733 face).
old_parity = '''assert pf.N1_BANDS[125] == {"a": (293_004, 295_003),
                                    "b_exit": (67_201, 67_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W125 row parity drift (r307; bm-a r730)"
        assert pf.N1_BANDS[126] == {"a": (295_004, 297_003),
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
            "registered W129 row parity drift (r307; bm-a r733)"'''
new_parity = '''assert pf.N1_BANDS[126] == {"a": (295_004, 297_003),
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
            "registered W128 row parity drift (r307; bm-a r733)"
        assert pf.N1_BANDS[129] == {"a": (301_004, 303_003),
                                    "b_exit": (68_201, 68_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W129 row parity drift (r307; bm-a r734)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w130_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W130 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 130 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '130: {"a": (303_004, 305_003)' in pf_src:
    print("pf: row 130 already present (idempotent skip)")
else:
    w129_row = '''    129: {"a": (301_004, 303_003), "b_exit": (68_201, 68_400),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w129_row) == 1, "pf: W129 row + closing brace needle"
    w130_block = '''    129: {"a": (301_004, 303_003), "b_exit": (68_201, 68_400),
         "engine_owner": "bm-a"},
    # W130 (bm-a r735 freeze, seat MSG-2026-10-05-1658-bma-w130-seat
    # pushed to origin 02e151b0a pre-freeze r565 law; band gate ADMIT
    # results/_r735bma_w130_band_gate.json: A arithmetic continuation
    # 303_003+1 -> 303_004..305_003 CLEAN hops=0; B first-clean
    # past-hit restart window after the REFUSED arithmetic
    # continuation 68_401..68_600 from the registered W129 B tail
    # 68_400+1 (refusal facts SEED_REGISTRY 68_500 t19_phantom_p1 +
    # 68_501 perpetual_n4_b1, D-20261002-05 pin past-hit restart
    # semantics, hops=1 -> 68_502..68_701); dual-window derive parity
    # with pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster
    # 95_000..95_003 + cross-face probe points 95_004/95_006 +
    # lfc/options actuals + N2/N4/N2-W15 probe points.
    # W131+ projection (gate-derived r735): A 305_004..307_003
    # CLEAN hops=0; B 68_702..68_901 CLEAN hops=0 (next freezer
    # must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W130 bands were never assigned).
    130: {"a": (303_004, 305_003), "b_exit": (68_502, 68_701),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w129_row, w130_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 130 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[130] after entry 129 ---
if '"batch": "PERPETUAL-N1-W130"' in n1:
    print("n1: WAVE_CONFIGS[130] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w129", "out_name": "n1_w129_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W129 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w129", "out_name": "n1_w129_results.json",
                            "engine_owner": "bm-a"},
                       130: {"batch": "PERPETUAL-N1-W130",
                            "prereg": ("research/PERPETUAL_N1_W130_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-TWENTIETH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 119 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W129 row bm-a r734 freeze "
                                       "5e8d140ef, SINGLE STATE zero seat gap W2..W129 all "
                                       "registered; W129 finalize landed same-window r735, ledger "
                                       "head 679,811, merged pool K=281,720; seat published=reserved "
                                       "MSG-2026-10-05-1658-bma-w130-seat PUSHED to origin 02e151b0a "
                                       "BEFORE this freeze per r565 early-visibility law (payload = "
                                       "seat MSG + pre-seat probe + probe receipt; deletion-set EMPTY; "
                                       "zero-UU clean push, behind 0 at fetch -- no race this window); "
                                       "pre-seat probe and freeze-window band-gate runs derive "
                                       "identical, no fork face), "
                                       "engine_owner=bm-a, wave 130: "
                                       "A = arithmetic continuation from the registered W129 A tail "
                                       "(303_004..305_003 CLEAN hops=0) + B = first-clean past-hit "
                                       "restart window after the REFUSED arithmetic continuation "
                                       "68_401..68_600 from the registered W129 B tail (68_502..68_701 "
                                       "hops=1; refusal identity machine-disclosed: SEED_REGISTRY "
                                       "68_500 t19_phantom_p1 + 68_501 perpetual_n4_b1, "
                                       "D-20261002-05 pin past-hit restart semantics; cross-window "
                                       "convergence with the r734 W129 gate-tail W130+ projection "
                                       "re-derived; ADMIT receipt results/_r735bma_w130_band_gate.py; "
                                       "W131+ projection per this window gate: A 305_004..307_003 "
                                       "CLEAN / B 68_702..68_901 CLEAN both hops=0; W1..W129 "
                                       "finalize ALL LANDED (W129 finalize one-pass bm-a r735, §7 "
                                       "backfill same commit; net chain head 679,811, merged pool "
                                       "K=281,720) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED "
                                       "r307 always on)"),
                            "a_seed_base": 303_004,        # law sec.4 W130 A: 303_004..305_003 (arithmetic continuation from the registered W129 A tail)
                            "b_exit_seed_base": 68_502,   # law sec.4 W130 B: 68_502..68_701 (first-clean past-hit restart after the REFUSED 68_401..68_600, refusal identity t19_phantom_p1 + perpetual_n4_b1, hops=1)
                            "shard_subdir": "n1_w130", "out_name": "n1_w130_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[130] inserted")

# --- 2b. materializer face insertion after the W129 face end ---
if "_set_wave(130)" in n1:
    print("n1: W130 materializer face already present (idempotent skip)")
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
    print("n1: W130 materializer face inserted")

# --- 2c. selftest prose face after the W129 prose ---
if 'law sec.4 W130 row, r735 bm-a] ' in n1:
    print("n1: W130 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W129 row, r734 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W129 row, r734 bm-a] "
          "+ W130 materializer face [same guard set, dep=W17..W129 outputs "
          "ALL PRESENT (landed net chain head 679,811 = W129 bm-a r735 "
          "one-pass, §7 backfill same commit; K=281,720 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-TWENTIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 119 + candidate) bm-a's forty-sixth owned "
          "claim per machine-derive (engine_owner==bm-a rows 45 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 130 = first "
          "FREE number after the REGISTERED W129 row bm-a r734 freeze "
          "5e8d140ef, SINGLE STATE zero seat gap W2..W129 all registered; "
          "seat published=reserved MSG-2026-10-05-1658-bma-w130-seat "
          "pushed to origin 02e151b0a BEFORE this freeze, r565 law "
          "(payload = seat MSG + pre-seat probe + probe receipt, "
          "deletion-set EMPTY; zero-UU clean push, behind 0 at fetch -- "
          "no race this window), A = ARITHMETIC CONTINUATION from the "
          "registered W129 A tail (303_004..305_003 CLEAN hops=0) + "
          "B = FIRST-CLEAN PAST-HIT RESTART window after the REFUSED "
          "arithmetic continuation 68_401..68_600 from the registered "
          "W129 B tail (68_502..68_701 hops=1; refusal identity "
          "machine-disclosed: SEED_REGISTRY 68_500 t19_phantom_p1 + "
          "68_501 perpetual_n4_b1, D-20261002-05 pin past-hit restart "
          "semantics; cross-window convergence with the r734 W129 "
          "gate-tail W130+ projection re-derived; ADMIT receipt "
          "results/_r735bma_w130_band_gate.py; W131+ projection per "
          "this window gate: A 305_004..307_003 CLEAN / B 68_702..68_901 "
          "CLEAN both hops=0) disclosed for the next freezer; not a "
          "free pick -- R250), law sec.4 "
          "W130 row, r735 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W130 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
