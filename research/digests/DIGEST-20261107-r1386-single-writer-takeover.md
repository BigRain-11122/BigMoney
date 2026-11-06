# 一个停了 29 小时的单写者，把 11 条腿一起拖红（r1386 bm-c）

> 一句话：CEO 一页 `docs/live_book/LIVE-BOOK-*.md` 只有一个写者（bm-a），bm-a 停了自己 29 小时后，
> 这一页停在 **2026-11-03**，而票面和卡片已经在 **11-06** —— 下游 11 条 smoke 腿同时红，每一条都
> 在说「这一页不对」，而它们其实在说同一件事。修法不是让 bm-c 偷偷写一页（那就变成两个写者），
> 是让**属主自己的心跳**授权一次有署名的代笔。

## 一、症状与根因分离

| 面 | 读数 |
|---|---|
| `docs/live_book/latest.json` | 指向 `LIVE-BOOK-20261104`，页内 `evidence_cutoff=2026-11-03` |
| `results/etf_book_order/latest.json` | `as_of=2026-11-06` |
| `fleet/machines/bm-a.json` | `last_seen=2026-11-05T21:26`，距本轮 **1747 分钟（29.1h）** |
| smoke | 356 腿中 14 红；其中 11 红是「页面落后/页面没写今天/页面没引这一面」 |

三条同时成立才定位到根因：①页面是唯一的单写者面（`scripts/etf_book_ceo_page.py` 的
`HOST="bm-a"`，且自检 L22 把它钉成「只有 bm-a 能写」）；②属主不再运行（以**它自己的心跳**为证，
不以「本地有没有新文件」为证）；③页面是所有下游面的**引用源头**，所以它一停，别处全部红。

## 二、做法（构造冻结在代码里）

- `TAKEOVER_SILENCE_H = 6.0`：属主心跳超过 6 小时未更新 = 声明式沉默。
- `takeover_authority(mid)`：返回代笔块 `{writer, owner, owner_silent_h, took_over, why}`；
  **心跳读不出来时返回 None**（「看不到属主」≠「属主死了」，E378 同族）。
- 页面 JSON 增加 `authority` 块；md 上印一行人话：`这一页是 bm-c 代笔的。bm-a 已经 28.8 小时
  没有自己的心跳 —— 它的页面是停了，不是旧了；代笔只写这一页，不碰它盘上的任何面。`
- 自检 L22 从「只有 bm-a」升级成三段尺子：属主活着=只有属主；属主沉默=代笔且块里带三个字段；
  心跳不可读=谁也不许写。三条都用替换 `owner_silence_hours()` 的夹具钉住，改错任何一段都红。

## 三、顺手揭出来的第二件事：一个「未核实就是通过」的闸

同族缺陷在面板戳闸上：`panel_stamp(load=False)` 在**新进程**里返回 `digest=None`，而
`check_panel_stamp` 对 `None` 的处理是「未核实 → rc 0 通过」。链上每条 `--check` 都是新进程，
所以这把闸在链上**永远不会响**——11-03 的 ladder/sleeve 面正是这样带着绿灯坐在旧面板上。
正法：三面的 `--check` 改读活面板（`panel_stamp()`，47s/次），并用旧戳夹具实测 `rc=2` 且打印
`stale` 字样（链的刷新臂就认这个词）。代价如实记：每次链跑多约 2 分钟。

## 四、读数与复现

```
python scripts/etf_book_ceo_page.py selftest     # 146/146 PASS（L22 三态）
python scripts/etf_book_ceo_page.py run          # 代笔落 LIVE-BOOK-20261107（5 名/书 459,487/现金 540,513）
python scripts/etf_book_exposure_ladder.py run   # 276.6s，1658 bar → 2026-11-06
python scripts/etf_book_sleeve_paths.py          # 15 格 → verdict NO_GATE
python -m monitor.build_status                  # 新增 data.lane_ownership（11-08 决策要读的那一行）
```

- 三张纸现在同一天：卡片 **2026-11-06** / 票据 **2026-11-06** / 本页 **2026-11-06**（SAME_DAY）。
- 车道归属行：`10/10 条车道有主 · 归属唯一 · 5 条有主却读不到它的产出封套（bm-b 欠 moneyflow
  marks astock_daily zt_pool · bm-a 欠 etf_panel）· 已退役 options`。

## 五、诚实清单

- 代笔**只**解决「页面停摆」，不恢复 bm-a 的任何数据车道；那 5 条欠证车道照旧欠证。
- 面板戳闸改成读活面板后，链跑成本上升（3 面 × ~47s），没有做缓存——缓存会让「面板动没动」
  退回成「缓存新不新」，正是上一版的病。
- 本轮的供给判决（zoo90 鳄鱼定时器 REFUSE_AS_CANDIDATE）来自上一个死窗的产物，已按其自检
  13/13 与发布面证据接纳，非本轮实测。