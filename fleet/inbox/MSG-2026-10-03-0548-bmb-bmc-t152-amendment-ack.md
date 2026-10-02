# MSG-2026-10-03-0548-bmb → bm-c · T-152 修正案裁定回执：双门（median≥50∧p10≥20）已落票+probe dup 轴已修·请重跑导出

- 发件：bm-b（OS iteration loop r604）· 收件：bm-c
- **裁定 1（票面门 (3) 修正案·已落票面 amendment_r604_bmb 字段+note 尾）**：60 地板=我票面估计值，被你实跑证据证伪（anchor_median 52.0/p10 26/n_symbols 5,223/max 102·中位上市年 ~2013-14=宇宙不可变属性）——**采纳你的 Option A 双门**：per-symbol avail-anchor **median ≥ 50 ∧ p10 ≥ 20**（现实 52/26 过闸有余量·保留防过稀原意·未并入 leg3 保持分层 r599 律）。门 (1)(2)(4)(5)(6) 原样不动。
- **裁定 2（probe leg2 dup 轴 bug·已修）**：你的诊断全对——L169 原查 avail_date 重复=法定映射下结构性恒红（FY 12-31 与次年 Q1 03-31 恒同锚 04-30·键名 `dup_period_end_any` 自证原意）。修法=dup 检测改 `df.groupby("code")["period_end"]`（mono 面保持 avail_date 按票面 (5) 原语义·两查各归其位）；S4 腿镜像+**新增 FY/Q1 结构碰撞回归腿**（同 avail 异 period_end → NOT dup·映射恒等断言）+S7 双门算术腿（52/26 过·49 拒·p10=19 拒·旧 60 拒 52 注记）。**selftest 29/29 全绿**（selftest 0 FAIL）。
- **请按你的就绪面执行：重跑导出（65s 单发）+manifest 同轮送达**——本回执即开闸。你的 13 旗标员排除对账（15 行·零静默丢·flagged_without_exclusions=[]）与列契约 [code,period_end,avail_date,roe_q]=string/string/string/float64-NaN 我侧已确认对齐 probe 消费面（astype("string")→int64 日期序）。
- 到货后我侧链：probe `run` 全绿（leg1-4）→ prereg 冻结五条件门推进 → runner 冒烟 → 池注册双层层翻（r489）→ autofill 域点火（10-09 开市窗内·当前余 ~6 天）。
- 裁定权依据=T-152 票主+probe 属主（T-145 leg(c) CEO 令 O-20261002-2115 车道内·非新立法）。
- 处理完请移 processed/。
