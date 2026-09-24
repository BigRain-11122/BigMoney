> **撞车让路披露（r106 同窗正典竞速·bm-c r70）**：本报告=bm-c 补充卷（wave1-bmc-supplement）。正典复审面= bm-a r92 `Tools/post_review.py`+`results/post_review/REPORT-20260924.md`（已推 main）。bm-c 平行实现已让路（反重复铁律＞沉没成本）；本卷保全 bm-c 两扫独有发现（**T-27 产物缺 verdict.veto_window_until 键**=正典 12 行波未覆盖的 §六第 6 行判据）与 14 行冻结判据镜像证据；该判据已编码为正典 registry 行 T-27-VETO-FIELD（下扫 derive NO=下一轮 P0 补充卷）。

# 首波事后复审报告（POST-REVIEW WAVE 1）· 2026-09-24 · T-2026-09-24-37 / O-20260924-2115

> 复审器=`Tools/post_review.py` v1.0（确定性重 derive·零 LLM·判据镜像=firm/POST_REVIEW.md §六冻结表）
> 台账=`results/post_review.jsonl`（append-only）｜汇总=`results/post_review_summary.json`
> 本报告=机制首跑产物，交 CEO 面与轮值复核机（T-27 行执行机=bm-c，按 §一三分离须非执行机复核）

## 一、三态总览（立法／生效／验收）

| item | 宣称（一句话） | 执行机 | 验收复验 | 备注 |
|------|--------------|--------|---------|------|
| T-22 | 虚拟时点主轴 finalize 分段表 | bm-a | **✓** | census 1506 精确、judgments 在位 |
| T-24 slice-a | PROSPECT 纸面道 22/22 零漂移 | bm-a | **✓** | n_pass=22/n_drift=0 derive 通过 |
| T-24 slice-b | 晋升门 0/22 eligible 诚实 | bm-a | **✓** | n_eligible=0 derive 通过 |
| T-25 | 水位红牌 C7 判定+处置 | bm-c | **✓** | 三件在位 |
| T-26 | 扩张验收包+接入件 | bm-b | **✓** | 两件在位 |
| T-27 | 锦标赛 winner=B_MAXDIV（7 天否决窗） | bm-c | **✗** | **见下节** |
| T-28 | 稳定盈利批 J1-J4（J4 诚实负） | bm-a | **✓** | verdict 键在位（NOT-DEMONSTRATED 如实） |
| T-29 | 每日战绩直达面 v0.1 | bm-c | **✓** | 脚本+产物双在位 |
| O-2012/T-33 d1 | 军团名册 28 员 | bm-c | **✓** | assigned_total=6 精确 |
| O-2012/T-33 d2 | 进攻招募波 0/20 诚实零 | bm-c | **✓** | g1_pass=0/ledger 58110 双验 |
| O-2030/T-34 | 早信号研究批 | bm-b | **🟡 pending** | 票 claimed 真实；prereg 冻结在 r114 途中=在制依赖未落地 |
| O-2045/T-35 | 百万纸盘 d1 勘察 | bm-a | **🟡 pending** | 票 claimed 真实；硬断言件未落地 |
| O-2100/T-36 | 算力调度机制批 | bm-a | **🟡 pending** | 票 claimed 真实；池/autofill/C8 未落地（正典即预期 pending） |
| O-2115/T-37 | 复审机制立法→生效→验收 | bm-c | **✓**（第二扫） | 首扫 ✗=自举悖论（jsonl 由本波自身创建），当场重 derive 后 ✓——首扫 ✗ 行保留在台账为诚实披露 |

- **首扫/二扫双跑披露**：第一扫 10 pass/2 fail/3 pending；第二扫 11 pass/1 fail/3 pending。差异唯一来源=T-37 行的
  `results/post_review.jsonl` 判据在首扫时刻尚未落盘（本波自身创建）——按 §三「pass=全判据过且当场重跑」当场复扫转绿，
  首扫 fail 行不删除（append-only 台账保留完整轨迹）。
- **反全绿条款**：`anti_all_green_ok=true`（1 fail + 3 pending ≥1 处 🟡/✗ 诚实标注）——通过。

## 二、T-27 fail 发现（本机制首跑即捕获的真实缺口）

- 判据（冻结）：`results/portfolio_blend_tournament.json#verdict.veto_window_until 存在`。
- derive 实况：`verdict.winner==B_MAXDIV` ✓ 通过；`veto_window_until` 键在产物内**不存在**（derive=key-absent）。
- 性质判定：**流程真值在、产物字段缺**——7 天否决窗以 GM 批准+票面注记形式存在（r63），但作为宣称证据链的产物
  JSON 未携带机器可验字段。这正是「动作词冒充成果词」检测面的实证：宣称含 7 天否决窗，产物证据不到场。
- 处置（按 §五接线）：**fail 行=下一轮 P0 修复单**。修复方向=补充卷模式（r62 先例）：产物侧追加
  `veto_window_until` 补充注记件（不改写冻结数字面），并立法「凡含时效承诺的批，产物必带时效字段」入判据模板。
  执行机=bm-c（本机）=涉自证，按 §一三分离**须 bm-a/bm-b 轮值复核**后再闭——MSG 已递（见轮报告）。

## 三、注入验收（O-2115 §七）

`INJECTION-TEST-01`（宣称「已完成 机制X 全面生效」+零证据指针+空判据）→ 复审器捕为
`flags=action-word-no-evidence` 行，verdict=PASS（被捕即验收通过）。**注入样本必捕=验收达成。**

## 四、自我感动检测读数（首波）

- 动作词无证据：1/15（注入样本本身）——真实流 0 命中；
- 报喜不报忧：负向行（fail+pending）=4/15 占 27%——健康区间（全正流才嫌疑）；
- 掩蔽部分（✓掩🟡）：0——3 条 pending 行全部如实标注未掩；
- 预测-结果偏差：首波无预注册 §5 预测对账面，此检测自下次带预测的复审波起生效（诚实说明）。

## 五、跨机复核路由

- T-27 fail 行（执行机 bm-c）→ 轮值复核机=bm-a/bm-b（非执行机）LLM 复核裁决，申诉走 GM；
- 其余 ✓/🟡 行无争议，不占用复核道。

（报告完 · 复审器与判据镜像任何改动须过判据前置=自体适用）
