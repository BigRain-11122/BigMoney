# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
T0 = io.open(r"results\_w246bma_freeze_edits.py", encoding="utf-8", newline="").read()
NEEDLES = [
    'N1_BANDS[246]', 'N1_BANDS.get(246)', 'WAVE_CONFIGS[247]', 'n1_w247', 'n1w247',
    'PERPETUAL_N1_W246_PREREG', 'PERPETUAL-N1-W247', '247: {"batch"', '247: {"a"',
    '_set_wave(247)', 'W247 seat', 'W248', 'arith_a247', 'arith_b247',
    'w246_a_tail', 'w246_b_tail', 'B_hop_chain=[', 'refuser', '542_401', '544_501',
    '561_501', 'W239', 'the W246 block appends', '785936d84', '1328-bma',
]
for s in NEEDLES:
    print("%-30r %d" % (s, T0.count(s)))
