"""Step 1 of 2 in the r1350 rebase resolution on knowledge/METHODOLOGY_ASSETS.md.

bm-a landed E255 on origin; the dead r1349 window had filed our quantile-floor card under the same
number. This stop takes origin verbatim (append-only ledger law) and renumbers OUR card to E256 --
the phase-atlas card this round adds arrives in the next replayed commit and will renumber to E257
there, so the ledger ends with unique numbers and origin ordering untouched.
"""
import io
import re
import subprocess

origin = io.open('_tmp_origin_cards.md', encoding='utf-8').read()
theirs = subprocess.run(['git', 'show', ':3:knowledge/METHODOLOGY_ASSETS.md'],
                        capture_output=True, text=True, encoding='utf-8').stdout


def card_block(text, num):
    m = re.search(r'^## E%d .*?(?=^## E\d+ |\Z)' % num, text, re.M | re.S)
    return None if m is None else m.group(0).rstrip('\n')


qt = card_block(theirs, 255)
assert qt and 'quoted percentile has a resolution' in qt, 'our quantile card not found'
qt = qt.replace('## E255 ', '## E256 ', 1)

out = origin.rstrip('\n') + '\n\n' + qt + '\n'
io.open('knowledge/METHODOLOGY_ASSETS.md', 'w', encoding='utf-8', newline='').write(out)
nums = [int(m.group(1)) for m in re.finditer(r'^## E(\d+)', out, re.M)]
print('cards', len(nums), 'max', max(nums), 'dupes', sorted({n for n in nums if nums.count(n) > 1}))
assert len(set(nums)) == len(nums)
print('step1 resolved')