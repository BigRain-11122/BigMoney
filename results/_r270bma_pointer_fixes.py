# -*- coding: utf-8 -*-
"""R270 bm-a GM s3 件⑥：s2 候选裁定后的指针修法执行器（字节级·幂等）。

- 裁定记录：research/AUDIT-20260926-S2-ADJUDICATION.md §二（每刀对应裁定#）
- 字节级替换：保 BOM/EOL/编码原面（r255/r257 五面探测律的执行面）
- 幂等：已应用=跳过；未找到=红（禁静默漏修）；重跑零重修
- selftest：python results/_r270bma_pointer_fixes.py selftest
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = "(2026-09-26 R270 GM "

# (file, regex-old(bytes-pattern), new(bytes), expected-max-count, ruling#)
REPLACES = [
    (r"research\SYSTEM_LOGIC.md", rb"data/regime_state\.json", rb"results/regime_state.json", 5, "7"),
    (r"research\CASH_LEG.md", rb"(?<!Money0923/)data/repo_daily\.csv", rb"Money0923/data/repo_daily.csv", 5, "7"),
    (r"research\FULL_INSTRUMENT_CENSUS.md", rb"(?<!/)results/instrument_census_probe\.py", rb"scripts/instrument_census_probe.py", 5, "7"),
    (r"research\RULES-AUDIT-20260924.md", rb"results/rules_check\.json", rb"logs/rules_check.json", 5, "7"),
    (r"research\BACKTEST_READINESS.md", rb"(?<!shortline/)screening/gtja191_ops\.py", rb"research/shortline/screening/gtja191_ops.py", 5, "7"),
    (r"research\BACKTEST_READINESS.md", rb"(?<!shortline/)screening/p1_factor_screen\.py", rb"research/shortline/screening/p1_factor_screen.py", 5, "7"),
    (r"README.md", rb"(?<!resolve/scripts/)scripts/classify_conflicts\.py", rb"Tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py", 5, "7"),
    (r"PLAN.md", rb"research/ideas\.md", "research/ideas.md（未建——idea 供给由 RESEARCH_MECHANISM 外源常态线承接·O-20260924-1721·R270 件⑥裁定⑩）".encode("utf-8"), 3, "10"),
    (r"research\CE_ADMISSION_V1.md", rb"results/ce_admission/CE_ADMISSION_B1\.json", rb"results/ce_admission/CE-ADMISSION-B1.json", 5, "9"),
    (r"research\CE_ADMISSION_INTAKE_B1_PREREG.md", rb"results/ce_admission/CE_ADMISSION_B1\.json", rb"results/ce_admission/CE-ADMISSION-B1.json", 5, "9"),
]

# (file, note-marker, note-line)  insert after FIRST line
HEAD_NOTES = [
    (r"research\SYSTEM_LOGIC.md", "GM 注记" + NOTE,
     "> GM 注记" + NOTE + "件⑥裁定③)：本件=遗留叙事文档——文中部分产物名（failed_daily.json 等 8 件）系愿景面从未落地；实况面以 firm/DOC_HIERARCHY.md H4 单源载体为准。"),
    (r"research\FACTOR_BLEND_V2.md", "GM 注记" + NOTE,
     "> GM 注记" + NOTE + "件⑥裁定④)：本件=判负线档案，所引产物（scripts/factor_blend_v2.py 与 results/factor_blend_v2_*）从未入仓（git 史零踪迹）——档案留原位不重建（归档不删律），指针=历史研究记录非实况面。"),
    (r"research\CE_ADMISSION_INTAKE_B1_PREREG.md", "AMENDMENT" + NOTE,
     "> AMENDMENT" + NOTE + "件⑥裁定⑨)：§results/§产物 产物名指针修正 CE_ADMISSION_B1.json→CE-ADMISSION-B1.json（实落位名·r248 history→entries 修正同族）；判据节零触碰（冻结纪律不破坏）。"),
]

# (file, section-marker, append-block)  append at end
APPENDS = [
    (r"research\R-20260925-bma-local-coding-pilot.md", "## GM 裁定补录" + NOTE,
     "\n## GM 裁定补录" + NOTE + "·T-83 s3 件⑥裁定⑥)\n\n"
     "- **不晋升**：任务 01-10 十候选脚本（rr_lint/wm_red_lint/opt_lane_digest/board_aging/inbox_aging/token_breakdown/leg_freshness/opt_cells_recon/lane_log_digest/hb_epoch_lint）零车道消费面——**消费驱动晋升律**（有车道消费才晋 scripts/，否则晋升即死码）；试点件留 `results/local_coding_pilot/tasks/` 即档案（归档不删）。\n"
     "- **任务 11/12 未实现**：handover_delta / daily_gap_audit（tasks/ 目录 01-10 实证；未来若需按新票重开，本试点不再排期）。\n"
     "- 本件任务表「python scripts/xxx.py」列=晋级后设计面路径；实况=results/local_coding_pilot/tasks/<nn>/<臂>/。引用以实况为准。\n"
     "- L4 上游指针 `HQ cph4/research/R-20260925-local-coding.md`（commit 9fcce33）=集团仓合法跨仓指针（在位实证），仓内 Test-Path 检测=假阳。\n"),
]


def main():
    dry = len(sys.argv) > 1 and sys.argv[1] == "selftest"
    n_done = 0
    for rel, old, new, maxc, ruling in REPLACES:
        p = os.path.join(ROOT, rel)
        b = open(p, "rb").read()
        hits = re.findall(old, b)
        if not hits:
            # idempotent: verify new already present
            if new in b:
                print(f"skip(already): {rel} [{ruling}]")
                continue
            print(f"RED: pattern not found in {rel}: {old!r}")
            sys.exit(1)
        assert len(hits) <= maxc, f"unexpected count {len(hits)} in {rel}"
        nb = re.sub(old, lambda m: new, b)
        if not dry:
            open(p, "wb").write(nb)
        n_done += 1
        print(f"fixed[{ruling}]: {rel} x{len(hits)}")
    for rel, marker, note in HEAD_NOTES:
        p = os.path.join(ROOT, rel)
        b = open(p, "rb").read()
        if marker.encode("utf-8") in b:
            print(f"skip(already): {rel} head-note")
            continue
        first_end = b.find(b"\n") + 1
        first_line = b[:first_end]
        rest = b[first_end:]
        eol = b"\r\n" if first_line.endswith(b"\r\n") else b"\n"
        nb = first_line + note.encode("utf-8") + eol + rest
        if not dry:
            open(p, "wb").write(nb)
        n_done += 1
        print(f"note: {rel} head-note inserted")
    for rel, marker, block in APPENDS:
        p = os.path.join(ROOT, rel)
        b = open(p, "rb").read()
        if marker.encode("utf-8") in b:
            print(f"skip(already): {rel} append")
            continue
        eol = b"\r\n" if b.endswith(b"\r\n") or b"\r\n" in b[-3000:] else b"\n"
        pad = b"" if b.endswith(b"\n") else eol
        nb = b + pad + block.replace("\n", "\r\n" if eol == b"\r\n" else "\n").encode("utf-8")
        if not dry:
            open(p, "wb").write(nb)
        n_done += 1
        print(f"append: {rel} GM adjudication section")
    print(f"{'DRY-RUN ' if dry else ''}done: {n_done} operations")


if __name__ == "__main__":
    main()
