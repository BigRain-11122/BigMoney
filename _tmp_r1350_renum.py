"""Renumber the phase-atlas card E256 -> E257 (bm-a took E255 on origin; the r1349 quantile card
moved to E256, so this round's card is the next free number). References travel with the card --
a card number that only exists in the ledger is a broken pointer (r1031 family).
"""
import io
import os
import re

edits = []


def patch(path, pairs):
    s = io.open(path, encoding='utf-8', newline='').read()
    orig = s
    for a, b in pairs:
        s = s.replace(a, b)
    if s != orig:
        io.open(path, 'w', encoding='utf-8', newline='').write(s)
        edits.append(path)


patch('knowledge/METHODOLOGY_ASSETS.md', [
    ('## E256 A grid cell is only a cell if it beats the calendar it was measured on',
     '## E257 A grid cell is only a cell if it beats the calendar it was measured on'),
    ('knowledge/METHODOLOGY_ASSETS.md#E256', 'knowledge/METHODOLOGY_ASSETS.md#E257'),
])
patch('Tools/s6_chain_bmc.py', [('# r1350 / E256:', '# r1350 / E257:')])
patch('smoke_test.py', [('# r1350 / E256:', '# r1350 / E257:')])
patch('research/ETF_BOOK_PHASE_ATLAS.md', [('E256', 'E257')])
patch('state-bm-c.json', [('knowledge/METHODOLOGY_ASSETS.md#E256',
                          'knowledge/METHODOLOGY_ASSETS.md#E257')])
patch('round_reports-bm-c.md', [('card E256', 'card E257')])

old_digest = 'research/digests/DIGEST-20261030-e256-phase-atlas.md'
new_digest = 'research/digests/DIGEST-20261030-e257-phase-atlas.md'
if os.path.exists(old_digest):
    patch(old_digest, [('E256', 'E257'), ('e256', 'e257')])
    os.replace(old_digest, new_digest)
    edits.append(old_digest + ' -> ' + new_digest)

# the atlas card's own Pos line names the digest
patch('knowledge/METHODOLOGY_ASSETS.md', [('DIGEST-20261030-e256-phase-atlas.md',
                                           'DIGEST-20261030-e257-phase-atlas.md')])

s = io.open('knowledge/METHODOLOGY_ASSETS.md', encoding='utf-8').read()
nums = [int(m.group(1)) for m in re.finditer(r'^## E(\d+)', s, re.M)]
print('max', max(nums), '| 256:', nums.count(256), '| 257:', nums.count(257))
print('edits:', edits)