# DIGEST-20261110-r1671 · E650 — do the 383 comprehension/lambda sites read a counted row key in a scope of their own?

**轮次** r1671 bm-b · 2026-11-10 · 承 E643（r1667）的 17,720 残量三桶 → 本轮只定价其中两个「自带作用域」的桶。

## 问题

E643 把「没有所属函数」的 17,720 个双深站点分成 module body 17,337 / comprehension 342 / lambda 41。后两桶是残量里唯一**求值作用域不是模块**的成员：comprehension 与 lambda 各自开一个作用域，所以它下标的那个名字可以是

1. 构造自己绑的名字（生成器目标变量 / lambda 形参）= **逐项读**，
2. 或者只能来自外部的名字 = **读外层行**，只是恰好写在推导式里。

这两者混在一起时，「383 个站点在推导式里」这句话对计数行读取面毫无信息量。

## 读数

| 量 | 值 |
|---|---|
| 语料 | 13,112 个 .py |
| 作用域内站点 | **383**（comprehension 342 / lambda 41） |
| 与 E643 逐桶对账 | comprehension 0 / lambda 0（**delta 0**） |
| 命中计数行键的站点 | **16**（键：`rows` 11 / `x1` 4 / `bar` 1） |
| 其中 own-scope / outer-scope / both / unresolved | **0 / 16 / 0 / 0** |
| 无计数键的站点 | 367 |
| 作用域内写站点 | **0** |
| 成员 base 形态 | named 818 / no_leftmost_name 15 |

判决 = **all-outer**：16 个命中计数键的站点，**没有一个**下标构造自己绑的名字。构造的作用域只决定「这次下标在哪求值」，不改变「读的是哪个对象」。

## 三条可复用律

1. **作用域不是对象身份**。「同一个键名在两个作用域里被读到」不等于读到两个对象；E650 实测 16/16 读的都是外层绑定的名字，所以这层嵌套对计数行读取面是零信息——把一个语法上下文当成语义差异来定价，是这一步最贵的错觉。
2. **两个独立的好列仍然不是联合分布**（承 E649，本条是第二次实证）。E643 的三桶各自都对，交叉「桶 × 键是否计数 × base 绑定在哪」之后才知道 367/383 根本不碰计数键；只看「383 个在推导式里」会把它误读成一块待解释的读取面。
3. **「自己绑的名字」必须现场量，不能按文本猜**。own-scope 集合是从 AST 的生成器目标（tuple/starred 递归）与 lambda 形参（含 `*args`/`**kwargs`/kwonly）现算的，fixture 里 `for (a, *b) in x` 与 `lambda a, *b, c=1, **d` 都有腿钉住——按 `for X in` 正则抓会把解包与星号目标漏掉。

## 诚实边界

- own-scope 是链上**所有**构造绑定名的并集，嵌套对（comprehension>comprehension）不区分内层外层。
- 名字绑在自身作用域里，**不等于**运行期它装的就是内层对象（调用方可以把行传进去）。本面说的是「名字在哪绑」，不是「运行时装了什么」。
- 经典 `for` 循环读行是 module body + loop 守卫桶（E649 已定价），不在这 383 里；同一种「逐项读」模式在另一个桶里，不能与本面相加。
- 经调用或属性链下标的站点发布最左名字（E633 规则）或不发布；无 base = unresolved_base，不猜。
- 键只取字面量；计算键（变量/join/f-string）在本面无字面键因而永不命中（E645/E651 各自定价该臂）。
- 只排除本轮自身文件；同族兄弟脚本仍在总体内，故站点数略大于 E643 自己的行走数（13,112 vs 13,099）。

## 证据

- `scripts/e650_comprehension_scope.py`（selftest **30/30** · `run`/`check`/`verify` → `problems=[]`）
- `results/state_tilt/COMPREHENSIONSCOPE.json` + `comprehensionscope_latest.json`
- `scripts/run_e650_smoke_leg.py` → 1/1 PASS；`--doctor` 翻红且字节还原 sha `b09b1ef1297d` 同进同出
- `smoke_test.py` leg E650 + `Tools/s6_chain_bmb.py` leg `comprehension_scope`
- POOL：E650 done / E654 seeded（16 个站点是否读到计数读行**同一个对象** = E645 的 reach 臂）