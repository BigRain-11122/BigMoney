# r295 bm-b 账本完整性修复档案（CN-TREND 败方双计 + CENSUS 三连同批 append 链修头）

**发现轮**：bm-b r295（2026-09-27 04:1x，5x 核对轮·bm-a r290 HANDOVER 行明示「实读平衡沿 bm-b 核对纪律待其下轮」=本轮法定职责）

## 实读证据（全部本轮实弹）

1. **CN_TREND_ETF_P1 同批双计 +2,007**
   - bm-a 正典收割 03:27:59（commit 6151dabb：finalize ok 4670.9s/2007 units/**ledger 207425**/attrition row 53）；
   - 本机败方烧批 pid 10544（r286 01:40 点火）在 r288 认领竞速裁定后**未被物理终止**，跑到 03:42:52 二次 finalize（elapsed 7360.8s，logs/autofill_CN-TREND-ETF-P1.log 尾行「finalize ok: cells=7 **ledger=209432**」），同批再 append +2,007 上链 209,432；
   - 覆写产物经 r293 commit（1f30f2f4）静默入 main（提交面无 trials_ledger 断言）。
2. **CENSUS_FUS_S2_W1 同批三连 append +9,036 幻影**
   - attrition 权威序列：CN_SOE 02:06:20 =191,864 → CENSUS 行声明 +4,518 但记 ledger_total_after=**205,418**（实际跳 +13,554 = **3×4,518** 整）；
   - 幸存产物 prev=200,900 = 191,864+2×4,518（即第三发 append），全 results 树无任何文件载 total∈{196,382, 200,900}（中间态同文件覆写灭迹）；
   - runner 单次 finalize 单次 append（census_fusion_s2.py L646）→ 三连=三次完整重跑重 finalize（relaunch/re-claim 族，与 CN-TREND 同族）。

## 修复（R252 链修头先例：移锚不动 4dp 科学值·零重跑·零判定变化）

| 件 | 修复 |
|---|---|
| results/cn_trend_ETF/p1_results.json | 先字节级还原 bm-a 正典（git checkout 6151dabb --，科学面逐键 diff=仅 ledger/n_eff 面与 runtime 元数据），再链修头 prev 205,418→196,382、total 207,425→**198,389** |
| results/census_fusion_s2/w1_results.json | prev 200,900→191,864、total 205,418→**196,382**（audit.ledger_trials_added=4,518 不动=本来就对） |
| results/gate_attrition.json | 幻影行（ts 03:42:52/209,432）字节级移除（54→53 entries）；CENSUS 行 total_after 205,418→196,382；CN_TREND 正典行 total_after 207,425→198,389 |
| results/post_review_criteria.json | 3 处 json_field 锚随真值更正（205418→196382·200900→191864·207425→198389；r290 判据修正合法序列，claim 文本留史不改） |

**不动面**（披露）：skill_line.n_eff/line 各 4dp 判定值维持判读时原值（R252 律）；cells/verdicts/nulls 两版逐键 diff=科学零差异（同 seed 确定性双跑，反而构成跨机复现实证）。

## 修复后验证

- 全链审计（results/_r295bmb_ledger_scan.py，73 批件）：INTERNAL_BALANCE_FAIL=0·DUP_BATCH_CONFLICTS=0·**HEAD=198,389**·链尾全连续 187,845→REV_OSC 189,859→CN_SOE 191,864→CENSUS 196,382→CN_TREND 198,389（191,864→200,900 缺口消除；余 18 gap 全为 ≤187,845 历史重锚面，HANDOVER 已档）；
- 复审器重 derive：**YES=36 NO=0 WAIT=5**（T-86-S2/T-87-CN-TREND 行随新锚全 YES）。

## 坑律（入 CODELY）

**认领竞速裁定「产物 void」≠物理终止——败方在飞进程必须实杀**；同批 append 幂等门必须跨进程（池 done 翻面/同名产物在场即拒）；产物 commit/push 前必实读 trials_ledger prev 链断言（r291 bm-a 池断言律的产物面扩展）。

## 顺手件

- results/_r295bmb_ledger_scan.py（5x 账本审计器，可复跑）
- results/_r295bmb_attrition_phantom_remove.py（幻影行字节级移除器，断言式）
- results/_r295bmb_chain_reanchor.py（链修头手术器，全部唯一性断言+JSON 复验）
