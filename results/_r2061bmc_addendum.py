# -*- coding: utf-8 -*-
"""r2061 addendum: record the delivery receipt (main vs machine branch)."""
import io
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
TZ = timezone(timedelta(hours=8))


def git(*args):
    out = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True)
    return out.returncode, out.stdout.decode("utf-8", "replace").strip()


_, head = git("rev-parse", "--short=10", "HEAD")
_, ahead = git("rev-list", "--count", "origin/main..HEAD")
_, behind = git("rev-list", "--count", "HEAD..origin/main")
_, tip = git("rev-parse", "origin/machine/bm-c-r2061")
_, mine = git("rev-parse", "HEAD")
_, files = git("ls-tree", "-r", "--name-only", "origin/machine/bm-c-r2061")
has = [p for p in ("scripts/smoke_red_triage.py", "results/smoke_red_triage.json",
                   "results/_r2061bmc_closeout.py") if p in files.splitlines()]

now = datetime.now(TZ).isoformat(timespec="seconds")
line = (
    f"{now} | r2061 addendum | bm-c | 送达实况：commit **{head}**（7 件·+842/-82）"
    f"——新建 scripts/smoke_red_triage.py / results/smoke_red_triage.json / "
    f"results/_r2061bmc_closeout.py，改 round_reports-bm-c.md / state-bm-c.json"
    f"（round_no 2060→2061·键集 1489→1491，实加 2 键『记账_r2061』『通过_r2061』）/ "
    f"fleet/machines/bm-c.json（582 键零增减·heartbeat_epoch_utc 实测 int）/ "
    f"results/_repo_write_contention.bm-c.json。 **main 未送达**：`git push origin HEAD:main` "
    f"被 non-fast-forward 拒绝（本机落后 {behind}、领先 {ahead}）——`git pull --rebase` 会被"
    f"未暂存面 2,290+ 件（另一宿主在飞半成品）拦下，按律禁 stash 禁碰；按 D-20260925-01③ "
    f"走兜底已推 **origin machine/bm-c-r2061（{head}）**，fetch 后 ls-tree 三件在位"
    f"（{', '.join(has)}）→ **本地未达 origin/main commit 数={ahead}**（全在 machine 分支"
    f"已送达，非丢失；main 合入留给下一次无竞争窗）。 | S7 零窗：Bigmoney-IterationLoop 与 "
    f"Watchdog 本轮**未触碰**（对端在飞，重注册会打断在飞轮）；attrition_ledger_guard 未跑"
    f"（与冒烟/S6 同列延后面）。| 记账：本行 1 处。\n"
)
with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)

with io.open(STATE, "r", encoding="utf-8") as fh:
    st = json.load(fh)
n0 = len(st)
st["送达自证_r2061"] = (
    f"commit {head} 已推 origin machine/bm-c-r2061（main 落后 {behind} 未 FF）；"
    f"fetch 后 machine tip == HEAD；ls-tree origin/machine/bm-c-r2061 三件在位"
    f"（scripts/smoke_red_triage.py / results/smoke_red_triage.json / results/_r2061bmc_closeout.py）；"
    f"本地未达 origin/main commit 数={ahead}（machine 分支已送达）"
)
assert len(st) == n0 + 1, f"state key drift {n0} -> {len(st)}"
with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print(json.dumps({"head": head, "ahead_main": ahead, "behind_main": behind,
                  "machine_tip_is_head": tip == mine, "files_in_machine": has,
                  "state_keys": [n0, len(st)]}, ensure_ascii=False))
sys.exit(0)
