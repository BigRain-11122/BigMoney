# -*- coding: utf-8 -*-
import io

t = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", errors="replace", newline="").read().replace("\r\n", "\n")
p = io.open(r"scripts/perpetual_faces.py", encoding="utf-8", errors="replace", newline="").read().replace("\r\n", "\n")
N1 = [
    'sorted(w for w in WAVE_CONFIGS if w < 195)',
    'sorted(w for w in WAVE_CONFIGS if w < 194)',
    'sorted(w for w in WAVE_CONFIGS if w < 196)',
    'WAVE_CONFIGS if w < 195):',
    'WAVE_CONFIGS if w < 194):',
    'range(17, 195):',
    'range(17, 194):',
    '# --- W195 materializer face',
    '# --- W194 materializer face',
    '# --- T-141 s2 lane face',
    'n1_w195',
    'n1_w194',
    'PERPETUAL_N1_W195_PREREG.md',
    '_set_wave(195)',
    '_set_wave(2)',
    'ONE HUNDRED-AND-NINETY-FIFTH engine wave',
    'one-hundred-tenth owned',
    'arith_a194',
    'arith_b194',
    'w194_a',
    'w194_b',
    'n3r1_used194',
    '"r909 bm-a] "',
    '"r905 bm-a] "',
    '+ W195 materializer face [same guard set',
    'MSG-2026-10-09-0844-bma-w195-seat',
    '841,145',
    '843,345',
    '424,720',
    '426,920',
    'b9b962672',
    'eb81c0878',
    'FIFTY-FIFTH',
    'FIFTY-SIXTH',
    'ONE HUNDRED-AND-NINETY-FIFTH ENGINE-OWNED WAVE',
    'engine_owner rows 184 + candidate',
    'W1..W194 finalize ALL LANDED',
]
PF = [
    '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),',
    '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),',
    '196: {"a"',
    '# W195 (bm-a r909 freeze',
    '# W194 (bm-a r905 freeze',
    '# W196+ projection (gate-derived r907)',
    '# W195+ projection',
    'MSG-2026-10-09-0844-bma-w195-seat',
]
for n in N1:
    print("N1", t.count(n), repr(n[:64]))
for n in PF:
    print("PF", p.count(n), repr(n[:64]))
