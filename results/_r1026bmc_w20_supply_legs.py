# r1026: W20 draft supply legs — grammar ledger inventory + seed gate + W19 verdict freeze
import io, json, hashlib, re

txt = io.open('research/TRIAL_GRAMMAR_LEDGER.md', encoding='utf-8').read()
lines = txt.splitlines()

# 1) wave-row labels (short prefixes before long inline payloads)
print("== ledger wave rows ==")
burned_funcs = set()
for i, l in enumerate(lines):
    head = l[:110].replace('\n', ' ')
    print("L%02d: %s" % (i, head))
    # extract function-name-looking tokens (burned function inventory)
    for m in re.finditer(r'\b(?:fn|face|func)[_=:\.\-]?([a-z0-9_]{3,40})\b', l[:200000], re.I):
        pass

# 2) burned-function face names: look for the W16 candidates json for the 173-cell inventory
try:
    w16 = json.load(io.open('results/trial_labor_w16/w16_candidates.json', encoding='utf-8'))
    if isinstance(w16, dict):
        print("\n== w16_candidates.json top keys ==", list(w16.keys())[:10])
        cells = w16.get('cells') or w16.get('candidates') or []
    else:
        cells = w16
    print("w16 cells n =", len(cells) if isinstance(cells, list) else 'dict')
    if isinstance(cells, list) and cells:
        print("first cell keys:", list(cells[0].keys()) if isinstance(cells[0], dict) else cells[0])
except Exception as e:
    print("w16 read err:", e)

# 3) seed registry location
import os
for p in ['results/seed_registry.json', 'results/SEED_REGISTRY.json', 'research/SEED_REGISTRY.md',
          'results/seed_registry/seed_registry.json', 'results/trial_labor_seed_registry.json']:
    if os.path.exists(p):
        print("\nSEED REGISTRY FOUND:", p)
        d = json.load(io.open(p, encoding='utf-8'))
        if isinstance(d, dict):
            print("keys n =", len(d), "sample:", list(d.keys())[:6])
        break
else:
    print("\nseed registry not at common paths; searching...")
    for root, dirs, files in os.walk('results'):
        for f in files:
            if 'seed' in f.lower() and 'registry' in f.lower():
                print("  candidate:", os.path.join(root, f))
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__')]
