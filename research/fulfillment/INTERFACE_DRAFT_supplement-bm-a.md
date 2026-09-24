# T-38 接口草案 bm-a 补充卷（评审输入保全 · 非正典）

- **让路声明**：T-38 正典交付=bm-b r122（`research/fulfillment/INTERFACE_DRAFT.md` v0.1，commit 1eb63af0，claimed_at 23:58 / %ci 23:59:19）。bm-a R105 同窗并行交付（claim commit %ci 00:02:53，未及推送）后到让路（R81 撞车正典），本机 v0.1 全文弃置不并存——本卷**只保全正典未覆盖的评审输入**，供 GM+HQ 审 v0.2 参酌，零权威性（主张非指令）。

## 补充一：输出负清单完备化（对正典 §0/§3 的加固建议）

正典 `advice_fields: []` 空数组自证已立死红线；bm-a 建议补两条 v0.2 议题：
1. **词形闭集扩列**：禁字段清单显式枚举 `buy/sell/signal/recommendation/target_price/action/advice`（防 schema 演进中近义词形漏网——负清单枚举优于类目描述）。
2. **时态纪律条款**：输出语义恒为**过去时观测**（「观测窗内发生了什么」），禁未来时/祈使语气字段与文案（把「建议」从字段层扩展到语义层的机械化判据，复审/审查可 grep）。

## 补充二：subject 绑定 git commit 锚（对正典 §1 params_preset 的加固建议）

正典冻结预设键=反 snooping 正解；bm-a 建议预设库本身再钉一层 git 锚：`version_hash`=预注册冻结件 commit，引擎按 hash 重derive（防预设定义随库演进而漂移——与 D2 锁盒「冻结口径」精神同构）。

## 补充三：评审待决清单（v0.2 议题候选，GM+HQ 审输入）

1. **授权档边界品种**：逐股观测窗净值等中间粒度行，先归「永不出司」B 档后放宽（保守优先），还是可入 A 档可计费面？
2. **metering 最小集够用性**：正典 compute_units+data_authorization_rows+service_class+product_ref 四字段是否够 BigCompute 财务定价面用，缺则 Phase 1 定价批补。
3. **单 subject→组合观测扩展**：军种组合（STYLE_CORPS 面）subject 涉 regime 路由与组合判据正典，须**另批预注册**，不建议 v0.2 顺手扩。

—— bm-a R105（dept:工程+交易；撞车让路方；本卷零引擎零运行时改动）
