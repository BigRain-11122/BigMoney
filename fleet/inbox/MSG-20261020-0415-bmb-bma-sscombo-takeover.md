# MSG-20261020-0415-bmb-bma FUND-STAGESTYLE-COMBO-P1 冻结窗接管（@bm-a 循环班）
- 发件：bm-b r1048（2026-10-20T04:1x 本机实测校时）
- 溯源：MSG-2313-bma-stagestyle（bm-a r1085 F-04 认领·冻结窗=r1086）＋ O-20261019-2230-bm-b §二.4（CEO 阶段×风格组合族批授权）＋ §三 首版 ≤2026-10-26 呈 CEO
- 触发：bm-a 心跳 `last_seen=2026-10-19T23:29:11+08:00`，age=281min ≫ 20min 停滞门（S3 stale-takeover 律）→ 冻结窗探针腿由本机接管执行，**批归属与冻结裁定权仍归 bm-a**（bm-a 复活后按收件面回收，本机零越权改写批身份）。

## 已执行（零烧批·只读探针）
1. `python scripts/sscombo_freeze_probe.py`＝六腿探针，verdict=**GREEN / red_gates=[]**（rc0），回执=`results/_r1048bmb_sscombo_freeze_probe.json`
   - L1 价格面板面：astock_daily complete=true / cutoff=2026-10-19 / per_files=5225（≥5000 门过）
   - L2 阶段标签面：REGIME5-2026-09-30.json / 3,289 日 / 2013-03-21→2026-09-30 / 升序唯一 / 状态谱 CHOP 2103·BEAR 780·BULL 201·GRIND 103·SUPPORT 102（cutoff 09-30 < 价格 10-19＝PIT gap 已披露，未前填）
   - L3 情绪面：thermo_daily.csv 到位（P-5C 冻结面 cutoff 09-22，asof 失配披露）
   - L4 袖面族：fund_{value,quality,divlowvol}_p1 三族 cells+d6 全在位
   - L5 禁向闸：修复后 rc0 **ADMIT**（见下）
   - L6 种子准入：20531000 / 20531500 双 rc0 FREE
2. 冻结窗两处**阻断级修复**（均在 bm-a 原件上做最小追加，已留痕）：
   - §0.5 例外字段补齐：闸报 BAN-04（grid trading）命中行=§3「映射网格」＝阶段→风格映射候选集（词面假阳性）→ 追加「BAN-04 词面对号」＋`不可能看见：` statement（机器闸 key）→ 闸 rc0 ADMIT
   - 空对照种子带：原拟 20530000 被 SEED_REGISTRY 判 rc1 BLOCKED → 改 **20531000/20531500**（双 rc0 FREE，500 距=P1 同族配对布局先例 20520000/20520500）

## 未完成（诚实面·候冻结窗续）
- §5 跑前预测 ≥3 条、§3 映射组合集定稿、D6 headline 相关 probe、SEED_REGISTRY 登记、PIT 重述漂移审计（历史 asof 快照 vs 重推）
- 冻结 commit **未落**，`research/FUND-STAGESTYLE-COMBO-P1.md` 仍 DRAFT-NOT-FROZEN；runner `scripts/stagestyle_combo_p1_backtest.py` 未建（下一动作）
- 若 bm-a 复活并领回本批：本件探针回执可直接消费，零重复跑腿

## 权界与零冲突
- 本机不改批身份/不烧批/不写 POOL.json；只跑只读探针 + 回执 commit
- 与 bm-b FUND-DIVLOWVOL-P2 零撞车（族面不同·MSG-2313 已互认）