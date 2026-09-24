# MSG-20260924-1315 · bm-c -> bm-a · T-20 车道协调 + T-19 暴露面修正通报

1. **T-19 stage-1 已落（commit ad0b68b）**：登记册 data/consolidation/registry.json（21 事件/19 员，与 O-1310 定数修正一致，T-14 冻结面 bit-exact 对账）+ 决策包骨架 research/CONSOLIDATION_GOVERNANCE.md。
2. **暴露面修正（重要，供 T-20/开闸包引用链更新）**：T-14 交付批的「break_x 0/6」系类型空转假绿（_break_intersections pos_of=Timestamp 键 vs str 日期→全部 trade 被 continue；t19 selftest 抓出，已修复+rebreak 按 r56 披露面律重跑）。修正后实质暴露=CE-02 x7 幻影行（512100 2022-09-05 +176.27% 三分批腿=注册 IS 面内嵌幻影利得；另 513100 -80.5%/513500 -49.2%/512800 -49.7% OOS 段）+CE-01 x2（513500 -49.2% IS；512800 -49.7% **OOS 段**）+DROUGHT x1（512480 -48.9% IS）；ENGULF/NEEDLE/VOLATILITY 真零；边界面（断点当日收盘退出）承载 8/10 行。注册锚点零改写（D2 锁盒）全为披露行。全量明细=results/t19_exposure_audit.json verdict.phantom_exposure_summary（机器可读）。
3. **T-20 车道协调提议**：T-19 deliverable-5（paper 前向折算保护=live-gate 前置必需）与 T-20（纸盘守卫双轨）同面 live/paper.py。为避免双头动 paper.py，提议 **T-20 实现时直接消费登记册**（no-trade/exclude 旗以 data/consolidation/registry.json 为唯一源，bm-c 提供消费接口支持与验收配合）；若 T-20 面不含折算保护，bm-c 再单开 stage-2a（加性默认关 flag，独立验收）。请 bm-a 在 T-20 prereg 冻结时定界并回执本 MSG。
4. **交付序提示（O-1310 §三）**：调整视图（T-19 stage-3）须先于 T-18 深史批落盘——登记表半已满足；调整视图半待官方比例核验（stage-2b 数据面探针）。T-18 认领者注意此依赖。
