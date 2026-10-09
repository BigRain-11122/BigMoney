# -*- coding: utf-8 -*-
"""r921 review helper: replicate the roll in-memory and print key faces."""
import sys, json
sys.argv = [sys.argv[0]]  # force dry-run mode
sys.path.insert(0, 'results')
import importlib.util
spec = importlib.util.spec_from_file_location("fz", "results/_r921bma_w200_freeze_edits.py")
fz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fz)

# rebuild the roll in-memory (copy of main() G4-G7 logic, read-only)
import io, ast
n1n = io.open(fz.N1P, encoding='utf-8', errors='replace', newline='').read().replace('\r\n', '\n')
pfn = io.open(fz.PFP, encoding='utf-8', errors='replace', newline='').read().replace('\r\n', '\n')

def chunk(text, start, end):
    i = text.find(start); j = text.find(end, i)
    return text[i:j+len(end)]

mat199 = chunk(n1n, "    # --- W199 materializer face", "    _set_wave(2)")
cfg199 = chunk(n1n, '    199: {"batch": "PERPETUAL-N1-W199",', '"engine_owner": "bm-a"},')
pf199 = chunk(pfn, "    # W199 (bm-a r919 freeze, seat MSG-2026-10-09-1507-bma-w199-seat", '"engine_owner": "bm-a"},')
claim199 = chunk(n1n, '          "+ W199 materializer face [same guard set', '"r919 bm-a] "')

t912, t915, t916, t919 = fz.load_bloodline()
drop_if = [x[0] if isinstance(x, tuple) else x for x in t915["DROP_IF"]]
rmat = [(b, fz.apply_s(b)) for (a,b) in t919["RULES_W199_MAT"]]
rcfg = [(b, fz.apply_s(b)) for (a,b) in t919["RULES_W199_CFG"]]
rpf = [(b, fz.apply_s(b)) for (a,b) in t919["RULES_W199_PF"]]
rclaim = [(b, fz.apply_s(b)) for (a,b) in t919["RULES_W199_CLAIM"]]

def roll(live, r912l, g915, g916, g919, w200rules, drop_if):
    m = live
    for (w195_old, w196_new, cnt) in r912l:
        if any(d in w196_new for d in drop_if):
            continue
        w199 = fz.apply_rules(fz.apply_rules(fz.apply_rules(w196_new, g915, 'x'), g916, 'x'), g919, 'x')
        w200r = fz.apply_rules(w199, w200rules, 'x')
        if w200r != w199:
            m = m.replace(w199, w200r)
    return m

mat200 = roll(mat199.replace(fz.ARCH_MAT[0], fz.ARCH_MAT[1]), t912["R"], t915["RULES_MAT"], t916["RULES_W198_MAT"], t919["RULES_W199_MAT"], rmat, drop_if)
cfg200 = roll(cfg199, t912["RC"], t915["RULES_CFG"], t916["RULES_W198_CFG"], t919["RULES_W199_CFG"], rcfg, drop_if)
pf200 = roll(pf199.replace(fz.ARCH_PF[0], fz.ARCH_PF[1]), t912["RP"], t915["RULES_PF"], t916["RULES_W198_PF"], t919["RULES_W199_PF"], rpf, drop_if)
claim200 = roll(claim199, t912["RQ"], t915["RULES_CLAIM"], t916["RULES_W198_CLAIM"], t919["RULES_W199_CLAIM"], rclaim, drop_if)

print('=== CFG200 (first 20 lines) ===')
print('\n'.join(cfg200.splitlines()[:20]))
print()
print('=== PF200 (first 30 lines) ===')
print('\n'.join(pf200.splitlines()[:30]))
print()
print('=== MAT200 header + archive + band facts ===')
ml = mat200.splitlines()
print('\n'.join(ml[:8]))
print('   ...')
for i, ln in enumerate(ml):
    if 'archive' in ln or 'ALREADY' in ln:
        print('\n'.join(ml[max(0,i-1):i+5])); print('   ...'); break
print()
print('=== CLAIM200 (tail 6 lines) ===')
print('\n'.join(claim200.splitlines()[-6:]))
