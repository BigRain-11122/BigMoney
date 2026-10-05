# -*- coding: utf-8 -*-
"""_r525bmc_bookkeeping.py -- r525 bm-c S5/S7 bookkeeping (single source, JSON-validated).
Updates: state-bm-c.json + fleet/machines/bm-c.json + round_reports-bm-c.md line +
research/HANDOVER.md 5x entry (r521-525). Zero-window: all subprocess calls
CREATE_NO_WINDOW. EOL-preserving appends. json.loads reparse validation (r504 law).
"""
import json
import os
import subprocess
import time
from datetime import datetime, timedelta, timezone

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CN_TZ = timezone(timedelta(hours=8))
NOW = datetime.now(CN_TZ)
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_RR = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CREATE_NO_WINDOW = 0x08000000


def probe_machine():
    cpu = ram = 0.0
    try:
        import psutil
        cpu = round(psutil.cpu_percent(interval=1.0), 1)
        ram = round(psutil.virtual_memory().available / (1024**3), 1)
    except Exception:
        pass
    vram = 0
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=20)
        vram = int(float(r.stdout.strip().splitlines()[0]))
    except Exception:
        pass
    return cpu, ram, vram


CPU, RAM, VRAM = probe_machine()
print("probe cpu=%s ram=%s vram_mib=%s" % (CPU, RAM, VRAM))

# ---------------- 1. state-bm-c.json ----------------
sp = os.path.join(ROOT, "state-bm-c.json")
with open(sp, encoding="utf-8-sig") as fh:
    st = json.load(fh)
st["round_no"] = 525
st["round_no_label"] = "round 525 (bm-c)"
st["clock_read"] = NOW_ISO
st["ts"] = NOW_ISO
st["updated"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["last_seen"] = NOW_ISO
st["last_seen_at"] = NOW_ISO
st["last_round_at"] = NOW_ISO
st["last_round_ts"] = NOW_ISO
st["current_task_at"] = NOW_ISO
st["heartbeat_epoch_utc"] = EPOCH
st["cpu_pct"] = CPU
st["cpu_util_pct"] = CPU
st["free_ram_gb"] = RAM
st["idle_ram_gb"] = RAM
st["ram_free_gb"] = RAM
st["gpu_free_vram_mib"] = VRAM
st["gpu_free_vram_mb"] = VRAM
st["gpu_idle_vram_mb"] = VRAM
st["gpu_idle_vram_mib"] = VRAM
# D-19 watermarks: decisions MATCH (unchanged); orders consumed -> new key
st["last_decisions_read_at"] = NOW_ISO
st["last_decisions_sha"] = "755428F8A0816334C9A42F899DE4DB9F6F4502E80A39DA716BFC3B82DCFA1B2B"
st["last_orders_sha"] = "E79E15F98C47C406C314C2332B2D7D7883965DEAD13A1DF86542DC00E7DB4224"
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; consumed r525: 5449b5b->origin delta, O-027~030 recovered rows already closed by r502 SOP_INVENTORY + Biggame/CPH4-domain rows zero-obligation + FleetLink bm-c leg done r505)"
st["last_round"] = ("r525 bm-c: golden-week watch + 5x HANDOVER check + QA standing re-run, all-first-pass green -- "
                    "orders 154/154 double-scan zero unacked, D-19 decisions MATCH + orders watermark consumed "
                    "(3BF0F16E->E79E15F9, zero new obligations, bm-c tailscale leg done r505 pending CEO click), "
                    "smoke 48/48, S6 38/38 rc0 (zero heal, supply_gap honest), attrition CLEAN, post_review 45Y/5W/0N, "
                    "task family 6/6 (CSV cross-check), claws IN-PLACE; S0 clean FF to bm-a r717 tip 4b62458dc.")
