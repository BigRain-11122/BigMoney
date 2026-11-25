# 页面百分号闸第二轮：把「一半是误报」修成可查的账

> 覆盖 `Tools/page_fmt_guard_v2.py`。它读第一轮闸（`Tools/page_fmt_guard.py`，r2111），
> 同一套规则只加三种压制，每种压制都有名字、有自己的自检夹具，并且被计数打印出来。

面：`results/page_fmt_guard_v2.scan.json`（生成 2026-11-26T01:21:51+0800）｜本页由 `scripts/page_fmt_guard_v2_page.py`
渲染，正文数字全部取自那张面，手改一位即 `--check` 变红。

## 这一轮压掉了什么

第一轮把三类**正确代码**报成缺陷（r2112 抽读 20 条定谳）。三种压制各自是一条规则，不是一份名单：

| 压制 | 计数 | 规则（凭什么放过） |
|---|---:|---|
| 侦测器字面量 | 12 | 整个值就是两个百分号；或它是比较运算的操作数（`assert "1.21%%" not in md`）；或最近的一次调用写进 `bad/err/issues/problems/fail/warn/note/diag/alerts/violations` 之一 |
| 映射转换 | 3 | 引发告警的 `%` 开的是合法的 `%(name)s` 映射转换 |
| 省略位数精度 | 1 | 引发告警的是 `%.f` / `%0.f`（精度不写数字），Python 接受 |
| 后来被格式化 | 3 | 字面量绑给一个名字（或绑进名字里装着的容器），这个名字后来被 `名字 % ...` 用掉，或在 for 循环里解包后其中一员被格式化 |

**净效果：第一轮 37 条 → 本轮残差 18 条，压掉 19 条（= 上表之和 19）。**
第一轮自己那份计数里还含本文件（夹具就是故意写坏的），已从对照里剔除：`Tools/page_fmt_guard_v2.py`。

## 读者今天真的在读到的（12 条，每条的页面名是搜出来的，不是猜的）

判据：把该字面量开头的 24 个可读字符拿去 `research/` + `docs/` 的**已发布 markdown 全文**里搜，
搜到就把它引到那一页。也就是说下面每一条，读者打开那一页就能看见两个百分号。

| 源文件:行 | 页面 |
|---|---|
| `scripts/defensive_ruler_decision_impact.py:329` | `research/DEFENSIVE-RULER-DECISION-IMPACT.md` |
| `scripts/etf_book_cap_beta_power.py:399` | `research/ETF_BOOK_CAP_BETA_POWER.md` |
| `scripts/etf_book_capacity_floor_gap.py:328` | `research/ETF_BOOK_CAPACITY_FLOOR_GAP.md` |
| `scripts/etf_book_entry_lag.py:243` | `research/ETF_BOOK_ENTRY_LAG.md` |
| `scripts/etf_book_lot_ladder.py:376` | `research/ETF_BOOK_LOT_LADDER.md` |
| `scripts/etf_book_open_slicing.py:468` | `research/ETF_BOOK_OPEN_SLICING.md` |
| `scripts/etf_book_phase_atlas_arms.py:2828` | `research/ETF_BOOK_PHASE_ATLAS_ARMS.md` |
| `scripts/idx_fut_carry_capital.py:406` | `research/IDX_FUT_BASIS_VERDICT.md` |
| `scripts/idx_fut_carry_impact_decay.py:458` | `research/IDX_FUT_CARRY_IMPACT_DECAY.md` |
| `scripts/idx_fut_roll_gap.py:498` | `research/IDX_FUT_ROLL_GAP.md` |
| `scripts/money_band_blind_spot.py:397` | `research/MONEY_BAND_BLIND_SPOT.md`, `research/MONEY_PREMIUM_CARRY_AUDIT.md`, `research/MONEY_SUBBAND_JUMP_AUDIT.md` |
| `scripts/policy_return_lattice.py:375` | `research/POLICY_RETURN_LADDER.md` |

## 没有出现在任何已发布页面上的（5 条，如实分组，不假装它们不存在）

| 源文件:行 | 类型 | 为什么读者可能还没看见 |
|---|---|---|
| `scripts/_r1684bmc_closeout.py:85` | LITERAL_DOUBLE_PCT | 机器面字符串：写进 JSON（心跳/结果面）而不是页面，读 JSON 的人会看见两个百分号 |
| `scripts/astock_veto_hedgeable_beta.py:478` | LITERAL_DOUBLE_PCT | 机器面字符串：写进 JSON（心跳/结果面）而不是页面，读 JSON 的人会看见两个百分号 |
| `scripts/astock_veto_hedgeable_beta.py:481` | LITERAL_DOUBLE_PCT | 机器面字符串：写进 JSON（心跳/结果面）而不是页面，读 JSON 的人会看见两个百分号 |
| `scripts/astock_veto_liquidity_legs.py:413` | BARE_PCT_IN_FORMAT | 真缺陷：这串要过 `%` 运算，而 `%；` 后面跟的是全角分号，Python 会在渲染时抛 ValueError（不是理论风险，是下一次跑 `--write` 就炸） |
| `scripts/etf_book_era_capacity.py:265` | LITERAL_DOUBLE_PCT | 页面写入器里的一行，但本次已发布页面里搜不到这句话——分支没跑到，或页面还没重生 |

## 与百分号无关、但共用同一条出生站的（1 条）

- `Tools/_r820bmc_close.py:130` — 这个文件根本编译不了：unterminated string literal (detected at line 130) (<unknown>, line 130)

## 还不接进链，因为残差还得先修

本轮只证明「闸可以只报真缺陷」，没有把残差修掉：18 条 = 17 条页面写入器里的字面量/非法转换
（其中 12 条已印在读者的页面上）+ 1 条编译不了的文件。
修法只有一种——未格式化的串把两个百分号写回一个。这些脚本面都已提交、多为别窗所写，
竞争窗里禁改共享面（r1907），所以这一条留给独占窗。顺序应当是：先修残差，再把本闸接成
`Tools/s6_chain_bmc.py` 的 check-only 腿与 `smoke_test.py` 的一条腿；接早了就是一条常红腿（r1789）。

## 这一面不回答什么

- 参数个数/形状不匹配（`"%(a)s" % 1`、`"%s %s" % (a,)`）：要操作数才能判，本闸只看字面量；
- f-string 与 `.format()`：那边百分号是普通文本，两边判都会错，直接跳过并计数（本次跳过 f-string 18568 个）；
- 不复核已发布页面本身是否还该印这个数：本闸只回答「这一串会不会原样漏到读者眼里」。

