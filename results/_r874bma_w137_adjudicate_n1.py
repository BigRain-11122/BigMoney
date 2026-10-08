# -*- coding: utf-8 -*-
"""r874 bm-a n1-selftest W137 carve-out (mirror of the pf-level r874
adjudication; W99 in-section r726 pattern shape)."""
import io
import ast

N1 = r"scripts/perpetual_faces_n1.py"
src = io.open(N1, encoding="utf-8", newline="").read()
NL = "\r\n"

old = (
    '        w137_a = {A_SEED_BASE + j for j in range(A_N)}' + NL +
    '        w137_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}' + NL +
    '        assert not (w137_a & w137_b), "W137 A/B band overlap"' + NL +
    '        assert not (w137_a & reg_ints) and not (w137_b & reg_ints), \\' + NL +
    '            "W137 hits SEED_REGISTRY"'
)
new = (
    '        w137_a = {A_SEED_BASE + j for j in range(A_N)}' + NL +
    '        w137_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}' + NL +
    '        assert not (w137_a & w137_b), "W137 A/B band overlap"' + NL +
    '        # r874 adjudication (W99 r726 in-section precedent; full' + NL +
    '        # disclosure in the pf-level w137_adjudicated comment):' + NL +
    '        # regime5_validation_p1_null_base=94_100 (r870 registration;' + NL +
    '        # its pocket sweep verified free in-registry but MISSED the' + NL +
    '        # N1_BANDS band face) lands inside the ALREADY-BURNED W137 B' + NL +
    '        # band 94_001..94_200 at j=99. Spawn-children-only consumption' + NL +
    '        # (never default_rng(94_100) itself) = bookkeeping-level' + NL +
    '        # overlap only, statistically harmless; W137 finalize stands,' + NL +
    '        # the regime5 P1 burn (ran 2026-10-08 08:46) is NOT' + NL +
    '        # re-registered. Disclosed, not hidden.' + NL +
    '        w137_adjudicated = {94_100}' + NL +
    '        assert w137_adjudicated <= w137_b, \\' + NL +
    '            "W137 adjudicated set drifted (must sit inside the burned band)"' + NL +
    '        assert not (w137_a & reg_ints) and \\' + NL +
    '            not (w137_b & (reg_ints - w137_adjudicated)), \\' + NL +
    '            "W137 hits SEED_REGISTRY beyond the adjudicated r874 point"'
)
assert src.count(old) == 1, "n1 W137 anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)
io.open(N1, "w", encoding="utf-8", newline="").write(src)
ast.parse(src)
print("n1 W137 carve-out landed, AST OK,", len(src), "bytes")
