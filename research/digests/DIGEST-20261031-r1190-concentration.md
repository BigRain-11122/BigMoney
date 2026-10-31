# r1190 (bm-a, 2026-10-31) — ETF 书收益集中度面落地 + 两枚运行坑

## 一、交付面

| 件 | 路径 | 状态 |
|---|---|---|
| 生成器 | `scripts/etf_book_concentration.py` | selftest 13/13 |
| 机器面 | `results/etf_book_concentration.json` | `--check` rc0（判词可从已发布行复算） |
| 人读件 | `research/ETF_BOOK_CONCENTRATION.md` | 中文，数字全来自面 |
| 方法论卡 | `knowledge/METHODOLOGY_ASSETS.md` E298 | append |
| 链腿 | `Tools/s6_chain_bmc.py` `etf_book_concentration`（在 `etf_book_order` 之前） | 31.2s rc0 |
| 操作面 | `ORDER-2026-10-30.md` 新增「这笔钱是从哪赚来的」 | 票面 selftest 80/80（leg46i） |
| smoke | 281/281 PASS 0 FAIL（终树） | 含新腿 E298 |

读数：前 1 名 7.5% / 前 3 名 22.1% / HHI 0.0241 → `BROAD|SURVIVES_WITHOUT_TOP3`；
删前三名 −1.99pp（9.60%→7.61%），删整条商品袖（41 只）−3.71pp（→5.89%，夏普 0.64，回撤 −11.8%→−22.3%）。

## 二、两枚坑（本轮实弹，值得复用）

### 坑 1：收口脚本「先写盘、后出错」＝计数器被吃掉

`_tmp_r1190_close.py` 第一次跑在拼报告行时 `TypeError`、第二次 `NameError`，但 **state 写在拼行之前**，
于是 `round_no` 被连加三次（1190→1193）。发现靠的是写后复读（`round_no` 与报告行不一致）。
正法：**收口脚本先构造完全部字符串字段，最后一步才落盘**；或落盘后立刻复读断言
「state.round_no == 旧值+1 且报告行只 +1 行」。同族=E 系列「有产无读」，这里是「有写无校」。

### 坑 2：跑着 smoke 时改共享腿表＝自己制造的红灯

第一遍全量 smoke 在飞时我把一条新腿加进 `Tools/s6_chain_bmc.py`，该 smoke 进程在跑到
「bm-a 链腿表 == 共享腿表」那条腿时读到 `legs=109 canonical=108` 判红。
这不是缺陷，是**自己的编辑与自己的测试赛跑**。
正法：批量跑的期间禁改被它断言的共享面（腿表/钩子/常量）；要么先停跑，要么等跑完再改，
并且**终树必须重跑**（r1183 律：改了就跑一次，不拿旧跑当证据）。本轮终树 281/281 全绿即为此。