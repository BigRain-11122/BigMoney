# QA — page_fmt_guard（r2111，bm-c，2026-11-26）

## 这个门拦的是什么

一个**纯静态**缺陷类别，近三轮各以一副面孔出现一次：

| 轮 | 症状 | 形态 |
|---|---|---|
| r2105 | `ValueError: unsupported format character '/'` | 已被 `%` 格式化的串里写了 `%/yr` |
| r2109 | 页面真的印出 `5%%` | 没走 `%` 的串里写了 `%%` |
| r2110 | `ValueError: unsupported format character '\|'` | 已格式化的表头里写了裸 `%` |

两种形态的转义规则**正好相反**，所以只能靠「这一串到底走不走 `%`」来判——`ast` 能答，不用执行。

## 判据（冻结在脚本内，先于首跑）

- `LITERAL_DOUBLE_PCT`：字面量含 `%%` 且**未**参与 `%` 运算，且该字面量是写入器（`add/append/write/emit/...`）的实参或容器值 → 读者会看到 `%%`。
- `BARE_PCT_IN_FORMAT`：字面量**参与** `%` 运算，但含一个不构成合法转换的 `%` → 渲染期 ValueError。
- 明确不判（写进 `scope.note`，不是静默放过）：f-string（`%` 在那里是普通字符）、`.format()`、docstring、拼接片段（`("%." + str(d) + "f") % x` 这种分片本身不是格式串）、非页面渲染文件、以及非写入器调用的实参（断言/异常消息里的 `%%` 是文本）。
- 本工具自己的源码自我排除（其 fixture 就是两类缺陷的样本）。

## 验证实况

| 项 | 结果 | 证据 |
|---|---|---|
| `--selftest` | **19/19 ALL_PASS** | 6 条 fixture（clean / literal / bare / 非页面 / f-string / docstring）+ 标签可分辨 + 合法转义不误报（`%.3f%%`、`%-8s|%05.2f|%+d|%*d`）+ 非法体裁必报（`%/yr`、`% |`）+ 语法错误不静默丢 + 真树跑通（>50 文件、每条告警带文件行号） |
| 全仓扫描 | 2,666 文件 / 1,194 页面渲染器 / 28,939 个含 `%` 常量 → **literal_double_pct=31、bare_pct_in_format=5、syntax_error=1** | `results/page_fmt_guard.scan.json` |
| 已发布页面实证 | **15 个 .md 现在真的躺着字面 `%%`**（`ETF_BOOK_CAPACITY_FLOOR_GAP.md` 5 处、`HANDOVER.md` 4 处、`IDX_FUT_BASIS_VERDICT.md` 3 处…） | `results/_r2111bmc_leak_verify.json` + 直接扫 md 全文 |

已亲自核对真伪的两条（防止闸门只会喊狼来了）：
- `scripts/etf_book_capacity_floor_gap.py:328` 是 `L.append("| reading | 1%% ADV | ...")`——未走 `%` 的写入器实参，**真缺陷**，页面确实印 `1%% ADV`。
- `scripts/astock_veto_hedge_band.py:551` 是 `("%." + str(digits) + "f") % float(x)`——拼接片段，**误报**，已加片段排除规则后消失（48→5）。

## 没做到的（如实）

- **未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`**：这两个文件本轮是对端未提交的脏面，竞争窗内禁写共享面（r1907）。因此本闸目前是**独立可跑工具**，不是链上腿。
- **未修那 31 条真实泄漏**：全部在他人脚本面里，改它们属于改共享面；修法明确（未格式化的串把 `%%` 改回 `%`），留待独占窗。
- **不判实参个数不匹配**（"not enough arguments"）：需要类型信息，本遍没有。
- 编码：`utf-8-sig` 优先、`gbk` 兜底；仍剩 1 个 `SYNTAX_ERROR`（非 UTF-8 且 GBK 也解不了的旧脚本），照报不藏。

## 复跑

```
python Tools\page_fmt_guard.py --selftest
python Tools\page_fmt_guard.py scan --json results\page_fmt_guard.scan.json
python results\_r2111bmc_leak_verify.py
```
