# -*- coding: utf-8 -*-
"""r734 bm-a W129 registry insertion: N1_BANDS row 129 (perpetual_faces.py)
+ WAVE_CONFIGS[129] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r733 _r733bma_w128_registry_insert.py verbatim + W129 facts
(both sides = arithmetic continuation CLEAN hops=0; B side already past the
cny_window_p1=68_000 refusal point of the W128 window family)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 0. transform the extracted W128 face -> W129 face ============
face = io.open(r".codely-cli\scratch_w128_face.txt", encoding="utf-8").read()

# --- 0a. blanket wave-number shift FIRST (uppercase; then verified needles) ---
n_w128 = face.count("W128"); n_w127 = face.count("W127")
face = face.replace("W128", "W129")
face = face.replace("W127", "W128")
assert face.count("W129") == n_w128 and face.count("W128") == n_w127, \
    "blanket count check"

# --- 0b. B-block: refusal semantics -> plain arithmetic (W129 B is CLEAN) ---
old_b = '''assert WAVE_CONFIGS[128]["b_exit_seed_base"] == 68_001, (
            "W129 B must be the first-clean past-hit restart window "
            "after the REFUSED arithmetic continuation 67_801..68_000 "
            "(refusal fact cny_window_p1=68_000 upper-edge endpoint, "
            "D-20261002-05 pin edge-endpoint family both-readings "
            "identical)")
        _arith_b128_refused = set(range(67_801, 68_001))
        assert _arith_b128_refused & reg_ints == {68_000}, \\
            "W129 B arithmetic window refusal face: exactly cny_window_p1"
        arith_b128 = set(range(68_001, 68_201))
        assert not (arith_b128 & reg_ints), \\
            "W129 B first-clean window must be CLEAN (hops=1 ADMIT face)"'''
new_b = '''assert WAVE_CONFIGS[129]["b_exit_seed_base"] == 68_201 == 68_200 + 1, (
            "W129 B must be the arithmetic continuation past the W128 "
            "registered B band tail")
        arith_b129 = set(range(68_201, 68_401))
        assert not (arith_b129 & reg_ints), \\
            "W129 B window must be CLEAN (arithmetic ADMIT face, hops=0)"'''
assert face.count(old_b) == 1, "face: B refusal block needle"
face = face.replace(old_b, new_b)

# --- 0c. band facts comment: refusal -> plain arithmetic (W129 facts) ---
old_facts = '''# band facts (law sec.4 W129 row, r733): A = the arithmetic
        # continuation from the registered W128 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the first-clean past-hit restart window after the
        # REFUSED arithmetic continuation 67_801..68_000 (refusal
        # fact cny_window_p1=68_000 upper-edge endpoint, hops=1,
        # D-20261002-05 pin edge-endpoint family both-readings
        # identical; cross-window convergence with the r732 W128
        # gate-tail W129+ projection).'''
new_facts = '''# band facts (law sec.4 W129 row, r734): A = the arithmetic
        # continuation from the registered W128 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the arithmetic continuation from the registered W128
        # B tail (CLEAN hops=0 both windows; B side already past
        # the cny_window_p1=68_000 refusal point of the W128 window
        # family; cross-window convergence with the r733 W128
        # gate-tail W129+ projection).'''
assert face.count(old_facts) == 1, "face: band-facts comment needle"
face = face.replace(old_facts, new_facts)

# --- 0d. specific needles FIRST (counts verified against the W128 face text;
#     the parity block added-row reference pf.N1_BANDS[128] must NOT be
#     touched by the wave-config drift needle, so parity runs LAST) ---
specific = [
    # long receipt/seat needles FIRST (substring-order law)
    ("_r733bma_w128_band_gate.py", "_r734bma_w129_band_gate.py", 1),
    ("MSG-2026-10-05-1612-bma-w128-seat", "MSG-2026-10-05-1627-bma-w129-seat", 1),
    ("bm-a r732 freeze f70372381", "bm-a r733 freeze 26ce3f5d6", 1),
    ("to origin 0826a8e65 BEFORE this freeze, r565 law (payload\n"
     "    #     = seat MSG + probe + probe receipt; deletion-set EMPTY;\n"
     "    #     first push raced origin forward 3 commits = r524\n"
     "    #     behind-signal, merge-mode zero-UU closeout, delivery\n"
     "    #     99e292c9d)",
     "to origin 3575842b2 BEFORE this freeze, r565 law (payload\n"
     "    #     = seat MSG + W128 finalize products + probe + probe\n"
     "    #     receipt; deletion-set EMPTY; first push raced origin\n"
     "    #     forward 10 commits = r524 behind-signal (bm-b r735 +\n"
     "    #     bm-c r555 same-window wave), merge-mode 18-UU canonical\n"
     "    #     resolver closeout, delivery 735eaa0ac)", 1),
    ("wave 126 = first free number", "wave 129 = first free number", 1),
    ("W128 finalize one-pass bm-a r733", "W128 finalize one-pass bm-a r734", 1),
    ("= W128 bm-a r733 one-pass", "= W128 bm-a r734 one-pass", 1),
    ("net chain head 675,411", "net chain head 677,611", 2),
    ("K=277,320", "K=279,520", 1),
    ("ONE HUNDRED-AND-EIGHTEENTH", "ONE HUNDRED-AND-NINETEENTH", 1),
    ("forty-fourth", "forty-fifth", 1),
    ("rows 43 + candidate", "rows 44 + candidate", 1),
    ("rows 117 + candidate", "rows 118 + candidate", 1),
    ("(r733 bm-a freeze", "(r734 bm-a freeze", 1),
    ("below 126 composes", "below 129 composes", 1),
    ("== 299_004 == 299_003 + 1", "== 301_004 == 301_003 + 1", 1),
    ("set(range(299_004, 301_004))", "set(range(301_004, 303_004))", 1),
    ("WAVE_CONFIGS[128]", "WAVE_CONFIGS[129]", 4),
    ("pf.N1_BANDS[128]", "pf.N1_BANDS[129]", 3),
    ("_set_wave(128)", "_set_wave(129)", 1),
    ("if w < 128", "if w < 129", 3),
    ("range(17, 128)", "range(17, 129)", 1),
    ("range(16, 128)", "range(16, 129)", 1),
    ("w128_a", "w129_a", 8), ("w128_b", "w129_b", 8),
    ("arith_a128", "arith_a129", 2),  # arith_b129 handled inside the B-block replacement
    ("n3r1_used128", "n3r1_used129", 3),
    ("n1w128", "n1w129", 2), ("n1_w128", "n1_w129", 2),
]
face = rep(face, specific, "face")

# --- 0e-2. registered row parity block shift LAST (W124..W127 -> W125..W128) ---
old_parity = '''assert pf.N1_BANDS[124] == {"a": (291_004, 293_003),
                                    "b_exit": (66_601, 66_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W124 row parity drift (r307; bm-a r729)"
        assert pf.N1_BANDS[125] == {"a": (293_004, 295_003),
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
            "registered W128 row parity drift (r307; bm-a r732)"'''
new_parity = '''assert pf.N1_BANDS[125] == {"a": (293_004, 295_003),
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
            "registered W128 row parity drift (r307; bm-a r733)"'''
assert face.count(old_parity) == 1, "face: row-parity block needle"
face = face.replace(old_parity, new_parity)

io.open(r".codely-cli\scratch_w129_face.txt", "w", encoding="utf-8", newline="\n").write(face)
print("face: W129 block transformed")

# ============ 1. perpetual_faces.py N1_BANDS row 129 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '129: {"a": (301_004, 303_003)' in pf_src:
    print("pf: row 129 already present (idempotent skip)")
else:
    w128_row = '''    128: {"a": (299_004, 301_003), "b_exit": (68_001, 68_200),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w128_row) == 1, "pf: W128 row + closing brace needle"
    w129_block = '''    128: {"a": (299_004, 301_003), "b_exit": (68_001, 68_200),
         "engine_owner": "bm-a"},
    # W129 (bm-a r734 freeze, seat MSG-2026-10-05-1627-bma-w129-seat
    # pushed to origin 3575842b2 pre-freeze r565 law; band gate ADMIT
    # results/_r734bma_w129_band_gate.json: A arithmetic continuation
    # 301_003+1 -> 301_004..303_003 CLEAN hops=0; B arithmetic
    # continuation 68_200+1 -> 68_201..68_400 CLEAN hops=0 (B side
    # already past the cny_window_p1=68_000 refusal point of the W128
    # window family); dual-window derive parity with pre-seat probe;
    # scan face = SEED_REGISTRY 187 int values + v1/W1 ext bands +
    # N3-R1 used-seed band + probe cluster 95_000..95_003 + cross-face
    # probe points 95_004/95_006 + lfc/options actuals + N2/N4/N2-W15
    # probe points.
    # W130+ projection (gate-derived r734): A 303_004..305_003
    # CLEAN hops=0; B first-clean 68_502..68_701 hops=1 (B arithmetic
    # window 68_401..68_600 carries a refusal point -> past-hit
    # restart; next freezer must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W129 bands were never assigned).
    129: {"a": (301_004, 303_003), "b_exit": (68_201, 68_400),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w128_row, w129_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 129 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[129] after entry 128 ---
if '"batch": "PERPETUAL-N1-W129"' in n1:
    print("n1: WAVE_CONFIGS[129] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w128", "out_name": "n1_w128_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W128 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w128", "out_name": "n1_w128_results.json",
                            "engine_owner": "bm-a"},
                       129: {"batch": "PERPETUAL-N1-W129",
                            "prereg": ("research/PERPETUAL_N1_W129_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-NINETEENTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 118 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W128 row bm-a r733 freeze "
                                       "26ce3f5d6, SINGLE STATE zero seat gap W2..W128 all "
                                       "registered; W128 finalize landed same-window r734, ledger "
                                       "head 677,611, merged pool K=279,520; seat published=reserved "
                                       "MSG-2026-10-05-1627-bma-w129-seat PUSHED to origin 3575842b2 "
                                       "BEFORE this freeze per r565 early-visibility law (delivery "
                                       "merge 735eaa0ac; first push raced origin forward 10 commits "
                                       "= r524 behind-signal bm-b r735 + bm-c r555 same-window wave, "
                                       "merge-mode 18-UU canonical resolver closeout); pre-seat "
                                       "probe and freeze-window band-gate runs derive identical, "
                                       "no fork face), "
                                       "engine_owner=bm-a, wave 129: "
                                       "A = arithmetic continuation from the registered W128 A tail "
                                       "(301_004..303_003 CLEAN hops=0) + B = arithmetic "
                                       "continuation from the registered W128 B tail "
                                       "(68_201..68_400 CLEAN hops=0; B side already past the "
                                       "cny_window_p1=68_000 refusal point of the W128 window "
                                       "family; cross-window convergence with the r733 W128 "
                                       "gate-tail W129+ projection re-derived; ADMIT receipt "
                                       "results/_r734bma_w129_band_gate.py; W130+ projection per "
                                       "this window gate: A 303_004..305_003 CLEAN / B first-clean "
                                       "68_502..68_701 hops=1 past-hit restart (refusal identity "
                                       "machine-disclosed at the W130 freeze window); W1..W128 "
                                       "finalize ALL LANDED (W128 finalize one-pass bm-a r734, §7 "
                                       "backfill same commit; net chain head 677,611, merged pool "
                                       "K=279,520) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED "
                                       "r307 always on)"),
                            "a_seed_base": 301_004,        # law sec.4 W129 A: 301_004..303_003 (arithmetic continuation from the registered W128 A tail)
                            "b_exit_seed_base": 68_201,   # law sec.4 W129 B: 68_201..68_400 (arithmetic continuation from the registered W128 B tail, CLEAN hops=0)
                            "shard_subdir": "n1_w129", "out_name": "n1_w129_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[129] inserted")

# --- 2b. materializer face insertion after the W128 face end ---
if "_set_wave(129)" in n1:
    print("n1: W129 materializer face already present (idempotent skip)")
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
    print("n1: W129 materializer face inserted")

# --- 2c. selftest prose face after the W128 prose ---
if 'law sec.4 W129 row, r734 bm-a] ' in n1:
    print("n1: W129 prose face already present (idempotent skip)")
else:
    prose_anchor = 'W128 row, r733 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''W128 row, r733 bm-a] "
          "+ W129 materializer face [same guard set, dep=W17..W128 outputs "
          "ALL PRESENT (landed net chain head 677,611 = W128 bm-a r734 "
          "one-pass, §7 backfill same commit; K=279,520 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-NINETEENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 118 + candidate) bm-a's forty-fifth owned "
          "claim per machine-derive (engine_owner==bm-a rows 44 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 129 = first "
          "FREE number after the REGISTERED W128 row bm-a r733 freeze "
          "26ce3f5d6, SINGLE STATE zero seat gap W2..W128 all registered; "
          "seat published=reserved MSG-2026-10-05-1627-bma-w129-seat "
          "pushed to origin 3575842b2 BEFORE this freeze, r565 law "
          "(delivery merge 735eaa0ac; first push raced origin forward 10 "
          "commits = r524 behind-signal, merge-mode 18-UU canonical "
          "resolver closeout; payload = seat MSG + W128 finalize products "
          "+ probe + probe receipt, deletion-set EMPTY), A = ARITHMETIC "
          "CONTINUATION from the registered W128 A tail (301_004..303_003 "
          "CLEAN hops=0) + B = ARITHMETIC CONTINUATION from the "
          "registered W128 B tail (68_201..68_400 CLEAN hops=0; B side "
          "already past the cny_window_p1=68_000 refusal point of the "
          "W128 window family; cross-window convergence with the r733 "
          "W128 gate-tail W129+ projection re-derived; ADMIT receipt "
          "results/_r734bma_w129_band_gate.py; W130+ projection per "
          "this window gate: A 303_004..305_003 CLEAN / B first-clean "
          "68_502..68_701 hops=1 past-hit restart, refusal identity "
          "machine-disclosed at the W130 freeze window) disclosed "
          "for the next freezer; not a free pick -- R250), law sec.4 "
          "W129 row, r734 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W129 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
