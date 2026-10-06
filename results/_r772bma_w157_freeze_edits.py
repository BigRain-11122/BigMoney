# -*- coding: utf-8 -*-
"""r772 bm-a W157 freeze edits: four insertions (pf N1_BANDS[157] row +
n1 WAVE_CONFIGS[157] + n1 W157 materializer leg + n1 PASS snippet).
EOL-adaptive (r370 law: files are CRLF-dominant -- blocks written CRLF);
needle count==1 (r745); insert-after-last-registered-row + post-anchor
content checks (r560); anchor = predecessor full lines, no whole-anchor
backfill (r580/r581); AST gate after every edit batch (r580/r581).
Value-map approach at the SOURCE-TEXT level (band strings verified intact
inside string fragments -- entry integrity probe + block probes r772):
digit-free placeholders prevent double-shift; the historical parity chain
(rows W138..W155, r307 pinned constants) is split out VERBATIM and extended
by one W156 row assert; post-map fixups correct the seat-citation chain
(seat leg4 -> seat W157+ projection; r771-sec8 typo face -> r772).
Bloodline: r771 _r771bma_w156_freeze_edits.py machinery, W157 facts
live-registry-driven (band gate _r772bma_w157_band_gate.json rc0; pre-seat
probe _r772bma_w157_probe.py; seat 4af40c72d; prereg xform r772 landed
research/PERPETUAL_N1_W157_PREREG.md)."""
import ast
import io

PF = r"scripts/perpetual_faces.py"
N1 = r"scripts/perpetual_faces_n1.py"
CRLF = "\r\n"

TOK = [
    ("PERPETUAL-N1-W156", "@B@"),
    ("PERPETUAL_N1_W156", "@PF@"),
    ("n1_w156", "@SD@"),
    ("n1w156", "@SD2@"),
    ("_r769bma", "@RD@"),
    ("360_004..360_203", "@OB@"),      # W156 B band
    ("357_804..358_003", "@PB@"),      # W155 B cite (dotted)
    ("358_004..360_003", "@AB@"),      # W156 A band
    ("357_804..359_803", "@NA@"),      # W156 naive A
    ("358_004..358_203", "@NB@"),      # W156 naive B
    ("357_804, 358_003", "@PBR@"),     # W155 b_exit row (comma)
    ("355_804, 357_803", "@PAR@"),     # W155 a row (comma)
    ("358_004, 360_003", "@AROW@"),    # W156 a row (comma, pf.py row literal)
    ("360_004, 360_203", "@BROW@"),    # W156 b_exit row (comma, pf.py row literal)
    ("358_003+1", "@ABASE@"),
    ("360_003+1", "@BBASE@"),
    ("358_003 + 1", "@ABASE2@"),
    ("360_003 + 1", "@BBASE2@"),
    ("360_204", "@BEND@"),             # arith_b range end (W156 naive-B end)
    ("360_004", "@BSEED@"),            # bare: b seed base + jump target
    ("358_004", "@ASEED@"),            # bare: a seed base + range start
    ("MSG-2026-10-06-1009", "@SEAT@"),
    ("MSG-0943", "@MSGS@"),            # seat-tail comment shorthand (W155 seat)
    ("ffce2936f", "@SEATSHA@"),
    ("dde679c63", "@PSHA@"),
    ("737,011", "@LEDG@"),
    ("338,920", "@K1@"),
    ("ONE HUNDRED-AND-FORTY-SIXTH", "@ORDW@"),
    ("engine_owner rows 145", "@R145@"),
    ("rows 71", "@R71@"),
    ("seventy-second", "@OWN72@"),
    ("fifteenth", "@F15@"),
    ("r769", "@RW@"),
    ("r768", "@PRW@"),
    ("W156", "@W@"),
    ("W155", "@WP@"),
    ("156", "@IDX@"),
    ("155", "@IDX2@"),
]
BACK = [
    ("@B@", "PERPETUAL-N1-W157"), ("@PF@", "PERPETUAL_N1_W157"), ("@SD@", "n1_w157"),
    ("@SD2@", "n1w157"), ("@RD@", "_r772bma"),
    ("@OB@", "362_204..362_403"), ("@PB@", "360_004..360_203"),
    ("@AB@", "360_204..362_203"), ("@NA@", "360_004..362_003"),
    ("@NB@", "360_204..360_403"),
    ("@PBR@", "360_004, 360_203"), ("@PAR@", "358_004, 360_003"),
    ("@AROW@", "360_204, 362_203"), ("@BROW@", "362_204, 362_403"),
    ("@ABASE@", "360_203+1"), ("@BBASE@", "362_203+1"),
    ("@ABASE2@", "360_203 + 1"), ("@BBASE2@", "362_203 + 1"),
    ("@BEND@", "362_404"), ("@BSEED@", "362_204"), ("@ASEED@", "360_204"),
    ("@SEAT@", "MSG-2026-10-06-113x"), ("@MSGS@", "MSG-1009"),
    ("@SEATSHA@", "4af40c72d"), ("@PSHA@", "13c989ba0"),
    ("@LEDG@", "739,211"), ("@K1@", "341,120"),
    ("@ORDW@", "ONE HUNDRED-AND-FORTY-SEVENTH"), ("@R145@", "engine_owner rows 146"),
    ("@R71@", "rows 72"), ("@OWN72@", "seventy-third"), ("@F15@", "sixteenth"),
    ("@RW@", "r772"), ("@PRW@", "r771"),
    ("@W@", "W157"), ("@WP@", "W156"),
    ("@IDX@", "157"), ("@IDX2@", "156"),
]


