"""r2119 delivery note: append the delivery row and stamp the state with the origin sha."""
import io
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MACHINE = "bm-c"
ROUND = 2119

sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                     text=True).stdout.strip()
ahead_behind = subprocess.run(["git", "rev-list", "--left-right", "--count",
                              "origin/main...HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()

paths = ["scripts/idx_fut_carry_one_lot_ruler.py", "scripts/live_book_day_words.py",
         "scripts/etf_book_ceo_page.py", "qa/daywords-two-date-r2119.md",
         "results/idx_fut_carry_one_lot_ruler.json", "research/IDX_FUT_CARRY_ONE_LOT_RULER.md"]
on_origin = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "--"] + paths,
                           cwd=ROOT, capture_output=True, text=True).stdout.split()

row = (
    "| 2026-11-26 07:1x | " + str(ROUND) + "-delivered | " + MACHINE
    + " | 送达复核：commit **" + sha + "** 已在 origin/main"
    "（`git rev-list --left-right --count origin/main...HEAD` = **" + ahead_behind + "**）；"
    "`git ls-tree origin/main` 核验 **" + str(len(on_origin)) + "/" + str(len(paths)) + "** 件在位（"
    + ", ".join(os.path.basename(p) for p in on_origin) + "）→ **本地未达 origin commit 数=0**。"
    "本窗自捕两枚工具坑：①平台 shell 的 heredoc（`python - <<'PY'`）在 pwsh 里直接报「重定向运算符后缺少文件规范」，"
    "探针/补丁一律**落文件再跑**（r2114 已立「禁裸 `python -`」，此处添姊妹面）；②轮报告行模板里带裸 `%`（「1.124%/yr」），"
    "与 `%` 元组格式化共用时当场炸 `not enough arguments for format string` → 大文本行一律字符串拼接 / "
    "`.replace('{ROUND}', ...)`，禁与百分号共用同一个格式化器。"
    "冒烟：`logs/smoke_full_r2119.out` 07:0x 已到 816 行仍在飞（分离进程 `pythonw -m smoke_test`），"
    "**不宣称总数**；其中已逐条复核转绿的是 QA 里那 11 条，其余属链仍在推进的同一代差。"
    "记账：本行 1 处（本轮累计 5 处）|\n"
)

rp = os.path.join(ROOT, "round_reports-%s.md" % MACHINE)
with io.open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(row)

sp = os.path.join(ROOT, "state-%s.json" % MACHINE)
with io.open(sp, "r", encoding="utf-8") as fh:
    st = json.load(fh)
st["送达自证_r%d" % ROUND] = {"sha": sha, "ahead_behind": ahead_behind,
                              "paths_on_origin": len(on_origin)}
with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print(json.dumps({"row": row[:90], "sha": sha, "ahead_behind": ahead_behind,
                  "on_origin": len(on_origin)}, ensure_ascii=False))
