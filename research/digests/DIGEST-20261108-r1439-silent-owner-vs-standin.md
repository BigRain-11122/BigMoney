# DIGEST 2026-11-08 r1439 bm-c — 静默属主 vs 替班者

**一句话**：板子把「bm-b 静默 222 小时，名下 astock_daily、marks」印成一句话，
但 astock_daily 每一轮都由 bm-c 声明接管（`authority.took_over_by=bm-c`，tail 11-06，
覆盖率 99.9%，封套 ts 就是当天 10:41）——同一行里，「已经有人在跑」与「没人管」被并成了一个列表。

## 读了什么

- `config/lane_hosts.json`（v 2026-11-08T07:5x）：12 条道口，含 bm-c 接管的 9 条；
  `update_astock_daily` **不在 map 里** → 板子按 LANES 静态 `owner=bm-b` 认人。
- `results/astock_daily_update_status.json`：`authority{ lane_owner=bm-b, writer_machine=bm-c,
  data_face_machine=bm-c, declared_takeover=true, took_over_by=bm-c }`，
  `takeover{ owner=bm-b, by=bm-c, reason="owner bm-b silent 214.0h >= 120min" }`，
  `panel.cutoff=2026-11-06`、`coverage_pct=99.9`、`per_files=5223`。
- `scripts/data_lane_freshness.py`：`declared_takeover_by` 已在行上（r1256/r1257 用于
  authority 判定），但 **hosts 聚合层没消费它**。

## 改了什么

`scripts/data_lane_freshness.py` 唯一文件：
1. hosts 聚合为每个属主维护 `lanes_taken_over{lane: machine}`；
2. 静默块输出两栏 `silent_waiting`（真没人管）与 `silent_taken_over`（已有替班）；
3. stdout / MD 两面同句打印（`waiting=marks taken_over=astock_daily<-bm-c`）；
4. selftest 新增 L31（28→29/29）钉两栏的值，不是钉「告警消失」。

## 实跑读数（2026-11-08 19:0x）

```
lanes=15 (registry=11 +lane_hosts_union=4 declared_writers=12)
SILENT-HOST-DOWN bm-b age_h=222.25 unverifiable=marks
SILENT-OWNER bm-a age_h=26.49 lanes=futures,heat,lhb,repo waiting=futures,heat,lhb,repo taken_over=-
SILENT-OWNER bm-b age_h=222.25 lanes=astock_daily,marks waiting=marks taken_over=astock_daily<-bm-c
verdict=host_down counts={'retired': 1, 'in_sync': 13, 'unverifiable': 1} worst=marks
```

改前同一时刻只有 `lanes=astock_daily,marks`，读者无法分辨哪一条还需要人。
bm-a 26.49h 静默是真告警（名下四道全 waiting），本轮不动。

## 集团令兑现（D-20261108-14 → @BigMoney）

- 首腿（D-20261108-02）验收「新鲜度脚本实跑含并集道数」：**满足**，`registry=11 + union=4`，
  `declared_writers=12`，stdout/MD/JSON 三面同数。
- 第二腿（D-20261108-03）验收「`fleet/backlog.md` 四卡号各 ≥1 命中」：**满足**，
  B-CITY3D-01(2)/B-CITY3D-02(1)/B-XIDUDU-01(1)/B-XIDUDU-02(1)，行 35-38，
  其中 B-XIDUDU-01 行内已带 D-20261108-15 的「18:00 前至少 1 件真实点火」期限（执行面属 BigCompute，非本司）。
- 本轮补的是这两腿之下的**第三层**：并集让道口可见，接管让「可见」不至于被读成「等属主」。

## 未验 / 未做

- 全量 smoke 本轮后台启动（pid 21916，`results/_smoke_r1439.out`），收轮时仍在跑，未见 FAIL。
- `timeseries` 之外的九道接管是否都带 `authority.took_over_by` 未逐一核（本轮只按行上字段消费）。