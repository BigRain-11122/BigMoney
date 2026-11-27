# 转债面板为什么一直停在 11-20 —— 以及「有写者」和「有人在写」之间差了什么

r2171 · bm-c · 正身 = `scripts/cb_dual_low.py`（check/update/status/selftest）、
`Tools/s6_chain_bmc.py`（腿 `update_cb_dual_low`）、`config/lane_hosts.json`、
`Tools/chain_writer_audit.py`（WRITER_MODES）、`qa/cb-panel-driver-r2171.md`

## §1 病灶：两张面都「对」，但它们说的是不同的日子

`scripts/cb_dual_low.py` 是第二条收益线（可转债双低轮动）的全部实现：`fetch` 一券一次从
东财拉全史、`build` 拼 `data/cb_panel.csv.gz`、`run` 出 `results/cb_dual_low.json`。
三个子命令都能跑，面板也能一眼看出新旧——可它的**面板从 2026-11-20 起就没动过**，
而结论面一直印着 11-20 的年化。

r2169 把这叫 `no_driver`：链里没有腿、计划任务里没有名、register 脚本里也没有，
`config/lane_hosts.json` 里连指派都没有。四条来源同时为空，不等于「没人需要它」，
只等于「没有任何机制在问它」。

更精确地说，是**两个问题**同时没人问：

1. **数据过期了吗？**（面板尾 bar vs 官方日历的 expected bar day）
2. **有人重新定价了吗？**（构建面板的字节 vs 结论面定价时的字节）

只答第一个，就会漏掉一种常见事故：面板被重建了（比如别人手工跑了 build），
而 `run` 没跑，于是结论面在「日期看起来对」的情况下印着旧书。
r1935 把这种「只重算自己」的自检叫永久绿，这里的通用形态是：
**自检要问的是世界，不是自己。**

## §2 第二枚坑：审计把写者的动词当成了范围

链写者审计（`Tools/chain_writer_audit.py`）的配对键是 `(script, scope)`，
`scope` = 脚本名之后的非选项 token，而 `WRITER_MODES={run,write,refresh,rebuild,snapshot,certify,fetch,build}`
里的词会被当作「这不是范围，这是写者动词」丢掉。

本轮的写者动词是 `update`——采集体家族的常用词，但不在那张表里。于是：

```
reader key = ('scripts/cb_dual_low.py', ())        # ... cb_dual_low.py check
writer key = ('scripts/cb_dual_low.py', ('update',))
```

两条腿落在两个 key 上，审计如实报告「这张面没有任何腿在重新生成它」，**而链其实每个过期窗
都会重新生成它**。全量冒烟的那条腿据此判红：

```
[FAIL] config: no checked face was left without a writer leg | 1 face(s) nobody regenerates,
       not in the baseline: scripts/cb_dual_low.py
```

修法是把 `update` 加进 `WRITER_MODES`（语义上它确实是写者动词），加之前先用模块内自检量过影响面：
findings 5 → 4，**没有任何一张面因此从 disclosed 翻成 red**（四种剩余全是 `NO_WRITER_MODE`
＝派生面，如实披露）。加之后 `--check` 印 `4 faces checked, 4 known check-only, 0 newly paired` rc0。

教训可以复用：**分类器的词表会漂移，而漂移的方向总是「它看不懂的新词 = 风险」**。
遇到「链明明在写，审计说没人写」，先问分类器认不认这个词，再去改链。

## §3 门长什么样（写死的口径）

`check` 的三件事，全部只读、约 0.05s（一个 JSON + 一次 stat）：

| 判据 | 失败态 | 谁买单 |
|---|---|---|
| 官方日历读不出 expected bar 日 | `rc2 INCOMPLETE`，**不含 STALE** | 不买单：重建治不了日历 |
| 面缺失（`data.last_bar` 没有） | `rc3 STALE ... face missing` | 链付一次 refresh（r1581 词） |
| 发布的那一天 < expected | `rc3 STALE`，同时点名两个日期 | 链付一次 refresh |
| 发布的那一天 > expected | `rc1 INCONSISTENT`，不含 STALE | 不买单：这是真分歧，要人看 |
| 状态面没记锚 / 面板字节变了 | `rc3 STALE` | 链付一次 refresh |

`update` 的次序固定：**先判「面板源是否已覆盖预期 bar 日」**——覆盖了就不联网，只 rebuild + reprice；
没覆盖才 `fetch --tail-after=<面板尾日>`（只重拉在该日仍活着的券，本轮 334 只，0 失败）→ `build` → `run`。
写完把新的面板字节锚记进 `results/cb_dual_low_update_status.json`。

## §4 本轮读数（面板 2007-07-12 → 2026-11-26，1051 只券 / 791,209 行）

| 配置 | 年化 | 夏普 | 最大回撤 | 年换手 |
|---|---|---|---|---|
| 20 只 / 20 日 / 10bp（主配置） | 7.35% | 0.758 | -22.6% | 4.60 |
| 同池等权（对照） | 6.44% | 0.701 | -23.7% | 1.14 |
| 不剔深度实值（强赎高危） | 7.06% | 0.717 | -26.9% | — |
| 20/20 · 5bp / 20bp / 40bp | 7.60% / 6.87% / 5.89% | 0.781 / 0.712 / 0.619 | -22.1% / -23.9% / -26.6% | 4.60 |
| 四个调仓相位 | 7.35 / 7.22 / 7.84 / 7.92% | 0.758 / 0.741 / 0.800 / 0.807 | -22.6 / -22.6 / -23.5 / -26.5% | — |

相对 11-20 那天（7.43% / 0.765 / -21.6%）只动了 4 个交易日，读数微降；**判词不变**——
主配置仍胜同池等权约 0.9pp、相位间不劣化、成本 40bp 仍正。这条线的价值不在今天的数字，
而在于它从「没人推的静态结论」变成「每个过期窗自动重算的面」。

> 这是测量面：不改任何生产书、不下单。
