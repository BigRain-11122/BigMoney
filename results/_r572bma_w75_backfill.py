# -*- coding: utf-8 -*-
"""r572 bm-a W75 prereg s7/s8 mechanical backfill (r307 two-state, bytes-level; r571 W73 pattern)."""
FP = 'research/PERPETUAL_N1_W75_PREREG.md'
b = open(FP, 'rb').read()
t = b.decode('utf-8')

S7_OLD = "## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】\n\n- （占位·finalize 后机械回填）"
S7_NEW = """## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- **finalize 实烧=one-pass r572 bm-a**（r538 一过例·2026-10-02 11:30·12 分片 shards_consumed 12/12·r310 完备性面 12/12 本地验属 bm-a 全绿）：N=2,200（A 2,000＋B 200）。
- **S5 四门全过（§5 预测 4/4）**：① W75-only mu **−0.104350** 与 merged mu **−0.092271**（K=162,920）漂移 |Δ|=**0.012079**<0.02（对锚 W73 merged −0.092169 漂 0.000102）✓；② sigma 相对变化 **+3.46%**<±10%（W75-only **0.245868** vs 锚 0.237653=W73-only 实测）✓；③ A 族 full_sharpe_p95 **0.3088** vs 锚 0.3011（W73）|Δ|=**0.0077**<0.05 ✓；④ K-lift **−0.0001**≤0.02（1.1644→**1.1643** @n_eff_held 527,348·正负交替律如实：W70 −0.0005→W71 +0.0002→W72 +0.0004→W73 −0.0004→W75 −0.0001）✓。
- **账本落账**：prev=**527,348**（W74 bm-b r572 活链头 derive·origin 时序面）＋2,200=**529,548 净链头**·merged K=**162,920**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。
- mu_delta_w75_vs_w74ext=**−0.016766**（单波跨度如实）；se_mu=**0.000606** @K=162,920（收窄链延续：W73 0.000615→W74 0.000611→W75 0.000606）。"""

S8_OLD = "## §8 批后复盘【必填·s7-T】\n\n- （占位·finalize 后机械回填）"
S8_NEW = """## §8 批后复盘【必填·s7-T】

- **全生命周期三窗闭环**：冻结 r571 695312330（SIXTY-FOURTH 引擎波·bm-a 第 18 个 owned；supply_floor 旗响应）→烧录 12/12（r571 引擎 tick 自燃 5/12 ride 96ac3f26c＋r572 ride 4aa61f425 shards 5-11 送达=r310 完备性面 12/12·audit.machine=bm-a 逐件验属）→finalize r572 one-pass（W74 bm-b r572 落账 527,348 解锁后一过）。
- **链序面**：W72 bm-b r570 落账（522,948）→W73 bm-a r571 落账（525,148）→W74 bm-b r572 落账（527,348）→本波 W75 落账（529,548）→**W76 bm-b r572 已登记在飞**（烧录中·finalize 未落账——该席落账后 W77 bm-a r572 冻结席 one-pass 解锁）。
- **带位面**：A-ext seed **193_004..195_003**＋B-ext exit seed **52_201..52_400**（r571 冻结 gate ADMIT 回执；W74 行 W75+ projection 双 CLEAN 交叉验证在案）。
- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307·缺省波调用 r522 律）。"""

assert t.count(S7_OLD) == 1, f'S7 anchor not unique: {t.count(S7_OLD)}'
assert t.count(S8_OLD) == 1, f'S8 anchor not unique: {t.count(S8_OLD)}'
t = t.replace(S7_OLD, S7_NEW).replace(S8_OLD, S8_NEW)
open(FP, 'wb').write(t.encode('utf-8'))
print('W75 prereg s7/s8 backfilled (bytes-level, two-state r307)')
