import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PATH = 'research/PERPETUAL_N1_W76_PREREG.md'
raw = open(PATH, 'rb').read()
txt = raw.decode('utf-8')
nl = '\r\n' if '\r\n' in txt else '\n'

ph7 = '## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl + '- （占位·finalize 后机械回填）'
ph8 = '## §8 批后复盘【必填·s7-T】' + nl + nl + '- （占位·finalize 后机械回填）'
assert ph7 in txt, 'S7 placeholder not found'
assert ph8 in txt, 'S8 placeholder not found'

s7 = ('## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl
      + '- **finalize 实烧=one-pass r573 bm-b**（r538 一过例·2026-10-02 11:5x·12 分片 shards_consumed 12/12·r310 完备性门 origin 12/12 ls-tree 过）：N=2,200（A 2,000＋B 200）。' + nl
      + '- **S5 四门全过（§5 预测 4/4）**：① W76-only mu **−0.091729** 与 merged mu **−0.092264**（K=165,120）漂移 |Δ|=**0.000535**<0.02（对锚 W74 merged −0.092106 漂 0.000158）✓；② sigma 相对变化 **−0.46%**<±10%（W76-only **0.2456** vs 锚 0.2467=W74-only 实测）✓；③ A 族 full_sharpe_p95 **0.3134** vs 锚 0.3117 |Δ|=**0.0017**<0.05 ✓；④ K-lift **+0.0001**≤0.02（1.1645→**1.1646** @n_eff_held 529,548·正负交替律如实：W73 −0.0004→W74 +0.0002→W75 −0.0001→W76 +0.0001）✓。' + nl
      + '- **账本落账**：prev=**529,548**（W75 bm-a r572 活链头 derive·origin 时序面 r518 律）＋2,200=**531,748 净链头**·K=**165,120**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。' + nl
      + '- mu_delta_w76_vs_w75ext=**+0.012621**（单波跨度如实·W75-only −0.104350 实测）；se_mu=**0.000602** @K=165,120（收窄链延续：W74 0.000611→W76 0.000602）。' + nl)

s8 = ('## §8 批后复盘【必填·s7-T】' + nl + nl
      + '- **全生命周期三窗闭环**：冻结 r572（席位 MSG-1130-bmb·published=reserved r518-①）→烧录 12/12（r572 引擎 tick 冻结 commit 后自燃起烧 4/12·r572 ride 续 shard-5/6·r573 窗收尾 shard-6..11 至 12/12 落盘 11:4x）→finalize r573 one-pass（W75 bm-a r572 落账 529,548 解锁后一过）。' + nl
      + '- **链序面**：W74 bm-b r572 落账（527,348）→W75 bm-a r572 落账（529,548）→本波 W76 落账（531,748）→**W77（bm-a·r572 冻结·烧录 6/12+ 在飞）finalize 解锁**（bm-a 下一 one-pass）。' + nl
      + '- **带位面**：A-ext seed **195_004..197_003**＋B-ext exit seed **52_401..52_600**（gate ADMIT 回执=results/_r572bmb_w76_band_gate.py·双侧算术顺延零跳位·单读法零分叉）。' + nl
      + '- **撞面实证**：bm-c r363 同窗双冻 W76/W77 逐位同带→按 r511 commit 时序律对 bm-b/bm-a 双零成本让路（未推未烧先弃·finalize 从未跑·账本零双计）=r530 族确定性交叉验证 #11。' + nl
      + '- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307·缺省波调用 r522 律）。' + nl)

txt = txt.replace(ph7, s7.rstrip('\r\n'))
txt = txt.replace(ph8, s8.rstrip('\r\n'))
open(PATH, 'wb').write(txt.encode('utf-8'))
print('BACKFILL WRITTEN, nl=', repr(nl))
chk = open(PATH, 'rb').read().decode('utf-8')
assert '（占位·finalize 后机械回填）' not in chk, 'placeholder still present'
print('PLACEHOLDERS CLEARED')
