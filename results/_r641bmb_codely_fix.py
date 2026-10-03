# -*- coding: utf-8 -*-
# r641 bm-b CODELY append (corrected): sync CODELY.md from origin (bm-c r437 +3
# lines) then append the r641 lesson -- accurate version. The earlier
# final_fix.py needle crashed pre-CODELY (report line was never malformed);
# and its drafted lesson blamed a phantom "CRT strftime %H failure" which the
# live diagnostic just FALSIFIED (plain typo "%Y-%m-%dTH:%M:%S" was the cause,
# strftime works). Evidence before law.
import os, subprocess, sys, datetime, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

n = datetime.datetime.now()
stamp = f"{n.year:04d}-{n.month:02d}-{n.day:02d} {n.hour:02d}:{n.minute:02d}"

r = subprocess.run(["git", "checkout", "origin/main", "--", "CODELY.md"], capture_output=True)
assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
raw = open("CODELY.md", "rb").read()
raw.decode("utf-8")  # strict: CODELY.md must be clean UTF-8 before append

lesson = (
    f"- [2026-10-04 {stamp} r641 bm-b] r641 收口窗三坑连环当场抓回（三 amend 自愈零 origin 伤害·证据先于立法："
    "「strftime CRT 失效」假说经 python -c 实弹诊断证伪=纯格式串笔误）：①钟串格式串笔误 "
    " \"%Y-%m-%dTH:%M:%S\"（字面 TH 非 T%H）产出 '2026-10-04TH:02:06+08:00' 畸形钟串入 state/心跳两面，"
    "弱断言「'T' in clock」放垃圾通过——律=钟串断言必走 ^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\+\\d{2}:00$ "
    "严格正则+epoch↔clock 交叉验，疑 CRT/环境障先最小实弹复现证伪再立法；②% 运算符格式化长 CJK 文"
    "（内含字面 % 字符）=ValueError 0x4e09 家族——长文一律 f-string 禁 % 运算符；"
    "③logs/iteration-loop/round_reports.md=混编码史（GBK 遗留行+UTF-8 新行）UTF-8 strict 读必炸 0xd1"
    "→该件一切手术走 bytes 模式 needle count==1（pit-encoding 容错读律复现面·本文件 append 用 newline='' "
    "防 CRLF 翻译）；附带=r640 存量心跳 epoch=1791076128 与其 clock 差 +8h（疑非 time.time() 单源·"
    "F7 只验 int 不交叉验·存量不改史），新写一律 int(time.time()) 直落。\n")
with open("CODELY.md", "a", encoding="utf-8", newline="") as f:
    f.write(lesson)
sz = os.path.getsize("CODELY.md")
print(f"CODELY synced + lesson appended; size={sz}B ({'OK<=50KB' if sz <= 51200 else 'OVER 50KB -> hot-cold sweep window'})")
