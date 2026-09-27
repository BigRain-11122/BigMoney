# results/_r144bmc_pit3.py -- third r144 pitlaw append (byte-face, idempotent)
# Written as a FILE because python -c through the PS console mangles Chinese
# (GBK eats quotes -> SyntaxError) and script files are the proven-stable
# path this round. Readback verification is part of the entry's own law.
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "CODELY.md")

ENTRY = (
    "- [2026-09-28 07:4x r144 bm-c] 坑律：**写层/控制台层内容失真双型——"
    "①strftime 格式串落盘丢 escape（r144 实弹：_r144bmc_bookkeeping.py L11 "
    "落盘后 H 前的 escape 丢、Y/m/d/M/S 全存，clock_read 产「TH:28:22」畸形值，"
    "R262 钟读律险红，轮内 json 回读断言捕获即修）；②python -c 过 PS 控制台="
    "中文 GBK 灭引号 SyntaxError（含格式串时更炸：引号断→数字面量裸奔）**。"
    "How to apply：①工具写文件含格式控制串，写后必 readback 核对再执行；"
    "②关键时间戳字段写后必 json 回读断言（T 分隔+时位 isdigit）；"
    "③中文+格式串混合内容一律走落盘脚本文件（write_file 中文面稳、"
    "python -c 控制台面禁）；④时间戳拼装用显式元组面。"
    "指针=results/_r144bmc_bookkeeping.py L11 实况+本 commit 修复段。\n"
)

raw = open(P, "rb").read()
marker = "写层/控制台层内容失真双型".encode()
if marker in raw:
    print("already present, no-op")
else:
    open(P, "wb").write(raw + ENTRY.encode("utf-8"))

back = open(P, "rb").read()
assert marker in back, "readback: entry missing"
assert b"\xef\xbb\xbf" == back[:3], "readback: BOM lost"
size = len(back)
print(f"readback OK: entry present, BOM kept, size={size}B "
      f"hard-line={'OK' if size <= 10240 else 'OVER'}")
