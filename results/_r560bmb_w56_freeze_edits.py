# -*- coding: utf-8 -*-
"""r560 bm-b: W56 freeze landing edits (INSERT-ONLY, count-asserted).

Lands the W56 registration faces AFTER the last registered row (55) --
never at a fixed positional anchor (the bm-a r559 W54-freeze
anchor-replace clobber lesson, r519-family 6th occurrence):
  1. pf.py      N1_BANDS[56] comment + entry   (insert after 55 entry)
  2. n1.py      WAVE_CONFIGS[56] entry         (insert after 55 entry)
  3. n1.py      selftest W56 materializer leg  (transform of the W55 leg:
     bands 155_004..157_003 / 47_201..47_400, zero-skip arithmetic
     continuation, declared-face block REMOVED -- W54/W55 covered by the
     prior-wave registry loop; set assertion extends to 55)
  4. n1.py      selftest summary segment (print-only descriptive)
Byte-safe LF splicing; every anchor must be found EXACTLY ONCE.
The canon md row lands separately AFTER the gate ADMIT re-run supplies
the machine-derived W57+ projection line.
"""
import sys

PF = "scripts/perpetual_faces.py"
N1 = "scripts/perpetual_faces_n1.py"


def die(msg):
    print(f"FREEZE-EDIT-FAIL: {msg}")
    sys.exit(1)


def rep1(hay: bytes, old: bytes, new: bytes, what: str):
    c = hay.count(old)
    if c != 1:
        die(f"{what}: expected 1 occurrence, found {c}")
    return hay.replace(old, new)


