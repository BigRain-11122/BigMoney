# -*- coding: utf-8 -*-
"""r285 bm-b S4: CODELY.md law-line append + round_reports addendum line.

Byte-face: CODELY.md append-only (probe tail newline first per r281 law);
round_reports.md append with leading \n safety. Both raw-binary writes.
"""
import io

CM = r"C:\Users\Administrator\Desktop\Bigmoney\CODELY.md"
RR = r"C:\Users\Administrator\Desktop\Bigmoney\logs\iteration-loop\round_reports.md"
import datetime as dt
NOW = dt.datetime.now()
TS = NOW.isoformat()

LAW = (
    "\n[2026-09-27 00:5x] 坑律（bm-b r285·HANDOVER 5x 核对链换新面·大文件 split 手术编辑新律·E1 写后自捕零外泄）：**split 锚定的大文件手术编辑，split 尾段=文件主体非末条目——「丢弃 parts[末] 淘汰最旧核对项」的设计把 parts[2]（=bm-a 275 条目+\\n## 一、起整个主体 175,999 字符）整段当旧条目弃掉=278,300B 文件截断成 4,557B（写后体积 printout 当场自捕，git checkout -- 秒恢复，零 commit 零外泄）**；正律=①尾段处理必须「掐头留体」：REST=parts[2] 自首个 \\n 起的文件主体，弃的只是段头那一条目行②改写类操作断言门必含体积单调面（len(out)>len(raw) 增量界）+主体完整性锚（\\n## 节标头+文件尾锚双探）——BOM/子串存在性断言不构成完整性③阈值类断言先实测再定（>200,000 拍脑门=字符/字节单位混用，断言自身成假红源）。指针=results/_r285bmb_handover.py 修正史（首版截断→git 恢复→掐头留体版+2325B 2+/1-）\n"
)

raw = open(CM, "rb").read()
if not raw.endswith(b"\n"):
    LAW = "\n" + LAW.lstrip("\n")
with io.open(CM, "ab") as f:
    f.write(LAW.lstrip("\n").encode("utf-8") if raw.endswith(b"\n") else LAW.encode("utf-8"))
raw2 = open(CM, "rb").read()
assert raw2.endswith(b"\n") and len(raw2) > len(raw) and len(raw2) - len(raw) < 2000
print(f"CODELY.md {len(raw)} -> {len(raw2)} (+{len(raw2)-len(raw)})")

ADD = (
    f"\n{TS} | r285 addendum (bm-b) | dept:工程 | S4 自捕近失误入册：HANDOVER 5x "
    "换新脚本首版 split 尾段误当旧条目整段丢弃=278,300B 截断成 4,557B（写后体积 "
    "printout 当场自捕·git checkout -- 秒恢复·零 commit 零外泄）；修正=掐头留体 "
    "（REST=parts[2] 首个 \\n 起主体）+体积单调门+主体完整性双锚，重跑落档 "
    "280,625B (+2,325) 2+/1-；坑律已入 CODELY.md（大文件 split 手术编辑律）"
    "\n"
)
raw = open(RR, "rb").read()
assert raw.endswith(b"\n"), "rr tail newline"
with io.open(RR, "ab") as f:
    f.write(ADD.encode("utf-8"))
raw2 = open(RR, "rb").read()
assert raw2.endswith(b"\n")
print("round_reports addendum appended")
