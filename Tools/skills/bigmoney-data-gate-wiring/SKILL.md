---
name: bigmoney-data-gate-wiring
description: BigMoney S6 数据采集 gate 脚本接线范式（update_*.py 家族契约）。Use when 新增/修改任何数据拉取器入 S6 维护链、设计零网络 no-op 门/分离后台刷新/checkpoint 断点续拉/conn-fuse/overlap 校验/exit-code 契约、写 selftest 子命令、或处理车道归属护栏（R31 仅 owner 机动作）。
---

# BigMoney 数据采集 gate 接线范式（bigmoney-data-gate-wiring）

S6 维护链成员=gate 脚本（`scripts/update_*.py` 家族），契约全家族同构。参考实现按复杂度取：`update_futures.py`（canonical 简式·全史一发+日截断 no-op 门）、`update_lhb.py`（披露窗≥17 时守卫）、`update_options.py`/`update_moneyflow.py`/`update_sina_mf.py`（分离后台全宇宙 pass+checkpoint+熔断）、`update_ths_panel.py`（源形状漂移旗标）、`ah_panel_puller.py`（逐对 checkpoint+交叉验毒）。spec 恒在 `research/shortline/<SPEC>.md`。

## 契约十律（新 gate 必须全过）

1. **零网络 no-op 门**：本地面板新鲜（complete 且 cutoff 覆盖预期完整 bar 日——15:30 完整性约定+本地 ETF 交易日历主源）时=exit 0 零网络 no-op；当日已采/周末/<30min 节流=合法 no-op。禁无条件全量拉取。
2. **分离后台刷新**：首拉/未完备=spawn 分离进程全宇宙 pass（限速 2.5s 级+checkpoint 断点续拉+锁+30min spawn 节流）；gate 本体立即返回 exit 0（已 spawn）不阻塞 S6 链。过期（cutoff 落后 20 交易日）=refresh-repull done-reset 全宇宙复拉。
3. **overlap 行级校验**：增量追加前对重叠行逐行比价（tol 1e-6 级）；失配=旗标+**本地不动**（源改史=诚实拒收，exit 3 披露）；retry≥3 pass=mismatch_stale 隔离。
4. **exit-code 契约**：0=正常/no-op/已 spawn/刷新在途；2=源失败/机制故障（原样上报勿掩盖）；3=源改史 overlap_mismatch（本地不动）。refresh 分离进程：0=完备；2=未完备（checkpoint 保全）；3=完备但有 overlap 失配。禁吞错禁改码。
5. **车道归属护栏（R31 判例）**：仅 owner 机动作（认领 commit 为凭），他机 stdout-only 诚实 no-op 零共享态写（R65 律）；`fleet/machine.json` machine_id 比对。
6. **原子写+完备守卫**：.tmp+os.replace；dedupe by date；严格递增日期；no-NaN 校验门；行壳防御（R58）。终态 cutoff 从面板字节 derive（零符号轮禁 None 覆写真值·R237）。
7. **conn-fuse**：连接级 3 连败停发（阻断解除后自愈）；禁依赖「短冷却」假设（EM 子域 IP 级持续阻断实证 F-06）；一切拉取 checkpoint 续拉勿从头重来（F-08 车道律：非 owner 重启共享链=结构性毁损）。
8. **窗口守卫**：交易日 09:15-15:30 禁拉+bar 未落禁拉+未记账周中日保守禁拉（面纪一致性律防错标日）；date-stamp=最后完整 bar 日。
9. **selftest 子命令**=离线守卫测试（禁网络禁写盘），smoke 注册 exit-code 契约断言；心跳/status 件在拉前写（crash 中途仍节流·r18 教训）。
10. **S6 链登记**：新 gate 入轮 prompt S6 链位次+`python -m smoke_test` 注册行；批纪律=数据道纯采集零回测零引擎（前向史≥12 个月才准新 prereg·T-67 §2 冻结律）。

## 数据源勘察先行

新源开工前先做源审计：子域分块诊断（EM push2/datacenter-web/emappdata 互不可证·F-06）、替代源备好、单探针验证后扩面（P-C 管线先例）；源改史面=改史旗标不本地重写。**ETF/基金价格面动量读数必加基金份额折算/拆分事件守卫腿**（512480 r60=−62% 级畸变实证·r239 律族）。
