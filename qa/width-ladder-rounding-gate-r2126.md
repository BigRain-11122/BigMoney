# 宽度阶梯那条腿为什么每轮都红 —— 缓冲区回读的舍入口径

- 轮次：r2126（bm-c）
- 时间：2026-11-26 11:0x-11:2x
- 证据件：`results/money_rounding_gap_probe.json`（探针）、`results/_r2126bmc_buffer_gap_fix_receipt.json`（干跑回执）
- 结论一句话：这条腿**按构造成立不了**，不是面算错。面的三个数各自舍入到 3 位，腿却要求 1e-9 的逐位相等。

## 1. 腿说的话

冒烟腿 `product: the width ladder names why it cannot be quoted, and the buffer line is tested on a point it never saw`
（`smoke_test.py` §width ladder）连续多轮报红，理由只有一句：

```
the published gap is not observed minus predicted
```

## 2. 面里的三个数

`results/etf_book_buffer_floor_readback.json`：

| 字段 | 值 |
|---|---|
| `observed_pp` | 0.748 |
| `predicted_pp` | 0.298 |
| `gap_pp` | **0.449** |
| `tolerance_pp` | 0.057 |
| `verdict` | REFUTED |

拿面上印的两个端相减：`0.748 - 0.298 = 0.450`，与 `gap_pp` 差 **0.001**。

## 3. 根因（生产者侧，非缺陷）

`scripts/etf_book_phase_atlas_arms.py::readback_of` 第 1668-1669 行：

```python
"predicted_pp": round(pred, 3), "observed_pp": round(obs, 3),
"gap_pp": round(gap, 3),          # gap = obs - pred，用未舍入的原始值算
```

三个数分别从原始值舍入。两个 3 位小数的端，重算差最多只能准到一个舍入步
（各 5e-4，合 1e-3）。腿的断言是：

```python
abs(round(obs - pred, 3) - gap_pp) > 1e-9   ->  red
```

`0.001 > 1e-9` 恒成立 → **无论数据怎么变，这条腿永远红**。

这就是 r1813 那条判例的精确复现（「四舍五入后的频率和不是分布——容差=舍入误差本身」），
以及 r1789 说过的危害：**永久红会训练读者把真缺陷当背景噪声**。

## 4. 家族扫描（有没有第二处）

探针把 `results/*.json` 里所有「一个差值字段 + 它该来自的两个端」的模式扫了一遍
（命名族：`*gap_pp` / `*delta_pp` / `*diff_pp` × `observed/predicted` / `a/b` / `high/low`）：

- 检查 2 对，命中 1 处 —— 就是它自己；
- **0 处**无法用舍入步解释（即没有第二处真不一致）。

所以这是一个孤例，不是系统性问题。

## 5. 修复方案（两条，建议都做，按此顺序）

1. **面印未舍入的端**（`scripts/etf_book_phase_atlas_arms.py`）
   加 `observed_pp_raw` / `predicted_pp_raw` / `gap_pp_raw`。
   好处：差值变成可逐位重建；标题数字不变，读者不受影响。
   代价：面上多一组数，必须写明「标题仍是 3 位那一组」。

2. **腿优先用原始值，缺省退回舍入步**（`smoke_test.py`）
   有 `*_raw` 就按 1e-9 核；没有就按 1e-3（= 两个 3 位端的舍入步）核，并在注释里写出这个数的来历。

只做第 2 条也能立刻转绿（一个常数），但那样「面根本没印原始值」这件事就没有守卫了。

## 6. 本轮为什么没有落地

S0 竞争探针 `Tools/repo_write_contention.py` 在本轮全程 **rc=3 CONTENTION**
（7 个宿主存活，37 处共享面在重叠窗内被写过）。按 r1907 同树多宿主律，
本轮只做新增文件面，不改共享面。修复已做成可复算、可拒绝的落地件：

```
python Tools/money_rounding_gap_fix.py --check   # 干跑，已验证
python Tools/money_rounding_gap_fix.py --apply   # 落地
```

干跑实测：

```
WOULD PATCH (--check):
  - - float(_rb.get("gap_pp"))) > 1e-9):
  + - float(_rb.get("gap_pp"))) > 1e-3):
  anchor unique, face passes at the rounding step, nothing written
```

落地件自带三道门（r2123 判例）：
锚点不唯一 → 拒绝；面在 1e-3 下也不通过 → 拒绝；写后读回不显示恰好一处改动 → 回滚。
所以它不会把别人已经动过的那一行再改一次。

## 7. 下一轮的精确续作点

1. 竞争解除后 `--apply`；
2. 单独跑该腿确认转绿（`python -m smoke_test` 全量约 15 分钟，或用腿名过滤）；
3. 再按方案第 1 条给面补 `*_raw`，把腿的容差退回 1e-9 并保留退路。
