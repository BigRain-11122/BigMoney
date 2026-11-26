# r2124 (bm-c) — 涨停池日期口径被上一轮改写，年度线可达性面首次发布

日期：2026-11-26 09:4x-10:0x ｜ 机：bm-c ｜ watermark：红=false / lane=healthy ｜ 竞争探针 rc0 CLEAN（单宿主）｜ 孤儿面=0

## 一、两件产品的来历

### 1) 上一窗被中断的产品：年度线到底有没有一格能过（`etf_book_year_line_reach`）

r2121 关掉了「加钱能不能买到许可」（`SIZE_CANNOT_BUY_THE_YEAR_TEST`），留下另一半没人回答：**冻结网格（4 宽度 × 3 调仓）里有没有一格能过年度线**。被中断的窗口把脚本/面/说明写完了却没提交，本轮承接并验收：

- `python scripts\etf_book_year_line_reach.py selftest` → **12/12 PASS**
- `python scripts\etf_book_year_line_reach.py check` → **CHECK OK（12 cells, verdict REACHED_IN_SHAPE_NOT_IN_CAPACITY）**
- 链腿实测：`python Tools\s6_chain_bmc.py 2124 --only=year_line_reach,year_line_reach_write` → **2/2 rc0**（write 因源面推进到 11-25 重跑 59.9s，check 0.9s 纯 JSON 读）
- 结论（可查面）：**N3_R10_10bp** 是唯一四面全过的格子（top-2 **67.97%** 对线 70.00%，年化 11.15%），但它的一天容量 **0.14 亿 < 门 0.20 亿**；保持五只票容量够，只能在 10 日调仓下压到 **70.54%（差 0.54pp）**。同一宽度下 R10 &lt; R20 &lt; R40 逐行成立 ⇒ **这条线吃的是时间，不是宽度**（宽度买容量，买不到年份形状）。

### 2) 本轮真活：涨停池的日期列被 r2123 的整改改成了另一种口径

r2123 对 2026-11-23 那天出了 `LATE_COMPLETION_SUPERSET` 裁定（143→146 行，正确），但落地时把 `日期` 写成 `20261123`（扁平）。后果：

| 面 | r2123 之前 | r2123 之后 |
|---|---|---|
| `data/zt_pool/zt.parquet` 日期列 | 1894 行全 `2026-11-23` 式 | **1897 行全 `20261123` 式** |
| 另外三池（zbgc/dtgc/strong） | ISO | ISO（未动） |
| 采集器自己的口径（`update_zt_pool.py` L162/169/292） | `%Y-%m-%d` | 未变 |
| 日账 `collected_days.json` | ISO | ISO |
| 追加去重 `old["日期"] == day` | 匹配 | **匹配不上** |

可见后果三条：①CEO 一页纸风险带打印「四面板截止日不一致：zt=20261123、zbgc=2026-11-23…」——同一天被印成两个日子；②冒烟 `product: the CEO page carries today's market risk tape` 与一页纸自检 `risk tape agrees with daily report §九` 转红；③采集器下次按 ISO 找当天会找空。

**修复**（`results\_r2124bmc_zt_date_caliber.py`，只动这一列，其它一律拒绝写）：
- 把整列 `YYYYMMDD` → `YYYY-MM-DD`；
- 写盘前硬断言：行数不变（1897）、**逐日计数集合恒等**、全部行 ISO、11-23 那天 = **146**（整改裁定的行数）。首版比较键空间写错（拿扁平键和 ISO 键比）当场判 REFUSED，改成一并在 ISO 键空间比才放行——**拒绝写是我自己的守卫在说话，不是我事后发现**；
- 收据 `results\_r2124bmc_zt_date_caliber.json`：`REWROTE-CALIBER`、problems=[]、distinct_days=33。

**修复后采集器正常推进**（`python scripts\update_zt_pool.py`，82s，8 次调用）：
```
zt 11-24: 55 行 / 11-25: 51 行   zbgc 68 / 30   dtgc 2 / 43   strong 85 / 80
cutoffs {'zt': '2026-11-25', 'zbgc': '2026-11-25', 'dtgc': '2026-11-25', 'strong': '2026-11-25'}
```
——这正是 r2123 挂在「09:28 后自动补两天」上的那条死信，本轮实测补上了，且四面板同日。

**读者面随后跟上**（两张共享面重生，非改判据）：
- `scripts\ceo_live_usage.py` → 风险带 `status=ok / cutoff 2026-11-25 / aligned **True**`，zt 51(-4)、zbgc 30(-38)、dtgc 43(+41)、strong 80(-5)，封板率 63.0%；页内那行「四面板截止日不一致」消失。
- `scripts\daily_report.py run` → §九 同步为「四面同为 **2026-11-25**」，跨面一致性腿恢复。
- `python scripts\ceo_live_usage.py selftest` → **ALL PASS**（修前唯一红腿 `risk tape agrees with daily report §九`）。

## 二、证据清单

| 动作 | 命令 | 结果 |
|---|---|---|
| 新产品自检 | `python scripts\etf_book_year_line_reach.py selftest` | 12/12 PASS |
| 新产品复算 | `... check` | CHECK OK（12 cells） |
| 新链腿 | `python Tools\s6_chain_bmc.py 2124 --only=year_line_reach,year_line_reach_write` | 2/2 rc0 |
| 口径修复 | `python results\_r2124bmc_zt_date_caliber.py` | REWROTE-CALIBER，problems=[] |
| 采集门 | `python scripts\update_zt_pool.py` | rc0，四面板 11-25 |
| 一页纸 | `python scripts\ceo_live_usage.py` + `selftest` | aligned True / ALL PASS |
| 战报 | `python scripts\daily_report.py run` | 四面同为 2026-11-25 |

## 三、未做（如实）

- **全量冒烟本轮未收总数**：以分离进程另跑 `logs\smoke_r2124b.log`（pid 21236，09:5x 起），轮末仍在飞 → 不宣称套件总数。上一趟被中断轮的读数是 **770/781 PASS · 11 FAIL**，本轮已关掉其中 3 条（CEO 一页纸 date/cash 腿、market risk tape 腿、外加被 zt 口径波及的战报面）。
- 其余 carried 红未碰：paper book NAV 身份（6.5e-09）、lane appended nothing、phase_atlas_arms 三臂重烧、day_delta、toll-ladder、premium 读数后价格、cost assumption、width ladder。
- **未改任何判据线去修绿**；`etf_book_year_line_reach` 的控制容差（share 5e-05 / CAGR 0.05pp）由脚本自检钉死，不因结果调整。
