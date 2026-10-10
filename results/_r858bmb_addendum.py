#!/usr/bin/env python
# r858 bm-b addendum writer: tech.md T23 slice-2 consumption record +
# round_reports.md r858 addendum line (push detour + in-window verdict).
# Binary-tail appends with per-file EOL matching (r838 EOL law).
# Encoding: pure ASCII body (repo PS/py GBK decode law).
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TECH = os.path.join(ROOT, "state", "queue", "tech.md")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")

now = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

TECH_REC = (
    "> r858 消耗记录（bm-b）：T23 slice-2 随机语法全量普查本轮完成出列（面板重建完备→r854 autofire watcher 三窗接力"
    "〔r854 armed 90min→honest timeout 03:27:56 receipt archived→r858 re-arm single-flight law〕→astock complete flip 03:34"
    "〔cutoff 2026-10-09·5,219/5,229·10 结构性失败股 quarantine 3/3 attempts 如实披露〕→全量 burn detached 564.1s·"
    "4,160 draws·62 ok/2 skip·48 unique formulas·500 census days→**frozen verdict line: census_holds=true = "
    "observed_family_max_abs_icir 0.353 > null_family_p95 0.139**〔h=1 next-day rank-IC family-max 面·b_nulls 64·"
    "min_cross 100·descriptive h=5 不入判词〕——随机语法族 max 超单式 null p95 约 2.5 倍=多重比较膨胀实证读数；"
    "N2 U3①起草窗〔r840 slice-1 已开·POSITIVE-with-riders〕现携族级阈值校准输入：未来 grammar-search prereg 判线"
    "必须族级（族 max vs 族 null p95）禁单式门；riders 照携（A158 血统负先验 157/158+GTJA 0/183+WQ 0/82·RL/MCTS "
    "宣称未核·stock 因子=测量面非可交易面）。证据=results/t23_census/CENSUS-2026-10-09.json+latest.json"
    "〔evidence_cutoff=2026-10-09〕+watch receipt 三代链〔_r854bmb archived timeout/_r858bmb fired〕。"
    "r857 verdict-window obligation <=10-11 06:00 当窗 discharge。"
)

ADDENDUM = (
    now + " | r858 bm-b addendum | "
    "PUSH DETOUR RECORD (post-closeout): first push blocked by pre-push claw (D results/_w209bmc_freeze_edits.py -- no owner "
    "evidence) = CORRECT fail-closed live-fire (r856 kin), NOT a local deletion -- origin advanced mid-round (bm-c r848 trio "
    "b2e4fd6ec/2d0415076/8fb839fb7 W209 freeze-prep bundle, files my base d550bf11c never had); NO --no-verify escape used; "
    "resolution = rebase onto 8fb839fb7, 31 UU faces all S6 idempotent re-derives resolved ours-side (r856 precedent), rebase "
    "--continue editor-failure editing-state sticky face = KNOWN r758 law (r782 entry leg-3), remedy executed as codified: "
    "git commit -F .git/rebase-merge/message -> git rebase --quit -> git checkout -B main a74272a5f branch reattach (abort "
    "avoided = would orphan completed replay); tree verified pre-push (books + T23 faces + bm-c bundle file present via "
    "ls-tree, parent=8fb839fb7); push LANDED 8fb839fb7..a74272a5f behind=0 ls-remote self-proof | "
    "T23 CENSUS BURN LANDED IN-WINDOW (fired 03:34:40, elapsed 564.1s, done 03:44:05): results/t23_census/"
    "CENSUS-2026-10-09.json + latest.json; frozen verdict line = census_holds=true (observed_family_max_abs_icir 0.353 > "
    "null_family_p95 0.139; 4,160 draws, 62 ok/2 skip, 48 unique formulas, 500 census days, evidence_cutoff=2026-10-09, "
    "universe 3,514/per-files 5,219 with 10 quarantined disclosed); r857 verdict-window obligation <=10-11 06:00 DISCHARGED "
    "SAME ROUND; tech.md T23 slice-2 consumption record appended (r840-anticipated slice-2 face closed); watcher pid17116 + "
    "burn pid25780 both exited, ZERO live seats, no re-arm needed | "
    "next r859: moneyflow IC next_pick unlock check (astock flip landed 03:34, next wm probe) -> W210 freeze prep PARKED on "
    "M9 gate (W209 freeze+finalize pending bm-c) -> holds: N2 U3(1) prereg window (now carries full-burn family-level "
    "threshold calibration face) / G2 fallback -> pool-EOL fleet adjudication watch -> O-20261011-0012 CPU-max maintained "
    "(engine queue dry until W209 gate opens)"
)


def append_tail(path, text, eol):
    data = text.encode("utf-8")
    with open(path, "ab") as f:
        size = os.path.getsize(path)
        if size > 0:
            f.write(eol)
        f.write(data)
    print("appended", os.path.basename(path), len(data), "bytes")


# tech.md: LF-dominant file tail convention check
tb = open(TECH, "rb").read()
tech_eol = b"\n" if not tb.endswith(b"\r\n") else b"\r\n"
append_tail(TECH, TECH_REC, (b"\n" if tech_eol == b"\n" else b"\r\n") + b"\n")

# round_reports.md: file currently ends with my r858 line (no trailing EOL)
rb = open(REPORT, "rb").read()
assert rb.endswith(b"CPU-max maintained"), repr(rb[-40:])
append_tail(REPORT, ADDENDUM, b"\r\n")
print("done")
