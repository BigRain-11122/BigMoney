# -*- coding: utf-8 -*-
"""r432 bm-c generic rebase take-ours resolver for racing regenerated faces.
Usage: python results/_r432bmc_take_ours.py <relpath> [<relpath> ...]
Law: r630 pick-verify-absorbed (racing same-day-idempotent regen faces:
newer origin side wins at pick level; own newer writes replay in later picks).
Marker-line anchored, byte-exact, .json validated by json.loads."""
import json
import re
import sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
MARK_START = re.compile(r'^<<<<<<< ')
MARK_MID = re.compile(r'^\|\|\|\|\|\|\| ')
MARK_SEP = re.compile(r'^=======$')
MARK_END = re.compile(r'^>>>>>>> ')


def resolve(rel):
    path = REPO + '\\' + rel.replace('/', '\\')
    text = open(path, 'rb').read().decode('utf-8')
    lines = text.split('\n')
    i, hunks = 0, []
    while i < len(lines):
        if MARK_START.match(lines[i].rstrip('\r')):
            s = i
            m = p = e = None
            j = i + 1
            while j < len(lines):
                if MARK_MID.match(lines[j].rstrip('\r')) and m is None:
                    m = j
                elif MARK_SEP.match(lines[j].rstrip('\r')) and m is not None and p is None:
                    p = j
                elif MARK_END.match(lines[j].rstrip('\r')) and p is not None:
                    e = j
                    break
                j += 1
            assert None not in (m, p, e), 'malformed hunk in %s' % rel
            hunks.append((lines[s + 1:m], s, e))
            i = e + 1
        else:
            i += 1
    assert hunks, 'no hunks in %s' % rel
    new_lines, cursor = [], 0
    for ours, s, e in hunks:
        new_lines.extend(lines[cursor:s])
        new_lines.extend(ours)
        cursor = e + 1
    new_lines.extend(lines[cursor:])
    final = '\n'.join(new_lines)
    resid = [l for l in new_lines
             if re.match(r'^(<<<<<<<|\|\|\|\|\|\|\||=======$|>>>>>>>)', l.rstrip('\r'))]
    assert not resid, (rel, resid[:2])
    if rel.endswith('.json'):
        json.loads(final)
    final.encode('utf-8')
    open(path, 'wb').write(final.encode('utf-8'))
    print('TAKE-OURS %s: %d hunk(s) resolved, markers=0, json ok' % (rel, len(hunks)))


for rel in sys.argv[1:]:
    resolve(rel)
print('GENERIC TAKE-OURS DONE for %d file(s)' % (len(sys.argv) - 1))
