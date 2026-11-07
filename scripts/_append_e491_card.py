# -*- coding: utf-8 -*-
"""Append the E491 methodology card (LF-only face; assert end-of-file newline style first)."""
import io
import sys

CARD = u"""
## E491 -- E489 说那个 _latest 副本「在别处写」：它就在同一个函数里的第二行，copy 的目标是第二个实参（r1516 bm-b）

**问题**：E489 把 50 个同目录写手分五档，其中恰好一行是 `bandthreshguard`：被追踪的写调用只写 `BANDTHRESHGUARD-2026-10-29.json`，而读者打开 `bandthreshguard_latest.json`，于是那一行被印成「拼出读者目录但另一个 basename（副本在别处写）」。那句话是推论：E489 的追踪只读写调用的**第一个**实参，而副本常常由 copy 调用做成，`shutil.copyfile(src, dst)` 的目标是**第二个**，这类调用在 E489 的语义里根本不存在。本面把推论换成测量。

**做法**：扫 `scripts/`、`Tools/`、`firm/` 下提到任何 `_latest.json` 的 Python 源（本期 287 个文件字面命中，自身与 E489 族排除），对每个调用同时折**两个实参**：copy 族（`shutil.copyfile/copy/copy2/move`、`os.replace/rename`）取第二个实参作目标、第一个作源；直写族（`open/write_text/write_json/dump_json`）取第一个作目标。按折出的目标 basename 分组，每组按构造器数与类型分档：同目录 copy / 跳目录 copy / 直写 / 多构造器 / 无静态构造器；并发布「目标是否真的在盘上」与「copy 源是否该名字的日期兄弟」两个字段。

**读数**（2026-11-07）：176 个 `_latest` 名 — 直写 **123**、**同目录 copy 2**、跳目录 copy 0、多构造器 51、无静态构造器 0。卡片自己的名字得到确定答案：`bandthreshguard_latest.json` 由 `scripts/e273_guard_from_threshold.py:385` 的 `shutil.copyfile(path, latest)` 写成，`latest = os.path.join(OUTDIR, LATEST)` 与 `path = os.path.join(OUTDIR, FACE)` **同一个目录常量、同一个函数**——所以 E489 那一行应读作「同一个写手的第二次写」，不是「第二个写手」。另一个同目录 copy 行 `foo_latest.json` 是 `scripts/e332_invisible_tail_recovery.py` 里的 **selftest 假件**（`results/x/foo_latest.json`，盘上不存在）：两个 copy 行里只有一个对应真实发布面（`faces_whose_destination_exists_on_disk` 已单独发布）。

**三条可复用**：
1. **实参位置是探针的语义**：copy 族把目标放在第二个实参、直写族放在第一个；只读第一个实参的追踪器不是「没看到崇彩」，是根本不在他的施工通道里。同一个名字「有人写吗」的答案取决于追踪器认得几种写法，而不取决于树里有没有写手。
2. **「同目录 copy」与「直写」必须分开计**：176 个最新名里 123 个是直写，只有 2 个是 copy；把 copy 当成「另一个写手」、或把两类合并计，都会把一个 1/50 的例外读成结构性现象。
3. **静态普查会把别人的假件当成面**：`results/x/foo_latest.json` 是另一个脚本 selftest 里的临时路径，盘上永远不存在；「目标是否在盘上」必须作为字段随行发布，否则 copy 计数会把样板代码算进真实面。

**验证**：`scripts/e491_latest_copier.py`（run rc0 / check problems=[] / verify 同树重建 problems=[] / **selftest 25/25**：同目录 copy + 日期兄弟 + 双实参折叠 + 跳目录 copy + 直写 + 多构造器 + 无构造器 + 在盘/不在盘 + 六个假件全红）；面 `results/state_tilt/LATESTCOPIER-2026-11-07.json` + `latestcopier_latest.json`（176 行）；S6 腿 `latest_copier` rc0 0.07s；smoke 腿 `E491 a latest copy is composed by a copy call the write-call census cannot see` 单跑 1/1 绿 + doctored 1/1 红（面 sha 归位）。

**适用范围**：只回答「静态可折的目标名里，谁在写、与源是否同目录」；glob 驱动的 copy、argv/env 拼名不在总体内（发布为「无静态构造器」而不是证明不存在），也不构成任何删面许可。
"""


def main():
    path = "knowledge/METHODOLOGY_ASSETS.md"
    raw = open(path, "rb").read()
    if b"\r\n" in raw:
        sys.stderr.write("refused: the target face is CRLF; this append is LF-only\n")
        return 2
    if not raw.endswith(b"\n"):
        sys.stderr.write("refused: the target face does not end with a newline\n")
        return 2
    with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(CARD)
    print("appended %d bytes" % len(CARD.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())