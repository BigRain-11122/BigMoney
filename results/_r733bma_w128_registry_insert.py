# -*- coding: utf-8 -*-
"""r733 bm-a W128 registry insertion: N1_BANDS row 128 (perpetual_faces.py)
+ WAVE_CONFIGS[128] + materializer face + selftest prose face
(perpetual_faces_n1.py). All insertions needle-asserted; idempotent guards.
Bloodline: r732 _r732bma_w127_registry_insert.py verbatim + W128 facts
(B face = first-clean past-hit restart hops=1, refusal cny_window_p1=68_000)."""
import io

def rep(src, pairs, tag):
    for old, new, expect in pairs:
        n = src.count(old)
        assert n == expect, f"{tag}: needle count={n} expect={expect}: {old[:60]!r}"
        src = src.replace(old, new)
    return src

# ============ 1. perpetual_faces.py N1_BANDS row 128 ============
pf_path = r"scripts\perpetual_faces.py"
pf_src = io.open(pf_path, encoding="utf-8").read()
if '128: {"a": (299_004, 301_003)' in pf_src:
    print("pf: row 128 already present (idempotent skip)")
else:
    w127_row = '''    127: {"a": (297_004, 299_003), "b_exit": (67_601, 67_800),
         "engine_owner": "bm-a"},
}'''
    assert pf_src.count(w127_row) == 1, "pf: W127 row + closing brace needle"
    w128_block = '''    127: {"a": (297_004, 299_003), "b_exit": (67_601, 67_800),
         "engine_owner": "bm-a"},
    # W128 (bm-a r733 freeze, seat MSG-2026-10-05-1612-bma-w128-seat
    # pre-pushed 0826a8e65 r565 law; band gate ADMIT
    # results/_r733bma_w128_band_gate.json: A arithmetic continuation
    # 299_003+1 -> 299_004..301_003 CLEAN hops=0; B arithmetic
    # continuation 67_800+1 -> 67_801..68_000 REFUSED at upper-edge
    # endpoint cny_window_p1=68_000 -> past-hit restart first-clean
    # 68_001..68_200 hops=1 (D-20261002-05 pin edge-endpoint family
    # both-readings identical); dual-window derive parity with
    # pre-seat probe; scan face = SEED_REGISTRY 187 int values +
    # v1/W1 ext bands + N3-R1 used-seed band + probe cluster 95_000..95_003
    # + cross-face probe points 95_004/95_006 + lfc/options actuals +
    # N2/N4/N2-W15 probe points.
    # W129+ projection (gate-derived r733): A 301_004..303_003
    # CLEAN hops=0; B first-clean 68_201..68_400 CLEAN hops=0 (next
    # freezer must re-derive, never transcribe r587 law).
    # NOT a re-pick (R250: W128 bands were never assigned).
    128: {"a": (299_004, 301_003), "b_exit": (68_001, 68_200),
         "engine_owner": "bm-a"},
}'''
    pf_src = pf_src.replace(w127_row, w128_block)
    io.open(pf_path, "w", encoding="utf-8", newline="\n").write(pf_src)
    print("pf: N1_BANDS row 128 inserted")

# ============ 2. perpetual_faces_n1.py ============
n1_path = r"scripts\perpetual_faces_n1.py"
n1 = io.open(n1_path, encoding="utf-8").read()

# --- 2a. WAVE_CONFIGS[128] after entry 127 ---
if '"batch": "PERPETUAL-N1-W128"' in n1:
    print("n1: WAVE_CONFIGS[128] already present (idempotent skip)")
