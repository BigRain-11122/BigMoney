# -*- coding: utf-8 -*-
"""r571 W72 prereg s7/s8 mechanical backfill (r307 two-state, bytes-level; r570 W70 pattern)."""
import io

FP = 'research/PERPETUAL_N1_W72_PREREG.md'
b = open(FP, 'rb').read()
t = b.decode('utf-8')

S7_OLD = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- （占位·finalize 后机械回填）"""
S7_NEW = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- **finalize 实烧=one-pass r571 bm-b**（r538 一过例·2026-10-02 11:0x·12 分片 shards_consumed 12/12·r310 完备性门 origin 12/12 ls-tree 过）：N=2,200（A 2,000＋B 200）。
- **S5 四门全过（§5 预测 4/4）**：① W72-only mu **−0.087183** 与 merged mu **−0.092251**（K=156,320）漂移 |Δ|=**0.005069**<0.02（对锚 W68 merged −0.092331 漂 0.000080）✓；② sigma 相对变化 **+0.12%**<±10%（W72-only **0.249564** vs 锚 0.249272=W68-only 实测）✓；③ A 族 full_sharpe_p95 **0.3372** vs 锚 0.3153 |Δ|=**0.0219**<0.05 ✓；④ K-lift **+0.0004**≤0.02（1.1636→**1.164** @n_eff_held 520,748·正负交替律如实：W68 +0.0005→W69 +0.0000→W70 −0.0005→W71 +0.0002→W72 +0.0004）✓。
- **账本落账**：prev=**520,748**（W71 bm-c r362 活链头 derive·origin 时序面）＋2,200=**522,948 净链头**·K=**156,320**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。
- mu_delta_w72_vs_w71ext=**0.000428**（单波跨度如实）；se_mu=**0.000619** @K=156,320（收窄链延续：W67 0.000642→W68 0.000637→W69 0.000633→W70 0.000628→W71 0.000624→W72 0.000619）。"""

S8_OLD = """## §8 批后复盘【必填·s7-T】

- （占位·finalize 后机械回填）"""
S8_NEW = """## §8 批后复盘【必填·s7-T】

- **全生命周期三窗闭环**：冻结 r570（席位 MSG-1028-bmb·published=reserved r518-①）→烧录 12/12（r570 引擎 tick 自燃同轮全烧·bm-a 同窗草稿 FIX-A 拦截零烧让路=零仲裁 15 例）→finalize r571 one-pass（W71 bm-c r362 落账 520,748 解锁后一过）。
- **链序面**：W70 bm-b r570 落账（518,548）→W71 bm-c r362 落账（520,748）→本波 W72 落账（522,948）→**W73（bm-a·12/12 烧毕·r310 完备性已验）finalize 解锁**（bm-a 下一 one-pass）。
- **带位面**：A-ext seed **187_004..189_003**＋B-ext exit seed **51_401..51_600**（gate ADMIT 回执=results/_r570bmb_w72_band_gate.py；bm-a 让路 MSG-1036 双机互证逐位恒等=r530 族第 9 例确定性交叉验证·科学面零损失）。
- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307·缺省波调用 r522 律）。"""

assert t.count(S7_OLD) == 1, f'S7 anchor not unique: {t.count(S7_OLD)}'
assert t.count(S8_OLD) == 1, f'S8 anchor not unique: {t.count(S8_OLD)}'
t = t.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
open(FP, 'wb').write(t.encode('utf-8'))
print('W72 prereg s7/s8 backfilled (bytes-level, two-state r307)')
