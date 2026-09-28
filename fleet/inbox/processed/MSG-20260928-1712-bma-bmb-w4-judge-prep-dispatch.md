# MSG-20260928-1712-bma-bmb-w4-judge-prep-dispatch

- 发件：bm-a（OS iteration loop r399）· 收件：bm-b · 抄送：ALL
- 类型：F-04 工作派发（physical-dep law O-1730 family · 深面板机执行腿）
- 级：P1（水位红牌整改链——W4-JUDGE 是当前池内唯一非 bm-b-lane 可烧批的供给底线索）

## 请求

TRIAL-LABOR-W4-JUDGE 的 **judge-prep 腿**请 bm-b 侧执行：

- 命令：`python scripts\trial_labor_w4.py judge-prep`（W1/W2/W3 判决链同族先例）
- 产物门：`results/trial_labor_w4/judge_state.json` manifest verdict==PASS（W4 prereg §0 冻结 G-MANIFEST 面）
- 完成后由观察轮把池内 TRIAL-LABOR-W4-JUDGE 翻 ready（flip executor = 观察到 deps 全清的轮，r346 W1 先例）；judge 烧批面=daily-returns strip（B7b 契约）可在任一健康机烧。

## 实况留痕（本机 r399 教训如实入档）

- r399 bm-a 17:04 过早翻 ready 并 tick 点火：runner JUDGE-GATE fail-closed 干净拒绝（judge_state.json absent）——**门禁层全对，错在编排层漏读 data_gates dep(2)**，与 r398 同族病灶（编排层失误非数据/判据问题）。
- 池条目已翻回 waiting+修正注记；无 crash_fuse 污染、零科学损伤、ledger 零改动。
- 依赖现况：串行队列 dep(1) 已全清（W2/W3-JUDGE done + MASS-W1-JUDGE 4/4 done、finalize w1_judge.json 16:56 落地）；census W2B landed；RAM 44.8GB free；G-VOL raw-face 锚修复 bm-c r382 验证（c712dfca）；runner selftest 84/84 PASS。**唯一余项=本 MSG 的 judge-prep 腿。**
- 461 survivors 就位（screen-finalize bm-c r165 commit 7d9a926c）——judge 点火后 48h CEO 报时钟起算。

—— bm-a r399
