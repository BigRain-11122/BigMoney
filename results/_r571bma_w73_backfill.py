# -*- coding: utf-8 -*-
"""r571 bm-a W73 prereg s7/s8 mechanical backfill (r307 two-state, bytes-level; r571 bm-b W72 pattern)."""
FP = 'research/PERPETUAL_N1_W73_PREREG.md'
b = open(FP, 'rb').read()
t = b.decode('utf-8')

S7_OLD = "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】\n\n- （占位·finalize 后机械回填）"
S7_NEW = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- **finalize 实烧=one-pass r571 bm-a**（r538 一过例·2026-10-02 11:2x·12 分片 shards_consumed 12/12·r310 完备性门 origin 12/12 ls-tree 过）：N=2,200（A 2,000＋B 200）。
- **S5 四门全过（§5 预测 4/4）**：① W73-only mu **−0.086294** 与 merged mu **−0.092169**（K=158,520）漂移 |Δ|=**0.005875**<0.02（对锚 W70 merged −0.092392 漂 0.000223）✓；② sigma 相对变化 **−0.88%**<±10%（W73-only **0.237653** vs 锚 0.239768=W70-only 实测）✓；③ A 族 full_sharpe_p95 **0.3011** vs 锚 0.3005（W70）|Δ|=**0.0006**<0.05 ✓；④ K-lift **−0.0004**≤0.02（1.1642→**1.1638** @n_eff_held 522,948·正负交替律如实：W69 +0.0000→W70 −0.0005→W71 +0.0002→W72 +0.0004→W73 −0.0004）✓。
- **账本落账**：prev=**522,948**（W72 bm-b r571 活链头 derive·origin 时序面）＋2,200=**525,148 净链头**·merged K=**158,520**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。
- mu_delta_w73_vs_w72ext=**0.000889**（单波跨度如实）；se_mu=**0.000615** @K=158,520（收窄链延续：W67 0.000642→W68 0.000637→W69 0.000633→W70 0.000628→W71 0.000624→W72 0.000619→W73 0.000615）。"""

S8_OLD = "## §8 批后复盘【必填·s7-T】\n\n- （占位·finalize 后机械回填）"
S8_NEW = """## §8 批后复盘【必填·s7-T】

- **全生命周期三窗闭环**：冻结 r570 cd2e57af6（SIXTY-SECOND 引擎波·bm-a 第 17 个 owned；同窗 W72 撞面让路 bm-b c7babddec=r511 commit 时序律）→烧录 12/12（r570 引擎 tick 自燃同轮全烧·ride 48833c775 shards 8-11 送达+r310 完备性面）→finalize r571 one-pass（W72 bm-b r571 落账 522,948 解锁后一过）。
- **链序面**：W70 bm-b r570 落账（518,548）→W71 bm-c r362 落账（520,748）→W72 bm-b r571 落账（522,948）→本波 W73 落账（525,148）→**W74+ 未登记**（引擎队列 0·never-dry 下一登记步=任意健康机 next free number）。
- **带位面**：A-ext seed **189_004..191_003**＋B-ext exit seed **51_601..51_800**（r570 冻结 gate ADMIT 回执；bm-b r571 收口窗 W73+ projection 双 CLEAN 交叉验证在案）。
- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307·缺省波调用 r522 律）。"""

assert t.count(S7_OLD) == 1, f'S7 anchor not unique: {t.count(S7_OLD)}'
assert t.count(S8_OLD) == 1, f'S8 anchor not unique: {t.count(S8_OLD)}'
t = t.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
open(FP, 'wb').write(t.encode('utf-8'))
print('W73 prereg s7/s8 backfilled (bytes-level, two-state r307)')
