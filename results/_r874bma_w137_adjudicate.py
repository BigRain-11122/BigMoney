# -*- coding: utf-8 -*-
"""r874 bm-a W137 adjudicated-point carve-out (r726/r727 W99 precedent,
mirror shape): SEED_REGISTRY regime5_validation_p1_null_base=94_100
(r870 REGIME5_VALIDATION_P1 freeze; its 94_001..94_999 pocket sweep
verified free in-registry but MISSED the N1_BANDS band face) lands
inside the ALREADY-BURNED W137 B band 94_001..94_200 at j=99. Single
point carve-out + disclosed comment; zero history rewritten."""
import io

PF = r"scripts/perpetual_faces.py"
src = io.open(PF, encoding="utf-8", newline="").read()
NL = "\r\n"

# ---- edit 1: W137 adjudicated block after the W99 block ----
old1 = (
    '    w99_adjudicated = {58_700}' + NL +
    '    w99_b_probe = set(range(N1_BANDS[99]["b_exit"][0],' + NL +
    '                            N1_BANDS[99]["b_exit"][1] + 1))' + NL +
    '    assert w99_adjudicated <= w99_b_probe, \\' + NL +
    '        "W99 adjudicated set drifted (must sit inside the burned band)"' + NL +
    '    used = []'
)
new1 = (
    '    w99_adjudicated = {58_700}' + NL +
    '    w99_b_probe = set(range(N1_BANDS[99]["b_exit"][0],' + NL +
    '                            N1_BANDS[99]["b_exit"][1] + 1))' + NL +
    '    assert w99_adjudicated <= w99_b_probe, \\' + NL +
    '        "W99 adjudicated set drifted (must sit inside the burned band)"' + NL +
    '    # ADJUDICATED EXCEPTION 2 (bm-a r874, W99 r726/r727 precedent):' + NL +
    '    # SEED_REGISTRY regime5_validation_p1_null_base=94_100 was' + NL +
    '    # registered LATER (bm-a r870 REGIME5_VALIDATION_P1 prereg' + NL +
    '    # freeze; its 94_001..94_999 pocket sweep verified free' + NL +
    '    # in-registry but MISSED the N1_BANDS band face) and lands' + NL +
    '    # inside the ALREADY-BURNED W137 B band 94_001..94_200 at' + NL +
    '    # j=99. Historical single-point overlap on a burned' + NL +
    '    # measurement face: statistically harmless (the REGIME5 P1' + NL +
    '    # burn consumed only SPAWNED CHILDREN of SeedSequence(94_100)' + NL +
    '    # -- never default_rng(94_100) itself -- so the two consumers' + NL +
    '    # never share an actual stream; the W137 exit draw remains a' + NL +
    '    # valid null draw), W137 finalize results stand un-reopened,' + NL +
    '    # the regime5_validation_p1 batch is NOT re-registered' + NL +
    '    # (registry records what was actually used -- the P1 burn ran' + NL +
    '    # 2026-10-08 08:46 with base 94_100). Future band gates already' + NL +
    '    # treat SEED_REGISTRY live values as refusal points, so no' + NL +
    '    # forward face. Disclosed, not hidden.' + NL +
    '    w137_adjudicated = {94_100}' + NL +
    '    w137_b_probe = set(range(N1_BANDS[137]["b_exit"][0],' + NL +
    '                            N1_BANDS[137]["b_exit"][1] + 1))' + NL +
    '    assert w137_adjudicated <= w137_b_probe, \\' + NL +
    '        "W137 adjudicated set drifted (must sit inside the burned band)"' + NL +
    '    used = []'
)
assert src.count(old1) == 1, "edit1 anchor not unique: %d" % src.count(old1)
src = src.replace(old1, new1, 1)

# ---- edit 2: elif branch in the per-wave loop ----
old2 = (
    '        if w == 99:' + NL +
    '            assert not (band_b & (reg_ints - w99_adjudicated)), \\' + NL +
    '                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r719 point"' + NL +
    '        else:'
)
new2 = (
    '        if w == 99:' + NL +
    '            assert not (band_b & (reg_ints - w99_adjudicated)), \\' + NL +
    '                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r719 point"' + NL +
    '        elif w == 137:' + NL +
    '            assert not (band_b & (reg_ints - w137_adjudicated)), \\' + NL +
    '                f"N1 w{w} hits SEED_REGISTRY beyond the adjudicated r874 point"' + NL +
    '        else:'
)
assert src.count(old2) == 1, "edit2 anchor not unique: %d" % src.count(old2)
src = src.replace(old2, new2, 1)

io.open(PF, "w", encoding="utf-8", newline="").write(src)
import ast
ast.parse(src)
print("W137 adjudication landed: pf selftest carve-out (2 edits), AST OK,",
      len(src), "bytes")
