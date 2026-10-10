# -*- coding: utf-8 -*-
"""r957 bm-a: W139/W140 SEED_REGISTRY adjudication (O-20261010-1906
request, r874 mirror with a CORRECTED argument path).

O-1906 option A presumed spawn-children-only consumption; live-source
verification found DIFFERENT facts, disclosed honestly:
- W139/94_500 (thermo_overlay_p1_nulls, bm-a r938 T-181 slice-1):
  thermo L283 consumes np.random.default_rng(94500+i) ITSELF (one
  integers(1,T) phase shift per null seed); the W139 B engine exit
  draw (n1 L7729) consumes default_rng(B_EXIT_SEED_BASE+j) itself ->
  same-family same-seed = SHARED STREAM at j=99. Harmless via
  disjoint injection faces (phase shifts enter the thermo-timeline
  null law; the engine draw enters the factor-cell exit axis; the
  two data faces never meet and neither inference reads the other).
- W140/94_700 (lhb_thermo_ic_p1_nulls, bm-a E5 slice-2): lhb L267
  uses Python stdlib random.Random(94700+i) = MT19937; the W140
  engine uses numpy default_rng = PCG64 -> DIFFERENT RNG families,
  same seed integer yields entirely different streams -> the two
  consumers never share an actual stream (stronger isolation than
  the r874 spawn-children argument).

Both are single-point bookkeeping overlaps on ALREADY-BURNED
measurement bands; W139/W140 finalize results stand un-reopened;
neither nulls batch is re-registered (registry records actual use).
Disclosed, not hidden.
"""
import io, ast

N1 = r"scripts/perpetual_faces_n1.py"
PF = r"scripts/perpetual_faces.py"
NL = "\r\n"

# ---------- n1 layer: 4 in-section carve-outs (r874 n1 mirror) ----------
src = io.open(N1, encoding="utf-8", newline="").read()

old = (
    '        assert not (w139_a & w139_b), "W139 A/B band overlap"' + NL +
    '        assert not (w139_a & reg_ints) and not (w139_b & reg_ints), \\' + NL +
    '            "W139 hits SEED_REGISTRY"'
)
new = (
    '        assert not (w139_a & w139_b), "W139 A/B band overlap"' + NL +
    '        # r957 adjudication (r874 mirror, O-20261010-1906; full' + NL +
    '        # disclosure in the pf-level w139_adjudicated comment):' + NL +
    '        # thermo_overlay_p1_nulls base=94_500 (bm-a r938 T-181' + NL +
    '        # slice-1 registration; its pocket sweep verified' + NL +
    '        # in-registry disjointness but MISSED the N1_BANDS band' + NL +
    '        # face) lands inside the ALREADY-BURNED W139 B band' + NL +
    '        # 94_401..94_600 at j=99. CORRECTED argument (NOT the r874' + NL +
    '        # spawn-children path): BOTH consumers consume' + NL +
    '        # default_rng(94_500) itself -- thermo draws one' + NL +
    '        # integers(1,T) phase shift per null seed, the W139 engine' + NL +
    '        # exit draw consumes the same PCG64 stream. Harmless via' + NL +
    '        # DISJOINT INJECTION FACES: the phase shifts enter the' + NL +
    '        # 1997-2026 thermo-timeline null law, the engine draw enters' + NL +
    '        # the factor-cell exit axis -- two data faces that never' + NL +
    '        # meet, and neither inference reads the other. W139' + NL +
    '        # finalize stands, the thermo batch is NOT re-registered.' + NL +
    '        # Disclosed, not hidden.' + NL +
    '        w139_adjudicated = {94_500}' + NL +
    '        assert w139_adjudicated <= w139_b, \\' + NL +
    '            "W139 adjudicated set drifted (must sit inside the burned band)"' + NL +
    '        assert not (w139_a & reg_ints) and \\' + NL +
    '            not (w139_b & (reg_ints - w139_adjudicated)), \\' + NL +
    '            "W139 hits SEED_REGISTRY beyond the adjudicated r957 point"'
)
assert src.count(old) == 1, "n1 W139-main anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)

old = (
    '        arith_b139 = set(range(94_401, 94_601))' + NL +
    '        assert not (arith_b139 & reg_ints), \\' + NL +
    '            "W139 B window must be CLEAN (arithmetic ADMIT face, hops=0)"'
)
new = (
    '        arith_b139 = set(range(94_401, 94_601))' + NL +
    '        # r957 adjudication (see the w139_adjudicated disclosure above):' + NL +
    '        assert not (arith_b139 & (reg_ints - w139_adjudicated)), \\' + NL +
    '            "W139 B window must be CLEAN beyond the adjudicated r957 point (arithmetic ADMIT face)"'
)
assert src.count(old) == 1, "n1 W139-arith anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)