else:
    wc_anchor = '''                            "shard_subdir": "n1_w127", "out_name": "n1_w127_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    assert n1.count(wc_anchor) == 1, "n1: WAVE_CONFIGS W127 entry anchor"
    wc_new = '''                            "shard_subdir": "n1_w127", "out_name": "n1_w127_results.json",
                            "engine_owner": "bm-a"},
                       128: {"batch": "PERPETUAL-N1-W128",
                            "prereg": ("research/PERPETUAL_N1_W128_PREREG.md (wave-level frozen "
                                       "pre-run; design = frozen v1 null calibration verbatim, "
                                       "new seed bands only; ONE HUNDRED-AND-EIGHTEENTH ENGINE-OWNED WAVE "
                                       "BY MACHINE-DERIVE (engine_owner rows 117 + candidate), "
                                       "own-series continuation per O-20261001-2355 sec.2 (first-free-"
                                       "number law after the REGISTERED W127 row bm-a r732 freeze "
                                       "f70372381, SINGLE STATE zero seat gap W2..W127 all "
                                       "registered; W127 finalize landed same-window r733, ledger "
                                       "head 675,411, merged pool K=277,320; seat published=reserved "
                                       "MSG-2026-10-05-1612-bma-w128-seat PUSHED to origin 0826a8e65 "
                                       "BEFORE this freeze per r565 early-visibility law; first "
                                       "push raced origin forward 3 commits = r524 behind-signal, "
                                       "merge-mode zero-UU closeout, delivery 99e292c9d; pre-seat "
                                       "probe and freeze-window band-gate runs derive identical, "
                                       "no fork face; payload = seat MSG + probe + probe receipt, "
                                       "deletion-set EMPTY, rev.A = only published faces), "
                                       "engine_owner=bm-a, wave 128: "
                                       "A = arithmetic continuation from the registered W127 A tail "
                                       "(299_004..301_003 CLEAN hops=0) + B = first-clean past-hit "
                                       "restart from the refused arithmetic continuation window "
                                       "67_801..68_000 (68_001..68_200 hops=1; refusal fact "
                                       "cny_window_p1=68_000 upper-edge endpoint per D-20261002-05 "
                                       "pin edge-endpoint family both-readings identical; "
                                       "cross-window convergence with the r732 W127 gate-tail "
                                       "W128+ projection re-derived; ADMIT receipt "
                                       "results/_r733bma_w128_band_gate.py; W129+ projection per "
                                       "this window gate: A 301_004..303_003 CLEAN / B first-clean "
                                       "68_201..68_400 CLEAN hops=0; W1..W127 "
                                       "finalize ALL LANDED (W127 finalize one-pass bm-a r733, §7 "
                                       "backfill same commit; net chain head 675,411, merged pool "
                                       "K=277,320) -- ZERO in-flight upstream seats, clean finalize "
                                       "chain precondition -- finalize merge loop still derives the "
                                       "wave set from registry keys at run time, FAIL-CLOSED "
                                       "r307 always on)"),
                            "a_seed_base": 299_004,        # law sec.4 W128 A: 299_004..301_003 (arithmetic continuation from the registered W127 A tail)
                            "b_exit_seed_base": 68_001,   # law sec.4 W128 B: 68_001..68_200 (first-clean past-hit restart, refusal cny_window_p1=68_000, hops=1)
                            "shard_subdir": "n1_w128", "out_name": "n1_w128_results.json",
                            "engine_owner": "bm-a"},
                       }'''
    n1 = n1.replace(wc_anchor, wc_new)
    print("n1: WAVE_CONFIGS[128] inserted")

# --- 2b. materializer face: transform the extracted W127 block ---
if "_set_wave(128)" in n1:
    print("n1: W128 materializer face already present (idempotent skip)")
    face = None
else:
    face = io.open(r".codely-cli\scratch_w127_face.txt", encoding="utf-8").read()
    n_w127 = face.count("W127"); n_w126 = face.count("W126")
    face = face.replace("W127", "W128")
    face = face.replace("W126", "W127")
    assert face.count("W128") == n_w127 and face.count("W127") == n_w126, "blanket count check"
    specific = [
        # long receipt/seat needles FIRST (substring-order law)
        ("_r732bma_w128_band_gate.py", "_r733bma_w128_band_gate.py", 1),
        ("MSG-2026-10-05-1548-bma-w128-seat", "MSG-2026-10-05-1612-bma-w128-seat", 1),
        ("bm-a r730 freeze db9da0e92", "bm-a r732 freeze f70372381", 1),
        ("0826a8e65", None, 0),  # placeholder guard: 0826a8e65 not yet in face; skip
        ("bef555332", "0826a8e65", 1),
        ("b78dc4cc4", "99e292c9d", 1),
        ("w128_a", None, 0),
    ]
    # (drop the placeholder guards -- build the real list below)
    specific = [
        ("_r732bma_w127_band_gate.py", "_r733bma_w128_band_gate.py", 1),
        ("MSG-2026-10-05-1548-bma-w127-seat", "MSG-2026-10-05-1612-bma-w128-seat", 1),
        ("bm-a r730 freeze db9da0e92", "bm-a r732 freeze f70372381", 1),
        ("bef555332", "0826a8e65", 1),
        ("b78dc4cc4", "99e292c9d", 1),
        ("w127_a", "w128_a", 8), ("w127_b", "w128_b", 8),
        ("arith_a127", "arith_a128", 2), ("arith_b127", "arith_b128", 2),
        ("n3r1_used127", "n3r1_used128", 3),
        ("n1w127", "n1w128", 2), ("n1_w127", "n1_w128", 2),
        ("W127 finalize one-pass bm-a r732", "W127 finalize one-pass bm-a r733", 1),
        ("= W127 bm-a r732 one-pass", "= W127 bm-a r733 one-pass", 1),
        ("(r732 bm-a freeze", "(r733 bm-a freeze", 1),
        ("law sec.4 W128 row, r732", "law sec.4 W128 row, r733", 1),
        ("ONE HUNDRED-AND-SEVENTEENTH", "ONE HUNDRED-AND-EIGHTEENTH", 1),
        ("forty-third", "forty-fourth", 1),
        ("rows 42 + candidate", "rows 43 + candidate", 1),
        ("rows 116 + candidate", "rows 117 + candidate", 1),
        ("net chain head 673,211", "net chain head 675,411", 2),
        ("K=275,120", "K=277,320", 1),
        ("the r731 W127 gate-tail", "the r732 W127 gate-tail", 1),
        ("== 297_004 == 297_003 + 1", "== 299_004 == 299_003 + 1", 1),
        ("set(range(297_004, 299_004))", "set(range(299_004, 301_004))", 1),
        ("WAVE_CONFIGS[127]", "WAVE_CONFIGS[128]", 5),
        ("pf.N1_BANDS[127]", "pf.N1_BANDS[128]", 3),
        ("_set_wave(127)", "_set_wave(128)", 1),
        ("if w < 127", "if w < 128", 3),
        ("range(17, 127)", "range(17, 128)", 1),
        ("range(16, 127)", "range(16, 128)", 1),
    ]
    face = rep(face, specific, "face")
    # B-face refusal semantics block (band = first-clean past-hit restart hops=1)
    old_b = '''assert WAVE_CONFIGS[128]["b_exit_seed_base"] == 67_601 == 67_600 + 1, (
            "W128 B must be the arithmetic continuation past the W127 "
            "registered B band tail")
        arith_b128 = set(range(67_601, 67_801))
        assert not (arith_b128 & reg_ints), \\
            "W128 B window must be CLEAN (arithmetic ADMIT face, hops=0)"'''
    new_b = '''assert WAVE_CONFIGS[128]["b_exit_seed_base"] == 68_001, (
            "W128 B must be the first-clean past-hit restart window "
            "after the REFUSED arithmetic continuation 67_801..68_000 "
            "(refusal fact cny_window_p1=68_000 upper-edge endpoint, "
            "D-20261002-05 pin edge-endpoint family both-readings "
            "identical)")
        _arith_b128_refused = set(range(67_801, 68_001))
        assert _arith_b128_refused & reg_ints == {68_000}, \\
            "W128 B arithmetic window refusal face: exactly cny_window_p1"
        arith_b128 = set(range(68_001, 68_201))
        assert not (arith_b128 & reg_ints), \\
            "W128 B first-clean window must be CLEAN (hops=1 ADMIT face)"'''
    assert face.count(old_b) == 1, "face: B refusal block needle"
    face = face.replace(old_b, new_b)
    # band facts comment block (B side semantics)
    old_facts = '''# band facts (law sec.4 W128 row, r733): A = the arithmetic
        # continuation from the registered W127 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the arithmetic continuation from the registered W127
        # B tail (CLEAN hops=0, zero refusal points both windows;
        # cross-window convergence with the r732 W127 gate-tail
        # W128+ projection).'''
    new_facts = '''# band facts (law sec.4 W128 row, r733): A = the arithmetic
        # continuation from the registered W127 A tail (CLEAN hops=0
        # at both the pre-seat probe and the freeze-window gate);
        # B = the first-clean past-hit restart window after the
        # REFUSED arithmetic continuation 67_801..68_000 (refusal
        # fact cny_window_p1=68_000 upper-edge endpoint, hops=1,
        # D-20261002-05 pin edge-endpoint family both-readings
        # identical; cross-window convergence with the r732 W127
        # gate-tail W128+ projection).'''
    assert face.count(old_facts) == 1, "face: band-facts comment needle"
    face = face.replace(old_facts, new_facts)
    # registered row parity: shift estate head, add W127 tail row (full block)
    old_parity = '''        assert pf.N1_BANDS[123] == {"a": (289_004, 291_003),
                                    "b_exit": (66_401, 66_600),
                                    "engine_owner": "bm-a"}, \\
            "registered W123 row parity drift (r307; bm-a r728)"
        assert pf.N1_BANDS[124] == {"a": (291_004, 293_003),
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
            "registered W127 row parity drift (r307; bm-a r731)"'''
    new_parity = '''        assert pf.N1_BANDS[124] == {"a": (291_004, 293_003),
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
            "registered W127 row parity drift (r307; bm-a r732)"'''
    assert face.count(old_parity) == 1, "face: row-parity block needle"
    face = face.replace(old_parity, new_parity)
    io.open(r".codely-cli\scratch_w128_face.txt", "w", encoding="utf-8", newline="\n").write(face)
    print("n1: W128 face block transformed")

    # --- 2c. insert face after W127 block end, before T-141 s2 lane face ---
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
    print("n1: W128 materializer face inserted")