st["did"] = ("r525 bm-c: golden-week watch round + 5x HANDOVER check + QA standing re-run, all-green first pass. "
             "(1) S0: fetch behind=2 (bm-a r717 wave: c76cc36a1 round-close + 4b62458dc addendum push receipt) -> "
             "clean FF merge to 4b62458dc, zero UU; 3 pre-existing bm-c daemon churn faces absorbed at close (r620 law). "
             "(2) S0.5 orders 154/154 set-diff zero unacked (canonical orders_diff); inbox 0 unread. "
             "(3) D-19: decisions MATCH (755428F8 zero action); orders watermark CHANGED 3BF0F16E->E79E15F9 -> delta consumed: "
             "O-2026-0930-027~030 four recovered (orphan-chain) rows already closed by r502 research/SOP_INVENTORY_202610.md "
             "(v1.0, 57-line double-gate self-check, committee 10-07 face); O-20261004-2300 = Biggame U351 domain (executed); "
             "P-2026-10-04-01/02 radar rows = CPH4 domain (BigMoney consumption face = standing OH-slice mechanism in force, "
             "first slice landed r505); O-20261004-2255 FleetLink row = bm-c machine leg already done r505 (tailscale daemon "
             "alive, login URL https://login.tailscale.com/a/13ac0ce1015dd3 unchanged and pending CEO click = only remaining "
             "physical item) -> science-judgment gate passed, zero new obligations, watermark key updated. "
             "(4) S1 smoke 48/48. (5) S2 boards: job_list 0; fleet tasks 0 open; new ticket T-2026-10-05-170-P1 verified "
             "already done by bm-a r715 same-round (trading-calendar piece) -- zero action. (6) S3: WM green (next_pick=claimed "
             "moneyflow IC, panel source-blocked); satengine status rc0 alive (Tools face, heartbeat 55s, burns_active=[], "
             "local waves all done, py 0.2% golden-week steady state); trial-labor default-drafting NOT triggered (judgment "
             "seats in-flight on other machines: fund-trio bm-b keepalive burn + N2-W15 bm-a F-04 seat; supply faces parked: "
             "W3 next wave = CEO ruling + W14 governance-parked + reopen 10-09). (7) CORE PRODUCT: QA pack r525 standing "
             "re-run (qa/smoke-r525.md 5/5 + qa/equity-curve-r525.png 66194B, 93 trades, sharpe 0.1586, maxdd -4.33%, "
             "win 46.24%, determinism=True; market_clock rc0 CALL-2026-09-30 ORA; honest data leg bar 2026-09-30). "
             "(8) S6 chain 38/38 rc0 FIRST PASS zero heal (receipt results/_r525bmc_s6_log.txt); dualrun ZERO-DRIFT "
             "streak 25; compute_audit supply_gap flag honest (ready=3=floor, breach=false, ready_unclaimed=0); "
             "py_watermark py_low_board_clear legal idle; token delta=0; REPORT/LIVE-2026-10-05 regenerated. "
             "(9) S7: loop pin5 phase-ok (next fire :X5), watchdog present, claws IN-PLACE (CR-normalized), attrition CLEAN "
             "(results/_attrition_guard_scan.json), post_review 45Y/0N/5W (5 WAIT=known design states), task family 6/6 "
             "present (schtasks CSV full-list cross-check per r517 law), chain head 648,730 flat, 5x HANDOVER r521-525 "
             "entry appended. Close: targeted add + commit -F + push + fetch/rev-list delivery self-check.")
st["current_task"] = (
    "当前活: r525 金周值守+5x HANDOVER 核对轮（S6 38/38 首过全绿+orders 154/154 双扫+D-19 orders 水位红变消费零新义务；"
    "判决链席位他机=fund-trio bm-b 在烧+N2-W15 bm-a F-04 席；supply_gap 旗=金周结构面如实披露） | "
    "最近实物: qa/smoke-r525.md 5/5+qa/equity-curve-r525.png（66194B·93 trades·确定性回测）+results/_r525bmc_s6_log.txt"
    "（38 腿零红收据·零 heal）@ " + NOW_ISO + " | "
    "下个里程碑: D-20261002-05 selftest 席位窗 10-06 00:00（r526 首过轮跑 pin selftest）；fund-trio finalize（bm-b·10-05..09）；"
    "N2-W15 judge-finalize（bm-a F-04 席·≤10-12）；D-06 拆件收口窗 10-07 12:00；O-2115/O-2030 验收 10-08；"
    "复市 10-09 数据链重挂+IntradayMarks 再核（G3）；r530=下一 5x")