old = (
    '        assert not (w140_a & w140_b), "W140 A/B band overlap"' + NL +
    '        assert not (w140_a & reg_ints) and not (w140_b & reg_ints), \\' + NL +
    '            "W140 hits SEED_REGISTRY"'
)
new = (
    '        assert not (w140_a & w140_b), "W140 A/B band overlap"' + NL +
    '        # r957 adjudication (r874 mirror, O-20261010-1906; full' + NL +
    '        # disclosure in the pf-level w140_adjudicated comment):' + NL +
    '        # lhb_thermo_ic_p1_nulls base=94_700 (bm-a E5 slice-2' + NL +
    '        # registration; its registration sweep MISSED the N1_BANDS' + NL +
    '        # band face, same miss family as r870/r899) lands inside' + NL +
    '        # the ALREADY-BURNED W140 B band 94_601..94_800 at j=99.' + NL +
    '        # STRONGER than the r874 spawn-children argument: the two' + NL +
    '        # consumers run DIFFERENT RNG algorithm families -- lhb' + NL +
    '        # uses Python stdlib random.Random(94_700+i) (MT19937), the' + NL +
    '        # W140 engine exit draw uses numpy default_rng(94_700+j)' + NL +
    '        # (PCG64) -- the same seed integer produces entirely' + NL +
    '        # different streams, so the two consumers never share an' + NL +
    '        # actual stream. Bookkeeping-level overlap only,' + NL +
    '        # statistically harmless. W140 finalize stands, the lhb' + NL +
    '        # batch is NOT re-registered. Disclosed, not hidden.' + NL +
    '        w140_adjudicated = {94_700}' + NL +
    '        assert w140_adjudicated <= w140_b, \\' + NL +
    '            "W140 adjudicated set drifted (must sit inside the burned band)"' + NL +
    '        assert not (w140_a & reg_ints) and \\' + NL +
    '            not (w140_b & (reg_ints - w140_adjudicated)), \\' + NL +
    '            "W140 hits SEED_REGISTRY beyond the adjudicated r957 point"'
)
assert src.count(old) == 1, "n1 W140-main anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)

old = (
    '        arith_b140 = set(range(94_601, 94_801))' + NL +
    '        assert not (arith_b140 & reg_ints), \\' + NL +
    '            "W140 B window must be CLEAN (arithmetic ADMIT face, hops=0)"'
)
new = (
    '        arith_b140 = set(range(94_601, 94_801))' + NL +
    '        # r957 adjudication (see the w140_adjudicated disclosure above):' + NL +
    '        assert not (arith_b140 & (reg_ints - w140_adjudicated)), \\' + NL +
    '            "W140 B window must be CLEAN beyond the adjudicated r957 point (arithmetic ADMIT face)"'
)
assert src.count(old) == 1, "n1 W140-arith anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)

ast.parse(src)
io.open(N1, "w", encoding="utf-8", newline="").write(src)
print("n1 W139/W140 carve-outs landed, AST OK,", len(src), "bytes")

# ---------- pf layer: definition block + used-loop elif chain ----------
src = io.open(PF, encoding="utf-8", newline="").read()

