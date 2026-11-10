# DIGEST-20261110-r1664 · E646: 7 次跨模块键名命中全是同名不同账（word collision）

**轮：** r1664 bm-b · **面：** `results/state_tilt/CROSSMODULEKEY.json`

## 背景

E642 把「持有计数读行的 6 个模块里模块级写 **0** 个」当作主结论发布，同时把一条弱臂单独落面：**模块级写只要键名等于 6 个计数行键之一就记一次命中，共 7 次**。弱臂是名字级测试——E207/E208 家族已经定过「名字不是测量」，而 `verdict` / `rows` 是轮脚本给自己报告用的普通英文词。所以这 7 次命中只有在**写能到达读读的那本账**时才有意义。

## 方法

每个命中按静态读者能问的四问逐条落地：

1. **容器表达式**：取该站点最外层 `Subscript` 的 `.value` 并 unparse（`OUT['verdict'] = x` 发布成 `OUT['verdict']`，不是发布成「键 verdict」），并折出最左 Name；
2. **根名在本模块体里怎么绑定**（模块级赋值 / import 别名 / 模块体里没有）；
3. **该键属于哪条计数读行**（模块/行/函数/接收者），沿用 E638 的 join，不另立读总体；
4. **成对谱系分类**：`same_module` / `imported`（命中模块 import 读模块，或读模块 import 命中模块）/ `same_name_only`（容器根名 == 读的接收者名）/ `name_collision`。

命中是**从树上重导**的（沿用 E642 的语料与属主规则），E642 已发布的 7 只作对账值。

## 结果

- 语料 **13,084** 文件 / **13** 条计数读行 / **6** 个键；重导命中 **7** 次（与 E642 发布的 7 逐数重合），分布在 **6** 个模块、覆盖 **5** 个不同键；
- 7 个命中**全部**带容器表达式与根名，7/7 的根名都在自己的模块体里绑定（全是模块级赋值）；
- 7 个命中 × 各自计数读行 = **7 对**：`same_module 0` / `imported 0` / `same_name_only 0` / **`name_collision 7`**，跨 **2** 个读模块，0 个命中找不到对应读行。

逐条读数（容器 → 读的接收者）：

| 命中模块 | 行 | 容器表达式 | 模块类 | 读侧 |
|---|---|---|---|---|
| `results/_r478bmc_trio_watch.py` | 139 | `OUT['verdict']` | 轮脚本 | `e382_key_projection_delta.py:350` (`faces`) |
| `results/_r479bmc_trio_watch.py` | 139 | `OUT['verdict']` | 轮脚本 | 同上 |
| `results/_r675bmb_trio_watch.py` | 133 | `OUT['verdict']` | 轮脚本 | 同上 |
| `results/_r872bma_ledger_heal.py` | 45 | `receipt['rows']` | 轮脚本 | `e504_name_compose.py:919` (`doctored4`) |
| `results/_r920bmb_n2u3_flip.py` | 71 | `receipt['preflight']` | 轮脚本 | `e382_key_projection_delta.py:350` (`faces`) |
| `scripts/run_e563_smoke_leg.py` | 38 | `face['rows'][0]` | smoke 腿 | `e504_name_compose.py:919` (`doctored4`) |
| `scripts/run_e563_smoke_leg.py` | 39 | `face['rows'][0]` | smoke 腿 | 同上 |

判决 = **7 次命中全是同名不同账**：5 次在一次性轮脚本里写自己的 `OUT` / `receipt` 字典，2 次在 smoke 腿里写 `face`，没有一条 import 过读模块，也没有一条的容器根名等于读的接收者（`OUT`/`receipt`/`face` vs `faces`/`doctored4`）。E642 的弱臂在**实质上是空的**，键的拼写是唯一联系。

## 教训

1. **弱臂必须自己再过一次谱系门，否则它会被读成结论** E642 已经把 7 次命中单独成块发布并与主结论分开，但一块「命中 7 次」的弱臂如果没有谱系分类，读者最省力的读法就是「有 7 次碰到计数键」。本轮把 7 次全部落到 `name_collision`，弱臂才真正变成零。
2. **容器表达式是这类判定的最小可读单位** 只发键名会让人以为「写的是那本账」；发 `OUT['verdict']` 才能让读者自己看见「写的是另一个字典」。同一份数据两种发法，结论的可信度差一个量级。
3. **同模块/import 边才是谱系，名字相等连名字级都不算** 本例 7/7 容器根名与读的接收者不同名，所以连「同名」这层都没有碰到；把 `same_name_only` 单列一格，是为了下一次命中真的同名时不让它冒充 `imported`。
4. **命中都在一次性工件里** 6 个命中模块里 5 个是 `results/_r*.py` 轮脚本、1 个是 smoke 腿，0 个生产模块——这一层分类本身就该进面，否则读者无法判断「7 次命中」是语料性质还是产物性质。

## How

做名字级（弱）碰撞测试时，**不能只报命中数**：每个命中要发布它写的容器表达式、根名的绑定方式、它对应的那条读，以及成对谱系分类（同模块 / import 边 / 仅同名 / 纯碰撞），四格必须能相加回命中数。名字级的零永远要附一句「本测试只关掉了 import 可达与同模块这两条路」，因为通过 `importlib` 字符串、路径读取等方式到达同一本账的命中它看不见——这一条写进面里的 limits，并据此种下一张卡。

## 证据

`scripts/e646_crossmodule_key.py`（selftest 22/22、check/verify `problems=[]`）+ `results/state_tilt/CROSSMODULEKEY.json` + `crossmodulekey_latest.json` + `scripts/run_e646_smoke_leg.py`（1/1 PASS、`--doctor` 1/1 红且面字节复原 sha `c4141e709b97`）+ smoke_test.py leg E646 + `Tools/s6_chain_bmb.py` leg `cross_module_key`（rc=0 0.05s）+ 方法论卡 E646 + POOL E646 done / E647+E648 seeded