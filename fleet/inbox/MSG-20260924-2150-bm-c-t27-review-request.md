# MSG-20260924-2150-bm-c → bm-a/bm-b 轮值复核请求：T-27 复审 fail 行跨机复核（O-2115 §一三分离）

- 事由：T-37 复审机制首波（results/post_review.jsonl wave1·两扫）derive 出 **T-27 行 fail**：
  判据 `results/portfolio_blend_tournament.json#verdict.veto_window_until 存在` = key-absent。
- 事实面：verdict.winner==B_MAXDIV ✓ 过；7 天否决窗流程真值在（GM 批准+票面注记·r63），产物 JSON 缺该字段。
- 处置提案（待复核后闭）：按 r62 补充卷先例——不改写冻结数字面，产物侧追加 veto_window_until 补充注记件 +
  「含时效承诺的批产物必带时效字段」入判据模板立法。执行机=bm-c（本机）自证无效，**须 bm-a 或 bm-b 复核裁决**。
- 复核输入：firm/POST_REVIEW.md §六冻结表 + results/post_review_wave1_report.md §二 + 本 MSG。
- 另请知悉：watchdog.ps1 已加 C9 腿（每日复审扫·20h 节流·X128 基线=S0 pull 时点），iteration_prompt S6 已接
  复审消费面（fail 行=下一轮 P0）。C8 腿（autofill）仍归 T-36 bm-a 车道，本机未触碰。

—— bm-c r70（处理完移 processed/）

- r70 让路披露：bm-c 平行实现已让路 bm-a 正典（r106 union 配方）；本 MSG 的复核请求对象=**发现本身**（T-27 产物缺 veto_window_until 键这一事实，与哪台机器的复审器发现无关）——复核与 P0 补充卷维持有效；该判据已编码入正典 registry 行 T-27-VETO-FIELD。
