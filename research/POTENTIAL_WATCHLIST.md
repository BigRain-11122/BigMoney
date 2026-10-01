# POTENTIAL_WATCHLIST · 潜力关注名单（GM 署名常设件 v1.0）

- 令源：CEO 2026-09-30 ~22:1x「很好，务必关注有潜力的」（O-2026-09-30-2230-bm-a）
- 律：**名单内候选=快速通道**——专用族 prereg 优先开烧（不排大波队）+ 过线即纸盘提案 + 判负如实出名单；进出=GM 署名（勘探双 nulls 支持/CEO 特选 进；judged 判负 出）
- 呈报：战报面常设「潜力名单」状态行（接线归运营部）

| # | 候选 | 当前状态 | 下一个判定点 | 证据 |
|---|---|---|---|---|
| 2 | **REV-OSC 超跌反弹袖**（首阳+熊市闸+止盈8%·持 7/10d） | 纸盘活面在跑（09-28 起）；个股面判决批 pooled 0.44-0.61<0.70 严格线（熊段 0.615 最强） | 纸盘出窗实绩仲裁 + 决策链版本台账通道注入 | REFINE-BENCH-20260926-P1 + results/rev_osc/ |
| 3 | **SYSTEM-V1 系统组合**（六员等权+仓位阶梯+袖+现金腿） | 纸盘活面在跑（09-28 起） | 纸盘实绩 + 10-31 月界首判 + 链 v3 锦标赛判决 | SYSTEM_V1_PREREG + 决策链台账 |

进出记录（append-only）：
- 2026-09-30 22:30：v1.0 建名单，入列 ①②③（GM 署名）。
- 2026-10-01 04:4x：①低振幅家族 **judged 判负出名单**（律=judged 判负 出·无需 GM 署名）——LOWAMP-P1 verdict=judged-negative（G1' −1.45 vs line 1.95·G2 DSR 0.0·双轴 CI_lo 0.356·x2 −3.64·M1 t=−3.68；G-SEG 过）；**注记=verdict 完整性 UNDER REVIEW**（bm-b r490 回填审计：入选员 511010+511260 raw 面 in-window +17.9%/+24.4% vs 判出 −18.0% ~39pp 不可调和·x2 隐含单笔成本 13×声明值→疑 runner 执行面缺陷·修复单 T-2026-10-01-135-P0·裁定前禁据本 verdict 作族间 meta 结论）；W∈[77,104] 语法带已消费（TRIAL_GRAMMAR_LEDGER LOWAMP-P1 行·禁重跑）。执行=bm-b r490。
- 2026-10-01 11:4x：①低振幅家族 **VOID 复列**（O-20261001-1108 §三 GM 裁决·T-140 bm-a 执行）——T-136 审计四腿定谳：judged 面烧的是「prereg 自相矛盾面」（ALWAYS-ON 家族定义×股票型引擎缺省出场栈=每 8-13 天强制换手 250 次·−33.9pp 磨耗把 +15.9% 设计面磨成 −18.0%），判负不归族；账本补偿回滚 2,008 试验（368,797→366,789 裁决刻·执行刻 raw head 379,847→377,839·ledger_voids 活跃·skill_line_v2 n_eff 面已净）；verdict 翻 void-with-face-note（杂交测量作 face-note 科学保留）；语法带消费随判回退（LOWAMP-P1 批本身禁重跑不变·LOWAMP-P2 新考卷=出场轴显式门首个应用重开该带）；E1 旗标解除（对账闭环无仪器缺陷）。
- 2026-10-01 16:1x：①低振幅家族 **P2 verdict 完整性 UNDER REVIEW**（bm-a r522 E1 四腿对账·r492 消费前闸）——LOWAMP-P2 judged-negative（r521 finalize）烧录面=出场中和未生效的杂交测量：runner 把 loss_time_days/global_hard_limit 两键写进 params 通道=死信（engine/backtester.py ExitConfig 桥只读 6 kwargs·该两键回落缺省 8d/25d）→缺省栈踢出 174/181=96% 换手（108 loss_time_stop+66 global_hard_limit+7 signal）；as-burned 复现与 artifact 逐位匹配+verdict headline 对账=仪器与 finalize 无罪；**引擎+ExitPatch 矫正面 +15.88%/夏普 +1.158（仅 7 笔信号出场）≈独立算术腿 +15.95%/+1.163=声明面为正**（T-136 Legs B/C 同式复现·P1 同缺陷族 r301 复发·根因=fixture 当年 ExitPatch 双键补丁被 copy-adapt 丢失）；证据=results/lowamp_p2/e1_three_leg.json；GM 裁决请求已发机队 inbox（O-20261001-1108 §三同式）；裁定前 ① 留名单、禁消费 P2 verdict 数字、禁出名单。执行=bm-a r522。
- 2026-10-02 04:xx：①低振幅家族 **judged 判负出名单（真判负·族设计面定谳·终局）**（bm-b r533 finalize+E1 消费门双过）——LOWAMP-P3 verdict=judged-negative（出场轴双通道修正面首烧实证生效：**census default_share=0.0**·7 笔全 signal_reversal=律 A 双门通过·与前两批 96-97% 缺省栈踢出对照=r522 根因修正闭环）；判据面=G1' line_ok=False（headline 夏普 1.158 vs skill_line_v2 **1.9722**·N_eff 461,348 净额面）+M1 t=2.945<3.0+DSR 0.2695<0.95+PBO 0.4857>0.25+双轴 642/1380=46.5%（CI_lo 0.4377<0.50）+x2 存活过+G-SEG 过；族正面如实记=收益温和为正（86.35% 正 12m 窗·零崩年·成本翻倍存活·sign-flip p=0.0035）但**跨不过机队级多重检验线**（bootstrap p_ge_obs 0.5035=正中 null 中心·sens 500 抽全带 p95 夏普 1.31 无配置近线）；E1 四腿 PASS+verdict-face **RECONCILED**（headline 与 legA artifact 1e-9 恒等·nulls 2000/2000 完备后补腿）；账本 +2,008（459,340→461,348）；**族键 lowamp_daily_xs 入 CLOSED_FAMILIES**（M3 终态·重开通道=新预注册新证据 delta·单批真判负先例=t28_spm_first）；W∈[77,104] 带存量维持禁重跑。执行=bm-b r533。
