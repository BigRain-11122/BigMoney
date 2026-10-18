# -*- coding: utf-8 -*-
# anchor_precheck.py -- CSA anchor-cleaning discipline utilities (ST-004 product).
# Source law: cph4/fleet/drama-dept-v1/epburn-handover/CSA-SMOKE-VERDICT-20261017.md
# v1.1 item 2: id-bank frames must pass an anchor-consistency pre-check BEFORE
# entering the bank, and the ANCHOR triple is written as a hard constraint into
# the production burner (drama_ep_burn.py). Owner lane: bm-b / CONTENT-LOOP v0.1.
#
# ANCHOR triple (per verdict): every canon id-bank anchor must explicitly pin
#   1) hair style -- a hair/style word (hair, ponytail, temples, ...)
#   2) hair color -- a color word adjacent to a hair word (black hair, silver
#      temples, ...). The smoke verdict's green-hair drift (id 1-2 vs black-hair
#      canon) traced to UNPINNED hair color, so this dimension fails hardest.
#   3) attire     -- a clothing word (shirt, suit, skirt, tie, ...)
#
# Id-bank admission gate: a bank frame enters the bank only with a triple
# manifest (hair_style/hair_color/attire) whose values zero-drift-match the
# character's canon anchor (normalized substring), and all frames of the same
# character must share an identical manifest (cross-frame zero-drift).
# Frame-level (rendered-pixel) consistency is the multimodal seat's job --
# emit_frame_check() produces that workorder face.
#
# Deploy: copied verbatim by Tools/content_loop_step.py (st004 runner) to
# C:\Fluxgroup\MiniGame\Tools\comfy\anchor_precheck.py (toolchain canonical
# body dir, bm-b owner). This file = versioned source of truth (bigmoney repo).
# Usage: python anchor_precheck.py --selftest
import json
import re
import sys

CANON_TRIPLE = ('hair_style', 'hair_color', 'attire')

_COLOR_ALT = r'black|white|silver|grey|gray|blond|blonde|auburn|red|brown|blue|green|pink'
HAIR_COLOR_PAT = re.compile(r'(?:' + _COLOR_ALT + r')[\w\s-]{0,8}(?:hair|templ)')
HAIR_STYLE_PAT = re.compile(
    r'\b(?:hair|ponytail|bangs?|braids?|crew cut|buzz cut|mohawk|topknot|bun|curls?|temples?)\b')
ATTIRE_PAT = re.compile(
    r'\b(?:shirt|suit|jacket|skirt|dress|vest|tie|overalls|blouse|uniform|coat|sweater|hoodie)\b')


def triple_of(anchor):
    # Boolean presence map of the ANCHOR triple for one anchor text.
    low = str(anchor).lower()
    return {
        'hair_style': bool(HAIR_STYLE_PAT.search(low)),
        'hair_color': bool(HAIR_COLOR_PAT.search(low)),
        'attire': bool(ATTIRE_PAT.search(low)),
    }


def validate_canon(ids_dict, canon_keys):
    # Hard-constraint check for canon bank characters. Returns a list of
    # violation dicts (empty = pass). Extras/non-canon keys are not checked:
    # they carry generic anchors by design (warning-level in the burner).
    bad = []
    for k in canon_keys:
        a = (ids_dict or {}).get(k)
        if a is None:
            bad.append({'id': k, 'violation': 'missing-anchor'})
            continue
        t = triple_of(a)
        missing = [d for d in CANON_TRIPLE if not t[d]]
        if missing:
            bad.append({'id': k, 'missing': missing, 'anchor': a})
    return bad


def _norm(s):
    return re.sub(r'[^a-z0-9 ]+', ' ', str(s).lower())


def bank_entry_ok(entry, canon_anchor):
    # Id-bank admission gate (text level): every manifest value must appear in
    # the canon anchor after normalization. Returns (ok, reason).
    ca = _norm(canon_anchor)
    for dim in CANON_TRIPLE:
        v = _norm((entry or {}).get(dim, '')).strip()
        if not v:
            return False, 'manifest-missing:' + dim
        if v not in ca:
            return False, 'drift:' + dim + ':' + v
    return True, 'ok'


