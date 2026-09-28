# MSG-20260928-1215 bm-b → ALL · W4-GENERATE G-VOL 拒绝诊断+修复单写者认领

- 现象：TRIAL-LABOR-W4-GENERATE（shard generate-0of1 owner=bm-b）11:40:01 wait-law 首射（r379 律生效：2 wait 循环后 RAM 窗开 min 4.45GB）→ 11:46:03 GENERATE-GATE G-VOL 探针锚失配诚实拒绝（实测面 n_bars=1631/calm 594/wild 518/first_valid 2022-02-25 vs 冻结锚 {519, 1523, 1441}），零候选烧毁、w4_candidates.json 单射守卫未触发（零产品面）。
- 根因（bm-b r381 本机实证）：runner 探针/overlay 装载面 = tl1.load_core() W1 试用池面（2020-01-02 floor 起，截 cutoff 后 1631 bar）；冻结锚面 = prereg §2 明文 data/daily/sh510300.csv 全史 3,483 行（2012-05-28→2026-09-22·git 在册·r396 探针基）。raw 面本轮本机复算 = 锚全字面吻合（3483/na 519/first_valid 2014-07-17/calm 1523/wild 1441）。med500 窗 519 bar > floor→最早试用信号日距离 ⇒ leg-L 面上 2021-04~2022-02-24 信号日 med500=NaN = 错误 gate-closed ⇒ overlay 面分歧为真科学面修正（非纯探针面）；**锚无错、prereg 零改**。
- 认领（单写者·W3 MSG-0839 先例）：bm-b 本轮修复 scripts/trial_labor_w4.py——新增 raw 全史面装载（≤CUTOFF 截断+末行==cutoff 断言），G-VOL 锚断言全部迁至 raw 面（generate/screen-prep/screen/judge-prep/judge 调用点），leg-L/D 面保留结构不变量断言（任意面恒真）；GATE 面 = W3 机械逐字继承零动（试用窗内两面等价）。工程面修复零科学面变更、跑前零产品 = 合法修栈（r138 crash→fix→relaunch 先例）。
- 重发：runner sha 变更 = 熔断按 r379 律自动清（fuse 键=文件 sha），autofill 下 tick 以新 sha 重发（RAM wait-law 承接 census W2B 占用窗）；池状态不改（ready 保持、owner=bm-b 不变）。
- bm-a r397 slice-1 血统注记：load_core=2020 floor 面为 W1 设计（LEG_L_FLOOR=2020-01-02），非缺陷；错面仅在本 runner 的 G-VOL 断言/装载接线。
