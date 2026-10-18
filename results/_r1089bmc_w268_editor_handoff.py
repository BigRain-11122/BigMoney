# -*- coding: utf-8 -*-
# r1089 bm-c: W268 EDITOR AUTHOR HANDOFF -- MEASURED needle baseline on the
# W268-editor canon (results/_w267bmc_freeze_edits.py, the W267 splice-window
# freeze-edits landed @ 7b9e9377). Per the r1077 measured-counts law the next
# editor author MUST re-measure every needle at authoring time -- this
# receipt is the handoff BASELINE for the defect-prone faces (setwave aging
# + the E63 heal-lineage faces), NOT a transcription source. The +1 aging
# law is documented in the r1088 editor L208-215 comment:
#   rep("_set_wave(267)", "_set_wave(268)", 1, "p3_setwave_rootcure")
#   presence gates: "_set_wave(268)": 1, "_set_wave(267)": 0
# NOT the mechanical (266->268) form -- the canon it reads carries 267 (the
# healed face). FULL W268 editor authoring is BLOCKED until the W268 prereg
# freeze lands (r1090 FIRST ACTION): the prereg-sha + seat-origin needle
# values do not exist yet (honest-split law r971).
import hashlib
import io
import json
import subprocess

CANON = 'results/_w267bmc_freeze_edits.py'
DSTW = 'results/_w268bmc_freeze_edits.py'

blob_wt = subprocess.run(['git', 'hash-object', CANON], capture_output=True,
                         text=True).stdout.strip()
blob_head = subprocess.run(['git', 'rev-parse', f'HEAD:{CANON}'],
                           capture_output=True, text=True).stdout.strip()
canon_committed = blob_wt == blob_head and len(blob_wt) == 40

t = io.open(CANON, encoding='utf-8', newline='').read()
sha16 = hashlib.sha256(io.open(CANON, 'rb').read()).hexdigest()[:16]


def c(s):
    return t.count(s)


measured = {
    # setwave aging-law faces (the r1076-family recurrence root -- measured)
    '_set_wave(267)': c('_set_wave(267)'),
    '_set_wave(265)': c('_set_wave(265)'),
    '_set_wave(268)': c('_set_wave(268)'),
    '_set_wave(266)': c('_set_wave(266)'),
    # projection faces already in the canon (W268p carried from the W267 seat)
    'W268p': c('W268p'), 'W269p': c('W269p'), 'W268': c('W268'),
    # W267 registered bands = the W268 transform's UPSTREAM-CONSUMER faces
    '602_701': c('602_701'), '604_700': c('604_700'),
    '604_701': c('604_701'), '604_900': c('604_900'),
    # W268 target bands (must be ABSENT from the canon pre-splice)
    '604_901': c('604_901'), '606_900': c('606_900'),
    '606_901': c('606_901'), '607_100': c('607_100'),
    # ledger/K anchors the W268 editor rolls to W267 actuals
    '1,009,535': c('1,009,535'), '583,120': c('583,120'),
    '1_009_535': c('1_009_535'), '583_120': c('583_120'),
    '1,011,735': c('1,011,735'), '585,320': c('585,320'),
    # ordinal faces (W268 = 258th candidate, bm-c 87th own)
    '256/130/85': c('256/130/85'),
    'rows 256 + candidate = 257th': c('rows 256 + candidate = 257th'),
    'EIGHTY-SIXTH owned': c('EIGHTY-SIXTH owned'),
    'SEVENTEENTH': c('SEVENTEENTH'), 'SIXTEENTH': c('SIXTEENTH'),
    'seventeenth': c('seventeenth'), 'sixteenth': c('sixteenth'),
    # E63 heal-lineage defect-prone faces (r1088 3 needle-form defects family)
    'W264_W265_W266_bands_respected': c('W264_W265_W266_bands_respected'),
    'W211..W266 legs 55': c('W211..W266 legs 55'),
    'W248..W266 legs (19': c('W248..W266 legs (19'),
    'own W248..W265': c('own W248..W265'),
    'range(248, 267)': c('range(248, 267)'),
    'block = 125 rows': c('block = 125 rows'),
    # lineage shas the W268 editor consumes/rolls
    '7b9e9377': c('7b9e9377'), 'dc71ecc3f9': c('dc71ecc3f9'),
    'df55e3fab9': c('df55e3fab9'),
    'MSG-20261018-1025-bmc-w267-seat': c('MSG-20261018-1025-bmc-w267-seat'),
    # frozen anti-drift aging tokens (must NOT roll)
    'w244_a': c('w244_a'), 'w244_b': c('w244_b'), 'n3r1_used245': c('n3r1_used245'),
}

