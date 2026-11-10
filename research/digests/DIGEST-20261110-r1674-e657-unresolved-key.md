# DIGEST r1674 bm-b — E657：未解析字符串句柄里的计数键位（体积，不是个案）

**问**：E655 发现 E647 把 percent-format 表达式交回成一个 unresolved 句柄就不再下降，句柄里的计数行键
因此进不了 E652 的键表。这个盲区有多大？

**法与读**：
- 句柄按 (行,列)+why 映回产生它的节点（BinOp/JoinedStr/Call），走该节点自己的子树取等于 6 个计数行键的
  字符串常量，按父节点角色分档（dict_literal_key / subscript_key / call_argument / comparison /
  string_constant / other_string）；span 用节点自身 `lineno..end_lineno`。
- 12,803 文件 / 89,706 句柄 → 707 文件携带 1,504 个句柄内键位：946 下标切片、558 隐形
  （call_argument 538 / other_string 17 / comparison 3）。538 个 call argument 几乎全是 `.get()` 读。
- 对 E652 的 23 行：匹配 5 个文件，全部 e652 carries=true，`carries=false 但带隐形站点`=**0** →
  已发布头条不动；702 个文件从未被 E652 定价（554 隐形站点）。

**结论（verdict）**：隐形站点存在于两支都看不见的角色，但**没有一处落在 E652 已发布的行里**，所以
盲区成本是「人口外的语料面」而不是「已发布计数的错误」。

**三条可复用判例**：
1. 「一支通 ≠ 两支出错」：E652 的两支（字面量 / 全树 Subscript）覆盖不同形状，报「隐形」必须先按角色分档。
2. 盲区体量必须按人口定价：707/1,504 是真的，但 0 个翻面；只报 558 会被读成「少算 558 处」。
3. 句柄不发布 span 就会被迫用语句 span 近似（E655 即如此），同语句旁挂的键会被误计；span 从节点取并
   用 selftest 钉死。

**产物**：`scripts/e657_unresolved_key.py`(18/18) · `results/state_tilt/UNRESOLVEDKEY.json` ·
`unresolvedkey_latest.json` · `scripts/run_e657_smoke_leg.py`(1/1, doctor 红且还原) · smoke leg + S6 leg
`unresolved_string_key` · 卡 E657 · 本条。
