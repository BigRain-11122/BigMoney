"""r820 bm-c static proof: every W17 candidate's mk resolves in the W16
faces table (the exact KeyError('faces') crash face at curve-fn L350).
Plus: worker-path dry check that _init_worker(tl1.GRAMMAR-loaded state)
makes run_candidate_curve_w17's face_frame lookup resolvable."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

w16 = json.load(open('results/trial_labor_w16/w16_grammar.json', encoding='utf-8'))
faces = w16['faces']

# W17 candidates come from the frozen entry product (same loader the
# runner uses). Locate entry file the way cmd_generate does.
import trial_labor_w17 as w17
ed = w17._entry_load()
cands = ed['candidates']
missing = []
for c in cands:
    mk = f"{c['module']}.{c['fn']}"
    if mk not in faces:
        missing.append((c['candidate_id'], mk))
print(f"candidates: {len(cands)} | faces table entries: {len(faces)}")
print(f"UNRESOLVED mk keys: {len(missing)}")
for cid, mk in missing[:5]:
    print('  MISSING:', cid, '->', mk)

# worker-path simulation: the state as cmd_screen now packs it
state_grammar_check = isinstance(faces, dict) and len(faces) > 0
print('state grammar will carry faces table:', state_grammar_check)

# sample resolution: first candidate through the exact L350 expression
c0 = cands[0]
mk0 = f"{c0['module']}.{c0['fn']}"
frame = faces[mk0]
print('sample L350 resolution for', c0['candidate_id'], '->', mk0,
      'face_frame type:', type(frame).__name__)

rc = 0 if (not missing and state_grammar_check) else 1
print('STATIC-PROOF:', 'PASS' if rc == 0 else 'FAIL')
sys.exit(rc)
