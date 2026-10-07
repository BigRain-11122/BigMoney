"""r860 bm-a round close, part 2: round report line + HANDOVER 5x stamp.
(state round_no + heartbeat already written in part 1.)"""
import io
import datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
R = 860

# --- round report line (repo root file) ------------------------------------
RP = r"round_reports-bm-a.md"
raw = io.open(RP, encoding="utf-8", newline="").read()
sep = "\r\n" if raw.endswith("\r\n") else "\n"
assert "| r860 |" not in raw, "r860 line already present"
line = (
    f"{NOW} | r{R} | bm-a | dept:策略+研究 | S0-1 anchor + orphan probe 孤儿面=1 "
    "(BigDomain cross-company read-only) | orders unacked=[] 双扫描 + DEC/ORD "
    "hash identical (ee659451/2bb2ee75) 零动作 | smoke 49/49 + watermark "
    "red=false healthy + satengine alive | 当前活=W16 漏斗三层推进（SCREEN->JUDGE）| "
    "最近实物=results/trial_labor_w16/w16_screen.json + w16_screen_cells.csv "
    "(03:44 finalize, null p95 0.5116 带内[0.50,0.52], 存活 40/173) + "
    "judge_state.json | 下个里程碑=W16-JUDGE daemon 点火 ~04:16 -> "
    "judge-finalize + s4 intake <=06:30 今日（48h CEO 呈报钟起于 judge-finalize）| "
    "PRODUCT: W16 SCREEN 373-cell burn complete 03:37 (checkpoint full) -> "
    "screen-finalize LANDED (null p95 0.5116 in-band, survivors 40/173) -> "
    "w16_screen.json + cells csv; judge-prep PASS 30s (manifest 48/48, census "
    "L/D frozen-equal, sixteen-gate dual-leg meta); TRIAL-LABOR-W16-JUDGE "
    "seat enrolled two-leg r859 law (submit validate + raw-text insert, "
    "pool 408) | infra heals: pool stale-compact revert (03:32:12 post-claim "
    "write lost owner_since -> origin-verbatim restore, claim 03:32:08 "
    "intact zero-info-loss); enrollment runner_args comma-string bug fixed "
    "both faces (W16-JUDGE argparse instant-exit root cause); fuse "
    "false-crash tombstones x2 (r824 precedent: JUDGE args-bug + SCREEN "
    "harvest-gap completion); SCREEN worker-claim + harvest flip done 03:58 "
    "(W13/W14 observing-round law) | S6 35 legs rc0 (dualrun ZERO-DRIFT "
    "408 entries streak 51 + pre-market no-ops legal + CEO faces regen "
    "REPORT/LIVE-2026-10-08 + dashboard + scorecard) | 3 pits appended "
    "(pit-pool-edit: runner_args 逗号串 / worker-claim 收割缺半三件套 / "
    "claim 后 compact 覆写) | HANDOVER 5x stamp r856-r860 | "
    "本地未达 origin commit 数=0（push 后 fetch 自证；被拒则 addendum 披露）"
)
if not raw.endswith("\n"):
    raw += sep
new = raw + line + sep
io.open(RP, "w", encoding="utf-8", newline="").write(new)
print("round report r860 line appended")

# --- HANDOVER 5x stamp (r860 % 5 == 0) -------------------------------------
HD = r"research\HANDOVER.md"
raw = io.open(HD, encoding="utf-8", newline="").read()
hs = "\r\n" if "\r\n" in raw else "\n"
assert "bm-a round 860 窗复核" not in raw, "5x stamp already present"
stamp = (
    f"> bm-a round 860 窗复核（2026-10-08 03:5x）：覆盖 r856-r860（法面权威="
    f"round_reports-bm-a.md 全量在库）。本窗净产出=**TRIAL_LABOR_W16 漏斗三层推进**"
    "（GENERATE done 10-07 19:20 n=173 -> SCREEN 373 cells 烧录 03:37 + finalize "
    "03:44〔null p95 0.5116 带内·存活 40/173·w16_screen.json+cells csv〕-> "
    "judge-prep PASS 30s 双腿 census 冻结恒等 -> JUDGE seat 入池 408 + 实参修正 + "
    "fuse 假崩双 tombstone（r824 范式）+ SCREEN 收割翻面 done 03:58〔W13/W14 观察轮 "
    "接管律〕；JUDGE 烧录 04:16 后 daemon 自取）+ r856-r859 三连 S0 风暴正典解"
    "（r857 cycle_position 普查产品 + r858/r859 双风暴收口）+ 3 坑律入册"
    "（pit-pool-edit：runner_args 逗号串 / worker-claim 收割缺半三件套 / claim 后 "
    "compact 覆写）。"
)
if not raw.endswith("\n"):
    raw += hs
new = raw + stamp + hs
io.open(HD, "w", encoding="utf-8", newline="").write(new)
print("HANDOVER 5x stamp appended (r856-r860)")
print("PART2 DONE")