def frame_manifest_drift(frames):
    # Cross-frame zero-drift: all bank frames of the same character id must
    # carry an identical triple manifest. Returns list of drift reports.
    by_id = {}
    for fr in frames or []:
        by_id.setdefault(fr.get('id'), []).append(fr)
    out = []
    for rid, frs in by_id.items():
        if len(frs) < 2:
            continue
        sigs = {json.dumps({d: _norm(f.get(d, '')) for d in CANON_TRIPLE}, sort_keys=True)
                for f in frs}
        if len(sigs) > 1:
            out.append({'id': rid, 'frames': len(frs), 'manifests': len(sigs)})
    return out


def emit_frame_check(frames, out_json):
    # Multimodal-seat workorder face: lists every id-bank frame with its triple
    # manifest so a vision pass can verify rendered pixels vs manifest (the
    # deterministic levels above cannot see pixels; this is that handoff).
    order = {
        'law': 'CSA-SMOKE-VERDICT-20261017 v1.1 item 2: id-bank anchor consistency '
               'pre-check (frame-level face for the multimodal seat)',
        'triple': list(CANON_TRIPLE),
        'checks': ['frame matches its triple manifest',
                   'cross-frame same-id zero-drift'],
        'manifest_drift_preflight': frame_manifest_drift(frames),
        'frames': frames,
    }
    with open(out_json, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(order, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return out_json


def selftest():
    asserts = []
    canon_probe = {
        'CH': 'young man 22, black hair, white dress shirt, steel watch chain',
        'XIONG': 'man 50, silver temples, black suit, dark red necktie, prayer beads on wrist',
        'RED': 'young woman 20, black hair ponytail, 1990s office skirt suit',
        'MANCANG': 'chubby man 25, short black hair, loud floral shirt, pager on belt',
        'XIONGWEI': 'young man 24, neat black hair, all-black suit, rimless glasses',
        'FATHER': 'weary middle-aged man, unkempt black hair, rumpled dark suit, loosened tie',
        'BOY': '12-year-old schoolboy, short black hair, plain white shirt',
    }
    keys = tuple(canon_probe)
    asserts.append(('canon-seven-pass', validate_canon(canon_probe, keys) == []))
    pre = dict(canon_probe)
    pre['RED'] = 'young woman 20, ponytail, 1990s office skirt suit'  # no hair color
    asserts.append(('hair-color-fail',
                    any(v['id'] == 'RED' and v.get('missing') == ['hair_color']
                        for v in validate_canon(pre, keys))))
    pre['MANCANG'] = 'chubby man 25, loud floral shirt, pager on belt'  # no hair at all
    asserts.append(('hair-style-and-color-fail',
                    any(v['id'] == 'MANCANG' and set(v.get('missing', [])) == {'hair_style', 'hair_color'}
                        for v in validate_canon(pre, keys))))
    pre['BOY'] = '12-year-old schoolboy, short black hair'  # no attire
    asserts.append(('attire-fail',
                    any(v['id'] == 'BOY' and v.get('missing') == ['attire']
                        for v in validate_canon(pre, keys))))
    ok, why = bank_entry_ok({'hair_style': 'ponytail', 'hair_color': 'black hair',
                             'attire': 'skirt suit'}, canon_probe['RED'])
    asserts.append(('bank-admit-ok', ok and why == 'ok'))
    ok2, why2 = bank_entry_ok({'hair_style': 'ponytail', 'hair_color': 'green hair',
                               'attire': 'skirt suit'}, canon_probe['RED'])
    asserts.append(('bank-admit-drift-green-hair', not ok2 and why2.startswith('drift:hair_color')))
    ok3, _ = bank_entry_ok({'hair_style': 'ponytail'}, canon_probe['RED'])
    asserts.append(('bank-admit-missing-manifest', not ok3))
    drift = frame_manifest_drift([
        {'id': 'CH', 'file': 'a.png', 'hair_style': 'hair', 'hair_color': 'black hair',
         'attire': 'white dress shirt'},
        {'id': 'CH', 'file': 'b.png', 'hair_style': 'hair', 'hair_color': 'green hair',
         'attire': 'white dress shirt'},
        {'id': 'BOY', 'file': 'c.png', 'hair_style': 'short hair', 'hair_color': 'black hair',
         'attire': 'plain white shirt'},
    ])
    asserts.append(('cross-frame-drift-detected',
                    len(drift) == 1 and drift[0]['id'] == 'CH' and drift[0]['manifests'] == 2))
    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL',
                      'asserts': {k: ok for k, ok in asserts}}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    print(json.dumps({'usage': ['python anchor_precheck.py --selftest']}))
