# Digest r1248 (bm-a) — 作废的行在别处仍是证据；闸只许管已定格的那根

**面**：`scripts/etf_book_card_track.py`
**卡**：`knowledge/METHODOLOGY_ASSETS.md` E368
**selftest**：20/20（新增 L7c；L7 改篡改**已定格** bar）

## 一、现象

轮首 S6 链 `etf_book_card_track` rc=1：

```
nav identity maxdev 1.32e-03 (ok=False, 7 bars)
```

同一条腿在 r1246 是 **2.0e-10**（6 bars）。差的不是本书算术，而是记录里多了一根 bar。

## 二、根因一：账本自己作废的行，消费者仍在读

账本（`scripts/etf_book_forward.py`）在 r1243 立了一条规则：一根被面板覆盖闸拒绝的 bar **不删**（删=改史），打 `withdrawn: True` 留在记录里，并停止进入定价与结算分区；活 bar 的选择器是 `published_bars(led)`。

卡追踪绕过了这个选择器，直接读 `led["bars"]`，于是把账本已经作废的 2026-11-02 重新拉去做身份自证。**该 bar 的 nav 是面板没数时按持有价平推出来的**（当日 10-30→11-02 变化 +0.003%，几乎是零），一旦面板补上真值，恒等腿立刻读出一个属于「作废路」的偏差。

修法：改调 `F.published_bars(led)`，并把被扣下的 bar 名字印进产物（`bars_withheld`），而不是悄悄少算几根。

## 三、根因二：闸只能管已定格的那根

修完作废行剩 **7.72e-05**，逐 bar 打印显示全部落在最新一根（2026-11-03）上：

| bar | 重算 | 账本 | 偏差 |
|---|---|---|---|
| 2026-10-26 | 1.0010304509 | 1.0010304509 | -4.7e-11 |
| 2026-10-27 | 1.0039951573 | 1.0039951687 | -1.1e-08 |
| 2026-10-28 | 1.0154165579 | 1.0154166137 | -5.6e-08 |
| 2026-10-29 | 1.0145312630 | 1.0145314121 | -1.5e-07 |
| 2026-10-30 | 1.0085989959 | 1.0085993056 | -3.1e-07 |
| 2026-11-03 | 1.0036816894 | 1.0037553579 | **-7.8e-05** |

最新那一根的面板当天仍在增员（`update_etf_wide` 两跑分别补到 11-02 与 11-03），拿它做「逐位必须相等」是量面板的成长，不是量账本的算术。这与 E270 已经写进账本的那条规则同源。

修法：调 `F.partition_settled()`（同一实现），把仍在填充的 bar 排除在自证外，并印出**被扣下的偏差大小**（`identity_not_policed_dev`）——否则「重放的 bar 少了」会被读成「更干净了」。

结果：**2.00e-10，6 根 bar，扣下 1 根并带数披露**。

## 四、会咬人的地方

夹具 L7「这条腿必须在账本被篡改时移动」原来篡改的是**最后一根** bar 的 nav。一旦最后一根被合法排除，夹具就永久绿而腿是瞎的（r1261 族：只在真面上断言答案的腿，在分类器坏掉时照样绿）。改成篡改已定格的那根，并新增 L7c 正面钉住「作废行不动恒等、且被点名扣下」。

## 五、同轮附带（数据面）

`data/daily` 宽表由 bm-c 车道维护，而 bm-c 心跳停在 2026-10-31T11:52（bm-b 停在 10-30T12:43）= 本机连续三天是唯一活机。书的面因此冻在 2026-10-30 并如实报 `feed_broken`。本轮按 `update_etf_wide --takeover`（TAKEOVER_STALE_MIN=120min，实测静默 4700min）接管刷新，面板 10-30 → **11-03**（1617→1618 名），两侧刷新均 `ok_with_refusals`（1 条 volume_drift 拒绝、36 名有历史空洞，原样披露）；`git diff --numstat -- data/daily` 删除行 **0** = 追加不改史。刷新后执行单重定价出 **TICKET-2026-11-03**。
## 六、本窗接手（第二轮修红）：白名单只认字段名，把合法重发读成人改

上五节是前一个窗写的（19:44 写完摘要后死在 close-out 前）。本窗按「死窗遗产机检、不信自报」接手：
`etf_book_card_track --selftest 20/20`、实跑 `nav identity 2.00e-10 / 6 bars`、
`identity_not_policed=['2026-11-03'] dev=7.7e-05`、`bars_withheld=['2026-11-02']`、
面板尾日 2026-11-03 与账本同日（`lag_on_panel_bars=0`）、执行单 `TICKET/ORDER-2026-11-03` 在盘且定价 bar=11-03——自报的每一条都对得上，才把这份遗产当本轮的实物。

接完遗产跑全链（`Tools/s6_chain_bma.py 1248`，**127/129 rc0**），两条非零腿里有一条是本窗的真红：

```
1 etf_book_live_widths  live-width face is inconsistent: 8 field(s) disagree with a
                        re-derivation while every copied field still matches and no source
                        is priced later: .as_issued.card_cagr_pp (12.17 vs 12.21); ...
2 fundamental           FATAL source fetch: stock_yjbb_em(20251231) failed:
                        Response ended prematurely
```

**根因不是手改，是白名单的形态错**。live-width 面把票据的 2x2 快照进 `as_issued`；票被重新定价一次（今天 11-02→11-03，19:28 生成 TICKET-2026-11-03）所有格整体动 0.03pp。放行分支本来是给这条无常输入开的，但它的条件写成了**路径前缀**（`as_issued.*`），而这个面还会把这些数字**再念一遍**在 `verdict_reasons` 的一句判词里——于是 14 条差异里第 14 条（那句话）不在白名单内，整次重发被判成手改，rc=1。

