# QA 卡 · `*_gib` 单位契约与族扫描（r2149）

**实物**
- `Tools/gpu_face.py`（`gpu_mem_family` unit 判定 + `face_family_keys` + audit 三腿改造 + 4 条自检腿）
- `Tools/gpu_alias_writer_census.py`（`unit_lies` → 残留守卫 + 2 条自检腿）
- `research/GPU_GIB_UNIT_CONTRACT.md`
- `fleet/inbox/MSG-20261126-2235-ALL-gib-unit-rewrite.md`

## 验收项

| # | 项 | 证据 | 结果 |
|---|---|---|---|
| 1 | 自检全绿（含 4 条新腿） | `python Tools/gpu_face.py --selftest` | **53/53 PASS** |
| 2 | 普查自检全绿（含 2 条新腿） | `python Tools/gpu_alias_writer_census.py --selftest` | **17/17 PASS** |
| 3 | 名字与单位同解 | `gpu_mem_family("gpu_free_gib")` | `("free","gb")`（旧：`("free","mib")`） |
| 4 | 族扫描不再按枚举 | `audit()` 走 `face_family_keys()` | `gpu_free_gib` 首次进入 spread 射程 |
| 5 | 残留会被判红（修法前行为） | `audit({... gpu_free_gib: 13752, gpu_free_mib: 4696})` | free 族 spread 命中，腿 L3h PASS |
| 6 | 一次探针即愈 | `python Tools/gpu_face.py apply` + `audit` | `gpu_free_gib` 13829 → **13.3**；`findings=[]`（36 键） |
| 7 | bm-c 心跳不再自相矛盾 | `results/gpu_alias_writer_census.json` | bm-c 无 free/used/total 冲突、无 names_lie |
| 8 | 面自洽可复核 | `python Tools/gpu_alias_writer_census.py --check` | `problems: []` |
| 9 | 他机残留如实点名 | census 句子 | bm-a `gpu_free_vram_gib=1038` → free spread 1,061,888 MiB（待其自身 apply） |

## 未做（如实）

- 全量冒烟未跑（套件窗口 >10min）；本面用 `audit()` 谓词直证那条冒烟腿的本机条件。
- S6 链未跑（`gpu_face` 已有链腿，本面未改链结构）。
- bm-a / bm-b 心跳未改（每机只写自己文件，交 inbox 消息；bm-b 的第二写者收编仍挂账）。
