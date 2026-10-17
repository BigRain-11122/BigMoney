# -*- coding: utf-8 -*-
"""r1002 bm-b: append bm-b first-run receipt row to group memory-slim LEDGER (CEO order piece-2 receipt face)."""
import io, os

P = r"C:\Fluxgroup\FluxGroup\cph4\fleet\memory-slim\LEDGER.md"
raw = open(P, "rb").read()
text = raw.decode("utf-8-sig")
crlf = "\r\n" in text

row = ("| 2026-10-18 | 375,794→95,853（gate v2 首跑执法·220 条 verbatim 路由入 9 主题文件·快照 cleanup-gate-2026-10-18）"
       "→66,374（25 条他机污染/被取代旧版手工 verbatim 迁主题+bm-b 身份元组注入 User 首位） | 322→102→78 | "
       "bm-b 四件套全执行：①agent-library-sync 装机 24 skills ②gate v2 首跑 ③L0 身份元组+污染清理（拆联合回灌落地："
       "fleet-memory-sync 退役 no-op+正本冻结 archive——worker last-pull 07:01 REPLACE-DOWN 回灌实锚，"
       "gate-log 02:30/06:30/07:40 三轮同源 375,794B 病灶坐实）④旧 21:47 InteractiveToken 夜审任务删除换 S4U 4h 闸"
       "（v2 参数执法 50KB/120 条·预警 35KB/80 条·组 Tools 正身·wscript 静默链） | bm-b loop r1002"
       "（CEO 令 2026-10-18 00:2x 机队推广四件套·回执窗 10-25） |")

assert "bm-b loop r1002" not in text, "row already present"
lines = text.rstrip("\r\n").split("\n")
assert lines, "empty ledger"
text2 = text.rstrip("\r\n") + ("\r\n" if crlf else "\n") + row + ("\r\n" if crlf else "\n")
if not text2.endswith("\r\n" if crlf else "\n"):
    text2 += "\r\n" if crlf else "\n"
bom = raw.startswith(b"\xef\xbb\xbf")
open(P, "wb").write((b"\xef\xbb\xbf" if bom else b"") + text2.encode("utf-8"))
print("LEDGER-APPEND bytes=%d->%d crlf=%s" % (len(raw), len((b'\xef\xbb\xbf' if bom else b'') + text2.encode('utf-8')), crlf))