修法：放行条件改成**内容等价**——`_as_issued_number_map()` 把两边各自的 as-issued 数字做成替换表（`%.2f` 与 `%+.2f` 两种印法都收），`_as_issued_echo()` 要求「替换后两句话逐字相等」才承认这条差异是同一事实的重述。判词末尾明说它放行了那句话。

**能咬人的地方**（照 E368 的老账再记一遍）：一条只在前向放行的闸，必须有一条反向夹具。新增 (d)/(e)：同样回滚数字的重发票 → rc=2（stale，链付刷新）；同一份 payload 只把句中 `= True` 改成 `-> True`（数字没动、语义动了）→ 仍 rc=1。selftest **122 legs / 0 failed**。

修后实跑 `--live-widths`（链付刷新）→ `--live-widths-check` **rc=0**：`COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT, paired gap 0.12pp on 20 phases, engine disagreement 2.035pp`。

`fundamental` 那条 rc=2 是源端（EM `stock_yjbb_em(20251231)` 连接提前结束），按纪律原样上报，不掩盖、不自愈。

## 七、第二条真红（同窗发现）：控制臂读错了列

`fundamental` 那条 rc=2 是源端故障，本窗按纪律只上报。真正需要修的第二条红在 smoke：三条腿同时红，指向同一件事——**面板今天被本机接管推到 11-03，而一批派生面还钉在 10-30，且它们的 `--check` 永远说 OK**。

```
[FAIL] product: E246 drawdown band reaches both trading pages | order=False(-25.0% ~ -17.4%)
[FAIL] product: the sleeve-gate answer survives a moved decision grid | page does not print ...
[FAIL] product: the page tells a de-levered book from a well-timed one | page priced on 2026-11-03 but the exposure face is 2026-10-30
```

修法不是放松断言，是按依赖序把面真的重算：`exposure_timing / exposure_ladder / sleeve_paths` → 11-03、`band_ruler` → `window_label` → `ceo_page` → `etf_book_order`。

重算时撞出**第三条红，且是本窗唯一的代码缺陷**：band ruler 的票据控制臂报 `IDENTITY_FAILED`（measured 12.56 vs published 7.71）。根因是**行结构变了而臂没跟着改**：reader 页第一行 r1247 才从「一个数」拆成 `全窗 / 2020-2023 / 2024+` 三列，而 `_published_band()` 仍取行首的 `full`；臂名写的是 12.78%（那是 2024+ 列），比的是自己的 685 根票据窗口。拆列前两数同源所以一直绿，拆列后立刻现形。

修：`_published_band()` 增加 `ticket_oos`，票据臂改读 2024+ 列；新增 selftest L8（夹具刻意让两列不同：`full=7.63 / oos=12.56`，断言读 oos 通过、读 full 失败）。selftest 12/12。修后 identity 三臂全过（12.56/12.56、9.60/9.60、18.33/18.33），判决回到诚实的 `ROWS_NOT_COMPARABLE`。

**顺带量到的一条结构性隐患（本轮未修，如实登记）**：`etf_book_exposure_timing/ladder`、`etf_book_sleeve_paths` 的 `--check` 只从「自己发布的行」重推判词，**从不问面板走到哪根 bar**——所以面板一前进，它们就静默变成 10-30 的旧世界而 check 仍绿。今天的红全是这条导致的；正确修法是给这三条 check 加「戳记 vs 当前面板」比较（失败即 stale → 链付 run），已列为下一轮第一指针。

## 八、第三窗接手（22:0x）：身份用日期，一天内重发两次就必红

上一窗修好「判词重述句按内容等价放行」之后，全链复跑仍然 `etf_book_live_widths rc=1`：

```
live-width face is inconsistent: 8 field(s) disagree with a re-derivation ...
  .as_issued.card_cagr_pp (12.21 vs 11.92); .as_issued.cells_cagr_pp.beta@12 (9.66 vs 9.51); ...
```

这次不是白名单的形态问题，是**身份键选错了**。闸用票据日期判断「重发还是手改」，而订单腿在面板长出新 bar 时会重写票据——今天同一会话里它写了两次（`TICKET-2026-11-03` 21:28 生成，面板刷新到 11-03 后 22:1x 再次重定价）。日期前后都是 `2026-11-03`，`theirs <= mine` 于是把第二次重发读成手改，八个格整体挪了 0.29pp 无人放行。

修法两条：

1. **身份换成内容指纹**：`as_issued.square_fingerprint` = 票据 `width_disclosure.square` 的 sha256 前 16 位。指纹相同而数字动了=手改（rc=1）；指纹不同=重发（rc=2，链付刷新）。日期只保留它能证伪的那一个方向——**更旧的**票据永远不是重发。
2. **整句消失必须单独放行**：碰撞消失时那条 coincidence 判词整条不见了，diff 是 `verdict_reasons (len 10 vs 9)`，逐条回声比对在不等长时根本没有格可对。长度差单独一条分支，且只承认「两侧各自 as-issued 块能生成的那几句」。

修后 `--live-widths` 重发面（新增 fingerprint 字段）+ `--live-widths-check` **rc=0**：`COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT, paired gap 0.12pp on 20 phases, engine disagreement 2.035pp`。selftest **126 legs / 0 failed**，新增三腿 (f) 同日重发→rc2、(g) 多一句 as-issued 重述→rc2、(h) 旁边多一句无关→rc1。方法论卡 = E371。
