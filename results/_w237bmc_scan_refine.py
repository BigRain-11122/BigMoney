# -*- coding: utf-8 -*-
"""r990 scan-refine surgery: replace over-broad blanket FORBID entries with
context-pinned count assertions (dbg_residue probe verdict: all 3 residues are
family-legal prior-wave citations that MUST be retained)."""
import io

P = 'results/_w237bmc_prereg_derive.py'
src = io.open(P, encoding='utf-8').read()

anchor = "# ---------- forbidden-residue scan ----------"
end_anchor = "assert not residue, 'forbidden residue: %s' % residue"
i = src.index(anchor)
j = src.index(end_anchor) + len(end_anchor)
block = src[i:j]
assert block.count('FORBID = [') == 1 and block.count('for f in FORBID') == 1
assert block.count("'536_004..536_203'") == 1
assert block.count("'_w236bma'") == 1 and block.count("'938,589'") == 1

new_block = (
    "# ---------- forbidden-residue scan (r990 context-pinned refine) ----------\n"
    "# blanket entries '536_004..536_203'/'_w236bma'/'938,589' REMOVED per dbg_residue\n"
    "# probe verdict: they are family-legal prior-wave citations that MUST be retained\n"
    "# (W236 registered B band = staircase rejector narration x2; _w236bma_freeze_edits.py\n"
    "# = template-source citation x1; 938,589 = W234 historical ledger head x1) -- pinned\n"
    "# below by exact count + phrase-context assertions instead of blanket substring ban.\n"
    "FORBID = ['534_004', '533_804', 'pre-W236 \\u5168\\u4e8c\\u767e',\n"
    "          'W2..W235', 'W1..W235', 'bm-a 120', 'r972 \\u7a97',\n"
    "          '0446-bma', '233 \\u884c live', 'owner rows 225', 'v2..W235',\n"
    "          'engine_owner \\u884c 225', '\\u6cf5\\u7b2c 234 \\u679a', 'bma rows 120',\n"
    "          'PERPETUAL-N1-W236', 'n1_w236/shard', '534004', '536004',\n"
    "          'W236-only mu \\u4e0e', 'W235 \\u5b9e\\u6d4b\\u952e', '0.3058',\n"
    "          'NINETY-SIXTH', '\\u7b2c\\u4e5d\\u5341\\u516d\\u4f8b', 'parity 94 \\u884c',\n"
    "          '39.1GB', 'r970 W235']\n"
    "residue = [f for f in FORBID if f in out]\n"
    "assert not residue, 'forbidden residue: %s' % residue\n"
    "\n"
    "# context-pinned legal prior-wave citations (r990 scan-refine)\n"
    "assert out.count('536_004..536_203') == 2, out.count('536_004..536_203')\n"
    "assert out.count('W236 \\u6ce8\\u518c B \\u5e26 536_004..536_203') == 2, 'rejector-band phrase x2'\n"
    "assert out.count('_w236bma') == 1 and out.count('_w236bma_freeze_edits.py') == 1\n"
    "assert out.count('938,589') == 1 and '\\u8d26\\u672c\\u5934 938,589 \\u673a\\u8bfb\\u00b7n1_w234_results.json' in out"
)
out_src = src[:i] + new_block + src[j:]
assert out_src.count('FORBID = [') == 1 and out_src.count('for f in FORBID') == 1
assert out_src.count('context-pinned') == 2
io.open(P, 'w', encoding='utf-8', newline='').write(out_src)
print('scan-refine OK: %d -> %d bytes' % (len(src), len(out_src)))
