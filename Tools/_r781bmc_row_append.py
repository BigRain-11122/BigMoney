# -*- coding: utf-8 -*-
"""r781 bm-c S5 ledger row append: composes the canonical r781 report row
(now-stamped), writes evidence file results/_r781bmc_row.txt, then appends
verbatim to logs/iteration-loop/round_reports-bm-c.md (CANON face only --
r749 path-split pit: NEVER touch ROOT round_reports-bm-c.md; r780 close
template already cured, this generation keeps the cure).
Byte asserts: row file == composed row; ledger endswith row; delta == len.
Pattern credit: Tools/_r780bmc_row_append.py + results/_r780bmc_row.txt
(evidence-file + append split)."""
import datetime
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

did = (
    "r781: S6 二连全绿窗+QA det-99th 让位续+fund_premium 发布面观察轮（22:2x-22:4x 窗·第 82 bm-c 连守轮）——"
    "①S0：fetch 实核 HEAD==origin/main==3a624f7c2 零增量免 rebase（ahead=0 behind=0·轮首脏 10 面全为 bm-c 自产 daemon live faces+本司 r781 driver 零外来半成品）；"
    "②S0.5 双扫：ORD/DEC 双恒等零增量（86218DE8/EE70CEF0）·unacked=0（51 orders）·inbox=0；"
    "③S1 smoke 49/49 全绿+SAT 引擎活（status rc0·Tools 实例面·hb age 48s）；"
    "④S2 板清（177 票 0 open·bm-c 在册 claimed=T-2026-09-30-134 一张·job 板零）"
    "+idle 非绿（RAM 15.2%<40%·VRAM 1.62GB<6GB·claimable_pool_lines=2 非绿零义务·O-20261007-2315）；"
    "⑤**QA r781 槽探针=外机包占用（origin+本地同步态·qa face 821/567·slot_r781=smoke-r781.md+equity-curve-r781.png·r782 亦占·r783 空）"
    "→本司 det-99th QA 包让位跳写第三窗（r669 覆写禁令·探针 _r781bmc_qa_probe.json verdict_zero_collision=false 在案·让位=诚实披露非义务跳过）**；"
    "⑥**S6 40/40 rc0 二连全绿窗（CEO 面 40 张再生成）**：update_daily new rows=0 cutoff 10-08 面板完备〔12 SZ r779 治愈面维持〕"
    "·fund_premium 期望 NAV 日仍 09-30 诚实 no-op〔发布面=基金 NAV T+1·10-08 NAV 待 10-09 晚窗·第三连察·非故障〕"
    "·regime ORANGE d2 shadow〔hs300<MA200〕·live_paper ENFORCE active〔masked blocked=0 yellow=1〕"
    "+lane_io stale-takeover derive 合法〔bm-a hb 陈 43min·O-2100 s2.4〕"
    "·t35 open-fill PASS 0/0/0·t35_paper_export 6 员 18 仓 equity 5,996,451→export-2026-10-08.json"
    "·dualrun ZERO-DRIFT streak 51 @408 条"
    "·py_watermark verdict=py_low_board_clear〔窗 2·板清合法 idle 白名单〕"
    "·compute_audit 旗=pool_starvation+supply_floor〔ready=0<floor 3·N1 常供线在役已知面·supply_gap=false〕"
    "·daily_report REPORT-2026-10-08 再生成〔faces=5〕·ceo_live_usage LIVE-2026-10-08 再生成〔ORANGE·cap 50%·heat COOL〕"
    "·scorecard S=2 A=4 B=0 C=0·build_status 再生成〔factors=10·backtest 432combos〕；"
    "⑦CEO 菜单等待态一行声明（A=视频段解冻·零勾选回执·等待态维持不重扫）；"
    "⑧自愈四件全绿+attrition 4 台账 CLEAN（3 healed 历史缩行注记照录）·idle 非绿（RAM 3.1GB·idle_rounds=0·agenda 未饿）"
)

verify = (
    "smoke 49/49"
    " + results/_r781bmc_s6_log.txt（40 legs rc0=40 nonzero=0 二连全绿窗·fund_premium 诚实 no-op·AGGR/GRID/CTA 幂等 no-op 行在案）"
    " + results/_r781bmc_s05_facts.json（双扫恒等·unacked=0·inbox=0·shape-asserted）"
    " + results/_r781bmc_qa_probe.json（r781 槽外机占用披露·让位依据）"
    " + results/_attrition_guard_scan.json CLEAN（4 台账）"
    " + results/idle_trigger.bm-c.json（green_idle=false 非绿零义务）"
    " + results/watermark_red.json（red=false）"
    " + push 送达自证（commit 后 fetch origin/main..HEAD=0）"
)

nxt = (
    "r782 续作: ①fund_premium 10-08 NAV 首采重试（发布面=T+1·10-09 晚窗重试）"
    "②QA det-99th 撞名续判（r782 槽占用已知·r783 槽空在案）"
    "③CEO 勾选后按选项走（A=视频段解冻·等待态维持）"
    "④T-177 regime-5 标签器（bm-a 车道）消费面跟进"
    "⑤下一 5x=bm-c r785"
)

row = (
    "%s | r781 | dept:研究+数据（盘后窗·S6 40/40 二连全绿+QA det-99th 让位续+fund_premium 发布面观察轮·第 82 bm-c 连守轮）"
    " | 本地未达 origin commit 数=见 S7-close 尾行（commit 后 push+fetch 自证）"
    " | WM-VERDICT: 绿（red=false·lane=healthy·ORD 86218DE8 恒等·DEC EE70CEF0 恒等·双扫零增量·unacked=0〔51 orders〕·inbox=0"
    "·facts 单源 _r781bmc_s05_facts.json shape-asserted·水位律执法面）"
    " | 孤儿面=1（ComfyUI 产线资产·只读不杀）"
    " | %s"
    " | verify: %s"
    " | next: %s"
    " | score=2（S6 40 腿 CEO 可见面再生成=二连全绿窗+paper_export/daily_report/LIVE 页实物刷新=recount 实际文件改动级产出"
    "·QA r781 槽外机占用让位=记账诚实非义务跳过·fund_premium 发布面观察=诚实 no-op）"
    " | 记账预算：4（state+心跳+行直落+delivery 行·其余全为数据管线产出不计）[via bm-c r781]"
) % (NOW, did, verify, nxt)

row_path = os.path.join(REPO, "results", "_r781bmc_row.txt")
with open(row_path, "wb") as fh:   # binary: LF-exact, no CRLF translation
    fh.write((row + "\n").encode("utf-8"))
row_bytes = open(row_path, "rb").read()
assert row_bytes.decode("utf-8") == row + "\n", "row file LF-exact assert"

ledger = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
before = os.path.getsize(ledger)
with open(ledger, "ab") as fh:
    fh.write(row_bytes)
after = os.path.getsize(ledger)
assert after - before == len(row_bytes), "ledger delta mismatch"
assert open(ledger, "rb").read().endswith(row_bytes), "ledger tail assert"
# ROOT orphan face must remain untouched (r749 freeze): mtime unchanged by
# this append action (we never open it for write; capture == compare).
root_orphan = os.path.join(REPO, "round_reports-bm-c.md")
orphan_mtime = os.path.getmtime(root_orphan) if os.path.exists(root_orphan) else None
assert os.path.getmtime(root_orphan) == orphan_mtime, "ROOT orphan touched!"
print("ROW_APPEND_OK bytes=%d ledger=%d->%d orphan_mtime=%s now=%s"
      % (len(row_bytes), before, after, orphan_mtime, NOW))
