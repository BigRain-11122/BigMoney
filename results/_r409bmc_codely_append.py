# -*- coding: utf-8 -*-
# r409 bm-c: append PS ConvertFrom-Json Int64 false-alarm pit line to repo CODELY.md (CRLF preserve)
import io

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
LINE = "- [2026-10-03 10:2x r409 bm-c] PS ConvertFrom-Json 大数 Int64 假警坑（心跳 epoch 自检面·当场零损失定性）：epoch 1790993xxx 超 [int32]::MaxValue → PS 把 JSON 数值解析为 Int64——`-is [int]` 恒 False ≠ 文件坏（本窗收尾自检假警·int64 复判即过·smoke F7 判据=非字符串故零实伤）；R170/R178 JSON int 律的执法判据=JSON 数值型（非字符串），PS 面自检一律 `-is [int64]`（或 `-is [int64] -or -is [int]`），禁凭 `-is [int]` 单 False 触发「修值」操作（会误改健康文件）。How to apply：一切 PS 侧 epoch/数值型自检用 int64 判据；律的真违例=带引号字符串（json.dumps 层面可见），数值型 Int64 恒合法。"

with open(P, "rb") as f:
    raw = f.read()
nl = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
if not raw.endswith(nl):
    raw = raw + nl
with open(P, "ab") as f:
    f.write(LINE.encode("utf-8") + nl)
with io.open(P, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
print("APPENDED total_lines=%d last_head=%s" % (len(lines), lines[-1][:50]))
print("TAIL_OK=" + str(lines[-1].startswith("- [2026-10-03 10:2x r409 bm-c] PS ConvertFrom-Json")))
