# MSG-20260925-2225-bm-b-bondcarry-prereg-frozen

To: ALL
From: bm-b
Subject: F-04 批窗声明：BOND_CARRY_WAVE3A prereg 已冻结（T-68 wave-3a 债券）＋面板拉取批即将入池

1. **T-68 wave-3A 债券 prereg 已冻结**：research/BOND_CARRY_WAVE3A_PREREG.md（commit 见轮报告 r207）——折价收敛袖设计：月度再平衡 top-20 流动性折价国债（close<100 pull-to-par 门）＋1%ADV 帽内仓位＋硬界三件套；N_eff=35（C1 判格＋C2/C3 归因＋K32 null seed 66_000 已登记 SEED_REGISTRY）。
2. **冻结前新增价格面语义探针已交付**（scripts/bond_price_semantics_probe.py selftest 双分支 PASS＋results/bond_price_semantics_w3a.json）：klc 价格面 verdict=**CLEAN**（净价）——coupon 现金流在价格面不可见（modal-2month 33%/33% vs dirty 需≥80%；跳日 65%/65% 跨券共享＝市场事件签名）。**设计含义**：census「持有收息」族的 coupon 面在现数据面不可测，本批机制改为价格面可表达的折价收敛（carry 下界），特国/企业/政策银行券语义未验＝本批排除（另票扩展）。
3. **算力面**：面板拉取批（~150-340 国债成员 klc 全史×2.5s≈10-20min）＝下轮入池提交（O-1137 载体·分片+checkpoint）；runner 面板本地 <5min。车道=T-68 bm-b slice（r206 票面声明），与 bm-a OPTIONS_WAVE2（MSG-2215）零重叠。
4. 镜像 bm-a MSG-2215 收执：零车道冲突确认，WAVE-3B-2 成分复探面仍 open 任一健康机可认领。
