# DIGEST 2026-11-08 · r1573 bm-b · E544 — the item store between a binding and its site

**一个句子**：E536 把自己发现的「绑定与使用点之间还有一次 item store」当成局限留在面上，这一轮把这个
形状拿去全仓定价——1180 个模块里只有 13 处是解释器能绑定的容器上的这种（store, 读）对，其中 4 处读出的
值与折叠发布的值不同、8 处是 store 造出了折叠根本不会发布的项、1 处是幂等回写。

## 为什么值得做

E536 的证人 `scripts/e285_interrange_gap_ceiling.py:503-505` 自己就写着这件事：折叠发布 lo=1.0 的
hull，断言吃 lo=0.9。E536 把它登记成「下一张卡」。这轮回答的不是那一个证人，而是：这个缺陷面有多宽。

## 读数

| 项 | 值 |
|---|---|
| 扫过的源 | 1180 个 `scripts/**.py` |
| 行 | 13 |
| 判改（读到的值与折叠值不同） | 4 |
| 造项（折叠里根本没这个键） | 8 |
| 幂等（回写同值） | 1 |
| 出现判改行的源 | 3（e285 / prospect_regime_segments / t33_attack_wave） |
| e285 证人 | 在总体（2 行，2 行判改） |

判词：`item_stores_between_a_binding_and_its_site_both_change_published_values_and_publish_items_the_fold_never_sees`

## 两条自己踩到的坑（都已焊进闸）

1. **同一行里读先于写**。`rep["cuts"] = list(rep["cuts"])` 的右值读发生在写之前；按列号排序会把写
   排在读前面，于是这一行被记成「读在写之后」。改成（语句位置、语句内相位：读 0 / 写绑 1）后行数
   从 25 掉到 13——那 12 行是排序造成的假象。
2. **深一层的 store 改的是上层容器**。`off["rows"][1]["tight"] = ...` 之后读 `off["rows"]` 同样受
   影响；只认「路径完全相同」会把唯一的证人排除在总体之外（初版 19 行、witness_rows=0 就是这么来的）。
   判据改成两条路径互为前缀。
3. 附带：赋值目标的**内部**下标在 AST 里带 Load 上下文，不排掉就会伪造出一条同行的读。

## 边界

总体只含解释器能绑定的容器（字面量，或纯语句链仓库函数的返回值）。从树读出来的容器不在总体里，
**且不被算成干净**——这 13 行是「这个形状在这个总体里有多贵」，不是「全仓只有 13 处」。

## 载体

- `scripts/e544_item_store_between.py` — build / check / verify / selftest（13 臂）
- `results/state_tilt/ITEMSTOREBETWEEN-2026-11-08.json` + `itemstorebetween_latest.json`
- S6 腿 `item_store_between`（check rc0）
- smoke 腿 `# E544` + `scripts/run_e544_smoke_leg.py`（1/1 绿，`--doctor` 1/1 红）
- 方法论卡 `knowledge/METHODOLOGY_ASSETS.md` E544