# -*- coding: utf-8 -*-
# r641 bm-b final fix batch: (1) bytes-mode surgery on round_reports.md last-line
# malformed timestamp (file = mixed GBK/UTF-8 history, strict utf-8 read crashes
# -- pit-encoding tolerant-read law, byte needle count==1 per r420 law);
# (2) sync CODELY.md to origin (bm-c r437 +3 lines) then append r641 lesson line;
# (3) strict re-verify state/heartbeat clock faces.
import json, os, re, subprocess, sys, time, datetime, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

n = datetime.datetime.now().astimezone()
off = int(n.utcoffset().total_seconds() // 3600)
iso = f"{n.year:04d}-{n.month:02d}-{n.day:02d}T{n.hour:02d}:{n.minute:02d}:{n.second:02d}+{off:02d}:00"

# ---- 1. report line byte surgery ----
rp = os.path.join("logs", "iteration-loop", "round_reports.md")
raw = open(rp, "rb").read()
needle = b"2026-10-04TH:02:06+08:00 | round 641"
cnt = raw.count(needle)
assert cnt == 1, f"needle count {cnt} != 1 (r420 law)"
raw2 = raw.replace(needle, iso.encode("ascii") + b" | round 641")
open(rp, "wb").write(raw2)
print("report line prefix fixed:", iso)

# ---- 2. CODELY.md: sync to origin then append lesson ----
r = subprocess.run(["git", "checkout", "origin/main", "--", "CODELY.md"], capture_output=True)
assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
btxt = open("CODELY.md", "rb").read()
try:
    btxt.decode("utf-8")
    mode = "utf-8-clean"
except UnicodeDecodeError:
    mode = "mixed"
lesson = ("- [2026-10-04 %s r641 bm-b] r641 收口窗钟串坑（当场抓回三 amend 自愈零 origin 伤害）：本机 strftime('%%H') 输出字面 'H' "
          "（'%%Y-%%m-%%dT%%H:%%M:%%S'→'2026-10-04TH:02:06+08:00' 畸形钟串=F7/R262 红项族·state/心跳/轮报告三面全中·"
          "弱断言「'T' in clock」放垃圾通过）——本机一切时钟串一律手写 f-string 数字拼装（零 strftime·零 %% 运算符——"
          "%% 字面量撞 CJK 文本同窗另炸 ValueError 0x4e09 双犯），断言走 ^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\+\\d{2}:00$ "
          "严格正则+epoch↔clock 交叉验；附带=logs/iteration-loop/round_reports.md 混编码史（GBK 遗留行）UTF-8 strict 读必炸 "
          "0xd1→该件一切手术走 bytes 模式 needle count==1（pit-encoding 容错读律复现面）；r640 存量心跳 epoch=1791076128 "
          "与其 clock 差 +8h（疑非 time.time() 单源·F7 不交叉验·存量面不改史），新写一律 int(time.time()) 直落。\n") % iso
with open("CODELY.md", "a", encoding="utf-8", newline="") as f:
    f.write(lesson)
print("CODELY synced-from-origin mode=%s + lesson appended" % mode)

# ---- 3. strict re-verify ----
RX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+[0-9]{2}:00$")
st = json.load(open("state.json", encoding="utf-8"))
hb = json.load(open(os.path.join("fleet", "machines", "bm-b.json"), encoding="utf-8"))
assert st["round_no"] == 641
assert RX.match(st["clock_read"]), st["clock_read"]
assert RX.match(hb["clock_read"]), hb["clock_read"]
assert isinstance(hb["heartbeat_epoch_utc"], int)
assert abs(hb["heartbeat_epoch_utc"] - time.time()) < 300
lastline = open(rp, "rb").read().rsplit(b"\n", 2)[-2]
assert lastline.startswith(iso[:10].encode()), lastline[:30]
print("STRICT VERIFY OK: state/heartbeat clock well-formed; report last line ts prefix OK")
