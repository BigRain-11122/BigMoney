"""r461 bm-a S7 closeout: orders re-scan + state bump + heartbeat + report line."""
import datetime
import glob
import io
import json
import os
import time

# S7 orders re-scan (dual-scan second leg)
disk = {os.path.basename(p) for p in glob.glob(r"fleet\orders\O-*.md")}
hb = json.load(io.open(r"fleet\machines\bm-a.json", encoding="utf-8"))
ack = set(hb.get("orders_ack", []))
diff = disk - ack
print("orders re-scan unacked:", sorted(diff) if diff else "[] clean")

# state
st = json.load(io.open(r"state-bm-a.json", encoding="utf-8"))
st["round_no"] = 462
st["did"] = (
    "r461: W13 SUMN adoption freeze whole-package landed (drafting-machine "
    "next-round self-freeze per berth-first-to-hold, first self-freeze "
    "precedent; W5/W6/W7 timeline mirror): (1) freeze trigger live re-verify "
    "= W12 full-chain consumed (judge-finalize 05:22:37 exit 0, w12_judge "
    "188/188 zero G1 zero G2, intake lawful-zero, CEO-REPORT-WAVE12 48h to "
    "10-02 05:22:37, attrition both faces CLEAN, ledger wave-12 "
    "67c86c9cf4ef1ca7, sec.7/8 backfilled) + pool all-done zero in-flight; "
    "(2) probe deterministic rerun SHA256 byte-identical (sha16 "
    "C2E5AAB0AC05906F, rc=0); (3) SEED_REGISTRY three keys "
    "20323000/20323500/20324000 registered same commit, three-step law ALL "
    "GREEN (138-key post-reg view, first-els 142952215/350730315/901874307 "
    "distinct, bands clean, facts _r461bma_w13_seed_law_facts.json); "
    "(4) frozen prereg TRIAL_LABOR_W13_PREREG.md (banner: trigger re-verify "
    "+ collision-4-check r252 law incl inbox-zero + checklist 1-10 replay "
    "+ W12 screen p95 0.513208 carried into sec.5.2 + 13-source declare "
    "window + DSR live head 355,375); (5) wave ticket T-2026-09-30-125 "
    "opened+claimed same round; (6) TRIAL-LABOR-W13-GENERATE catalog pre-arm "
    "(W12 mirror, runner_exists gated, three-verify complete); (7) freeze MSG "
    "dual-signal; (8) push rejected mid-window on parallel bm-b r449 (W8 "
    "step-1) + bm-c r257 (SLOT-7 runner landed) -- stash runtime file + "
    "rebase clean + catalog union JSON-valid verified both sides (SLOT-7 "
    "armed + W13 entry, 14 entries) + push LANDED 8bc04fd63; (9) S6 39-leg "
    "chain ALL rc=0 incl update_lhb rc=0 SELF-HEAL (r456 exit-3 "
    "source-revision quarantine closed) + attrition guard CLEAN; (10) S7 "
    "machinery: loop pin=8 no-op, watchdog registered, claw parity, "
    "IntradayMarks Ready next fire today 09:25"
)
st["verify"] = (
    "smoke 26/26; orders 122/122 dual-scan zero-diff; freeze four-piece on "
    "origin 8bc04fd63 (rebased clean); seed three-step ALL GREEN facts "
    "in-tree; frozen prereg self-checks PASS (84 lines, sec.7 placeholder "
    "discipline); S6 39/39 rc=0 (lhb self-heal confirmed); attrition guard "
    "CLEAN; dualrun zero-drift streak continues; heartbeat epoch int "
    "self-verified"
)
st["next"] = (
    "r462: (1) W13 runner build slice scripts/trial_labor_w13.py = G-SUMN "
    "fail-closed anchor gate (decidable 3,363/open 387/first-decidable "
    "120/sumn10 368/slope 387up-0down/mirror XOR=0) + verbatim-import "
    "a158_tsgate_probe + r446 surgical pit law: prep/finalize/judge-prep "
    "real-data identity-face three-command first-run BEFORE declaring "
    "runner landed -> selftest -> catalog runner_exists flip -> GENERATE "
    "pool enqueue -> autofill burn -> SCREEN -> JUDGE; (2) 10-01 "
    "month-first-round trio (science_audit+monthly_briefing+self_review "
    "idempotent) + REGIME_GUARD v3 date-gate auto-activation hands-off; "
    "(3) IntradayMarks 9:25 fire result check after 09:25 today "
    "(D-20260929-04 leg-1); (4) verdict watches: SLOT-7 NNL-BREADTH (bm-c "
    "lane, <=48h), W6 48h CEO face due 10-02 06:40, W12 48h face due 10-02 "
    "05:22:37; (5) supply_floor: SLOT-7 ready=1 + W13 gated pending runner "
    "-> runner build unblocks second ready; (6) S9C amend veto window to "
    "10-07 passive"
)
st["last_round_at"] = "2026-09-30T07:50:00+08:00"
st["current_task"] = "r461 closed (W13 freeze landed 8bc04fd63); next = W13 runner build slice"
st["updated"] = "2026-09-30T07:50:00+08:00"
json.dump(st, io.open(r"state-bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# heartbeat
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
hb["last_seen"] = now_iso
hb["current_task"] = "r461 W13 freeze landed (push 8bc04fd63); r462 = W13 runner build"
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
json.dump(hb, io.open(r"fleet\machines\bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# self-verify epoch int type + clock T-separator
back = json.load(io.open(r"fleet\machines\bm-a.json", encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in back["clock_read"], "clock must be ISO T-separated"
print("heartbeat epoch int OK:", back["heartbeat_epoch_utc"],
      "clock:", back["clock_read"])

# round report line
line = (
    "2026-09-30T07:5x+08:00 | r461 | dept:研究+策略+舰队 (W13 收编冻结轮) | "
    "WM-VERDICT: 绿 (watermark_red red=false lane=healthy 07:10; 本轮 WM probe "
    "rc=0; py 尾窗低位=夜窗合法态·池 0 ready 翻面前=W13 门控待 runner) | "
    "CEO 可见面: 当前活=W13 SUMN 收编冻结 whole-package 落地（起草机次轮自冻结"
    "·首例·泊位先到持有条款兑现）; 最近实物=research/TRIAL_LABOR_W13_PREREG.md "
    "(FROZEN·07:3x commit 8d8078e32→rebase 后 origin 8bc04fd63) + SEED_REGISTRY "
    "三键 20323000/20323500/20324000 + facts results/_r461bma_w13_seed_law_"
    "facts.json + 波级票 T-2026-09-30-125 + TRIAL-LABOR-W13-GENERATE 门控条目 + "
    "MSG-20260930-073x-bma-ALL（07:39 push LANDED）; 下个里程碑=W13 runner 构建"
    "scripts/trial_labor_w13.py（G-SUMN fail-closed 锚门+verbatim-import+r446 "
    "真数据三命令首跑前置律）→ GENERATE 入池 autofill 点火→ SCREEN→ JUDGE"
    "（窗 ≤48h·判决面 48h CEO 呈报随落地起计） | did: S0-1 锚 bm-a→pull Already "
    "up to date→S0.5 令差集 122/122 零未回执+decisions 尾零新行→S1 smoke 26/26→"
    "S2 双板零 open 票→S3 W13 冻结窗：触发器①活读复验（W12-JUDGE 05:22:37 全链"
    "落地+池全 done 零在飞）+探针重跑字节恒等+三步律 ALL GREEN（rg 命中全可分类"
    "=泊位/冻结文档+registry 占位注释·W7 r255 先例族）+冻结横幅十项回放+T-125 "
    "同轮开票认领+目录预武装（三查镜像 W12 条目）+MSG 双信号；中窗 push 撞 bm-b "
    "r449（W8 step-1）+bm-c r257（SLOT-7 runner landed）并行窗=stash 运行时件+"
    "rebase 干净+catalog union JSON 校验双面保全（SLOT-7 armed+W13 条目 14 "
    "entries）+push LANDED；S6 39 腿全 rc=0——含 update_lhb rc=0 自愈（r456 "
    "exit-3 源改史隔离窗闭合）+dualrun 零漂移+attrition guard CLEAN；S7 机制："
    "loop pin=8 no-op+watchdog 幂等重注+pre-commit 钳 parity+IntradayMarks "
    "Ready 次发 09:25 | verify: smoke 26/26; orders 122/122 双扫; 冻结四件 "
    "origin 8bc04fd63 实证; 三步律 facts ALL GREEN; 冻结件自检 PASS（§7 占位"
    "纪律）; S6 39/39 绿; 心跳 epoch int+clock T 分隔自证 | next: (1) W13 "
    "runner build（r446 三命令真数据首跑前置律）→ catalog flip → GENERATE 入池"
    "→ autofill 烧 (2) 10-01 月首轮三件套+REGIME_GUARD v3 日期门 hands-off "
    "(3) IntradayMarks 09:25 后查火果（D-20260929-04 leg-1） (4) SLOT-7/"
    "W6/W12 48h verdict/CEO 面 watch (5) 下轮 5x=r465 HANDOVER [via bm-a]\n"
)
with io.open(r"logs\iteration-loop\round_reports-bm-a.md", "a",
             encoding="utf-8") as f:
    f.write(line)
print("round report line appended")