def vmap(s: str) -> str:
    for a, b in TOK:
        s = s.replace(a, b)
    for a, b in BACK:
        s = s.replace(a, b)
    # post-map citation fixups (seat-projection cite chain honesty)
    s = s.replace("seat leg4", "seat W157+ projection")
    s = s.replace("r771 gate leg3 + r771 sec8", "r771 gate leg3 + r772 sec8")
    return s


def edit(path, pairs):
    src = io.open(path, encoding="utf-8", newline="").read()
    for i, (old, new) in enumerate(pairs):
        n = src.count(old)
        assert n == 1, f"{path}: needle {i} count={n} expect=1: {old[:80]!r}"
        src = src.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="").write(src)
    ast.parse(io.open(path, encoding="utf-8", newline="").read())
    print(f"{path}: {len(pairs)} edits landed, AST gate PASS")


pfsrc = io.open(PF, encoding="utf-8", newline="").read()
n1src = io.open(N1, encoding="utf-8", newline="").read()

# --- a1: pf.py W156 comment block + row -> append W157 comment block + row -----
i1 = pfsrc.find("    # W156 (bm-a r769 freeze")
assert i1 > 0, "pf W156 comment block not found"
r156 = pfsrc.find('156: {"a": (358_004, 360_003)', i1)
assert r156 > i1, "pf W156 row not after comment block"
j1 = pfsrc.find('"engine_owner": "bm-a"},', r156) + len('"engine_owner": "bm-a"},')
block156_pf = pfsrc[i1:j1]
assert block156_pf.count("engine_owner") == 1 and "13c989ba0" not in block156_pf
a1 = block156_pf + CRLF + "}"
r1 = block156_pf + CRLF + vmap(block156_pf) + CRLF + "}"

# --- a2: n1.py WAVE_CONFIGS entry ----------------------------------------------
k = n1src.find('156: {"batch"')
assert k > 0, "n1 W156 entry not found"
m = n1src.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
entry = n1src[k:m]
a2 = entry + CRLF + "                       }"
r2 = entry + CRLF + "                       " + vmap(entry) + CRLF + "                       }"

# --- a3: materializer block (chain split-verbatim + one-row extension) --------
w = n1src.find("# --- W156 materializer face")
t2 = n1src.find("# --- T-141 s2 lane face", w)
assert 0 < w < t2, "materializer anchors missing"
block = n1src[w:t2]
ci = block.find("assert pf.N1_BANDS[138]")
cj = block.find("# prior-wave disjointness")
assert 0 < ci < cj, "chain boundaries missing"
pre, chain, post = block[:ci], block[ci:cj], block[cj:]
import re
chain_rows = re.findall(r"assert pf\.N1_BANDS\[(\d+)\]", chain)
assert chain_rows == [str(x) for x in range(138, 156)], chain_rows
w156row = ('assert pf.N1_BANDS[156] == {"a": (358_004, 360_003),' + CRLF +
           '                                    "b_exit": (360_004, 360_203),' + CRLF +
           '                                    "engine_owner": "bm-a"}, \\' + CRLF +
           '            "registered W156 row parity drift (r307; bm-a r771)"' + CRLF +
           "        ")
block157 = vmap(pre) + chain + w156row + vmap(post)
a3 = block + "# --- T-141 s2 lane face"
r3 = block157 + "# --- T-141 s2 lane face"

# --- a4: PASS snippet claim insertion ------------------------------------------
cs = n1src.find('"+ W156 materializer face')
assert cs > 0, "W156 claim start not found"
ce = n1src.find('"r769 bm-a] "', cs) + len('"r769 bm-a] "')
claim = n1src[cs:ce]
a4 = '"r769 bm-a] "' + CRLF + '          "+ T-141 s2 "'
r4 = '"r769 bm-a] "' + CRLF + "          " + vmap(claim) + CRLF + '          "+ T-141 s2 "'

# --- apply the four edits ---------------------------------------------------------
edit(PF, [(a1, r1)])
edit(N1, [(a2, r2), (a3, r3), (a4, r4)])

# --- post-edit structural assertions --------------------------------------------
import sys
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import importlib
import perpetual_faces as pf
importlib.reload(pf)
assert sorted(pf.N1_BANDS)[-1] == 157 and len(pf.N1_BANDS) == 155, \
    "pf N1_BANDS row-count drift after W157 insert"
assert pf.N1_BANDS[157] == {"a": (360_204, 362_203),
                            "b_exit": (362_204, 362_403),
                            "engine_owner": "bm-a"}, "W157 row face drift"
assert pf.N1_BANDS[156] == {"a": (358_004, 360_003),
                            "b_exit": (360_004, 360_203),
                            "engine_owner": "bm-a"}, "W156 row survived (r560 no-replace law)"
import perpetual_faces_n1 as n1mod
importlib.reload(n1mod)
assert n1mod.WAVE_CONFIGS[157]["a_seed_base"] == 360_204 and \
    n1mod.WAVE_CONFIGS[157]["b_exit_seed_base"] == 362_204, "W157 seed bases drift"
assert n1mod.WAVE_CONFIGS[157]["shard_subdir"] == "n1_w157" and \
    n1mod.WAVE_CONFIGS[157]["out_name"] == "n1_w157_results.json", "W157 path drift"
print("post-edit structural assertions PASS: N1_BANDS 155 rows tail W157, "
      "W156 row intact, WAVE_CONFIGS[157] seeded")