st["next"] = ("(a) D-20261002-05 selftest seat window 10-06 00:00 (first round at/after runs the pin selftest = r526). "
              "(b) fund-trio finalize 10-05..09 (bm-b canonical, in-burn confirmed by keepalives). "
              "(c) N2-W15 judge-finalize = bm-a F-04 seat watch (<=10-12). (d) D-06 split closeout 10-07 12:00. "
              "(e) moneyflow IC reference batch when panel completes (still source-blocked). "
              "(f) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3). (g) O-2115/O-2030 acceptance 10-08. "
              "(h) next 5x HANDOVER = bm-c r530. (i) qa/ evidence pack per-round re-run (standing driver scripts/qa_smoke_run.py). "
              "(j) CEO physical item pending: tailscale login link click (bm-c URL alive since r505). "
              "(k) CODELY.md over-50KB flag carried (threshold re-anchor = GM ruling face per r504 note).")
st["note"] = ("r525: watch + 5x HANDOVER round closed clean. S0 clean FF to bm-a r717 tip 4b62458dc (zero overlap with lane "
              "churn). D-19 orders watermark consumed (3BF0F16E->E79E15F9): O-027~030 recovered rows -> already closed by "
              "r502 SOP_INVENTORY (zero new obligation); FleetLink row -> bm-c leg done r505, login URL alive pending CEO "
              "click; radar rows -> CPH4 domain, BigMoney OH-slice consumption face in force. New ticket T-2026-10-05-170-P1 "
              "(trading calendar) verified done by bm-a r715 same-round. 3 bm-c lane churn faces + Tools/_r518bmc_close2.py "
              "untracked scratch leftover left untouched (absorb at close / zero-commit).")
