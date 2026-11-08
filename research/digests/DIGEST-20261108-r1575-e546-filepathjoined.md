# DIGEST 2026-11-08 · r1575 bm-b · E546 — the file-naming constant read as a directory

**一句话**：E537 说 35 个 `__file__` 派生常量命名的是**文件**而不是目录，这一轮把这 35 个常量被消费的 49 处站点全部定价——**没有任何一处把它当目录 join**，31 处明确当文件读，4 处（三处 abspath 恒等比较、一处默认实参）不属于任何一类、如实记 unknown。

## 为什么值得问

一个名字叫 `SRC`/`OUT_PATH` 的常量，读者默认它是前缀。`os.path.join(SRC, "x")` 一旦出现，得到的是 `…/run_e336_smoke_leg.py/x`——一个不存在、也永远创建不出来的路径。这类缺陷不会报错，只会让下游读到空。E537 把 35 个这样的常量点名留在面上，但没回答「有没有人这么用」。

## 读数

| 量 | 值 |
|---|---|
| 普查总体（E537 发布） | 35 常量 / 6 名字 |
| 直接站点 | 49（file 32 / directory **0** / probe 0 / unknown 17） |
| 一跳站点（同模块被调函数） | 1（file 1 / directory **0**） |
| 行类 | 31 file-only / 4 unknown-only / 0 directory |
| 名字分布 | SRC 23、OUT_PATH 5、SELF 4、RESULTS_JSON、EW_PATH、CAL_PATH |

判词：`every_file_named_constant_is_read_as_a_file_where_a_site_says_which`

## 两条自己踩到并修掉的

1. **fixture 里 `HERE` 同时被 `dirname(HERE)` 和 `join(HERE, "nothing.csv")` 用到**——按规则它**本来就该**是目录行，是自测的期望写错了。留下的 fixture 里 `HERE` 只喂 `dirname`（file 行）、`UNUSED` 只被 name 一次（unread 行）、`SRC` 两种都有（directory 行），三种行类各有证人。
2. **Vocabulary 改字典后漏改推导式**：`{s["shape"]: 0 for s in SHAPE_VOCAB}` 把字符串当字典下标，`build` 直接崩——这类「改了数据结构没改消费点」只有跑起来看得见。

## 边界

只扫定义常量的模块（导入侧 `imports_published_elsewhere` 逐行披露但**不分类**）；交给本扫描不跟的函数/比较/默认实参的站点一律记 unknown，**不记 clean**；`what_the_consumer_gets` 是拼写而非运行时路径。

## 载体

`scripts/e546_file_named_constant_use.py`（selftest 20/20、check problems=[]、verify identical）·
`results/state_tilt/FILEPATHJOINED-2026-11-08.json` + `filepathjoined_latest.json` ·
S6 腿 `file_named_constant_use` · smoke 腿 `# E546`（1/1 绿、--doctor 红）· 卡 E546