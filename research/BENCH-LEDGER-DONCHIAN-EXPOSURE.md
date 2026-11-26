# 单位缺陷的射程：它走到我们自己的判决记录了吗

- 轮次：bm-c r2145（竞争窗 CONTENTION·只落新增文件面）
- 面：`scripts/bench_ledger_donchian_exposure.py` → `results/bench_ledger_donchian_exposure.json`
- 生成：2026-11-26T19:0x+08:00
- 上游：r2142（找到缺陷）→ r2143（量宽度）→ r2144（算成钱）→ **本件（问它有没有污染已经定案的记录）**

前三件都在 `bench_*` 卡片内部。这一件问的是另一类问题：**那 14 条臂只活在四张卡片里，还是也站在我们已经下过判词的族下面？** 如果后者，我们要走 reopen 通道；如果前者，它就是一份报告里的错，不是科学记录里的错。

答案：**是后者之外**。判词 `LEDGER_NOT_EXPOSED`。

## 1. 我们盘上有多少张面在说 donchian

扫 `results/**/*.json`，命中 77 张面、**1,154 行**带 donchian 标签的记录。按面自己的 schema 分三条血统：

| 血统 | 面数 | donchian 行 | 价格基准 | 是否受影响 |
|---|---:|---:|---|---|
| bench 卡片（`cards`/`arms`/`criteria`） | 5 | **41** | 收益指数 vs 原始价位 | **是**（r2142 已证：`bench_core.align_futures` 交 1.0 起的收益指数，high/low 仍是原始价，比 96×–6,980×） |
| mass 试验（`cells`/`candidates`/`prereg`/`grammar_sha256`） | 60 | **1,089** | 共用原始 OHLC | **否**（见 §2） |
| 未分类（roster/registry/board 一类） | 12 | 24 | — | 无判断 |

41 行不是 14 条臂。r2141 已经量过「一条测量被两张卡各印一遍」，本件不重算臂数，只用行数说明**受影响的行全部落在 bench 卡片血统里**，一条也没有落到试验账本血统。

被排除的自审面 6 张（`bench_donchian_unit_audit` / `bench_signal_scale_invariance` / `bench_donchian_repair_rerun` / `bench_live_thread_dedupe` / `bench_go_ruler_audit` / 本件自己）——它们按构造就会提 donchian，算进去等于让这份报告自我膨胀。排除理由逐条印在 JSON 的 `self_audit_excluded` 里，不是静默丢弃。

## 2. 试验账本为什么不算受影响：一条代码腿，不是一句安慰

1,089 行 donchian 记录（含 `results/shortline_cta_p1.json` 71 / `shortline_cta_p2_noau.json` 71 / `shortline_cta_wave1.json` 142）跑在 mass 试验血统上。它们不受影响，理由有两条，都在代码里可查：

**证据一（面板门）**：`scripts/trial_labor_w4.py:1071` 在跑任何规则之前断言面板列集包含 `open/high/low/close/volume` —— 规则拿到的三序列同源同尺度。本件的 AST 探针去找这条断言，找不到就把该血统降级为 `UNKNOWN`（而不是默认绿）。

**证据二（CTA 屏自洽）**：那三张 `shortline_cta_*` 面出自 `scripts/cta_p1_screen.py`。它的 donchian 是

```python
def sig_donchian(close, hi=55, lo=20):
    up_break = close > close.rolling(hi).max().shift(1)
    dn_break = close < close.rolling(hi).min().shift(1)
```

——**上下轨都由同一个 `close` 滚动窗口算出**，任何公共尺度因子直接在比值里抵消。这不是"运气好"，是这条规则根本不读 high/low。AST 探针（`scripts/cta_p1_screen.py:69`，滚动基座集合 = `{close}`，参数里没有 high/low）把这句话做成了可复跑的断言。

对照 r2142 的缺陷面：`bench_generic.sig_donchian` 收的是另一路输入（收益指数 close + 原始 high/low），所以它才把"永远做空"当成信号。

## 3. 已经关掉的族有没有引用受影响的面

`scripts/science_gates.CLOSED_FAMILIES` 现役 9 族。逐族把 `evidence` 字段拿去和扫到的 77 张面对撞：

- **命中受影响面的族：0 个**。
- 被引用的路径全部落在 `research/*.md` 与 `results/wild_route/*` 一类，不涉及 bench 卡片的 donchian 行。

因此 `cta_futures_p1`（`negative_x3`，证据指向 `research/STRATEGY_LIBRARY.md`）这条判负**不是**被缺陷臂撑住的：撑住它的是三张 CTA 屏，而三张屏的 donchian 按构造免疫（§2 证据二）。

**如实留一个未验收的接口**：注册簿的证据字段指向 `research/STRATEGY_LIBRARY.md`，没有直接点名那三张 `shortline_cta_*` 面。所以"三屏免疫"这句话是本件**另起一条路径**证明的，不是从注册簿的字面链上读出来的。要让这条链完全闭死，需要把面路径写进族证据字段——那是改共享面的动作，竞争窗里不做，记进下轮指针。

## 4. 这份报告不主张什么

- 不主张 14 条缺陷臂已经修好。它们还在 `bench_generic` 里，修 `sig_donchian` 的单位是共享代码面，等无竞争窗。
- 不主张 41 行就是 41 条臂。行数是"提到 donchian 的记录"，臂数要按 r2141 的去重口径算。
- 不主张 mass 试验血统全部干净。本件只证明"面板带原始 OHLC 列"与"CTA 屏上下轨同源"两件事；其余 57 张 mass 面的数据路径未逐张读代码。
- 12 张未分类面共 24 行无判断，原样列出，不并入任何一条结论。

## 5. 复跑

```
python scripts\bench_ledger_donchian_exposure.py run      # 重 derive 并落 JSON
python scripts\bench_ledger_donchian_exposure.py check    # 盘上面与重 derive 逐键比对（ok / STALE）
python scripts\bench_ledger_donchian_exposure.py selftest  # 15 腿离线自检
```

自检 15/15 PASS、`--check` 与 `run` 一致（`verdict=LEDGER_NOT_EXPOSED faces=77`）。
