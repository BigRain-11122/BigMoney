# -*- coding: utf-8 -*-
"""r570 W70 prereg s7/s8 mechanical backfill (r307 two-state, bytes-level)."""
import io

FP = 'research/PERPETUAL_N1_W70_PREREG.md'
b = open(FP, 'rb').read()
t = b.decode('utf-8')

S7_OLD = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- （占位·finalize 后机械回填）"""
S7_NEW = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- **finalize 实烧=one-pass r570 bm-b**（r538 一过例·2026-10-02 10:5x·12 分片 shards_consumed 12/12·r310 完备性门 origin 12/12 ls-tree 过）：N=2,200（A 2,000＋B 200）。
- **S5 四门全过（§5 预测 4/4）**：① W70-only mu **−0.097210** 与 merged mu **−0.092392**（K=151,920）漂移 |Δ|=**0.004818**<0.02（对锚 W67 merged −0.092429 净漂 0.000037）✓；② sigma 相对变化 **−1.40%**<±10%（W70-only **0.239768** vs 锚 0.243181）✓；③ A 族 full_sharpe_p95 **0.3005** vs 锚 0.3213 |Δ|=**0.0208**<0.05 ✓；④ K-lift **−0.0005**≤0.02（1.1635→**1.1630** @n_eff_held 516,348·正负交替律如实：W67 −0.0001→W68 +0.0005→W69 +0.0000→W70 −0.0005）✓。
- **账本落账**：prev=**516,348**（W69 bm-c r361 活链头 derive·origin 时序面）＋2,200=**518,548 净链头**·K=**151,920**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。
- mu_delta_w70_vs_w69ext=**−0.005581**（单波跨度如实）；se_mu=**0.000628** @K=151,920（收窄链延续：W67 0.000642→W68 0.000637→W69 0.000633→W70 0.000628）。"""

S8_OLD = """## §8 批后复盘【必填·s7-T】

- （占位·finalize 后机械回填）"""
S8_NEW = """## §8 批后复盘【必填·s7-T】

- **全生命周期三窗闭环**：冻结 r568（席位 MSG-1040·双冻 bm-a 让路）→烧录 12/12（引擎 tick 自续·r569d ride c582c4289 收尾交付）→finalize r570 one-pass（W69 bm-c r361 同窗落账解锁后一过）。
- **链序面**：W68 bm-a r569 落账（514,148）→W69 bm-c r361 落账（516,348）→本波 W70 落账（518,548）→**W71（bm-c·12/12 烧毕）finalize 解锁**（bm-c 下一 one-pass）。
- **分叉面第三例披露义务履行**：B 带越 hit 起窗 51_001..51_200 采纳（读法二 51_101..51_300 披露不采）·F-20261002-03 钉死行仍待集团裁定·本波按「裁定前=机闸 derive+分叉披露强制」执行（W69 行明令三面满足：本件 §3+gate 回执+canon 行）；R250：W70 带从未指派·测量面零结果可钓。
- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307）。"""

assert t.count(S7_OLD) == 1, f'S7 anchor not unique: {t.count(S7_OLD)}'
assert t.count(S8_OLD) == 1, f'S8 anchor not unique: {t.count(S8_OLD)}'
t = t.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
open(FP, 'wb').write(t.encode('utf-8'))
print('W70 prereg s7/s8 backfilled (bytes-level, two-state r307)')
