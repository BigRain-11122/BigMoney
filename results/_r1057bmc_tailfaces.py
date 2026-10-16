# -*- coding: utf-8 -*-
# r1057 bm-c scratch: extract exact bytes of the P5e tail-assert A/B faces + pre/pfcmt/rcpt-note faces from the W254 freeze script (needle source-of-truth for the W255 editor derive).
import io
t = io.open(r'results\_w254bmc_freeze_edits.py', encoding='utf-8').read()
i = t.find('staircase-affects-A walk THIRD consecutive A-hop: the naive')
print('--- A-face msg context (repr) ---')
print(repr(t[i-260:i+900]))
j = t.find('B 1-HOP own-A RESERVATION CASCADE face: the naive continuation')
print('--- B-face assert context (repr) ---')
print(repr(t[j-400:j+700]))
k = t.find('same-freeze mutual exclusion')
print('--- mutual-exclusion face (repr) ---')
print(repr(t[k-320:k+320]))
