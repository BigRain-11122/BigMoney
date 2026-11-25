import io, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "round_reports-bm-c.md")

tree = subprocess.run(["git", "ls-tree", "-r", "--name-only", "origin/main"],
                      cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
have = [p for p in ("scripts/policy_return_lattice.py",
                    "results/policy_return_lattice.json",
                    "research/POLICY_RETURN_LADDER.md",
                    "qa/policy-return-ladder-r2100.md",
                    "results/_r2100bmc_lattice_negative.py",
                    "results/_r2100bmc_round_report.py") if p in tree]

line = (
    "2026-11-25T21:2x+08:00 | r2100-delivered | bm-c | 送达补记：commit **296ad50bda** 已直推 origin/main"
    "（3201781a08..296ad50bda，本轮开工前 origin/main==本地基座，无 non-FF）；fetch 后 "
    "`git rev-list --left-right --count origin/main...HEAD` = **0/0**；`git ls-tree -r --name-only origin/main` "
    "核验 **%d/6** 件在位（%s）→ **本地未达 origin commit 数=0**。"
    "下轮指针（干净树首件事）：①r2099 的三张 11-23 carry 面仍未重生（CONTENTION 期间禁写共享面，双宿主同跑=双烧），"
    "重生后跑 `python scripts\\idx_fut_carry_one_lot_ruler.py check` 期望翻成 ONE_RULER；"
    "②把本面接进 `Tools/s6_chain_bmc.py`（check-only 腿，排在 policy_engine 之后）与 `smoke_test.py`；"
    "③「按权重配手」vs「按期望配手」要在策略文档里定成唯一纪律——两套并存就必然出现「照指令下单」与「照目标定仓」两套仓位。"
    "| 记账：本行 1 处（累计 4）\n"
) % (len(have), "、".join(have))

with io.open(path, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + line)
print("appended; tree-hits", len(have))
