import io

LINE = (
    "| 2026-11-23 22:1x | r2010 **addendum**（送达核验 + 一处口径说明）"
    " | commit **734e71f7b8** 已推 origin/main（4fa8db2c85..734e71f7b8），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r origin/main` 八件 blob 在位（scripts/astock_veto_fill_wait.py / "
    "results/astock_veto_fill_wait.json / research/ASTOCK_VETO_FILL_WAIT.md / "
    "负控 results/_r2010bmc_fill_wait_negative.py 与收口三件 `_r2010bmc_*`（`git add -f` 走既有 `_r[0-9]*` 惯例）/ "
    "results/_r2010bmc_fill_wait_run.log）→ **本地未达 origin commit 数=0**。"
    "**口径说明（读者会追问的那个数）**：板块诊断表里主板的 `min_slack_to_limit` 是 **-5.04%**，"
    "意思是有一只名字的当日开盘涨幅**超过了该板块 10% 的涨停线**——这在真实竞价里不可能，"
    "本面只在前复权（qfq）序列上见过这种：除权日的价格假跳，或次新股首日不设涨跌幅。"
    "它**不是真涨停**，也**不影响任何一条腿的收益**（板块距离只是印出来的诊断列，不参与判定），"
    "只影响那一列的最小值；已把这句话写进 `write_md`，重跑后与脚本一致。"
    "**未验证（承上条）**：全量 smoke 与 S6 链未跑（竞争窗，`smoke_test.py` / `logs/smoke_legs.json` / "
    "`Tools/s6_chain_bmc.py` 为对端写的共享面）；本面尚未接 smoke 两腿与 S6 腿。 |"
)

path = "fleet/round_reports-bm-c.md"
with io.open(path, "a", encoding="utf-8", newline="") as fh:
    fh.write(LINE + "\n")
print("appended", len(LINE), "chars")
