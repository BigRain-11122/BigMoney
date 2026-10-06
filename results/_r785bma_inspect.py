# -*- coding: utf-8 -*-
"""r785 dry-run inspector: print the vmap_fix'd W161 pf block + key n1 entry
fragments for eyeball verification before the real freeze edits land."""
import io
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("dr", "results/_r785bma_w161_dryrun2_core.py")
# We can't import the dryrun (it prints); instead re-derive inline via exec of the
# freeze script's TOK/BACK/FIXUPS definitions.
src = io.open('results/_r785bma_w161_freeze_edits.py', encoding='utf-8').read()
start = src.find('TOK = [')
end = src.find('# --- apply the four edits')
core = src[start:end]
ns = {'CRLF': "\r\n", 'io': io}
exec("import ast, json, re, os\n" + core.split('pfsrc = io.open')[0], ns)
vmap = ns['vmap']; vmap_fix = ns['vmap_fix']

EO = '"engine_owner": "bm-a"},'
pfsrc = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read()
i1 = pfsrc.find("    # W160 (bm-a r783 freeze")
j1 = pfsrc.find(EO, pfsrc.find('160: {"a": (366_804', i1)) + len(EO)
blk = pfsrc[i1:j1]
new = vmap_fix(blk, "pf")
print("=== NEW W161 pf block ===")
print(new)
print("=== leftover-token scan ===")
for t in ("@W", "@IDX", "@RW", "@PRW", "@GATE", "@SEC8", "@PUSH", "@LEDG", "@K1", "@NA@", "@AB@", "@BB@", "@OB@", "@NB@", "@PA@", "@PB@"):
    if t in new:
        print("LEFTOVER TOKEN:", t)
print("scan done")
