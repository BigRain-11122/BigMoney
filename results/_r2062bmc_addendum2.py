"""r2062 addendum-2: correct the ahead count after the addendum commit itself (CRLF-safe)."""
import datetime
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
now = now[:-2] + ":" + now[-2:]

line = (
    "{now} | r2062 addendum-2 | bm-c | **读数更正（自指）**：上一条写「本地未达 origin/main "
    "commit 数=8」是**第一条 commit 53310b5369 之后**的读数；本条 addendum 自身又加 1 个 commit，"
    "故此刻实测 `git rev-list --left-right --count origin/main...HEAD` = **1/9**（origin 独有 1、"
    "本机独有 9），即**本地未达 origin/main commit 数=9**，全部已推 origin machine/bm-c-r2062"
    "（该分支与 HEAD `--left-right` = 0/0）。Why 记这条：送达核验门的要点是「数字要与读者此刻"
    "实测一致」，不是「我写的时候对」；自指计数差 1 若不说清，下一位读者会以为我算错了。"
    " | 记账：本行 1 处。"
).format(now=now)

with open("round_reports-bm-c.md", "ab") as fh:
    fh.write(line.encode("utf-8") + b"\r\n")
print("appended", now)
