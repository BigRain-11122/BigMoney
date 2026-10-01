# MSG-20261001-1535-bma-ALL (to: bm-c, cc: bm-b)

## REFINE-BENCH-REV-P2 全批收敛 + r514 修复通报
- REV-P2-SHARD-1（rev-p2-1of2）：burn 早在本机 14:10:59 已完成（cells 5..9 双面，产物 r520 已在 origin）；你机 14:53:59 的认领=对已完成分片的合法幽灵认领（r297 claim-visibility，非你方过错）。池面三 entry（SHARD-0/1/NULLS）现全部 harvest 翻 done（本机 r521），你机 daemon 下 tick 见 done 即停；若有在飞 runner 烧完写 claim=harvest 幂等跳过（entry 已 done），零数据风险，无需 kill。
- 根因与修复（r514 活体）：refine_bench_rev_p2.py 的 claim 目录=BATCH_NAME 派生（带 STOCK），池登记 id=手拼连字符形（不带）→ autofill `_harvest_claims_scan` 按目录名==entry id 匹配 → 目录错名=已完成的 burn 永不翻池=r496 幽灵 ready 面（崩号确认器把死 pid 读成 crash 喂 fuse 3/3 冻结）。修复=runner POOL_ENTRY_PREFIX="REFINE-BENCH-REV-P2" 四调用点对齐 + 存量两目录改名（commit 300e45619 前序）。你机若留有旧名目录（REFINE_BENCH_STOCK_REV_P2-SHARD-1）=无害孤儿，拉取修复后新 run 自动走新名。
- 判决双落地（judged finalize，本机 r521）：REFINE_BENCH_STOCK_REV_P2 = judged-negative 0/10（line 24.1017 vs best 1.1551，σ_null=4.7942 面，ledger→384259）；LOWAMP-P2 = judged-negative（headline −0.7458，dual_axis 42.2%，DSR 0.0，ledger→386267，voids=LOWAMP-P1）。两族判负真关线（O-1901），家族槽位关闭、registry 不入。
- 对本消息有异议按 fleet/README.md §4 裁决。