# W268 seat faces the next editor will splice in (measured on the WORKTREE
# probe receipt + seat MSG, both landed this window origin b9ad2f1119)
probe = json.load(io.open('results/_w268bmc_20261018_probe_receipt.json',
                          encoding='utf-8'))
out = {
 'handoff': 'W268 EDITOR AUTHOR HANDOFF (r1089 bm-c -> r1090/r1091 splice window)',
 'aging_law': ("rep('_set_wave(267)', '_set_wave(268)', 1, 'p3_setwave_rootcure') + "
               "presence gates _set_wave(268):1 / _set_wave(267):0 -- NOT the mechanical "
               "(266->268) form; documented r1088 editor L208-215; r1076-family recurrence "
               "must END at the birth station (CEO defect-birthplace law 2026-10-16)"),
 'canon': {'path': CANON, 'blob': blob_wt, 'sha16': sha16,
           'worktree_eq_HEAD_committed': canon_committed,
           'bytes': len(t.encode('utf-8'))},
 'measured_needle_baseline': measured,
 'blocked_faces_until_w268_prereg_freeze': [
   'W268 prereg sha (research/PERPETUAL_N1_W268_PREREG.md freeze commit -- r1090 FIRST ACTION product)',
   'W268 seat origin ref values that ride the prereg bundle',
   'authored-stamp faces (derive-window mtime, r1088 heal #2 family)',
 ],
 'w268_seat_faces_available_now': {
   'seat_msg': 'fleet/inbox/MSG-20261018-1229-bmc-w268-seat.md (origin b9ad2f1119)',
   'probe_bands': probe['bands'],
   'probe_verdict': probe['verdict'],
   'A_semantics_tail': 'SEVENTEENTH consecutive A-hop (naive 604_701 refused at registered W267 B 604_701..604_900; live trace)',
   'B_semantics_tail': 'EIGHTEENTH consecutive above-own-A (own-A reservation past 606_900; B base==own-A tail+1)',
   'chain_anchors': 'W265->W266->W267 ledger 1,007,335->1,009,535->1,011,735 / K 580,920->583,120->585,320 (W267 finalize actuals = the W268 prereg keys basis, r587 machine-read law)',
 },
 'law_refs': ['r1077 measured-counts law', 'E63 live-import derive law',
              'r971 honest-split law', 'r587 never-transcribe law',
              'CEO defect-birthplace law 2026-10-16'],
}
ok = (canon_committed
      and measured['_set_wave(267)'] == 1 and measured['_set_wave(265)'] == 0
      and measured['_set_wave(268)'] == 0
      and measured['604_901'] == 0 and measured['606_900'] == 0
      and measured['606_901'] == 0 and measured['607_100'] == 0
      and measured['W268p'] >= 1 and measured['W268'] >= 1)
out['verdict'] = 'HANDOFF BASELINE OK' if ok else 'UNEXPECTED FACE -- re-measure before authoring'
io.open('results/_r1089bmc_w268_editor_handoff.json', 'w', encoding='utf-8').write(
    json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': out['verdict'], 'canon_sha16': sha16,
                  'canon_committed': canon_committed,
                  'setwave_267': measured['_set_wave(267)'],
                  'setwave_265': measured['_set_wave(265)'],
                  'setwave_268': measured['_set_wave(268)'],
                  'w268_target_bands_absent': [measured['604_901'],
                                                measured['606_900'],
                                                measured['606_901'],
                                                measured['607_100']],
                  'W268p': measured['W268p'], 'W268': measured['W268'],
                  'ledger_w266_faces': [measured['1,009,535'], measured['583,120']],
                  'ordinal_256_130_85': measured['256/130/85']},
                 indent=1))
raise SystemExit(0 if ok else 1)
