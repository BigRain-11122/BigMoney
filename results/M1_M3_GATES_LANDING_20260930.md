# M1 t 值门槛 + M3 类级认输台账 落地简报（CEO 面）

- 立法源：集团外审 D-20260930-37（CEO 令「打磨方法论」）M 系七件之 **M3+M1**，本司自领采纳 bm-a r482（job#1·D-37 拍板③ 优先序：M5 成本口径 r479 已落 → M7 集团已落 → **M3 → M1** → 本轮毕）
- 生效面：**前瞻生效**——只约束此后冻结的新预注册；既有冻结批维持原判（档存重估=新程序非翻案律）。RW-5 冻结窗内零烧批零判据变更，本件=既有件内容修订（MSG-1330 §2 合法面）

## 修前 vs 修后对账表（D-40 表述纪律）

| 面 | 修前 | 修后 | 为什么 |
|---|---|---|---|
| **M1 多重检验 t 门槛** | 无此门。DSR 面被账本 N_eff 稀释（36.2 万试验后门槛随账本上涨），无一道**廉价、不被 N 稀释**的新因子 t 门 | 新因子/策略主张必报 t 面并过 **t≥3.0**（Harvard/Liu/Zhu 2016）；缺 t=拒收非放行；`t_from_sharpe` 派生仅当无直接 IC t 时允许 | 头部共认：试了成千上万个因子后，老课本 t≥2.0 的「显著」大半是抽签抽出来的；3.0 是多重检验后的诚实线 |
| **M3 类级认输** | 判负是**批级**——族判负后同一族可再立新 prereg 无对号机制，死面库存散在 STRATEGY_LIBRARY §〇 表格（人读、无机器门） | `science_gates.CLOSED_FAMILIES` 6 条在册（CTA 期货×3/CN 五组合 19 格/野路子 1569 格/FACTOR_BLEND/T-28 SPM/微盘崩塌域）；新 prereg `closed_family_check` 对号——**在册无新证据声明=禁烧**；复活唯一通道=新预注册声明新证据增量（O-1105 新证据=新预注册）或条目既定通道（T-28 复跑窗 10-31/微盘 CEO 一句话） | 头部（Medallion 型）纪律：认输要认得彻底——同一张考卷不许反复重考；但真有新证据（如机制/数据/计算面修复）合法复活，不搞永久黑箱 |

## 实测数字（本窗）

- `python -m scripts.science_gates selftest`：**63/63 PASS**（新增 6 断言：t 已知答案 SR=1.0/T=1512→t=√6≈2.449、薄样本<20 拒收、门槛边界 2.99 拒/3.0 过、缺输入拒收、闭合族三态（open/rejected/reopen_channel_declared）、登记表完整性）
- M1 咬合例：6 年期 SR=1.0 策略 t≈2.45 **不过** 3.0；SR=2.5 同窗 t≈6.12 **过**——便宜的第一道筛，在烧批前就拦住「抽签抽出来的显著」
- M3 咬合例：`closed_family_check("factor_blend")`（无声明）=**rejected 禁烧**；带新证据增量声明=reopen_channel_declared（新 prereg 冻结通道）

## 交付件清单

1. `scripts/science_gates.py` M1/M3 节（`M1_T_HURDLE`/`t_from_sharpe`/`m1_t_value_gate`/`CLOSED_FAMILIES`/`closed_family_check`）+ selftest 6 断言
2. `research/CLOSED_FAMILIES.md` v1.0（人读镜像台账·升格自 STRATEGY_LIBRARY §〇 死面库存·归档不删）
3. `research/PREREG_TEMPLATE.md` 两必填项接线：§3 闭合族对号声明【M3】+ §4 新因子 t 面申报【M1】

## 剩余 M 系队列（D-37 拍板③序）

M2 数据清洁优先律 → M4 研究-交易隔离 → M6 转化率闸（后续轮次按序自领；M5/M7/M3/M1 已毕 4/7）

—— bm-a r482 · 2026-09-30 17:2x · 证据=science_gates selftest 63/63 · 复审锚=selftest「M3 CLOSED_FAMILIES registry integrity」断言
