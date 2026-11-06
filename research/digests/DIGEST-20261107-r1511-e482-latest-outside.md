# DIGEST 2026-11-07 r1511 (bm-b) -- E482：36 个 twin 族之外被拼出来的 *_latest.json，盘上有文件吗

**卡片**：E487 · **脚本**：`scripts/e482_latest_outside.py`（selftest 23/23）· **面**：`results/state_tilt/LATESTOUTSIDE-2026-11-07.json` + `latestoutside_latest.json`

## 缘起

E479 把总体定义成 36 个族名 twin，另外报了一句见证：147 个源、689 个 opener 站点在拼一个**不属于任何族**的 `*_latest.json`。那句话是「扫描不瞎」的证明，然后就没了 —— 既没问那个文件存不存在，也没问谁写它。一个读者拼出来的名字如果树上没有文件，它读的就是一张可能不存在的面。

## 做法

规则沿用 E479（basename 以 `_latest.json` 结尾且不属于 36 个 twin），把每一个站点落成行，字面量对树解析一次，拼写再与「谁按字面写它」join。解析六档：

| 档 | 含义 |
|---|---|
| path | 字面量带目录且该路径存在 |
| tail | 目录不存在，但同名文件在树里别处（E366 两种地址形式）|
| single | 裸 basename 且恰好一个文件有它 |
| several | 裸 basename 且多个文件有它（存在性成立、目录不成立）|
| template | 拼写不带具体名字（`%s_latest.json`、`_latest.json`）|
| none | 树里没有这个拼写 |

## 读数（2026-11-07）

- **201 个不同拼写 / 512 个去重站点 / 147 个源**。源数与父面**逐字相等** → 总体一致。
- 站点数 512 与父面的 689 不同，原因是定义：E479 数**字面量出现次数**（本树今日 697 次），本面数 **(source, line, literal) 三元组**。两个站点计数不是同一个测量；只有源数可对账。
- **195 个拼写解析到盘上的文件（491 站点）**；**6 个解析不到（21 站点）**：
  - 3 个模板：`_latest.json`（13 站点）、`banddraw%s_latest.json`（3）、`%s_latest.json`（1）
  - 3 个 selftest 伪件名：`a_latest.json`、`b_latest.json`、`fixture_latest.json`（写手往临时目录写）
  - → **`no_file_carries_it_and_no_source_writes_it` = 0**：没有一个真读者在开一张没人产的面。
- **111 个拼写「文件在 + 有源按字面写它」**（405 站点）；**84 个拼写「文件在、但没有源按字面写它」**（106 站点）—— 这就是 E473 族：写手运行时拼名字，字面量普查看不见。
- 4 个拼写的同名文件不止一份（`gateclamp`/`gateoperands`/`gateprint`/`legeps` 各 2 份）。

## 判决

`most_outside_opener_sites_resolve_to_a_file_but_some_open_a_spelling_no_file_carries` —— 491/512 站点解析到真文件；剩下 21 个里 17 个是模板、4 个是夹具，**不是**死读者。

## 三条可复用

1. **「零」要分两类**：解析不到的文件必须再分「模板不带名字」与「临时目录伪件」。混成一句「6 个死读者」就是把 3 个模板 + 3 个夹具读成一个真实缺陷（E444/E462 同族）。
2. **父面计数与子面计数只有定义相同才可比**：E479 的 689 是出现次数、本面的 512 是三元组。源数相等才是总体一致的证据；站点数相等与否不说明任何事（E368/E369「出处≠复现」的姊妹面）。
3. **字面量普查的盲区是写完就忘的**：106 个「没人写」的站点绝大多数正是运行时拼名。任何「按字面没人写就删面」的保留规则都必须先跑本面。

## 验证

- `run` rc0；`check` problems=[]；`verify` 同树重建 problems=[]；`selftest` 23/23（六档解析 + 四类分支 + 计数/判决自洽 + 3 个 doctored 面全红）。
- S6 腿 `latest_spelling_exists` rc0 0.07s（`results/_r1511bmb_s6_chain.json`）。
- smoke 腿 `E482 an outside-population latest spelling resolves to a file or is named as one that does not`：单跑 1/1 绿，doctored 1/1 红，面 sha 归位 `4b87897400bc`。

## 下游

E487 已入池（ready）：**84 个「文件在、没有字面写手」的拼写里，有多少有「合成写手」**（模块常量里带拼写词干）—— 这一桶 106 站点正是字面量普查的结构性盲区。