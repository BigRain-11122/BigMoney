import io, os

card = """
### E635 · 文件被重写不等于心跳：mtime 是钟，ts 是读数（r1673 bm-c）

这一轮打开仓时看到 `fleet/machines/bm-c.json` 的 mtime 是 17:20:02（就是本窗开窗那一刻），而文件里的 `ts` / `last_seen` / `heartbeat_epoch_utc` 全都停在 **16:44:49**。两者差 36 分钟，两个都对：17:0x、17:1x、17:2x 三个窗口都重写过这个文件（原子写、merge-only），但三次写出的内容与上一版**逐字节相同**（`git diff` 只有「文件末尾少了换行」这一行差异）——死窗在写心跳之前就断了，于是心跳内容一直冻在上一轮。任何按 **mtime** 判活性的读者都会说「这台机 4 分钟前还活着」（假阳），而按 `ts` 判的读者会说「它 36 分钟没报了」（在这次是对的，在只重写文件时也是对的）。**正法**：活性一律读内容里的 `ts`/`heartbeat_epoch_utc`，mtime 只用来判「有没有人碰过这个文件」；心跳写入器在合并写入时必须刷新 `ts`（merge-only 写手最容易犯的错就是把时钟当成调用方字段，调用方不传就保留旧值）。

**同族第二枚（同一轮实证）**：`--only` 跑页面腿而不跑它的上游 `data_lane_freshness`，页面照样渲染，机队表里印的是**机队面那一刻**的机龄（实测板上 as_of 10:56，页面 17:24 渲染时印「bm-c 0.6 小时」，而本机 4 分钟前刚写过心跳）。页面已经诚实披露了板上 as_of，但读者拿到的是「0.6 小时」这个数。**正法**：凡读别面产物的页，`--only` 配方里必须连生产者一起点名（本轮改成 `data_lane_freshness,etf_book_ceo_page,live_book_section_bars` 3/3 rc0，机龄立刻变成 18.2 小时 / 15.2 天 / 0.7 小时的真值）。

**第三枚（死窗遗产的正确处理）**：上一窗留下的 `etf_book_ceo_page.py` 未提交改动，代码注释里带着它自己的轮号（`r1673`），这一窗据此认出「这是同一条线的半成品」而不是「别人的脏改动」，先 `py_compile` 再 `selftest 347/347` 再链跑再实渲染，验证通过才认领提交——**认领前先验证，验证前先认出来**；不认就重写=同一件事做两遍。
"""

p = "knowledge/METHODOLOGY_ASSETS.md"
raw = io.open(p, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw else "\n"
if not raw.endswith(eol):
    raw += eol
raw += card.replace("\n", eol)
io.open(p, "w", encoding="utf-8", newline="").write(raw)
print("card appended, eol =", repr(eol), "bytes", len(raw))