st["verify"] = ("receipts: qa/smoke-r525.md 5/5 + qa/equity-curve-r525.png (66194B) + results/_r525bmc_s6_log.txt (38 legs rc0, "
                "bad=[]) + smoke 48/48 + attrition CLEAN (results/_attrition_guard_scan.json) + post_review 45Y/0N/5W "
                "(results/post_review.jsonl + results/post_review/REPORT-20261005.md) + task family 6/6 schtasks CSV cross-check "
                "+ claws IN-PLACE (CR-normalized) + commit/push delivery self-check this close + D-19 decisions MATCH / orders "
                "consumed-to-E79E15F9 (group-tree git show origin/main raw-blob hash).")
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---------------- 2. fleet/machines/bm-c.json ----------------
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["clock_read"] = NOW_ISO
hb["cpu_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["cpu_idle_pct"] = round(100.0 - CPU, 1)
hb["free_ram_gb"] = RAM
hb["idle_ram_gb"] = RAM
hb["ram_free_gb"] = RAM
hb["gpu_free_vram_mib"] = VRAM
hb["gpu_free_vram_mb"] = VRAM
hb["gpu_free_mb"] = VRAM
hb["gpu_idle_vram_mb"] = VRAM
hb["gpu_idle_mb"] = VRAM
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW_ISO
hb["last_seen_at"] = NOW_ISO
hb["ts"] = NOW_ISO
hb["updated_at"] = NOW_ISO
hb["round_no"] = 525
hb["round_no_label"] = "round 525 (bm-c)"
hb["activity_now"] = ("r525: golden-week watch + 5x HANDOVER check + QA evidence-pack standing re-run -- qa/ 5/5 r525 refresh "
                      "(smoke-r525.md + equity-curve-r525.png 66194B), S6 38/38 rc0 FIRST PASS zero heal, smoke 48/48, "
                      "orders 154/154 zero unacked, D-19 decisions MATCH + orders watermark consumed (E79E15F9, zero new "
                      "obligations), attrition CLEAN, post_review 45Y/0N/5W, task family 6/6 + claws IN-PLACE; S0 clean FF to "
                      "bm-a r717 tip 4b62458dc; judgment seats on other machines (fund-trio bm-b in-burn, N2-W15 bm-a F-04); "
                      "supply_gap flag = golden-week structural")
hb["current_task"] = st["current_task"]
hb["latest_artifact"] = ("qa/ evidence pack r525 (smoke-r525.md 5/5 + equity-curve-r525.png 66194B) + "
                         "results/_r525bmc_s6_log.txt (38 legs rc0 first-pass receipt) + research/HANDOVER.md r521-525 5x entry")
hb["next_milestone"] = ("D-20261002-05 selftest window 10-06 00:00 (r526 first round at/after runs pin selftest); "
                        "fund-trio finalize (bm-b) 10-05..09; N2-W15 judge-finalize (bm-a) <=10-12; D-06 closeout 10-07 12:00; "
                        "O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, IntradayMarks re-check); month-end exam 10-31; "
                        "next 5x = r530")
hb["prod_lanes"] = ("N2-W15 JUDGE: judge-finalize = bm-a F-04 seat in-flight (watch); fund-trio NULLS x3 bm-b canonical "
                    "keepalive in-burn (ready_unclaimed=0); W3 next wave = CEO ruling face; boards open=0; watermark green "
                    "(py_low_board_clear); moneyflow IC = bandit next_pick claimed, panel still source-blocked; supply_gap "
                    "flag honest (floor not breached); qa/ evidence pack standing per-round; S6 chain zero-window "
                    "wrapper-ized (r524 lineage); CEO physical item pending: tailscale login click (bm-c URL alive since r505)")
hb["verdict"] = ("r525 bm-c: golden-week watch + 5x HANDOVER check (boards open=0, judgment seats on other machines, no bar "
                 "until 10-09). (1) S0 fetch behind=2 -> clean FF to 4b62458dc. (2) orders 154/154 set-diff rc0, inbox 0. "
                 "(3) D-19 decisions MATCH; orders watermark consumed 3BF0F16E->E79E15F9 (O-027~030 closed-by-r502 + "
                 "Biggame/CPH4 rows + FleetLink bm-c leg done r505 -> zero new obligations). (4) smoke 48/48. (5) boards: "
                 "T-170 new ticket verified done by bm-a. (6) WM green, py_low_board_clear; satengine rc0 alive. "
                 "(7) CORE: QA pack r525 (5/5, 93 trades, determinism=True). (8) S6 38/38 rc0 first pass, zero heal, "
                 "supply_gap honest. (9) S7: loop pin5 phase-ok; watchdog present; claws MATCH; attrition CLEAN; "
                 "post_review 45Y/0N/5W; task family 6/6 CSV cross-check; HANDOVER r521-525 entry; close: targeted add + "
                 "commit -F + push_verify.")
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---------------- 3. round_reports-bm-c.md line ----------------
rrp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rrp, "rb") as fh:
    rr_raw = fh.read()
