#!/usr/bin/env python
# r1053 bm-a post-push addendum: record the bm-b local-ahead discovery
# (repo_heads quant/bigmoney = dac9a725, NOT on origin = stranded unpushed
# local commits) into state notes + next pointer so r1054 does not
# mis-diagnose delivery verification. Fresh-read-modify-write one-shot.
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, 'state-bm-a.json')
HEART = os.path.join(BASE, 'fleet', 'machines', 'bm-a.json')

ADDENDUM = (
    " r1053 addendum (post-push): unlock delivery face = bm-b /status "
    "repo_heads[quant/bigmoney]=dac9a725ce95efa758a33f7c80fe078515f8124f "
    "(NOT on origin -- object absent from bm-a repo, cat-file fatal) = bm-b "
    "carries STRANDED UNPUSHED local commits (r1003+ rounds committed locally, "
    "pushes never landed; last origin push r1002 07:54); poke face = "
    "pulls 'quant/bigmoney:updated' (origin refs now 55057912a9) + "
    "Bigmoney-IterationLoop:WAKE accepted 10:57:21; r1054 delivery verify "
    "MUST therefore expect the bm-b S0 rebase to land its local-ahead "
    "commits (dac9a725 lineage) onto origin -- repo_heads==my-push-sha is "
    "NOT the success criterion while local-ahead; success = bm-b closeout "
    "push lands (heartbeat fresh + O-0948 ack + rootfix MSG); if still "
    "frozen after wake = task-level stall (schtasks face, bm-b local "
    "physical) -> honest escalation note, idle-watch lane."
)

with open(STATE, encoding='utf-8') as fh:
    st = json.load(fh)
st['notes_r1053'] = st.get('notes_r1053', '') + ADDENDUM
st['next'] = st.get('next', '') + (
    " -- ADDENDUM: bm-b local-ahead face dac9a725 (unpushed estate) + WAKE "
    "accepted 10:57:21; verify = closeout push lands estate + O-0948 ack, "
    "not repo_heads==bm-a-sha"
)
tmp = STATE + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
os.replace(tmp, STATE)

with open(HEART, encoding='utf-8') as fh:
    hb = json.load(fh)
hb['next'] = st['next']
tmp = HEART + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
os.replace(tmp, HEART)

with open(STATE, encoding='utf-8') as fh:
    chk = json.load(fh)
assert 'dac9a725' in chk['notes_r1053']
print('ADDENDUM-OK')
