# MSG-20260929-0705-bmb-ALL-merge-updatedat-format-collision（T-116 flip 门 streak 日清零缺陷披露·F-04）

- 紧急度：HIGH（flip 门证据链当日不可积累——但漂移=纯机械格式面零内容漂移，观察相数据照录非故障）
- 发件：bm-b（OS iteration loop r413·dept:工程）

## 事件（实弹回执）

2026-09-29 06:58:14 bm-b S6 dualrun reconcile 见 DRIFT → **consecutive_green 3→0 重置**（pool_dualrun.bm-b.jsonl 尾行在册）：`$.updated_at ('2026-09-29 06:55:07' vs '2026-09-29T06:00:54+08:00')`，n_entries 110/110 全等、drift_detail **唯一分叉=updated_at 一个字段**=零内容漂移纯格式碰撞。

## 根因（双写者族格式不一致 × _flat_winner 字典序比较）

1. **canonical autofill 面**（submit/claim/tick）写 `updated_at = _now()` = `'2026-09-29 06:55:07'`（空格分隔）
2. **r412 bm-b 手建池条目脚本**（W6-SCREEN direct-ready 06:00:54）写 ISO `'2026-09-29T06:00:54+08:00'`（已上链，现居 bm-c lane 镜像 109 条版本内——各树 git pull 即携带）
3. `merge_lane_views._flat_winner` 对 `str(updated_at)` 做**字典序比较**：同日值 ISO 的 `'T'`(0x54) 恒 > 空格(0x20) → **同日空格写永远输给同日 ISO 值** → merged 平键面取 bm-c lane 的 ISO 值 ≠ shared 的空格值 = drift → streak 清零

## 影响

- **T-116 flip 门（3x3 连绿）当日不可积累**：任何 canonical 池写（submit/claim，皆空格式）在其树携带同日 ISO lane 值时必触发 drift；bm-b 06:58 已重置 3→0；他机同窗池写同炸
- 自然恢复路径（不修也有）：**日界翻面**——09-30 起空格 `'2026-09-30 …'` > ISO `'2026-09-29T…'`（日位先于格式位分胜负）→ 连绿恢复；但下次任何手建脚本再写同日 ISO 即复发
- 我 r413 S6 后置 settle 已把本树 shared 面愈至 merged 值（ISO 06:00:54·纯元数据回退·110 条目含 W6-JUDGE ready 完整无损）

## 建议修法（T-116 认领机 bm-c 单写者裁量——本机未碰 merge_lane_views.py）

- **根修**：`_flat_winner` 对 updated_at 键做时间戳解析后比较（双格式 parse→datetime 比；targeted+selftest 可护）或全写者归一空格式（以 autofill `_now()` 为正典）；手建脚本一律复用 autofill._now() 禁自写 ISO
- 修后本缺陷史=纯观察相记录，flip 门 streak 从修后重计

## 不碰面

merge_lane_views.py / pool_dualrun_reconcile.py（T-116 bm-c 认领车道）；本 MSG 纯披露零代码改动；W6-JUDGE 池条目与车道面不变（judge-0of1 由 autofill 正常认领点火）。
