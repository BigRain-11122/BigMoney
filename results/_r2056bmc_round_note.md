# r2056（并行执行体·竞争窗只落新增文件面）

- 时间：2026-11-24T22:35 起（本窗），窗口内未改任何共享面。
- watermark：red=false / lane=healthy（读 `results/watermark_red.json`；未在生产面重算，理由见下）。
- 孤儿面=0（`python Tools/orphan_face_probe.py` → `{"py_faces": 6, "orphans": 0, "orphans_cleared": 1}`）。
- 同宿主竞争探针：`python Tools/repo_write_contention.py --lookback-min 45` → **rc=3 CONTENTION**
  （证据 `results/_repo_write_contention.bm-c.json`：本机另有 interactive 宿主 pid 80112 自 2026-11-24 21:08 存活，
  22:35 轮首前已写 15 张共享面，重叠窗 0 张）→ 按 r1927/r1907 律：**只落新增文件面，禁改共享面、禁重跑 S6 链与全量冒烟**。

## 本轮产品（新增文件面）

一晚上的十九个答案被分成四类，用的是每格自己已经写下的功效戳，而不是再判一次：

- `scripts/bench_night_rollup.py`（build / `--check` / `--selftest`）
- `results/bench_night_rollup.json`
- `research/BENCH_NIGHT_ROLLUP.md`
- 负控 `results/_r2056bmc_rollup_negative.py`

读数（窗口 21:20–22:00，按各结果件自己的 `generated` 取件，19 格）：

| 类 | 数 | 意思 |
|---|---|---|
| 格级过门 | 1 | `basis_timing_perm`（IC +7.36pp / IM +3.64pp vs 零假设 p95，p=0.000） |
| 臂级过门 | 4 条 = **2 条不同读数** | 商品 TSMOM 120d/250d 多空，在 `robust_tsmom_commodity` 与 `census_commodity` 里各跑了一次，读数逐位相同 |
| 有功效的判决 | 7 | 4 个 NO_EDGE 真否定 + 1 不稳 + 1 混杂 + 1 偏正 |
| 问不出声 | 10 | 判词写否定，但 MDE > 自己的目标（1 个差 1 个月、9 个要 4–83 年） |
| 不判词 | 1 | `paper_basis_timing` TRACKING |

最硬的一句：`pair_index_60d` 的 MDE 9.20pp 撞 3.00pp 目标，要现在样本的 9.40 倍（**还要再攒 83 年**）；
这类格子重跑不会变成判决，只会再买一次「看不见」。

两枚自捕（均已修，且各留一条自检腿）：

1. 臂级「最好一臂」首版取的是**第一条臂**（`read_arms` 把 `common_window` 摊平后，选择函数还在读旧键），
   于是 `census_commodity` 印成 +2.76% 而不是 +5.24%（自检腿：多臂格里被引用的必须是最大值，6 格）。
2. 首版用标签串去重「过门臂」，而两格的标签词表不同（`120d` vs `tsmom|{'lookback': 120…}|ls`），
   去重退化成 4 条假独立；正法=**按读数三元组去重**（同一规则重跑读数逐位相同），去重后 2 条。

## 验证

- `--selftest` **18/18 PASS**
- `run` rc0；`--check` **rc0**（19 格 / 逐格判词·功效·MDE·倍数复算 / 页面块逐字）
- 负控 **9/9 PASS**（手改一格 rc1 点名且不带 STALE；输入一字节 rc3 STALE 且不带 CHECK FAILED；
  翻功率戳把 SILENT 翻成 FINDING；页面手改一位 rc1；页面丢标记 rc1；缺面 STALE；未知判词不落桶；四个发布件逐字节未动）

## S0.5 / S7（读多写零）

- 集团 `docs/decisions.md`：`git show origin/main:docs/decisions.md` 原字节落盘 sha256 **79e3083b**（250,586B），
  与本机自持水位恒等 → **零新决策行**。（按 r1911/r2048 律：不经 PowerShell 字符串往返、不加 `2>&1`。）
- orders 差集、心跳 `orders_ack`、`state-bm-c.json` round_no：**本窗一律未写** —— 这三张面正被 interactive 宿主写，
  叠加写会把它的回执/轮号冲掉。轮号因此不取 2056 之外的号，本行以「r2056 旁轮」自署。
- S6 链与全量冒烟：**连续第 7 轮未跑**（竞争窗禁跑），如实记。
- 两爪、attrition 守卫：本窗未复核（同为共享面写动作），如实记。

## CEO 过程可见面

- 当前活：把今晚 21:20–22:00 一口气交卷的 19 个格子按「有功效的否定 / 问不出声」分开。
- 最近实物：**K:\Fluxgroup\FluxGroup\quant\bigmoney\research\BENCH_NIGHT_ROLLUP.md**（2026-11-24 22:47·
  1 格过门 + 2 条臂级规则 + 10 个问不出声，最坏还要攒 83 年）。
- 下个里程碑：(a) 竞争窗关后把这面接 S6 链腿 + 全量冒烟（≤48h）；(b) 把 10 个「问不出声」的目标边际
  改写成与样本相称的量级并重排 WORK-BANK（≤48h，需改共享面）；(c) 两条过门臂（商品 TSMOM 120d/250d 多空）
  单独立案跑成本+容量（≤48h）。

## 未验证（如实）

1. 不重算任何一格的收益、成本、容量：全部逐字取自各结果件自己的字段。
2. 「过门」只等于「它自己的判据过了」，不等于入册，也不等于可下单。
3. 功效戳（`powered_for_target`）本身没被独立复核；本面只做「它说没功效就当没功效」的读法。
4. MDE→倍数用平方根律（MDE ∝ 1/√n），是近似；真实所需样本随波动结构会偏离。
5. S6 链、全量冒烟、心跳、轮号、orders 回执均未动（竞争窗）。

记账：本文件 1 处 + 产品三件（脚本/JSON/页面）= 4 处新文件；共享面 0 处改写。

## 送达自证 + 轮号实况（提交后复核）

- commit **712d26f507** 已推 origin/main（`19e9a5cb81..712d26f507`），fetch 后 **AHEAD=0 / BEHIND=0**，
  `git ls-tree -r --name-only origin/main` 五件全在位（`scripts/bench_night_rollup.py`、`results/bench_night_rollup.json`、
  `research/BENCH_NIGHT_ROLLUP.md`、`results/_r2056bmc_rollup_negative.py`、本文件）→ **本地未达 origin commit 数=0**。
- 推送后复跑：`--check` **rc0**、负控 **9/9 PASS**（发布件在提交后再被判绿一次）。
- **轮号实况（本窗自捕）**：本窗落件期间对端已用同一号发了自己的轮 —— `3b0890f8da round 2056: 27 of 28 money-shelf names…`，
  随后 `19e9a5cb81 round 2057: yield the tree to the peer host; read-only maintenance receipt`（对端已识别本窗并让树）。
  本窗因未写 `state-bm-c.json` 才没有吃掉对端的计数；「旁轮 + sideline」自署是对的，**后续并行窗一律照此**，
  禁再按「dequeue 到的下一个号」自署 2056 以外的整号。

