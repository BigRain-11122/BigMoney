# DIGEST 2026-11-08 r1422 (bm-c) — 供给层的第三十个红：它一直在说「等预注册落地」，而预注册目录已经烧完了

## 起因

`compute_audit` 的 `supply_floor` 从 r1415 起连红到本轮：`ready 0 < floor 3`，breach 约 11,800 分钟。
r1199 把它拆成「机制故障 vs 选题债」，r1421 又拆出「题都过不了自己的日历」。三层归因都在
**消费端**（池面/票面/队列/日历收据），没有人看过**供给端自己**：那个被指定为补救面的
`Tools/fill_ladder.py`，每轮只有一行输出。

本轮跑 `python Tools/fill_ladder.py --dry-run`，被印出来的只有一行：

```
[ladder] no lawful supply candidate passed gates -- honest no-op;
         floor breach 0<3 stands until preregs land
[ladder]   blocked: INNOVATION-QUOTA-SLOT-3 (prereg closed (已判决): ...)
```

一个读者会读成「有一行被门卡住，把那行的预注册修好就有供给」。实测不是：

| 事实（本轮实测） | 数 |
|---|---|
| 目录行数 `Tools/fill_ladder_catalog.json` | 23 |
| 已在池里（`existing_ids` 命中，状态全为 `done`） | **22** |
| 未入池且被门挡住 | 1（`INNOVATION-QUOTA-SLOT-3`，其预注册 `INNOVATION_QUOTA_W3_PREREG.md` 状态行写着已判决） |
| 可入池（available） | **0** |

也就是说：这 23 行里 22 行**早就烧完了**，剩下 1 行是**判负终局、按法不该再烧**。
把 SLOT-3 的预注册「修好」不是修法，是回烧一个已判决的族（r1381 立过的正是这条）。
供给目录已**耗尽**，而工具的输出结构里没有「我手上没有货了」这句话。

## 缺陷（出生地）

`run()` 用 id 做幂等：`if cid in existing_ids: continue`。幂等本身是对的（不重投已经在池里的活），
但它同时把「已烧完」从**报告**里删掉了——于是：

- 目录耗尽（22 spent / 0 available）
- 单行被门挡（0 spent / 1 blocked）

两句完全不同的状态印出**同一句话**「stands until preregs land」，而它们要的动作相反：
前者要**写一份新预注册**（议题债，人写的活），后者要**解一行的门**（工具/法面的活）。
这正是 r1199 立的规则（「一条红如果没人能对着它做事，它就不是旗」）在供给端复发，
也是 E426（一个红只量一层，就把两种相反的动作印成同一个词）的第三层。

## 本轮做的两件事（都可跑、可验）

### 1 `fill_ladder explain`：逐行分类 + 并集日历判决

`Tools/fill_ladder.py` 新增 `explain` 子命令与 `results/fill_ladder_face.json`（与 `run()` 共用
`_gate_pass` / `consumer_plan_missing` / `workers_plan_missing` / `runner_args_missing`
同一实现，禁第二份判定）。每行落一个类：`spent` / `blocked` / `lane_foreign` / `available`，
判词：

| 判词 | 条件 | 该做什么 |
|---|---|---|
| `SUPPLY_AVAILABLE` | available ≥ 1 | 跑 `fill_ladder` 入池 |
| `ALL_ROWS_BLOCKED` | blocked ≥ 1 且 spent = 0 | 解门（预注册/依赖） |
| `EXHAUSTED_NO_LAWFUL_SUPPLY` | available = 0 且 spent ≥ 1 | 写新预注册（议题债） |
| `CATALOG_EMPTY` | 目录零行 | 目录本身坏了 |

同时把 r1421 的日历面 import 进来（单读者，不重算），一行印出两半：

```
[ladder-face] ready=0 floor=3 | catalog 23 rows: spent 22 / blocked 1 / lane_foreign 0 /
              available 0 -> EXHAUSTED_NO_LAWFUL_SUPPLY |
              calendar: NO_CANDIDATE_PASSES_CALENDAR (4 candidates, 4 refused)
```

这就是供给层一直缺的那句话：**手上没有可投的货，而且已有的四本书没有一本过得了自己的日历**。
前一格的动作是写题，后一格的动作是等证据（r1421 已定谳：空池不是缺题，是缺一年证据）。

顺带把 `run()` 的 no-op 行补上了 spent 计数（`22 of 23 catalog rows are already in the pool`），
让默认输出不再把「耗尽」说成「等预注册」。

### 2 `calendar_admitted:<book>` 门：入池前先问日历

上一轮留的里程碑是「让 fill_ladder 入池前先问日历面」。本轮把它做成**门**而不是假想：
`enqueue_gates` 新增 `calendar_admitted:<book>`，走同一 `_calendar_block()`：
只有字面 `ADMIT` 放行；`CONDITIONAL/REFUSE/UNADJUDICABLE_PHASE` 拒；日历面读不出来 = `UNKNOWN` 拒
（未知不是通过）；收据里根本没提过这本书 = `UNJUDGED` 拒（没被判决 ≠ 被判通过，r98 同族）。

**诚实边界**：这条门今天**在岗但零命中**——目录 23 行没有任何一行声明 `book_key`，所以没有行去问它。
一条永不触发的门是装饰，所以本轮的产品主体是 §1 那张脸（每轮随 S6 链刷新），门是给下一批
「重新推导某本已判负的书」的候选准备的：那一批出现时，门会自己咬住，不需要再改工具。
（这与 r1381 的 `prereg closed` 门是同一条思路的两层：族判负拒回烧，书判负拒重推。）

## 验证

- `python Tools/fill_ladder.py selftest` → PASS，新增腿：类矩阵（spent/blocked/lane_foreign/available）、
  祖父边界两侧（在池里且无 schema 字段 = spent，不在池里且无 schema 字段 = blocked）、
  判词词表四则、日历 join 词表、`calendar_admitted` 四条（ADMIT 放行 / 拒并点名失败检查 /
  UNKNOWN 拒 / UNJUDGED 拒）、汇总行必须同时带 spent 与日历词。
- `python Tools/fill_ladder.py explain` → 上述实测行落 `results/fill_ladder_face.json`。
- S6 链新增 `ladder_face` 腿（紧跟 `compute_audit`，即举旗的那条腿）实跑 rc0；
  `python Tools/s6_chain_bmc.py --selftest` 9/9 PASS。
- `smoke_test.py` 两条腿：`fill_ladder selftest` 与 `fill_ladder explain --dry-run`（干跑，套件不重写已发布面）。

## 下一窗

- 供给面的下一步不在工具里：目录耗尽意味着**必须有人写一份新预注册**，且它要过的第一道门是日历
  （r1420：五相位同词才算判得出；r1421：四本书 4/4 被拒）。写什么题属于研究方向决策，不是本工具能代劳的。
- 当第一份新 pre reg 落地、并入目录时，记得给它带上 `book_key`：那一步会让 `calendar_admitted` 门第一次真正咬合。
- moneyflow 首拉仍在跑（done 3,247/5,226，每符号约 121 bar）；`MF_IC_P1` 冻结门的
  `n_symbols≥5,000 且信号日≥150` 仍未达，批继续依法等待。