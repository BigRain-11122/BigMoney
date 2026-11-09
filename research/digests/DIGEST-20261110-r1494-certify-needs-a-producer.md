# DIGEST 2026-11-10 r1494 (bm-c) — 认证面需要生产者，提示要指向能答的命令

## 现象（两个洞，同一条面）

`docs/data_lanes/FRESHNESS.md` 的「Tails read from a sample」段：

```
- `ah_panel`: 40 of 187 symbols read, tail 2026-11-09 (holder share unknown -- run `certify`)
- `astock_daily`: 40 of 5223 symbols read, tail 2026-11-09; the full scan holds it in 2,874 of 5,223 ...
```

1. `ah_panel` 的提示让读者去跑 `certify`，但 `certify_rows` 遍历的是手写 `LANES` 表，
   `ah_panel` 是 `config/lane_hosts.json` 映射出来的车道，**不在那张表里** → 跑十次也不会读它。
2. `results/data_lane_tail_certification.json` 是 11-09 21:38 手跑的。面板每天推进，
   于是每一轮页面都写「certification is older than this scan」，两条 smoke 腿常红：
   - `fleet: a panel tail read by sample is certified against a full scan`
   - `fleet: the board page carries the full scan's holder count`

## 根因分类

- 洞 1 = E289 族「同一概念两份实现」：看板的注册表是 `board_lanes()`，认证的注册表是 `LANES`。
- 洞 2 = E477 族「被读但没有生产者」：这张面有两个消费者（两条 smoke 腿 + 人读页面），
  链里没有任何腿写它。手跑一次的证书对一条每天推进的面板就是一次性商品。

## 修法

1. `certify_rows` 默认车道集改为 `board_lanes(root=root)`（与看板同源）。`ah_panel` 立刻可认证：
   187/187 持有最新 bar，尾 2026-11-09。
2. `panel_fingerprint(dir, pattern)` = (文件数, 最新 mtime, 总字节)。`certify` 对指纹未变的车道
   沿用上一行（`reused: true` + 原 `scanned_at`），全沿用时**一字不写**并 rc0 —— `as_of` 保持
   「文件被读的时刻」语义，不会被运行时刻冲刷成假新。
3. `cert_row_state(cert_row, board_row)` → `current` / `stale` / `missing`：页面 `_holder_sentence`
   与两条 smoke 腿共用。陈旧时页面印「certification is older than this scan」且不引用持有数；
   腿对陈旧判「认证过期，去重跑」，不再判「页面撒谎」。
4. 链腿 `data_lane_tail_certification` 接在 `data_lane_freshness` **之前**：页面引用的证书必须先写。

## 实测读数（2026-11-10 05:2x bm-c）

| lane | full tail | sample tail | files read | 持有最新 bar |
|---|---|---|---|---|
| futures | 2026-11-09 | 2026-11-09 | 10/10 | 9（1 个落后：主力合约切换） |
| repo | 2026-11-09 | 2026-11-09 | 11/11 | 11 |
| moneyflow | 2026-11-09 | 2026-11-09 | 5,225/5,226 | 5,225 |
| astock_daily | 2026-11-09 | 2026-11-09 | 5,223/5,223 | 2,927→2,938（bm-b 回填中，仍有 ~2,290 落后） |
| ah_panel | 2026-11-09 | 2026-11-09 | 187/187 | 187 |

- 首次全扫描 153s；第二次运行 **0.83s**（4/5 车道沿用，只有 astock_daily 因 bm-b 正在回填而重读）。
- 第三次（面板未动）**0.3s 零写**：`no-op: every panel's bytes are unchanged since ... nothing rewritten`。
- 链腿单跑 `--only data_lane_tail_certification,data_lane_freshness` → 2/2 rc0。

## 对抗验证（闸不能变瞎）

- 陈旧认证（full 2026-11-06 vs board 2026-11-09）仍判 `stale`，未认证的车道判 `missing`，
  认证比看板新时判 `current`（此时才要求逐字相等）。
- selftest 32/32（新增 L33 复用门 / L34 单一判据）。

## 未完成

- 全量 smoke（本轮只复算了改动直接覆盖的两条腿：两条均 CLEAN）。
- bm-b 名下 astock_daily 的 ~2,290 个落后符号仍是 bm-b 的回填进度，不是本机的活。