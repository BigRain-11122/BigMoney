# QA · book_pair_weight_rule · r2180

## 本司清单

| 项 | 判据 | 结果 | 证据 |
|---|---|---|---|
| 能跑 | `run` / `check` / `selftest` 三入口 | PASS | `run` 出 JSON+MD（6 臂 walk + 4 臂 fixed + 半窗检验）；`check` rc0 `{"ok": true, "problems": []}` |
| 算术自证 | selftest 全绿 | PASS | `selftest: 19/19 PASS`（A 成本/回撤、D 付费 vs 免费路径、E 持有、F 摘要、G 短切片、H check 契约三态） |
| 已知真值对账 | 与父面 `book_pair_blend` 已发布 Sharpe 1e-6 内一致 | PASS | `reconciliation.diff_full_window = +0.0000`、`matches_published=true`（1.066 vs 1.066） |
| 规则不重写 | 只 import 父面加载器，权重读 `best.w_cb` 不重选 | PASS | `target` 字段记 `face/field/why`，本面无权重搜索代码 |
| 漂移可检 | 父面板字节或公布权重动 → STALE + rc3 | PASS | selftest H1/H2/H3 三条行为腿（正常 rc0 / 父面板动 rc3 / 权重动 rc3） |
| 一份测量只印一遍 | `page_repeat_guard scan` | PASS | `[repeat] 4 face(s) scanned, 0 repeated sentence(s)` |
| 未验证如实 | 节奏/回看同窗挑选、trailing 噪声、父面偏差 | PASS | 面内 `unverified[6]` 与 MD 末节逐条印出 |
| 不合成数据 | 无缩放/置换/造年；只做 `b/a-1` 与权重加权 | PASS | `method.no_synthesis` + 代码路径 |

## 本轮两处自捕（都改了，不是记下来就算）

1. **同一句测量在页面上印了两遍**（r1911 族）：`## The arm that needs no hindsight at all` 一节先手写前缀「A neutral 50/50 … earns Sharpe …」，再把 `naive['sentence']`（同一句话）接在后面；而 verdict 段末尾也拼了同一个 `naive['sentence']`。于是 50/50 那一组数字与结论在一页出现两次。改法：verdict 段改成一句不含数字的指向（"It also loses to a plain 50/50 … (that arm is scored below)"），专节只印 `naive['sentence']` 一次。改后 `s.count('A neutral 50/50') == 1`，守卫 0 repeated。
2. **`run` 与 `check` 的窗口口径不同，读的时候容易混**：verdict 里 `hold 30/70 paid quarterly` 是 **1.224**（计分窗 2021-02-01 起、1409 bars），而页面上那张「页面印的数」是 **1.065**（全窗 2020-01-03 起）。两面都对，差的是窗口。已在 MD 的两张表头分别写明「every arm scored from 2021-02-01」与「FULL window」，并在对账节点明 `+0.1580` 的差来自窗口不是来自书。

## 未完成（如实）

- **未跑全量冒烟**：10 分钟轮窗装不下 ~1142s 套件；本轮只跑了链腿与本面 selftest，**禁读成套件已全绿**。
- **冒烟腿待补**：本轮把它写进 `smoke_test.py`（见提交），但补腿后未复跑全量套件验证新腿在真数据上变绿——下轮首件事是 `python -m smoke_test` 全量确认。
- 成本仍不含税、标的内买卖价差、整手网格、净值-交易价差（面内已列）。

## 结论

面可跑、可看、算术自证与父面 Sharpe 对账全绿，判词 `THE_RULE_LOSES_TO_HOLDING_THE_SPLIT`（规则 1.103 < 固定 30/70 的 1.224，也 < 无后视 50/50 的 1.161）已发布到 `results/book_pair_weight_rule.md`、`research/BOOK_PAIR_WEIGHT_RULE.md`，并接进 S6 链腿。**未跑全量冒烟 = 未完成全部收口**，如实留账。
