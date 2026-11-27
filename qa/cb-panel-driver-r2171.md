# QA — r2171 (bm-c) — 转债双低这条线第一次有了驱动（check/update 门 + 链腿 + 车道指派）

## 本轮回答的问题

r2169 的归因面把 `cb_panel` 判成 `no_driver`：写入器 `scripts/cb_dual_low.py` 在盘、
面板停在 **2026-11-20**，而链腿／计划任务／register 脚本三源全空、连 `config/lane_hosts.json`
里也没有指派。于是 `results/cb_dual_low.json`（第二条收益线的结论面）一直印的是那一天的年化与夏普。

r2170 留给本轮的指针就是这条：(a) 先定宿主、先写「已覆盖即零网络」的门，再接腿。

## 改了什么

| 面 | 改动 | 为什么 |
|---|---|---|
| `scripts/cb_dual_low.py` | 新增 `check` / `update` / `status` / `selftest` 四个子命令 + `check(expected, pub, stamp, recorded)` 纯函数 | 面板此前没有任何驱动，也没有任何面问过「我过期了吗」。`check` 问的是**官方日历的 expected bar day**（外部锚）与**这张面自己发布的那一天**；`update` 是唯一会花钱的写者，面板已覆盖预期完整 bar 日即零网络 no-op |
| 同上 | `check` 同时把「构建面板的字节」记成锚（`size`+`mtime`），状态面 `results/cb_dual_low_update_status.json` 落盘 | 只比日期会漏掉第二种过期：面板被重建了、而定价它的那张面没人重跑。r1935 的同族——「不知道在跟谁比」不等于「我很好」 |
| `config/lane_hosts.json` | `cb_dual_low: bm-c` + authority 追注 | r2169 的判词里这一条连指派都没有；指派必须是对**已有驱动**的命名，所以本文件和链腿同轮落地 |
| `Tools/s6_chain_bmc.py` | 新腿 `update_cb_dual_low`（check 0.2s → 只有 STALE 才付 update） | 链腿之后紧跟 `update_lhb_inst`：两条都是 EM datacenter 采集族、都是 bm-c 车道 |
| `Tools/chain_writer_audit.py` | `WRITER_MODES` 增补 `update` | 审计把写者的动词当成了**范围**：`... cb_dual_low.py update` 与它自己的 `... check` 落在两个 key 上，于是链正在写这张面时，审计报告「没人写它」（详见 research/CB_PANEL_DRIVER.md §2） |

## 实测证据

刷新（分离进程，`python scripts\cb_dual_low.py update`，rc0，**157.3s**）：

```
cb_dual_low: refresh (panel 2026-11-20 / published 2026-11-20 / expected 2026-11-26, tail_after=2026-11-20)
[fetch] bonds=1067 pending=334 incremental=318 tail_after=2026-11-20 workers=4
  334/334 ok=334 fail=0
[build] files=1051 rows=808457
[run] panel rows=791209 codes=1051 2007-07-12 -> 2026-11-26
  n=20 r=20 cost=10.0bp -> CAGR 7.35% SR 0.758 MDD -22.6% turn 4.60/yr
  bench(全池等权 r20)  -> CAGR 6.44% SR 0.701 MDD -23.7%
  no-ITM-filter        -> CAGR 7.06% SR 0.717 MDD -26.9%
cb_dual_low: updated (published 2026-11-26, expected 2026-11-26) in 157.3s
```

零网络门（同一命令第二次，**0.4s**）：

```
cb_dual_low: no-op (panel 2026-11-26 == expected 2026-11-26, priced and stamped)
```

链腿（`python Tools\s6_chain_bmc.py --only=update_cb_dual_low`）：

```
0 update_cb_dual_low 0.2s check OK: published bar == expected 2026-11-26, panel stamp 25433554B/2026-11-27T11:31:14
chain: 1/1 rc0
```

**链会付费自愈（r1850/r1934 契约的真面证明）**——把面板 mtime 改写一格（字节锚失配）后：

```
$ python scripts\cb_dual_low.py check
check STALE: the built panel changed since the status face was written
  ({'size': 25433554, 'mtime': '2026-11-27T11:31:14'} -> {..., 'mtime': '2026-11-27T11:34:21'})     rc3

$ python Tools\s6_chain_bmc.py --only=update_cb_dual_low
0 update_cb_dual_low 54.8s check OK: ... +refresh(rc=0,54.2s)     rc0
```

（这条路径**不联网**：面板源已覆盖 11-26，写者只做 rebuild + reprice，54s 对 157s 的差别就是那次
 334 券增量拉取。）

自检（10 腿，含 6 条行为腿用真实 `check()` 吃毒）：

```
cb_dual_low selftest 10/10
  L2 日历读不出 → rc2，且不含 STALE 字样（重建治不了日历）
  L3 面缺失 → rc3 且说 face missing（r1581 的修复词）
  L4 旧 bar → rc3 且同时点名两个日期
  L5 比日历还新 → rc1，且绝不说 STALE（把真分歧留成红）
  L6/L7 没记锚 / 字节变了 → rc3 STALE
```

下游面重 derive 后的读数：

```
data_lane_freshness : in_sync cb_panel tail=2026-11-26   （原 stalled 11-20）
lane_lag_attribution: counts {"in_sync":13, "retired_by_design":1, "host_dead_takeover_available":1,
                             "gate_blocked":1}          （cb_panel 已不在待修表）
                    剩余可动 3 条：ah_panel=源端断连 / heat=收盘窗 / options=设计退役
chain_writer_audit  : 395 legs（138 paired）· faces 178 · 174 有写者腿 · check-only **0 red / 4 disclosed**
chain_contract_word : n_legs 395 · n_writer_legs 138 · n_candidates 13 · n_permanent_red 0
lane_ownership      : OWNERSHIP_UNIQUE 16 lanes · conflicts none
```

## 全量冒烟（如实）

本轮背景跑了一次全套（分离进程，1114s）：**792/794 PASS, 2 FAIL**，两条都是本轮自己改动的正确反应，
且两条的底层命令复跑均已 rc0：

| 冒烟腿 | 冒烟时的红 | 复跑 |
|---|---|---|
| `product: every lane names one host before any task is re-enabled` | `cb_panel.authority: 'data_lane_freshness.LANES' -> 'config/lane_hosts.json'` | `python scripts\lane_ownership_declaration.py run` → `OWNERSHIP_UNIQUE, conflicts: none` rc0 |
| `config: no checked face was left without a writer leg` | `scripts/cb_dual_low.py` 不在基线 | `python Tools\chain_writer_audit.py --check` → `4 faces checked, 4 known check-only, 0 newly paired` rc0 |

**未跑改后的第二遍全量**（每次约 16-19 分钟），因此本轮不宣称「套件全绿」——只宣称
「本轮引入的两条红已按各自写者重 derive 到 rc0」。

## 未做 / 未验证（如实）

1. 未跑改后的全量冒烟（见上）。
2. 未跑完整 S6 链（395 腿）；本轮只跑点名单腿 5 条 + 四个固定腿（对账/attrition/算力审计/水位）。
3. `check` 只认三件事：官方日历的 expected bar 日、本面发布的那一天、构建面板的字节锚。
   面板源 CSV 若被外部改史而字节没动（例如某只券被单独重拉但没 rebuild），`check` 读不到；
   这是写者下次 `update` 全扫时才发现（同 r2164/r2167 已披露的同族局限）。
4. `cb_panel` 的宿主指派由本机写入；他机若要接这条车道，改 `config/lane_hosts.json` 一处即可，
   写者自带 `lane_host_of()` 守卫（非宿主只印一行诚实 no-op）。
