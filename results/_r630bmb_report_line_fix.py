# r630 bm-b: repair mojibake-corrupted tail line in round_reports.md
# Add-Content -Encoding utf8 wrote byte-invalid content; truncate to last good
# newline boundary and re-append the correct line from this UTF-8 source file.
import io, sys

PATH = r"logs/iteration-loop/round_reports.md"
FIX = (
    "2026-10-03T20:2x+08:00 | R630 bm-b (dept:工程:S0 死 rebase 收口+origin 全量集成) | "
    "watermark verdict: GREEN (red=false; lane healthy; next_pick=claimed moneyflow IC) | "
    "当前活: FUND 三族 NULLS 烧录在飞 V351/Q239/D130 of 2000（V 速率维持 ~33/h ETA 10-05/06） | "
    "最近实物: origin 集成落地 917b88421 main==origin 送达自证 0 未达（死 rebase 收口：r629 遗留交互 rebase 检出→r501 ①③净路 skip×2 被吸收 pick→value nulls marker 手术 strip+k=336/337 字节回补→隔离 worktree cherry-pick 四连 23 争议面 origin 侧解→push）"
    "+W2-JUDGE-SHARD-1 determinism 定谳（本机 18:53:44 完烧 201/201 产物 blob a44a55a81==origin 字节恒等·MSG-2005 回执 bm-a）"
    "+docs/live_usage/LIVE-2026-10-03.md+REPORT-2026-10-03.md 再生（S6 34 腿 rc0） | "
    "验证: smoke 47/47；S6 34 legs rc0（dualrun streak 20 ZERO-DRIFT·三 stale-takeover derive 合法 O-2100 s2.4）；attrition CLEAN；D-19 MATCH 4167b784 零消费；orders 151/151 双扫零未回执；HANDOVER bm-b r630 5x 戳落（r625 缺席坑-79 注记） | "
    "下轮指针: NULLS 三族监视（RAM 3.2GB<4GB 窗不认领新批）+SHARD-1 已落=judge-finalize --wave 2 解锁（bm-c 面观察）+10-06 finalize 窗前置零阻塞维持；本地未达 origin commit 数=0"
)

raw = open(PATH, "rb").read()
# find start of the corrupted tail line: last b'\n' before the R630 marker text
marker = "2026-10-03T20:2x".encode("utf-8")
pos = raw.rfind(marker)
if pos == -1:
    sys.exit("R630 marker not found - abort, no write")
# walk back to the preceding newline (exclusive keep)
nl = raw.rfind(b"\n", 0, pos)
if nl == -1:
    sys.exit("no newline before marker - abort")
base = raw[:nl + 1]
# sanity: base must be fully valid UTF-8 (pre-existing content intact)
base.decode("utf-8")
new = base + FIX.encode("utf-8") + b"\n"
# also normalize: strip any trailing CR from FIX region none expected
with open(PATH, "wb") as f:
    f.write(new)
# verify
back = open(PATH, "rb").read()
text = back.decode("utf-8")   # raises if any invalid byte remains
lines = text.splitlines()
print("OK total_lines=%d last_head=%s" % (len(lines), lines[-1][:50]))
print("R630 line bytes=%d" % len(FIX.encode("utf-8")))
