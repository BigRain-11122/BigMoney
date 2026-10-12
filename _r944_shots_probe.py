# -*- coding: utf-8 -*-
import io, re, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SP = r'K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\30s-reel-v1\mv_full_shots.py'
t = io.open(SP, encoding='utf-8').read()
ids = re.findall(r'\(\s*"([A-Z0-9_]+)"\s*,\s*([\d.]+)\s*,\s*([\d.]+)', t)
print('tuples:', len(ids))
print([i[0] for i in ids])
fr = r'K:\Fluxgroup\archive\mv0001-kf-frames-bmc-r840\frames_full'
names = sorted(os.listdir(fr))
print('frames:', len(names))
print(names[:50])