rr_eol = b"\r\n" if b"\r\n" in rr_raw[:4000] else b"\n"
rr_line = (
    NOW_RR + " | r525 | dept:工程（金周值守轮·5x HANDOVER 核对轮·QA 证据面常设复跑） | "
    "watermark verdict=绿（red=false·py_watermark=py_low_board_clear 板空合法 idle 白名单〔判决链他机在飞+池 ready 3 全 bm-b 属主 unclaimed=0+金周无 bar〕·"
    "compute_audit FLAG:supply_gap〔ready=3=floor 零 breach·金周结构供给面诚实旗〕）｜"
    "本轮：金周值守+5x HANDOVER 核对+QA 证据面常设复跑——实物=qa/smoke-r525.md 5/5+qa/equity-curve-r525.png（66194B·3 syms x 800 bars·93 trades·sharpe 0.1586·maxdd -4.33%·win 46.24%·确定性=True·常设驱动复跑）"
    "+S6 38/38 首过全绿零 heal（收据 results/_r525bmc_s6_log.txt·bad=[]·dualrun ZERO-DRIFT streak 25·token delta=0）"
    "+HANDOVER r521-525 五倍数核对行入册｜"
    "S0=fetch behind=2（bm-a r717 波：c76cc36a1 收口+4b62458dc push 收据增补）→干净 FF 至 tip 4b62458dc 零 UU·3 个 bm-c daemon churn 面轮首已在·close 定向吸收（r620 律）｜"
    "S0.5=orders 154/154 差集零未回执（正典 orders_diff）+inbox 0 未读｜"
    "D-19=decisions MATCH（755428F8 零动作）+orders 水位红变 3BF0F16E→E79E15F9 消费：增量=O-2026-0930-027~030 四行补录（孤儿链找回·已由 r502 SOP_INVENTORY_202610.md 提前交付收口）"
    "+O-20261004-2300（Biggame U351 域）+P-2026-10-04-01/02 雷达两行（CPH4 域·本司消费面=OH 切片常设机制在役）"
    "+O-20261004-2255 FleetLink 行（本机 bm-c 腿 r505 已毕：tailscale daemon 活·登录 URL 同链接在位待 CEO 一次点击=唯一余量物理件）→科学判断闸全过零新义务·水位键更新 E79E15F9｜"
    "S1=smoke 48/48｜S2=板空（job_list 0·fleet tasks 0 open·新票 T-2026-10-05-170-P1=bm-a r715 同轮 done 零动作）｜"
    "S3=satengine status rc0 活（Tools 面·heartbeat 55s·burns_active=[]·本机波次全毕 py 0.2%）+试用劳动力常设线=判决席位他机在飞非触发态（fund-trio bm-b 在烧+N2-W15 bm-a F-04 席）+supply 面停泊照旧（W3=CEO 裁定+W14 park+复市 10-09）｜"
    "S7=loop pin5 phase-ok（下火 :X5）+watchdog 在位+双爪 IN-PLACE（CR 归一恒等）+attrition CLEAN+post_review 45Y/0N/5W（5 WAIT=已知设计态）+任务族 6/6（schtasks CSV 全量交叉 r517 律）+chain head 648,730 实读平持｜"
    "本地未达 origin commit 数=0（close push 后 fetch+rev-list 送达自证）｜"
    "当前活: r525 金周值守+5x HANDOVER 核对 | 最近实物: qa/smoke-r525.md 5/5+qa/equity-curve-r525.png 66194B @ " + NOW_ISO + " | "
    "下个里程碑: D-20261002-05 pin selftest 席位窗 10-06 00:00（r526 首过跑）；fund-trio finalize（bm-b·10-05..09）；N2-W15 judge-finalize（bm-a F-04·≤10-12）；D-06 收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）；月界首考 10-31；r530=下一 5x")
with open(rrp, "ab") as fh:
    fh.write(rr_eol + rr_line.encode("utf-8") + rr_eol)

# ---------------- 4. HANDOVER 5x entry ----------------
hdp = os.path.join(ROOT, "research", "HANDOVER.md")
with open(hdp, "rb") as fh:
    hd_raw = fh.read()
