"""r2062 addendum append (CRLF-safe, byte append -- never rewrites earlier lines)."""
import datetime
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
now = now[:-2] + ":" + now[-2:]

line = (
    "{now} | r2062 addendum | bm-c | 送达实况：commit **53310b5369**（10 件·+894/-45）"
    "——新建 scripts/smoke_red_root_cause.py / results/smoke_red_root_cause.json / "
    "research/SMOKE-RED-ROOT-CAUSE.md / qa/smoke-red-root-cause-r2062.md / "
    "results/_r2062bmc_negctl.py / results/_r2062bmc_closeout.py，改 round_reports-bm-c.md / "
    "state-bm-c.json（round_no 2061→2062）/ fleet/machines/bm-c.json（582 键零增减·"
    "heartbeat_epoch_utc 实测 int）/ results/_repo_write_contention.bm-c.json。 "
    "**main 未送达**：`git push origin HEAD:main` 被 non-fast-forward 拒绝（origin 领先 1、"
    "本机领先 8）——`git pull --rebase` 会被另一宿主 2,290+ 未暂存面拦下，按律禁 stash 禁碰；"
    "按 D-20260925-01③ 走兜底已推 **origin machine/bm-c-r2062（53310b5369）**，fetch 后 "
    "ls-tree 四件在位、`git rev-list --left-right --count origin/machine/bm-c-r2062...HEAD`=0/0 "
    "→ **本地未达 origin/main commit 数=8**（全在 machine 分支已送达，非丢失）。 "
    "| S7 零窗（只读查证·未重注册）：schtasks /query 经 Tools/Invoke-SilentExe.ps1 零窗包装——"
    "Bigmoney-IterationLoop **正在运行**（下次 1:20）/ Bigmoney-LoopWatchdog **就绪**（下次 1:17），"
    "两者均在位且对端在飞，本轮不触碰；attrition_ledger_guard 未跑（竞争窗，与冒烟/S6 同列延后面）。 "
    "| 记账：本行 1 处。"
).format(now=now)

with open("round_reports-bm-c.md", "ab") as fh:
    fh.write(line.encode("utf-8") + b"\r\n")

print("appended", now, "chars", len(line))
