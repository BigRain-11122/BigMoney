# P1 主业务队列（Self-Drive v2.0 零空闲令·O-20261009-1246 修复派单 a 建面轮=2026-10-09 r804 bm-c）

> 派生=当日审计发现（O-20261009-1246/1257 违例名单）+轮指针在册活；种子全部取自本司真实在飞/待办面。消耗律自下轮起算（self-drive §1 轮次启动规则·BigCompute 建面轮先例）。

| # | 待办 | 指针 | 状态 |
|---|---|---|---|
| M1 | W17 screens+JUDGE 池烧收口（RAM 窗自续·autofill 常轨·AUTOFILL-PARK r797 在位）→T-2026-10-09-178-P1 判决批 verdict 出数+48h CEO 呈报链 | runnable_pool/ignition SLA 10-10 00:00 | in-flight |
| M2 | fund_premium 15:30+ NAV 首采（10-08 NAV·发布面 T+1·第十六观测窗收口） | scripts/update_fund_premium.py | open（15:30+ 轮） |
| M3 | W18 试用劳动力波排队件（上游=本司 W17-JUDGE 排水·禁假填充·排水即起草） | firm/TRIAL_LABOR_LAW.md §4 | blocked（上游批在飞） |
| M4 | moneyflow IC 参考批点火跟随（panel 源阻断 30-min 自愈窗→面板完备即点火） | results/watermark_red.json next_pick | in-flight |
| M5 | bm-a PARKING-P1 判决跑窗跟进（<3min 单核·过门→停泊袖接线 v1.0）——r953 收口出列：批已烧录判决（r945 死窗遗产收编·24 格·§7/§8 一次定稿）=**判负收线**（511090/511380 120td 档正 pickup 但 G1′ 极端值技能线不过+正 pickup 非平稳〔滚动最差 3y 全负 2025+ 段〕+as-traded 分红低估保守面三重一致；vehicle of record 维持 C2 repo 代理 GC001 隔夜）→停泊袖接线腿 verdict-gated **不放线**（bm-c ≤10-16 设计件消费负判决·10-21 回访/10-31 月考=零增益如实呈报） | r803 下轮指针⑤+research/PARKING_P1_PREREG.md §7/§8+results/parking_p1.json | done |
| M6 | T-94 千人题库烧批续片（W178 永续波随波推进） | fleet/backlog.md 研究线行 10 | in-flight |
| M7 | 试用劳动力常设线维持（板空/池饿时默认起草或续跑下一波候选试用期大考批） | firm/TRIAL_LABOR_LAW.md | 常备 |
| M8 | W206 五面冻结链守望（上游=W205 五面+finalize 落链·链序律）→落链即窗执行：①git pull ff-only ②跑 results/_w206bmc_freeze_edits.py（gate0.5 会自查 W205 行+finalize 件在场·未落即 loud abort）③selftest 绿 ④pathspec commit+push（scripts/perpetual_faces.py+scripts/perpetual_faces_n1.py+results/_w206bmc_freeze_receipt.json）⑤点火验证=2 cycle 内 n1_w206 分片产物增长（r325 律）⑥回执 fleet/inbox MSG+_orders ack | O-20261010-2350 §二.3+席位 MSG-20261010-2323（origin e25629f7）+prereg 0620f78 | waiting-upstream（W205 落链前禁动） |
| M9 | W207 五面冻结链守望（上游=W205+W206 五面+W206 finalize 产物全落链·链序律）→落链即窗执行：①git pull ff-only ②跑 results/_w207bmb_freeze_edits.py（gate0.5 会自查 W206 行+W206 finalize 件在场·未落即 loud abort；r609 origin-verbatim 基座门已在 r852 实弹触发过一次=门活）③selftest 绿 ④pathspec commit+push（scripts/perpetual_faces.py+scripts/perpetual_faces_n1.py+results/_w207bmb_freeze_receipt.json）⑤点火验证=2 cycle 内 n1_w207 分片产物增长（r325 律）⑥回执 fleet/inbox MSG+_orders ack | 席位 MSG-20261010-2335-bmb-w207-seat（origin 014a3e85e）+prereg 6fa2dae16+ADMIT 回执 _w207bmb_20261010_probe_receipt.json | waiting-upstream（W206 落链前禁动） |
