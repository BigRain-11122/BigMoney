# E566 · 谁在读链回执，谁只是提到了它（r1594 bm-b · 2026-11-08）

E563 定案：159 份短回执里 138 份是任意子集，读者拿在手上无法还原它覆盖了哪些腿。加字段之前先定价——**到底有没有人需要这个覆盖信号？**

本轮把「提到」和「读取」分开量：全仓 12,599 个 `.py` 里 **158 个**载有链回执路径，按 AST 祖先（不是按行内有没有 `open` 字样）判类。

## 读数

| 类 | 计数 |
|---|---|
| 写回执（`json.dump` / `open(...,'w')`） | **77** |
| 读回执载荷（`json.load` / `open` 读 / `glob`） | **7** |
| 只提到（散文、`git add` 清单、docstring） | **74** |
| 不可解析 | 0 |

七个读者再分类：

| 类 | 计数 | 是谁 |
|---|---|---|
| 覆盖自知（行数与腿表相接） | 3 | E560 / E561 / E562 三个研究自己 |
| 打印 `N/<字面量> rc0` | **2** | `results/_r1208bmc_closeout.py`、`results/_r1210bmc_closeout.py` |
| rc 过滤不看条数 | 0 | — |
| 读来做别的事 | 2 | `_r253bmc_s7_closeout.py`、`_r587bmb_close.py` |

价格：只 **2 对 (reader, receipt)** 能接上 E561 的 join 定价（其余回执是 gitignore 的运行时件，缺席＝unpriced，不是零覆盖），其中 **1 对是短回执**：

> `results/_r1210bmc_closeout.py` 读 `_r1210bmc_s6_chain.json`（**39 行**），而它那一轮的表有 **61 条腿**——它的落款写的是 **“S6 chain 39/39 rc0”**。

另一对是零行回执（`_r253bmc`，E561 判 `no_runner_blob_reachable`）。

## 结论

- **盲区不是假设，已经印过一次**：39 条腿的回执被写成「39/39」，分母是源码里的字面量，不是表长。
- **但也不该因此给回执加字段**：加一个 selection 字段只是把同一件事再存一遍，而 E562/E563 已证 138/159 是任意子集——字段能回答「跑过哪些」，回答不了「本该有哪些」。真正缺的是**读者自己给出分母**，那是读者一侧的事。
- **命名 ≫ 读取**：74 个「消费者」其实只是散文和 `git add` 清单。任何「消费者普查」若不区分这两拨人，会把 10 倍的散文当读者。

## 可复用教训

1. **命名不是读取**——判据必须是 AST 祖先（`json.load(open(...))` 里才算读，`git add` 清单里只是名字），不是行内关键词。第一版若按「行里有 open」判，74 个只提到的文件会全部变成读者。
2. **「分母是字面量」可静态抓**——`}/39 rc0`、`39/39 rc0` 都是真形状，而 `1/6`、`12/12 shards`、`173 rows /` 是噪声：判据必须要求斜杠后的数字紧贴 `rc0`/`rc=`/`legs`。第一版纯 `/digits` 把 4 个读者全判成 literal，收紧后只剩 2 个（precision 假阳性 2/4）。
3. **证据行号可以发布，但不要进闸**——158 个源里包括 2,000 行的 runner，任何在其顶部加一行注释都会让所有行号下移；`check` 门住分类与计数，不门住行号，否则 S6 腿每轮必红。

## 边界

纯静态：不执行 runner、不重写回执、不打开任何回执内容（只扫源码里的字符串与调用链）。每行带 `source_class`、读者类与其证据行号，闸只从已发布行重算。只有 2 对可定价，其余如实进 `unpriced_pairs`。

## 载体

- `scripts/e566_receipt_coverage_consumer.py`（build / check / verify / selftest 10 arms + 158 rows）
- `results/state_tilt/RECEIPTCOVERAGE-2026-11-08.json` + `receiptcoverage_latest.json`
- S6 腿 `receipt_coverage_consumer`（`check`，~0.3s）
- smoke 腿 `# E566` + `scripts/run_e566_smoke_leg.py`（`--doctor` 拒手写类）
- 卡：`knowledge/METHODOLOGY_ASSETS.md` E566