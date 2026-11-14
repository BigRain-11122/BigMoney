import io

card = """

### E637 · 台账清零那一轮，要求「台账非空」的腿会变成「要求某块别修」（r1675 bm-c）

`PAGE_DAY_LEDGER` 上只剩一行 owed（`capital_block` 三句话把票据那天的单叫「今天」）。把这一行修掉、删行，`selftest` 立刻红了——不是修错，而是 L261 的断言里写着 `and page_day_debt_owed()`：它本来是用「欠债列表非空」来证明 `owed()` 这个读数活着，欠债清零后这句话变成了**要求某一块继续不修**。同一轮第二枚：L127 断言「block 的每一行都落到页面上」，用的是 `capital_block(_cf)`（无 page_day＝旧措辞）去比用页面日生成的页面，于是这一修复让该腿以 `52/53` 报页面缺行。**正法**：①凡是「必须存在 N 条病态」的清点腿，把 N 换成夹具行——在 try 块里塞一条假 owed，读 `owed()`，读完回滚；腿要断言的是**机制能发现病态**，不是**病态存在**；②凡「函数输出必须出现在页面上」的腿，被比对的块必须用**页面自己的参数**生成（`page_day=page["generated_for_date"]`），否则测的是两个版本的字面量是否相等。判据一句话：腿红了先问它测的是「东西对不对」还是「东西还是不是坏的」。
"""

p = "knowledge/METHODOLOGY_ASSETS.md"
s = io.open(p, encoding="utf-8").read()
with io.open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(s.rstrip("\n") + card)
print("appended", len(card))
