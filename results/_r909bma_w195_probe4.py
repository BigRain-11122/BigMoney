# -*- coding: utf-8 -*-
import io

n1n = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8',
              newline='').read().replace('\r\n', '\n')
c0 = n1n.find('194: {"batch": "PERPETUAL-N1-W194"')
c1 = n1n.find('"engine_owner": "bm-a"},', c0)
cfg = n1n[c0:c1 + len('"engine_owner": "bm-a"},')]
k = cfg.find('"a_seed_base"')
eol = cfg.find('\n', k)
print('ASEED:', repr(cfg[k:eol]))
k2 = cfg.find('"b_exit_seed_base"')
eol2 = cfg.find('\n', k2)
print('BEXIT:', repr(cfg[k2:eol2]))
k3 = cfg.find('"shard_subdir"')
eol3 = cfg.find('\n', k3)
print('SHARD:', repr(cfg[k3:eol3]))