def main() -> int:
    # ---------- 1. pf.py N1_BANDS[56] ----------
    cur = open(PF, "rb").read()
    if b'56: {"a": (155_004, 157_003)' in cur:
        print("pf: N1_BANDS[56] already present (idempotent skip)")
    else:
        block = (
            b"    # r560 bm-b freeze: wave 56 = first FREE number after the\n"
            b"    # registered W55 row (W55 registration union-repaired the\n"
            b"    # same round after the bm-a r559 W54-freeze anchor-replace\n"
            b"    # clobber -- r519-family 6th occurrence; this registration\n"
            b"    # consumes the repaired registry face). BOTH SIDES\n"
            b"    # ARITHMETIC CONTINUATION from the W55 tail, no skip:\n"
            b"    # A 155_004..157_003 (= W55 A end 155_003 + 1) and\n"
            b"    # B 47_201..47_400 (= W55 B end 47_200 + 1) -- both\n"
            b"    # windows CLEAN == the W55 row W56+ WARNING projections\n"
            b"    # (machine re-derived at freeze per r535 law). ADMIT\n"
            b"    # receipt at prereg time\n"
            b"    # (results/_r560bmb_w56_band_gate.py vs the 53-row\n"
            b"    # pre-W56 registered table + live SEED_REGISTRY values +\n"
            b"    # probe cluster 95_000..95_003 r335 discovery leg +\n"
            b"    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529\n"
            b"    # mandatory leg; origin slot vacancy machine-checked).\n"
            b"    # NOT a re-pick (R250: W56 bands were never assigned).\n"
            b"    56: {\"a\": (155_004, 157_003), \"b_exit\": (47_201, 47_400),\n"
            b"         \"engine_owner\": \"bm-b\"},\n"
        )
        anchor = (
            b"    55: {\"a\": (153_004, 155_003), \"b_exit\": (47_001, 47_200),\n"
            b"         \"engine_owner\": \"bm-b\"},\n}"
        )
        cur = rep1(cur, anchor, anchor[:-1] + b"\n" + block + b"}",
                   "pf W55 entry + dict close")
        open(PF, "wb").write(cur)
        print("pf: N1_BANDS[56] inserted after 55")

    # ---------- 2. n1.py WAVE_CONFIGS[56] ----------
    cur = open(N1, "rb").read()
    if b"56: {\"batch\": \"PERPETUAL-N1-W56\"" in cur:
        print("n1: WAVE_CONFIGS[56] already present (idempotent skip)")
    else:
        block = (
            b"                       # FORTY-FIFTH ENGINE-OWNED WAVE (r560 bm-b freeze):\n"
            b"                       # bm-b's SEVENTEENTH owned claim (sixteen\n"
            b"                       # delivered incl. W55 burned 12/12 the same\n"
            b"                       # window with products delivered to origin\n"
            b"                       # r310 gate, finalize queued behind the\n"
            b"                       # W53->W54->W55 predecessor chain\n"
            b"                       # FAIL-CLOSED r307); wave 56 = first FREE\n"
            b"                       # number after the registered W55 row (W55\n"
            b"                       # registration union-repaired the same round\n"
            b"                       # after the bm-a W54-freeze anchor-replace\n"
            b"                       # clobber -- r519-family 6th occurrence).\n"
            b"                       # BOTH SIDES ARITHMETIC CONTINUATION from\n"
            b"                       # the W55 tail no skip: A 155_004..157_003\n"
            b"                       # (= W55 A end 155_003 + 1) and B\n"
            b"                       # 47_201..47_400 (= W55 B end 47_200 + 1),\n"
            b"                       # both CLEAN machine-derived per the W55\n"
            b"                       # row W56+ WARNING; ADMIT receipt\n"
            b"                       # results/_r560bmb_w56_band_gate.py. NOT a\n"
            b"                       # re-pick (R250: W56 bands were never\n"
            b"                       # assigned).\n"
            b"                       56: {\"batch\": \"PERPETUAL-N1-W56\",\n"
            b"                            \"prereg\": (\"research/PERPETUAL_N1_W56_PREREG.md (wave-level frozen \"\n"
            b"                                        \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
            b"                                        \"new seed bands only; FORTY-FIFTH ENGINE-OWNED WAVE, \"\n"
            b"                                        \"own-series continuation per O-20261001-2355 sec.2 \"\n"
            b"                                        \"(first-free-number law over the registered W55 row), \"\n"
            b"                                        \"engine_owner=bm-b, wave 56 BOTH SIDES ARITHMETIC \"\n"
            b"                                        \"CONTINUATION no skip (A 155_004..157_003, B \"\n"
            b"                                        \"47_201..47_400); upstream W53/W54/W55 finalizes \"\n"
            b"                                        \"NOT landed at this freeze = three in-flight chain \"\n"
            b"                                        \"seats honest note, finalize merge loop derives the \"\n"
            b"                                        \"wave set from registry keys at run time and stays \"\n"
            b"                                        \"FAIL-CLOSED on any not-yet-finalized upstream seat, \"\n"
            b"                                        \"r307 two-state law)\"),\n"
            b"                            \"a_seed_base\": 155_004,        # law sec.4 W56 A: 155_004..157_003 (arithmetic continuation)\n"
            b"                            \"b_exit_seed_base\": 47_201,     # law sec.4 W56 B: 47_201..47_400 (arithmetic continuation)\n"
            b"                            \"shard_subdir\": \"n1_w56\", \"out_name\": \"n1_w56_results.json\",\n"
            b"                            \"engine_owner\": \"bm-b\"},\n"
        )
        anchor = b"                       }\nPREREG = WAVE_CONFIGS[2][\"prereg\"]"
        cur = rep1(cur, anchor,
                   block + b"                       }\nPREREG = WAVE_CONFIGS[2][\"prereg\"]",
                   "n1 WAVE_CONFIGS close + PREREG")
        open(N1, "wb").write(cur)
        print("n1: WAVE_CONFIGS[56] inserted after 55")

    # ---------- 3. n1.py selftest W56 materializer leg ----------
    cur = open(N1, "rb").read()
    if b"# --- W56 materializer face" in cur:
        print("n1: W56 materializer leg already present (idempotent skip)")
    else:
        s = cur.find(b"    # --- W55 materializer face")
        if s < 0:
            die("W55 materializer leg not found (prerequisite)")
        fin = b"    finally:\n        _set_wave(2)\n"
        e = cur.find(fin, s)
        if e < 0:
            die("W55 leg finally not found")
        e += len(fin)
        leg = cur[s:e]

        # 3a. comment + _set_wave header wholesale
        hs = leg.find(b"    _set_wave(55)\n")
        if hs < 0:
            die("W55 leg _set_wave(55) not found")
        new_head = (
            b"    # --- W56 materializer face (r560 bm-b freeze, own-series law\n"
            b"    #     under CEO de-throttle order O-20261001-2355 sec.2):\n"
            b"    #     bm-b's SEVENTEENTH owned claim (sixteen delivered incl.\n"
            b"    #     W55 burned 12/12 the same window, products delivered to\n"
            b"    #     origin r310 gate; W53/W54/W55 finalizes = the three\n"
            b"    #     in-flight upstream seats at this freeze, finalize merge\n"
            b"    #     loop FAIL-CLOSED at run time per r307 two-state law).\n"
            b"    #     BOTH SIDES ARITHMETIC CONTINUATION from the W55 tail\n"
            b"    #     no skip (A 155_004..157_003 / B 47_201..47_400, both\n"
            b"    #     CLEAN == the W55 row W56+ WARNING projection machine\n"
            b"    #     re-derived; ADMIT receipt\n"
            b"    #     results/_r560bmb_w56_band_gate.py; not a re-pick --\n"
            b"    #     R250: W56 bands were never assigned) --\n"
            b"    _set_wave(56)\n"
        )
        leg = leg[:leg.find(b"    # --- W55 materializer face")] + new_head + \
            leg[hs + len(b"    _set_wave(55)\n"):]

        # 3b. declared-face block removal (W54 covered by prior-wave loop)
        ds = leg.find(b"        # bm-a PUBLISHED W54 declaration disjointness leg")
        if ds < 0:
            die("W55 leg declared-face block not found")
        de_marker = b'            "W55 bands hit the bm-a declared W54 bands (published=reserved " \\\n' \
                    b'            "r518-1, MSG-0615 addendum)"\n'
        de = leg.find(de_marker, ds)
        if de < 0:
            die("W55 leg declared-face block end not found")
        de += len(de_marker)
        leg = leg[:ds] + leg[de:]

        # 3c. mechanical renames (count-asserted)
        leg = rep1(leg, b"WAVE_CONFIGS[55][\"a_seed_base\"] == pf.N1_BANDS[55][\"a\"][0]",
                   b"WAVE_CONFIGS[56][\"a_seed_base\"] == pf.N1_BANDS[56][\"a\"][0]",
                   "a_seed mirror")
        leg = rep1(leg, b"WAVE_CONFIGS[55][\"b_exit_seed_base\"] == \\\n            pf.N1_BANDS[55][\"b_exit\"][0]",
                   b"WAVE_CONFIGS[56][\"b_exit_seed_base\"] == \\\n            pf.N1_BANDS[56][\"b_exit\"][0]",
                   "b_seed mirror")
        leg = rep1(leg, b"WAVE_CONFIGS[55].get(\"engine_owner\") == \\\n            pf.N1_BANDS[55].get(\"engine_owner\")",
                   b"WAVE_CONFIGS[56].get(\"engine_owner\") == \\\n            pf.N1_BANDS[56].get(\"engine_owner\")",
                   "owner mirror")
        leg = rep1(leg, b'"W55 A band drift vs law mirror"', b'"W56 A band drift vs law mirror"', "A drift msg")
        leg = rep1(leg, b'"W55 B band drift vs law mirror"', b'"W56 B band drift vs law mirror"', "B drift msg")
        leg = rep1(leg, b'"W55 engine_owner drift (law mirror parity)"', b'"W56 engine_owner drift (law mirror parity)"', "owner msg")
        n = leg.count(b"w55_a")
        if n < 3:
            die(f"w55_a count {n} < 3")
        leg = leg.replace(b"w55_a", b"w56_a")
        n = leg.count(b"w55_b")
        if n < 3:
            die(f"w55_b count {n} < 3")
        leg = leg.replace(b"w55_b", b"w56_b")
        leg = rep1(leg, b'"W55 A/B band overlap"', b'"W56 A/B band overlap"', "overlap msg")
        leg = rep1(leg, b'"W55 hits SEED_REGISTRY"', b'"W56 hits SEED_REGISTRY"', "registry msg")
        leg = rep1(leg, b'f"W55 {nm} hits v1"', b'f"W56 {nm} hits v1"', "v1 msg")
        leg = rep1(leg, b'f"W55 {nm} hits W1"', b'f"W56 {nm} hits W1"', "w1 msg")
        leg = rep1(leg, b'f"W55 {nm} hits probe seeds"', b'f"W56 {nm} hits probe seeds"', "probe msg")
        # prior-wave loops: 2 sites (band disjointness + shard-dir collision)
        c = leg.count(b"                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54):")
        if c != 2:
            die(f"prior-wave loop count {c} != 2")
        leg = leg.replace(b"                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54):",
                          b"                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54,\n                      55):")
        leg = rep1(leg, b'f"W55 A hits W{wprev}"', b'f"W56 A hits W{wprev}"', "A hits msg")
        leg = rep1(leg, b'f"W55 B hits W{wprev}"', b'f"W56 B hits W{wprev}"', "B hits msg")
        leg = rep1(leg, b"n3r1_used55 = set(range(70_000, 70_006))", b"n3r1_used56 = set(range(70_000, 70_006))", "n3r1 name")
        leg = rep1(leg, b"assert not (w56_a & n3r1_used55) and not (w56_b & n3r1_used55), \\\n            \"W55 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"",
                   b"assert not (w56_a & n3r1_used56) and not (w56_b & n3r1_used56), \\\n            \"W56 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"",
                   "n3r1 assert")
        leg = rep1(leg, b'"W55 bands must clear the lfc actual draw range"', b'"W56 bands must clear the lfc actual draw range"', "lfc msg")
        leg = rep1(leg, b'"W55 bands must clear the options_wave2 actual draw range"', b'"W56 bands must clear the options_wave2 actual draw range"', "options msg")
        # band facts wholesale (two asserts)
        old_facts = (
            b"        # band facts (law sec.4 W55 row, r559): skip faces machine-pinned --\n"
            b"        # A starts at the bm-a declared W54 A end + 1 (published-tail\n"
            b"        # continuation, W19-A re-base family); B starts at the\n"
            b"        # SEED_REGISTRY point xlib_synth_null_b=47_000 + 1 (W51-B\n"
            b"        # re-base family).\n"
            b"        assert WAVE_CONFIGS[55][\"a_seed_base\"] == 153_004 == 153_003 + 1, \\\n"
            b"            \"W55 A must start at the bm-a declared W54 A end + 1 \" \\\n"
            b"            \"(published=reserved r518-1 skip face, window \" \\\n"
            b"            \"153_004..155_003 first-clean machine-derived)\"\n"
            b"        assert WAVE_CONFIGS[55][\"b_exit_seed_base\"] == 47_001 == 47_000 + 1, \\\n"
            b"            \"W55 B must start at the SEED_REGISTRY point \" \\\n"
            b"            \"xlib_synth_null_b=47_000 + 1 (window 47_001..47_200 \" \\\n"
            b"            \"first-clean machine-derived, W51-B re-base family)\"\n"
        )
        new_facts = (
            b"        # band facts (law sec.4 W56 row, r560): BOTH SIDES\n"
            b"        # ARITHMETIC CONTINUATION (A 155_004 = W55 A end\n"
            b"        # 155_003 + 1; B 47_201 = W55 B end 47_200 + 1, both\n"
            b"        # windows CLEAN -- no skip family).\n"
            b"        assert WAVE_CONFIGS[56][\"a_seed_base\"] == 155_004 == 155_003 + 1, \\\n"
            b"            \"W56 A must start at the registered W55 A end + 1 \" \\\n"
            b"            \"(arithmetic continuation window 155_004..157_003 CLEAN -- \" \\\n"
            b"            \"no skip family)\"\n"
            b"        assert WAVE_CONFIGS[56][\"b_exit_seed_base\"] == 47_201 == 47_200 + 1, \\\n"
            b"            \"W56 B must start at the registered W55 B end + 1 \" \\\n"
            b"            \"(arithmetic continuation window 47_201..47_400 CLEAN -- \" \\\n"
            b"            \"no skip family)\"\n"
        )
        leg = rep1(leg, old_facts, new_facts, "band facts block")
        leg = rep1(leg, b"_entry_shard_of(0, 12) == (\"PERPETUAL-N1-W55-SHARD-0\",\n                                          \"n1w55-0of12\"), \"W55 entry identity\"",
                   b"_entry_shard_of(0, 12) == (\"PERPETUAL-N1-W56-SHARD-0\",\n                                          \"n1w56-0of12\"), \"W56 entry identity\"", "shard0 identity")
        leg = rep1(leg, b"_entry_shard_of(11, 12) == (\"PERPETUAL-N1-W55-SHARD-11\",\n                                          \"n1w55-11of12\")",
                   b"_entry_shard_of(11, 12) == (\"PERPETUAL-N1-W56-SHARD-11\",\n                                          \"n1w56-11of12\")", "shard11 identity")
        leg = rep1(leg, b'SHARD_DIR.endswith("n1_w55") and OUT.endswith(\n            "n1_w55_results.json"), "W55 path drift"',
                   b'SHARD_DIR.endswith("n1_w56") and OUT.endswith(\n            "n1_w56_results.json"), "W56 path drift"', "path drift")
        leg = rep1(leg, b'f"W55 shard dir collides with W{wprev}"', b'f"W56 shard dir collides with W{wprev}"', "dir collide msg")
        # per-wave prereg check
        leg = rep1(leg, b'"research", "PERPETUAL_N1_W55_PREREG.md")), \\\n            "W55 per-wave prereg missing (materializer requirement)"',
                   b'"research", "PERPETUAL_N1_W56_PREREG.md")), \\\n            "W56 per-wave prereg missing (materializer requirement)"', "prereg check")
        # deps comment + loop message wholesale
        old_deps = (
            b"        # W55 finalize cumulative deps: W17..W52 outputs ALL PRESENT\n"
            b"        # (static landed seats incl. the bm-c r351 triple finalize\n"
            b"        # W50/W51/W52, chain head 478,948); W53 = REGISTERED with\n"
            b"        # finalize NOT landed (in-flight); W54 = DECLARED by bm-a\n"
            b"        # (unregistered at this freeze -- its output CANNOT be pinned;\n"
            b"        # the finalize merge loop derives the wave set from registry\n"
            b"        # keys at run time and stays FAIL-CLOSED on any\n"
            b"        # not-yet-finalized upstream seat, r307 two-state law).\n"
        )
        new_deps = (
            b"        # W56 finalize cumulative deps: W17..W52 outputs ALL PRESENT\n"
            b"        # (static landed seats incl. the bm-c r351 triple finalize\n"
            b"        # W50/W51/W52, chain head 478,948); W53/W54/W55 =\n"
            b"        # REGISTERED with finalizes NOT landed at this freeze\n"
            b"        # (three in-flight chain seats; the finalize merge loop\n"
            b"        # derives the wave set from registry keys at run time and\n"
            b"        # stays FAIL-CLOSED on any not-yet-finalized upstream\n"
            b"        # seat, r307 two-state law).\n"
        )
        leg = rep1(leg, old_deps, new_deps, "deps comment")
        leg = rep1(leg, b'f"W55 finalize cumulative dep (W{_depw} output) missing"',
                   b'f"W56 finalize cumulative dep (W{_depw} output) missing"', "dep loop msg")
        # finalize wave-set derivation face
        old_set = (
            b"        # finalize wave-set derivation face (r511 derive law): prior-wave\n"
            b"        # set derives from registry keys below 55 (no 15; incl. 48..53 --\n"
            b"        # all registered; W54 declared-but-unregistered at this freeze,\n"
            b"        # FAIL-CLOSED at run time when bm-a registers it).\n"
            b"        assert sorted(w for w in WAVE_CONFIGS if w < 55) == \\\n"
            b"            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n"
            b"             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,\n"
            b"             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,\n"
            b"             50, 51, 52, 53, 54], \\\n"
            b"            \"W55 prior-wave set must derive from registry keys (no 15, \" \\\n"
            b"            \"incl. 48..54; W54 registered by bm-a r559 at the pinned \" \\\n"
            b"            \"declared bands -- r307 two-state parity)\"\n"
        )
        new_set = (
            b"        # finalize wave-set derivation face (r511 derive law): prior-wave\n"
            b"        # set derives from registry keys below 56 (no 15; incl.\n"
            b"        # 48..55 -- all registered, W53/W54/W55 finalizes in flight,\n"
            b"        # FAIL-CLOSED at run time).\n"
            b"        assert sorted(w for w in WAVE_CONFIGS if w < 56) == \\\n"
            b"            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,\n"
            b"             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,\n"
            b"             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,\n"
            b"             50, 51, 52, 53, 54, 55], \\\n"
            b"            \"W56 prior-wave set must derive from registry keys (no 15, \" \\\n"
            b"            \"incl. 48..55; three in-flight finalize seats honest note)\"\n"
        )
        leg = rep1(leg, old_set, new_set, "set derivation block")

        # insert the transformed leg after the W55 leg, before T-141 marker
        anchor = b"\n    # --- T-141 s2 lane face"
        c = cur.count(anchor)
        if c != 1:
            die(f"T-141 marker count {c} != 1")
        ins_at = cur.find(anchor)
        cur = cur[:ins_at] + b"\n" + leg + cur[ins_at:]
        open(N1, "wb").write(cur)
        print("n1: W56 materializer leg inserted after W55 leg (transformed)")

    # ---------- 4. n1.py selftest summary segment ----------
    cur = open(N1, "rb").read()
    if b"+ W56 materializer face" in cur:
        print("n1: W56 summary segment already present (idempotent skip)")
    else:
        seg = (
            b"          \"+ W56 materializer face [same guard set, dep=W17..W52 \"\n"
            b"          \"outputs ALL PRESENT (chain head 478,948 post the bm-c \"\n"
            b"          \"r351 triple finalize); W53/W54/W55 registered with \"\n"
            b"          \"finalizes NOT landed at this freeze = THREE in-flight \"\n"
            b"          \"chain seats, finalize merge loop stays FAIL-CLOSED at \"\n"
            b"          \"run time per r307 two-state law), FORTY-FIFTH \"\n"
            b"          \"ENGINE-OWNED WAVE bm-b's seventeenth owned claim \"\n"
            b"          \"engine_owner=bm-b per engine de-throttle law \"\n"
            b"          \"O-20261001-2355 sec.2 own-continuous-series (wave 56 = \"\n"
            b"          \"first FREE number after the registered W55 row, W55 \"\n"
            b"          \"registration union-repaired this round after the bm-a \"\n"
            b"          \"W54-freeze anchor-replace clobber -- r519-family 6th \"\n"
            b"          \"occurrence), BOTH SIDES ARITHMETIC CONTINUATION from \"\n"
            b"          \"the W55 tail no skip (A 155_004..157_003 / B \"\n"
            b"          \"47_201..47_400 both CLEAN machine-derived per the W55 \"\n"
            b"          \"row W56+ WARNING; ADMIT receipt \"\n"
            b"          \"results/_r560bmb_w56_band_gate.py; not a free pick -- \"\n"
            b"          \"R250), N3-R1 used-seed leg, probe-seed cluster leg, \"\n"
            b"          \"law sec.4 W56 row, r560 bm-b] \"\n"
        )
        anchor = b"          \"+ T-141 s2 \""
        cur = rep1(cur, anchor, seg + anchor, "summary T-141 marker")
        open(N1, "wb").write(cur)
        print("n1: W56 summary segment inserted")

    print("FREEZE-EDITS-OK: 4 faces landed (canon md row pending gate ADMIT)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
