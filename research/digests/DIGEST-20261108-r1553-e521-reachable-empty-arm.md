# E521 — the unguarded read that would actually raise, and the 15 guards the census could not see

窗口：r1553 bm-b（2026-11-08）｜产物：`scripts/e521_reachable_empty_arm.py`、`results/state_tilt/EMPTYARMREACH-2026-11-08.json` + `emptyarmreach_latest.json`

## 立论

E515 发布了 199 个「生产代码里无卫读取分支型被调方结果」的站点，97 个是下标读取。**无卫读不是崩溃的计数**：只有当被调方的空臂真能从**这个站点**被走到，读取才会抛。于是本轮把这 199 行逐条定价：被调方到底有几条空臂（含 return-path 普查永远数不到的**隐式落空**）、读法会不会抛、站点自己传的字面量是否已经把空臂排除或保证。

## 读数（199 站点 / 118 个被调方 / 91 个源）

| 判决 | 站点 |
|---|---|
| 读是真理测试，空值不抛 | **92** |
| 读会抛，但**读这一行本身**就带着条件表达式守卫 | **15**（其中 7 个否则会走到可达空臂） |
| 读会抛，被调方**任何路径上都没有空臂** | 39 |
| 读会抛，空臂可达性无法从这个站点判定 | 52 |
| 读会抛，**空臂无遮拦可达** | **1** |

读法分布：`subscripted` 97（其中条件表达式守卫 10、无空臂 37、不可判 49、可达 1）、`method_call_on_the_result` 10（守卫 5、不可判 3、无空臂 2）、`truth_tested_only` 92（全良性）。

**唯一那条**：`scripts/e333_surviving_e3xx_conclusions.py:291` `sig = consumer_signal(...)` 后第 292 行 `sig["delta"]`。被调方 `consumer_signal` 在第 184 行有一条**无分支遮蔽的 `return None`**（三个 kind 分支之外），所以空臂无条件可达。今天没炸，只是因为入口表里第四个 entry 的 `signal` 是 `None`、被上面一行 `if entry.get("signal"):` 挡掉；**换一个不在 {e326,e328,e329} 里的新 signal 名，下标就在 None 上抛**。

## 可复用教训

- **条件表达式是守卫，可它写在读那一行里**：`d.get("k") if isinstance(d, dict) else None`、`name.rsplit(".",1)[-1] if name else None`、`three.get("summary") or {} if three else {}` —— 语句级「call 与 read 之间有没有守卫」的普查对这 15 个站点一律读成「无卫」。本窗第一版也照抄了这个盲点（8 条「可达」里 7 条是这个形状），加了 `read_line_guard`（同一行、`IfExp` 的测试点名**读表达式的根名**）之后才收敛到真正的 1 条。
- **隐式落空在这次人口里是 0，但这是测出来的 0**：父面全部 1,186 个被调方都有显式空返回，所以「函数跑到末尾掉下来返回 None」这条臂在 199 站点上一个都没出现。把它单列成字段（`sites_that_carry_an_implicit_fallthrough_arm...`）比并进「空臂」总数更诚实——否则读者会以为普查漏了一半。
- **「守卫点名了参数」不等于「这个站点能满足」**：`if not x: return None` 遇上站点传 `[2]` 是排除，遇上传 `None` 是保证，遇上传 `vals` 是什么都不知道。三档分开（`EXCLUDED_BY_LITERAL` / `GUARANTEED_BY_LITERAL` / `UNDECIDED_NON_LITERAL`），别把「不可判」洗成任何一种。
- **不是空值测试就当没测**：`if n > 3: return None` 里的 `None` 与实参空不空无关，一律 `UNDECIDED_OTHER_GUARD`。把「任何提到参数的测试」都算成空值守卫，会把不可判的 52 条缩成几条假安全。
- **`empty_arms==0` 的计数必须叫它数的东西**：39 是「会抛且无空臂」的站点，不是「被调方没有空臂」——40 行 `empty_arms==0` 里还有 1 行是真理测试。字段从 `callees_with_no_empty_arm_located_here` 改名为 `rows_with_no_empty_arm_located_here`（E207 名即语义族）。

## 验证

`scripts/e521_reachable_empty_arm.py`：`build` rc0 / `check` problems=0 / `verify` 重建 problems=0（逐字节同源）/ **selftest 25/25** —— 夹具六臂：无条件 None、隐式落空、空值守卫（字面量排除／字面量保证／非字面量不可判）、别的测试不当守卫、无空臂；条件表达式守卫另有三腿（根名解析、带守卫行、裸读行）；四枚 doctored 面全被拒。
smoke 腿 `# E521`：`scripts/run_e521_smoke_leg.py` 单跑 1/1 绿、`--doctor` 1/1 红且面字节还原（sha `d3dc311a249a`）。

**未跑**：全量 smoke 套件（~20-30min）、S6 其余链腿、`monitor.build_status`、`daily_scorecard`、采集器族与 market/paper 链——不宣称。