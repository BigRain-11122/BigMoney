# -*- coding: utf-8 -*-
"""r586 bm-a W104-into-W105 union resolver (same-window double-freeze).

Origin landed bm-c W105 (551c2fd81/f2db133c5/565a6b254) which skipped
the published-but-unregistered W104 seat (bm-a MSG-20261002-1712).
My W104 freeze (035528fee) sits on the pre-W105 base. This script
constructs the union of the 3 shared files: origin blob as base (bm-c
W105 content verbatim-preserved), my W104 blocks inserted at their
anchored positions, PLUS one r531-1 minimal amendment: the bm-c W105
materializer-leg static wave-set assert was written for the W104-ABSENT
state (range(16, 104)); with W104 registered the set becomes
range(16, 105) -- amended with disclosure per r531-1/r541 precedent
(W48/W32 dep-pin auto-join lineage). Bytes-in == bytes-out audited.
"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def origin_blob(path):
    r = subprocess.run(["git", "show", "origin/main:" + path],
                       capture_output=True)
    assert r.returncode == 0, f"origin blob missing: {path}"
    return r.stdout.decode("utf-8")

def mine_blob(path):
    # blob space (LF) per r373 autocrlf dual-space law: my HEAD commit
    # carries the same content as the working tree (no post-commit
    # edits); git show HEAD returns the LF blob so both sides of the
    # union live in the same (LF) space.
    r = subprocess.run(["git", "show", "HEAD:" + path],
                       capture_output=True)
    assert r.returncode == 0, f"HEAD blob missing: {path}"
    return r.stdout.decode("utf-8")

def write_bytes(path, text):
    # working-tree space is CRLF (autocrlf=true); git add normalizes
    # back to the LF blob on commit (r373 law).
    with open(path, "wb") as f:
        f.write(text.replace("\n", "\r\n").encode("utf-8"))

report = []

# ---------- 1) scripts/perpetual_faces.py (N1_BANDS) -------------------------
org = origin_blob("scripts/perpetual_faces.py")
mine = mine_blob("scripts/perpetual_faces.py")
# my block: from my W104 comment start to just before the closing "}" of N1_BANDS
i0 = mine.index("    # W104 (r586 bm-a freeze):")
i1 = mine.index('    104: {"a": (251_004, 253_003), "b_exit": (59_601, 59_800),')
i2 = mine.index('"engine_owner": "bm-a"},', i1) + len('"engine_owner": "bm-a"},')
my_block = mine[i0:i2] + "\n"
assert my_block.count("104: {") == 1 and "bm-a" in my_block
# anchor in origin: right after the W103 row (their W105 comment start)
w103_row_end = '    103: {"a": (249_004, 251_003), "b_exit": (59_401, 59_600),\n         "engine_owner": "bm-b"},\n'
assert org.count(w103_row_end) == 1
a0 = org.index(w103_row_end) + len(w103_row_end)
assert org[a0:a0+60].startswith("    # NINETY-FOURTH ENGINE-OWNED WAVE"), org[a0:a0+60]
union = org[:a0] + my_block + org[a0:]
# audit: both rows present, disjoint, W103 before W104 before W105
assert union.index('103: {"a": (249_004') < union.index('104: {"a": (251_004') < union.index('105: {"a": (253_004')
assert '104: {"a": (251_004, 253_003), "b_exit": (59_601, 59_800),\n         "engine_owner": "bm-a"},' in union
write_bytes("scripts/perpetual_faces.py", union)
report.append("perpetual_faces.py: W104 block inserted before W105 comment; both rows + W103 ordering verified")

# ---------- 2) scripts/perpetual_faces_n1.py (3 insertions + 1 amend) -------
org = origin_blob("scripts/perpetual_faces_n1.py")
mine = mine_blob("scripts/perpetual_faces_n1.py")

# 2a) my WAVE_CONFIGS entry: between my W103 entry end and the dict close
j0 = mine.index('104: {"batch": "PERPETUAL-N1-W104",')
j1 = mine.index('"engine_owner": "bm-a"},', j0) + len('"engine_owner": "bm-a"},')
my_cfg = mine[j0:j1]
assert my_cfg.count('PERPETUAL-N1-W104') == 1
# insert into origin before their 105 entry
k0 = org.index('105: {"batch": "PERPETUAL-N1-W105",')
union = org[:k0] + my_cfg + "\n" + org[k0:]
assert union.index('"batch": "PERPETUAL-N1-W103"') < union.index('"batch": "PERPETUAL-N1-W104"') < union.index('"batch": "PERPETUAL-N1-W105"')

# 2b) my materializer leg: from my leg comment to my leg's closing finally
m0 = mine.index("    # --- W104 materializer face (r586 bm-a freeze, own-series law")
m1 = mine.index("    # --- T-141 s2 lane face", m0)
my_leg = mine[m0:m1]
assert my_leg.count("_set_wave(104)") >= 1 and my_leg.count("W104") > 10
# insert into origin before their W105 leg comment
n0 = union.index("    # --- W105 materializer face")
union = union[:n0] + my_leg + union[n0:]
assert union.index("W104 materializer face") < union.index("W105 materializer face")

# 2c) my print text: "+ W104 materializer face [...] r586 bm-a] " block
p0 = mine.index('"+ W104 materializer face [same guard set, dep=W17..W99 "')
p1 = mine.index('"+ T-141 s2 "', p0)
my_print = mine[p0:p1]
assert "r586 bm-a] " in my_print and "W104 materializer face" in my_print
q0 = union.index('"+ W105 materializer face')
union = union[:q0] + my_print + union[q0:]
assert union.index("W104 materializer face [same guard set") < union.index("W105 materializer face [same guard set")

# 2d) r531-1 minimal amendment: their W105 static wave-set assert was
# written for the W104-ABSENT state; with W104 registered the set is
# range(16, 105). Amend + disclose (r531-1/r541 precedent).
old_assert = (
    'assert sorted(w for w in WAVE_CONFIGS if w < 105) == \\\n'
    '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n'
    '            [w for w in range(16, 104)], \\\n'
    '            "W105 prior-wave set must derive from registry keys (no 15; " \\\n'
    '            "W2..W103 registered single state; W104 seat-gap honest note)"')
new_assert = (
    'assert sorted(w for w in WAVE_CONFIGS if w < 105) == \\\n'
    '            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n'
    '            [w for w in range(16, 105)], \\\n'
    '            "W105 prior-wave set must derive from registry keys (no 15; " \\\n'
    '            "W2..W104 registered single state; W104 seat-gap AMENDED to " \\\n'
    '            "registered by the bm-a r586 union per r531-1 minimal-amend)"')
assert union.count(old_assert) == 1, "W105 static wave-set assert anchor not found verbatim"
union = union.replace(old_assert, new_assert)
# also amend the preceding comment line (stale W2..W103 prose, same r531 law)
old_cmt = (
    "        # registered wave below 105 composes; wave 15 excluded by\n"
    "        # design; W104 seat-published unregistered honest note (W2..W103\n"
    "        # all registered -- W104 gap disclosed, r519/r578 precedent).")
new_cmt = (
    "        # registered wave below 105 composes; wave 15 excluded by\n"
    "        # design; W104 was seat-published unregistered at the bm-c r376\n"
    "        # freeze (r519/r578 precedent) and is REGISTERED by the bm-a\n"
    "        # r586 union -- set amended to W2..W104 per r531-1 law.")
assert union.count(old_cmt) == 1, "W105 wave-set comment anchor not found verbatim"
union = union.replace(old_cmt, new_cmt)
write_bytes("scripts/perpetual_faces_n1.py", union)
report.append("perpetual_faces_n1.py: W104 WAVE_CONFIGS entry + W104 materializer leg + W104 print text inserted; bm-c W105 static wave-set assert range(16,104)->(16,105) r531-1 minimal amendment with disclosure")

# ---------- 3) research/PERPETUAL_FACES.md (law table row) --------------------
org = origin_blob("research/PERPETUAL_FACES.md")
mine = mine_blob("research/PERPETUAL_FACES.md")
r0 = mine.index("- N1 波104（r586 bm-a 冻·prereg 时展行）：")
r1 = mine.index("\n", r0) + 1
my_row = mine[r0:r1]
assert "251_004..253_003" in my_row and "59_601..59_800" in my_row
# anchor: their W105 row in origin
s0 = org.index("- N1 波105（r376 bm-c 冻·prereg 时展行）：")
union = org[:s0] + my_row + org[s0:]
assert union.index("N1 波103（") < union.index("N1 波104（") < union.index("N1 波105（")
write_bytes("research/PERPETUAL_FACES.md", union)
report.append("PERPETUAL_FACES.md: W104 law row inserted between W103 and W105 rows; ordering verified")

print("UNION RESOLVED (3 files):")
for r_ in report:
    print(" -", r_)
print("OK")
