# QA 证据 · r2058 · 车道交接说明（`scripts/ingest_lanes_doc.py`）

- 轮次：r2058（bm-c，2026-11-24）
- 令源：`fleet/orders/O-20261124-2300-bm-c.md` §1-C（金融资料交接：逐条写明重建命令 / 数据源与频率 / 覆盖与已知缺口）
- 产物：`scripts/ingest_lanes_doc.py`、`research/INGEST/LANES-DASHENG.md`、`research/INGEST/LANES-DASHENG.json`

## 四条腿（原样 rc）

| 腿 | 命令 | rc | 证据 |
|---|---|---|---|
| 自检 | `python scripts/ingest_lanes_doc.py selftest` | 0 | 27/27 PASS（见下） |
| 生成 | `python scripts/ingest_lanes_doc.py` | 0 | `LANES-DOC ok lanes=15 files=13950 bytes=1575857959 scripts=15` |
| 面新鲜 | `python scripts/ingest_lanes_doc.py --check` | 0 | `LANES-DOC check ok lanes=15` |
| 负控 | 见下 §负控 | 3 / 0 | 面被改一位即 rc3 并点名 |

## selftest 27 腿

```
ok   lanes unique                     ok   resolve via registry
ok   date idx by name                ok   resolve via convention
ok   day idx second                  ok   resolve unknown -> None
ok   no date col -> None             ok   build lanes count
ok   bom date col                    ok   build totals sum
ok   norm date                       ok   every lane resolved
ok   norm date empty                 ok   render deterministic
ok   norm date garbage               ok   writer map non-empty
ok   lag 0 when aligned              ok   writer map cb_panel
ok   lag 1                           ok   resolve declared
ok   lag 2 skips weekend             ok   docstring extracted
ok   lag 0 when ahead                ok   docstring missing -> None
ok   calendar coverage read          ok   tail line readable
ok   calendar monotonic
SELFTEST 27/27 PASS
```

## 负控（面漂移必须自称 STALE）

1. 手动把 `research/INGEST/LANES-DASHENG.md` 里任一体量数字改一位 → `--check` 返回 **rc3** 且文案含 `STALE`、点名声道落后于盘（复跑生成器后 rc0）。
2. 删除 `research/INGEST/LANES-DASHENG.json` → `--check` 返回 **rc3** 且文案为 `STALE face missing`。

（两条均在验证后按字节复原，复原后 `--check` rc0。）

## 本轮挡下的假声明（自捕）

初版把 `cb_daily` 按 `scripts/update_cb_daily.py` 约定找不到脚本，直接印成「无重建脚本 → 只能分包」——
盘上真写者是 `scripts/cb_dual_low.py`（`scripts/data_lane_freshness.py` 的 `WRITER_FACES` 里写着），
`ext_slots` 同理是 `scripts/backfill_ext_slots.py`。
修法不是补两条字符串，而是加**写者登记表解析 + 三级解析链**（declared → writer-registry → 约定名），
并加 4 条自检腿钉死它；现在 15/15 车道都解析出脚本，分包面因此是空的（真结论：不需要分包）。

## 未验证（如实）

1. 未跑全量 `smoke_test` 与 S6 链——轮首竞争探针 rc=3（同树另有 interactive 宿主在写共享面），按 r1907/r1927 竞争窗禁跑。
2. 覆盖区间是**文件首尾行**的并集，不是逐 bar 完整性检查：中间缺日不报（那是 `data_lane_freshness` 的职责，本面不重造）。
3. 「数据源与频率」是脚本文档字符串的原样引用，未逐条核对端点可达性。