old = (
    '    w138_adjudicated = {94_300}' + NL +
    '    w138_b_probe = set(range(N1_BANDS[138]["b_exit"][0],' + NL +
    '                            N1_BANDS[138]["b_exit"][1] + 1))' + NL +
    '    assert w138_adjudicated <= w138_b_probe, \\' + NL +
    '        "W138 adjudicated set drifted (must sit inside the burned band)"'
)
new = old + NL + (
    '    # ADJUDICATED EXCEPTION 5 (bm-a r957, O-20261010-1906 request,' + NL +
    '    # r874 precedent family, found red by the W204 five-face freeze' + NL +
    '    # selftest window on origin): SEED_REGISTRY' + NL +
    '    # thermo_overlay_p1_nulls=94_500 was registered LATER (bm-a r938' + NL +
    '    # T-181 slice-1 registration; the registration face verified' + NL +
    '    # in-registry disjointness but MISSED the N1_BANDS band face --' + NL +
    '    # same miss family as the r870/r899 pocket sweeps) and lands' + NL +
    '    # inside the ALREADY-BURNED W139 B band 94_401..94_600 at j=99.' + NL +
    '    # CORRECTED argument (NOT the r874 spawn-children path -- the' + NL +
    '    # thermo runner consumes default_rng(94_500+i) itself, and so' + NL +
    '    # does the W139 engine exit draw at j=99: same-family same-seed' + NL +
    '    # = SHARED PCG64 stream). Harmless via DISJOINT INJECTION FACES:' + NL +
    '    # the thermo null law draws one integers(1,T) phase shift per' + NL +
    '    # null seed into the 1997-2026 thermo timeline; the W139 engine' + NL +
    '    # draw randomizes the factor-cell exit axis -- two data faces' + NL +
    '    # that never meet, and neither statistical inference reads the' + NL +
    '    # other, so no spurious-correlation channel exists. W139' + NL +
    '    # finalize results stand un-reopened, the thermo_overlay_p1' + NL +
    '    # batch is NOT re-registered (registry records what was actually' + NL +
    '    # used -- the thermo burn ran 2026-10-09 with base 94_500).' + NL +
    '    # Future band gates already treat SEED_REGISTRY live values as' + NL +
    '    # refusal points, so no forward face. Disclosed, not hidden.' + NL +
    '    w139_adjudicated = {94_500}' + NL +
    '    w139_b_probe = set(range(N1_BANDS[139]["b_exit"][0],' + NL +
    '                            N1_BANDS[139]["b_exit"][1] + 1))' + NL +
    '    assert w139_adjudicated <= w139_b_probe, \\' + NL +
    '        "W139 adjudicated set drifted (must sit inside the burned band)"' + NL +
    '    # ADJUDICATED EXCEPTION 6 (bm-a r957, same O-20261010-1906' + NL +
    '    # request): SEED_REGISTRY lhb_thermo_ic_p1_nulls=94_700 was' + NL +
    '    # registered LATER (bm-a E5 slice-2 LHB_THERMO_IC_P1' + NL +
    '    # registration; same N1_BANDS miss family) and lands inside the' + NL +
    '    # ALREADY-BURNED W140 B band 94_601..94_800 at j=99. STRONGER' + NL +
    '    # than the r874 spawn-children argument: the two consumers run' + NL +
    '    # DIFFERENT RNG algorithm families -- lhb consumes Python' + NL +
    '    # stdlib random.Random(94_700+i) (MT19937), the W140 engine exit' + NL +
    '    # draw consumes numpy default_rng(94_700+j) (PCG64) -- the same' + NL +
    '    # seed integer produces entirely different streams, so the two' + NL +
    '    # consumers never share an actual stream. Bookkeeping-level' + NL +
    '    # overlap only, statistically harmless; the W140 exit draw' + NL +
    '    # remains a valid null draw. W140 finalize results stand' + NL +
    '    # un-reopened, the lhb_thermo_ic_p1 batch is NOT re-registered.' + NL +
    '    # Future band gates already treat SEED_REGISTRY live values as' + NL +
    '    # refusal points, so no forward face. Disclosed, not hidden.' + NL +
    '    w140_adjudicated = {94_700}' + NL +
    '    w140_b_probe = set(range(N1_BANDS[140]["b_exit"][0],' + NL +
    '                            N1_BANDS[140]["b_exit"][1] + 1))' + NL +
    '    assert w140_adjudicated <= w140_b_probe, \\' + NL +
    '        "W140 adjudicated set drifted (must sit inside the burned band)"'
)
assert src.count(old) == 1, "pf w138-def anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)

old = (
    '        elif w == 138:' + NL +
    '            assert not (band_b & (reg_ints - w138_adjudicated)), \\' + NL +
    '                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r874 point"' + NL +
    '        else:'
)
new = (
    '        elif w == 138:' + NL +
    '            assert not (band_b & (reg_ints - w138_adjudicated)), \\' + NL +
    '                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r874 point"' + NL +
    '        elif w == 139:' + NL +
    '            assert not (band_b & (reg_ints - w139_adjudicated)), \\' + NL +
    '                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r957 point"' + NL +
    '        elif w == 140:' + NL +
    '            assert not (band_b & (reg_ints - w140_adjudicated)), \\' + NL +
    '                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r957 point"' + NL +
    '        else:'
)
assert src.count(old) == 1, "pf used-loop anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)

ast.parse(src)
io.open(PF, "w", encoding="utf-8", newline="").write(src)
print("pf W139/W140 carve-outs landed, AST OK,", len(src), "bytes")
