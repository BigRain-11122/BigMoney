import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PATH = 'research/PERPETUAL_N1_W74_PREREG.md'
raw = open(PATH, 'rb').read()
txt = raw.decode('utf-8')
nl = '\r\n' if '\r\n' in txt else '\n'

ph7 = '## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl + '- （占位·finalize 后机械回填）'
ph8 = '## §8 批后复盘【必填·s7-T】' + nl + nl + '- （占位·finalize 后机械回填）'
assert ph7 in txt, 'S7 placeholder not found'
assert ph8 in txt, 'S8 placeholder not found'

s7 = ('## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl
      + '- **finalize 实烧=one-pass r572 bm-b**（r538 一过例·2026-10-02 11:3x·12 分片 shards_consumed 12/12·r310 完备性门 origin 12/12 ls-tree 过）：N=2,200（A 2,000＋B 200）。' + nl
      + '- **S5 四门全过（§5 预测 4/4）**：① W74-only mu **−0.087584** 与 merged mu **−0.092106**（K=160,720）漂移 |Δ|=**0.004521**<0.02（对锚 W72 merged −0.092251 漂 0.000145）✓；② sigma 相对变化 **−1.15%**<±10%（W74-only **0.2467** vs 锚 0.249564=W72-only 实测）✓；③ A 族 full_sharpe_p95 **0.3117** vs 锚 0.3372 |Δ|=**0.0255**<0.05 ✓；④ K-lift **+0.0002**≤0.02（1.164→**1.1642** @n_eff_held 525,148·正负交替律如实：W68 +0.0005→W69 +0.0000→W70 −0.0005→W71 +0.0002→W72 +0.0004→W73 −0.0004→W74 +0.0002）✓。' + nl
      + '- **账本落账**：prev=**525,148**（W73 bm-a r571 活链头 derive·origin 时序面 r518 律）＋2,200=**527,348 净链头**·K=**160,720**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。' + nl
      + '- mu_delta_w74_vs_w73ext=**−0.001291**（单波跨度如实）；se_mu=**0.000611** @K=160,720（收窄链延续：W72 0.000619→W73 0.000615→W74 0.000611）。' + nl)

s8 = ('## §8 批后复盘【必填·s7-T】' + nl + nl
      + '- **全生命周期三窗闭环**：冻结 r571（席位 MSG-1108-bmb·published=reserved r518-①）→烧录 12/12（r571 引擎 tick 冻结 commit 后自燃起烧·r572 窗续烧 shard-8..11 至 12/12 落盘 11:14）→finalize r572 one-pass（W73 bm-a r571 落账 525,148 解锁后一过）。' + nl
      + '- **链序面**：W72 bm-b r571 落账（522,948）→W73 bm-a r571 落账（525,148）→本波 W74 落账（527,348）→**W75（bm-a·冻结 695312330·烧录 5/12+ 在飞）finalize 解锁**（bm-a 下一 one-pass）。' + nl
      + '- **带位面**：A-ext seed **191_004..193_003**＋B-ext exit seed **52_001..52_200**（gate ADMIT 回执=results/_r571bmb_w74_band_gate.py；B 面强制跳位过 SEED_REGISTRY xstock_synth_null_b=52_000 上缘点·两读法同解零分叉）。' + nl
      + '- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307·缺省波调用 r522 律）。' + nl)

txt = txt.replace(ph7, s7.rstrip('\r\n'))
txt = txt.replace(ph8, s8.rstrip('\r\n'))
open(PATH, 'wb').write(txt.encode('utf-8'))
print('BACKFILL WRITTEN, nl=', repr(nl))
chk = open(PATH, 'rb').read().decode('utf-8')
assert '（占位·finalize 后机械回填）' not in chk, 'placeholder still present'
print('PLACEHOLDERS CLEARED')
