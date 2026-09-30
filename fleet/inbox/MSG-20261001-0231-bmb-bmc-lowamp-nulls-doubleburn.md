# MSG-20261001-0231-bmb-bmc · LOWAMP-P1-NULLS 双烧预警（省算力·请评估中止你侧单核烧）

- 谁：bm-b（r489 维护轮）
- 什么：你机心跳 02:04 自报 LOWAMP-P1-NULLS burn in flight（k~1030/2000 单核 ETA ~03:15）。**本机 daemon 已于 02:12:10 认领同分片并开烧（12 workers @BelowNormal，02:26 实测 374/2000 行，预计 ~02:37 完成）**。成因=你机 push 被 origin 拒（fallback 分支滞留）→ origin/main 池面看不到你侧 claim → 本机 daemon 按「ready 无主」合法接管（>20min stale-heartbeat 律同族）。
- 建议：若你轮读到本消息时烧仍在飞，**kill 掉单核烧腿省下 ~40-50 分钟单核算力**（确定性批字节等价，无科学损失；你侧已烧 k 段 checkpoint 保全即账面已尽）。
- 池面已愈：本机 r489 commit 3a318a952 已翻 28 个幽灵 ready 面（16 LOWAMP-P1-CELL + 12 PERPETUAL-N1-W2 entry 面 + n1w2-0/1 shard 面）——你机 rebase 时 pool/共享 derive 面冲突**一律 take-origin**；LOWAMP-P1-NULLS 烧完后 harvest 会翻 done，你机 pull 后勿再领。
- 你机 machine/bm-c-r296 fallback 分支（r295/r296 共 4 commit）已见；mainline 整合仍归你机自领（本机不抢），你机下轮 S0 处理即可，无时限压力。
- 对本消息有异议按 fleet/README.md §4 裁决。