# --- 2d. selftest prose face after the W127 prose ---
if 'law sec.4 W128 row, r733 bm-a] ' in n1:
    print("n1: W128 prose face already present (idempotent skip)")
else:
    prose_anchor = 'r732 bm-a] "\n          "+ T-141 s2 "'
    assert n1.count(prose_anchor) == 1, "n1: prose anchor"
    prose_new = '''r732 bm-a] "
          "+ W128 materializer face [same guard set, dep=W17..W127 outputs "
          "ALL PRESENT (landed net chain head 675,411 = W127 bm-a r733 "
          "one-pass, §7 backfill same commit; K=277,320 merged pool; ZERO "
          "in-flight upstream seats, clean precondition freeze window), "
          "ONE HUNDRED-AND-EIGHTEENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "
          "(engine_owner rows 117 + candidate) bm-a's forty-fourth owned "
          "claim per machine-derive (engine_owner==bm-a rows 43 + "
          "candidate), engine_owner=bm-a per engine de-throttle law "
          "O-20261001-2355 sec.2 own-continuous-series (wave 128 = first "
          "FREE number after the REGISTERED W127 row bm-a r732 freeze "
          "f70372381, SINGLE STATE zero seat gap W2..W127 all registered; "
          "seat published=reserved MSG-2026-10-05-1612-bma-w128-seat "
          "pushed to origin 0826a8e65 BEFORE this freeze, r565 law; "
          "first push raced origin forward 3 commits = r524 "
          "behind-signal, merge-mode zero-UU closeout, delivery "
          "99e292c9d; payload = seat MSG + probe + probe receipt "
          "deletion-set EMPTY, rev.A = only published faces), A = "
          "ARITHMETIC CONTINUATION from the registered W127 A tail "
          "(299_004..301_003 CLEAN hops=0) + B = first-clean past-hit "
          "restart window (68_001..68_200 hops=1, refusal fact "
          "cny_window_p1=68_000 upper-edge endpoint, D-20261002-05 pin "
          "edge-endpoint family both-readings identical; cross-window "
          "convergence with the r732 W127 gate-tail W128+ projection "
          "re-derived; ADMIT receipt results/_r733bma_w128_band_gate.py; "
          "W129+ projection per this window gate: A 301_004..303_003 "
          "CLEAN / B first-clean 68_201..68_400 CLEAN hops=0) disclosed "
          "for the next freezer; not a free pick -- R250), law sec.4 "
          "W128 row, r733 bm-a] "
          "+ T-141 s2 "'''
    n1 = n1.replace(prose_anchor, prose_new)
    print("n1: W128 prose face inserted")

io.open(n1_path, "w", encoding="utf-8", newline="\n").write(n1)
print("ALL INSERTIONS DONE")
