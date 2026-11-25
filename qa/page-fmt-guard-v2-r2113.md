# QA — 页面百分号闸第二轮（r2113 bm-c）

被测件：`Tools/page_fmt_guard_v2.py`（第一轮 `Tools/page_fmt_guard.py` 的加严版）、
`scripts/page_fmt_guard_v2_page.py`（页面渲染器）、面 `results/page_fmt_guard_v2.scan.json`、
页面 `research/PAGE_FMT_GUARD_V2.md`。

本轮是**竞争窗轮**（`results/_repo_write_contention.bm-c.json` rc3：命 2 宿主，开工前 16 张共享面
已被对端写过）→ 只落新增文件面，未改共享面、未重跑 S6 链、未跑全量冒烟、未写 state/心跳（对端持有）。

## 1 立项依据（上一轮已判、本轮接手）

r2112 抽读第一轮闸 37 条命中的 20 条，判它「大约一半对」并给出三条廉价修法，结论
`DO_NOT_WIRE_YET`（`results/_r2112bmc_page_fmt_guard_triage.json`）。本轮把那三条修法落成代码，
但**不靠名单**——每种压制都是一条可复述的规则，且各自有自检夹具。

## 2 三条压制规则

| 规则 | 内容 | 计数 |
|---|---|---:|
| DETECTOR_LITERAL | 整个值就是两个百分号；或字面量是比较运算的操作数（`assert "1.21%%" not in md`）；或最近调用写进 `bad/err/issues/problems/fail/warn/note/diag/alerts/violations` 之一 | 12 |
| MAPPING_FORMAT | 引发告警的 `%` 开的是合法 `%(name)<conv>` 映射转换 | 3 |
| RELAXED_PRECISION | 引发告警的是 `%.f` / `%0.f`（精度不写数字），Python 接受（实测 `'%0.f' % 1.53 == '2'`） | 1 |
| TEMPLATE_APPLIED_LATER | 字面量绑给某名字（或绑进该名字装的容器），该名字后来被 `名字 % ...` 用掉；或在 `for` 里解包后其中一员被格式化 | 3 |

净效果：第一轮 **37 → 残差 18**，压掉 19 = 上述四项之和（面内 `counts.suppressed` 与
`v1_reference.total` 可逐位复算）。第一轮自己的计数里含本文件（夹具故意写坏），已从对照中剔除。

## 3 残差分诊（不看名单，看已发布页面）

判据：把字面量开头 24 个可读字符拿去 `research/` + `docs/` 的已发布 markdown 全文里搜。
- **12 条搜到页面**（读者今天打开那页就能看见两个百分号）：DEFENSIVE-RULER-DECISION-IMPACT、
  ETF_BOOK_CAP_BETA_POWER、ETF_BOOK_CAPACITY_FLOOR_GAP、ETF_BOOK_ENTRY_LAG、ETF_BOOK_LOT_LADDER、
  ETF_BOOK_OPEN_SLICING、ETF_BOOK_PHASE_ATLAS_ARMS、IDX_FUT_BASIS_VERDICT、IDX_FUT_CARRY_IMPACT_DECAY、
  IDX_FUT_ROLL_GAP、MONEY_BAND_BLIND_SPOT（+2 页同句）、POLICY_RETURN_LADDER。
- **3 条机器面**：`scripts/_r1684bmc_closeout.py:85`（心跳 JSON）、
  `scripts/astock_veto_hedgeable_beta.py:478/481`（结果面 JSON 的 `cost_model`/`verdict_rule`，
  已用 `rg` 在 `results/astock_veto_hedgeable_beta.json` 实见两个百分号）。
- **1 条潜在页面缺陷**：`scripts/etf_book_era_capacity.py:265` 的返回句会被 `"- %s" % sentence_fit(s)`
  原样印上页面，但该分支在已发布页里没跑到（搜不到那句话）。
- **1 条会炸的**：`scripts/astock_veto_liquidity_legs.py:413`，字符串要过 `%` 运算而正文里有
  `%；`（全角分号）——`write_doc` 里无条件执行，下一次 `--write` 就抛 ValueError。
  本闸实报 `offender="%；"` 与上下文窗口。
- **1 条与百分号无关**：`Tools/_r820bmc_close.py:130` 未闭合字符串（py_compile rc=1），
  单列为 SYNTAX_ERROR，不混进页面缺陷。

## 4 证据

| 项 | 命令 | 结果 |
|---|---|---|
| 自检 | `python Tools/page_fmt_guard_v2.py --selftest` | **35/35 ALL_PASS** |
| 面自校 | `python Tools/page_fmt_guard_v2.py check` | **CHECK_OK residues=18 suppressed=19 mode=per-file**（1s） |
| 深自校 | `python Tools/page_fmt_guard_v2.py check --deep` | 与扫描同一条推导（147s，见轮报告） |
| 页面自校 | `python scripts/page_fmt_guard_v2_page.py --check` | **CHECK_OK page matches the face byte for byte** |
| 负控 | `python results/_r2113bmc_v2_negative.py` | **11/11 ALL_CONTROLS_PASS** |

负控 11 条覆盖：干净脸绿 / 改计数=CHECK FAILED 且**不含 STALE** / 改输入摘要=STALE /
删一条命中=CHECK FAILED 且点名文件行 / 脸上凭空多一条=CHECK FAILED 且点名 /
页面干净绿 / 页面改一位数字=rc3 且点名行号 / 页面按字节复原 / 自检仍 ALL_PASS。

## 5 本窗自捕

1. **字符串字面量里的 `%%` 不是转义**：第一版夹具按「`%%` 会被解释成一个 `%`」写（那是 `%`
   运算的规则，不是字面量规则），于是 6 条夹具全部测了个假动作——自检 29/35 红把这件事当场抓出。
   修法：夹具直接写「落盘后的字符」，并在注释里写明这一点。
2. **`bad_conversions` 的压制不能按「整串」判**：`"x %(g)s %|"` 同时含合法映射与非法转换，
   若整串因含 `%(...)` 就放过，会把真缺陷吞掉。改为「本轮无告警时才去追认第一轮的告警属于哪类盲点」
   （`first_pass_only_class`），并加一条自检钉死「真缺陷永不被归因到盲点」。
3. **`check` 首版全树重扫要 149s**，负控 8 条腿直接跑到超时（5 分钟无输出被取消）。改为默认逐文件
   复核（脸登记了哪些文件就只读那些文件 + 文件数），`--deep` 才全树；负控 4s 通过。

## 6 未做（如实）

1. 未修那 17 条页面写入器缺陷（全在已提交的共享脚本面上，竞争窗禁改）——修法明确：
   未格式化的串把两个百分号写回一个；`astock_veto_liquidity_legs.py:413` 把 `%；` 改成 `%；` 之外
   的写法（或该串不走 `%`）。
2. 未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者都是对端未提交的脏面）。顺序=先修残差
   再接腿，接早了就是常红腿（r1789）。
3. 未写 state/心跳（多宿主共写态面，对端持有）；未跑全量冒烟（竞争窗纪律）。
4. 不判参数个数/形状不匹配（需要操作数），f-string 与 `.format()` 明示跳出并计数。