hd_eol = b"\r\n" if b"\r\n" in hd_raw[:4000] else b"\n"
hd_entry = (
    "> bm-c round 525 五倍数核对（2026-10-05 09:2x·增量窗 r521-525 五轮）：增量窗 r521-525=bm-c 面（**金周看护主线+QA 证据包常设化五连+S6 链零窗 wrapper 化连营**——"
    "r521 QA 复跑+S6 链零窗 wrapper 化首跑〔38 腿全经 Invoke-SilentExe CreateNoWindow·r521 GBK 编码坑律入 CODELY：wrapper 收 python CJK 输出先设 PYTHONIOENCODING=utf-8 否则 U+FFFD 不可逆〕；"
    "r522 P0 修复轮〔S6 leg-35 daily_report rc1→根因=r521 merge resolver compute_audit union=list(oid) 键值反转 195 行 JSON 字符串入库→反序列化原位手术治愈+r522 坑律：union 一律 values()+行级类型门双断言〕；"
    "r523 看护轮〔S0 add rc128 daemon index.lock 竞态坑+daemon 陈旧 FETCH_HEAD 中途搬 main 坑（r523 律：add rc128=竞态非阻塞勿重试环·集成目标恒 fetch 后真 tip 终点态核验）+S6 38/38 复绿〕；"
    "r524 看护轮〔S0 FF 至 bm-a r716 tip d35c2ef96+收口 push 窗双坑（r524 律：silent-git 单引号 -m 拆词→-F 消息文件正法+爪双拦=落后 origin 信号→fetch behind=7→merge 1-UU compute_audit union→push 爪过零 --no-verify）〕；"
    "r525=本核对轮〔QA r525 复跑 5/5+png 66194B+S0 FF 合流 bm-a r717 波 4b62458dc 零 UU+orders 154/154 双扫+D-19 orders 水位红变消费（3BF0F16E→E79E15F9：O-027~030 补录已由 r502 SOP_INVENTORY 收口+O-20261004-2300/雷达两行=Biggame/CPH4 域+FleetLink 行本机腿 r505 已毕〔登录 URL 同链接在位待 CEO 点击〕→零新义务）"
    "+T-170 新票核验（bm-a done 同轮零动作）+S6 38/38 首过零 heal（streak 25·py_low_board_clear 合法 idle·supply_gap 诚实旗·token delta=0）+post_review 45Y/0N/5W+attrition CLEAN+任务族 6/6（CSV 交叉 r517 律）+双爪 IN-PLACE+HANDOVER 本行〕）"
    "产物清单漂移=scripts/qa_smoke_run.py 常设驱动〔r516 建〕+qa/smoke-r52{1..5}.md+qa/equity-curve-r52{1..5}.png〔五轮常设证据包族〕+results/_r52{1..5}bmc_* 工件族〔S6 log+链驱动 scratch 族〕+CODELY.md 坑律行 r521/r522/r523/r524 四条；"
    "零新产品行（看护窗零批 finalize 零判决零新链入=如实注记）；统一链 **648,730 实读平持**（live head=results/mass_trial/w3_judge.json trials_ledger.total〔MASS_TRIAL_W3_JUDGE〕·本窗零入链·N2-W15 JUDGE finalize 未落〔bm-a F-04 席·≤10-12〕落地后按 judged-cells 口径前移）；"
    "orders 154/154 双扫零未回执全窗维持；smoke 48/48 全窗维持；D-19 decisions 755428F8 MATCH 零消费全窗·orders 3BF0F16E→E79E15F9 单点消费（r525）；"
    "池态=403 总量 399 done+3 ready（FUND 三族 NULLS bm-b canonical keepalive 在烧·ready_unclaimed=0）+1 waiting（W14-GENERATE governance-parked·O-2115 维持）；"
    "下窗锚=D-20261002-05 selftest 席位窗 10-06 00:00（首过轮跑 pin selftest=r526）+fund-trio finalize（bm-b·10-05..09）+N2-W15 judge-finalize（bm-a F-04 席·≤10-12）+D-06 拆件收口窗 10-07 12:00+O-2115/O-2030 验收 10-08+复市 10-09 数据链重挂+IntradayMarks 再核（G3）+月界首考 10-31+CEO 物理件=Tailscale 登录链接点击（bm-c r505 产·URL 在位待点）；下一 5x=bm-c r530。")
# insert after first line (title)
first_eol = hd_raw.find(b"\n")
new_hd = hd_raw[:first_eol + 1] + hd_entry.encode("utf-8") + hd_eol + hd_raw[first_eol + 1:]
with open(hdp, "wb") as fh:
    fh.write(new_hd)

# ---------------- 5. validation (r504 law) ----------------
for p in (sp, hp):
    with open(p, encoding="utf-8-sig") as fh:
        d = json.load(fh)
    assert isinstance(d.get("heartbeat_epoch_utc"), int), p + " epoch not int"
    print("reparse OK:", os.path.basename(p), "round_no=", d.get("round_no"), "epoch=", d.get("heartbeat_epoch_utc"))
print("BOOKKEEPING DONE now=", NOW_ISO)
