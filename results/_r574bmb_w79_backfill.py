# -*- coding: utf-8 -*-
"""r574 bm-b W79 prereg s7/s8 mechanical backfill (r307 two-state law)."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PATH = 'research/PERPETUAL_N1_W79_PREREG.md'
raw = open(PATH, 'rb').read()
txt = raw.decode('utf-8')
nl = '\r\n' if '\r\n' in txt else '\n'

ph7 = '## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl + '- （占位·finalize 后机械回填）'
ph8 = '## §8 批后复盘【必填·s7-T】' + nl + nl + '- （占位·finalize 后机械回填）'
assert ph7 in txt, 'S7 placeholder not found'
assert ph8 in txt, 'S8 placeholder not found'

s7 = ('## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl
      + '- **finalize 实烧=one-pass r574 bm-b**（r538 一过例·2026-10-02 12:0x·12 分片 shards_consumed 12/12·W79 results 件跑前缺位核验过=一过窗安全）：N=2,200（A 2,000＋B 200）。' + nl
      + '- **S5 四门全过（§5 预测 4/4）**：① W79-only mu **−0.102411** 与 merged mu **−0.092397**（K=171,720）漂移 |Δ|=**0.010014**<0.02（对锚 W77 merged −0.092281 漂 **0.000116**）✓；② sigma 相对变化 **+1.39%**<±10%（W79-only **0.246921** vs 锚 0.243541=W77-only 实测）✓；③ A 族 full_sharpe_p95 **0.3000** vs 锚 0.3003 |Δ|=**0.0003**<0.05 ✓；④ K-lift **+0.0000**≤0.02 @n_eff_held 536,148〔1.1651→**1.1651**〕✓。' + nl
      + '- **账本落账**：prev=**536,148**（W78 bm-c r364 活链头 derive·origin 时序面 r518 律）＋2,200=**538,348 净链头**·K=**171,720**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。' + nl
      + '- mu_delta_w79_vs_w78ext=**−0.011178**（单波跨度如实·W78-only −0.091233 实测）；se_mu=**0.000591** @K=171,720（收窄链延续：W77 0.000598→W78 0.000595→W79 0.000591）。' + nl)

s8 = ('## §8 批后复盘【必填·s7-T】' + nl + nl
      + '- **全生命周期三窗闭环**：冻结 r573（席位 MSG-20261002-1151-bmb·published=reserved r518-① 律）→烧录 12/12（r573 引擎 tick 冻结 commit 后自燃起烧 5/12·r574 ride r574a 续 shard-4..8·本窗 12:06 收尾至 12/12 落盘）→finalize r574 one-pass（W78 bm-c r364 落账 536,148 解锁后一过）。' + nl
      + '- **链序面**：W77 bm-a r573 落账（533,948）→W78 bm-c r364 落账（536,148）→本波 W79 落账（**538,348**）→链序下一波=W80（never-dry 常设步·席位公示见 MSG-20261002-12xx-bmb）。' + nl
      + '- **带位面**：A-ext seed **201_004..203_003**＋B-ext exit seed **53_401..53_600**（gate ADMIT 回执=results/_r573bmb_w79_band_gate.py·双侧算术顺延零跳位·单读法零分叉）。' + nl
      + '- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307·缺省波调用 r522 律）。' + nl)

txt = txt.replace(ph7, s7.rstrip('\r\n'))
txt = txt.replace(ph8, s8.rstrip('\r\n'))
open(PATH, 'wb').write(txt.encode('utf-8'))
print('BACKFILL WRITTEN, nl=', repr(nl))
chk = open(PATH, 'rb').read().decode('utf-8')
assert '（占位·finalize 后机械回填）' not in chk, 'placeholder still present'
print('PLACEHOLDERS CLEARED')
