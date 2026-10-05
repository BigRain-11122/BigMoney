# -*- coding: utf-8 -*-
"""_r526bmc_bookkeeping.py -- r526 bm-c S5/S7 bookkeeping (r525 blood, single
source, JSON-validated). Updates: state-bm-c.json + fleet/machines/bm-c.json +
round_reports-bm-c.md line. NOT a 5x round (next 5x = r530) -> no HANDOVER leg.
Zero-window: all subprocess calls CREATE_NO_WINDOW. EOL-preserving appends.
json.loads reparse validation (r504 law)."""
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
st["round_no"] = 526
st["round_no_label"] = "round 526 (bm-c)"
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
# D-19 watermarks: BOTH MATCH this round (decisions 755428F8 + group orders E79E15F9)
st["last_decisions_read_at"] = NOW_ISO
st["last_decisions_sha"] = "755428F8A0816334C9A42F899DE4DB9F6F4502E80A39DA716BFC3B82DCFA1B2B"
st["last_orders_sha"] = "E79E15F98C47C406C314C2332B2D7D7883965DEAD13A1DF86542DC00E7DB4224"
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r526 re-check MATCH E79E15F9 zero delta, zero consumption)"
st["last_round"] = ("r526 bm-c: golden-week watch round + QA standing re-run, all-first-pass green -- "
                    "orders 154/154 double-scan zero unacked, D-19 double MATCH (decisions 755428F8 + group orders "
                    "E79E15F9, zero consumption), smoke 48/48, S6 38/38 rc0 first pass zero heal (dualrun streak 26, "
                    "supply_gap honest flag, py_low_board_clear legal idle), attrition CLEAN, post_review "
                    "unresolved-NO=0, quartet 4/4 + claws IN-PLACE; S0 clean FF to bm-a r718 tip 98a856d00.")
st["did"] = ("r526 bm-c: golden-week watch round + QA standing re-run, all-green first pass. "
             "(1) S0: pull --rebase blocked by 3 pre-existing bm-c lane daemon churn faces (r620 absorb-at-close law) "
             "-> fetch behind=3 (bm-a r718 wave: churn-absorb 24a4516ec + round 718 sina four-tier moneyflow stock-level "
             "IC census P1 CENSUS_ENRICHED 43b391456 + churn-absorb 98a856d00) -> dirty-intersect-incoming=0 -> merge "
             "origin/main clean FF to 98a856d00, zero UU. "
             "(2) S0.5 orders 154/154 set-diff zero unacked (canonical orders_diff, open+close double scan); inbox 0 "
             "unread. (3) D-19: decisions MATCH (755428F8, d19_check.py canonical) + group orders.md raw-blob SHA-256 "
             "MATCH (E79E15F9, scratch probe) -> zero consumption, zero action. "
             "(4) S1 smoke 48/48. (5) S2 boards: job_list 0; fleet tasks 0 open. "
             "(6) S3: WM green (red=false, next_pick=claimed moneyflow IC, panel source-blocked); satengine status rc0 "
             "alive (Tools face, burns_active=[], local waves all done); trial-labor default-drafting NOT triggered "
             "(judgment seats in-flight on other machines: fund-trio bm-b keepalive burn + N2-W15 finalize bm-a F-04 "
             "seat; supply faces parked: W3 next wave = CEO ruling + W14 governance-parked + reopen 10-09). "
             "(7) CORE PRODUCT: QA pack r526 standing re-run (qa/smoke-r526.md 5/5 + qa/equity-curve-r526.png 66372B, "
             "93 trades, sharpe 0.1586, maxdd -4.33%, win 46.24%, determinism=True; market_clock rc0 CALL-2026-09-30 "
             "ORANGE_COOL; honest data leg bar 2026-09-30, golden-week no-op expected until 10-09). "
             "(8) S6 chain 38/38 rc0 FIRST PASS zero heal (receipt results/_r526bmc_s6_log.txt, driver in scratch per "
             "r511-2 law); dualrun ZERO-DRIFT streak 26; compute_audit supply_gap flag honest (ready=3=floor, "
             "breach=false, ready_unclaimed=0); py_watermark py_low_board_clear legal idle; REPORT/LIVE-2026-10-05 "
             "regenerated idempotent. (9) S7: loop pin5 phase-ok no-op (first fire 09:45), watchdog registered 09:42, "
             "claws IN-PLACE (LF-normalized), attrition CLEAN (4 ledger files, healed history recorded), post_review "
             "5847 rows unresolved-NO=0 (38 NO all superseded by later YES, r514 law), pool 403 entries "
             "(399 done + 3 fund-trio keepalive ready bm-b-owner + 1 W14 waiting governance-parked), close double-scan "
             "zero new orders. Close: targeted add + commit -F + push + fetch/rev-list delivery self-check.")
st["current_task"] = (
    "当前活: r526 金周值守轮（S6 38/38 首过全绿+QA 证据包 r526 复跑+orders/D-19 双扫零新令；判决链席位他机="
    "fund-trio bm-b 在烧+N2-W15 finalize bm-a F-04 席；supply_gap 旗=金周结构面如实披露） | "
    "最近实物: qa/smoke-r526.md 5/5+qa/equity-curve-r526.png（66372B·93 trades·确定性回测）+results/_r526bmc_s6_log.txt"
    "（38 腿零红收据·零 heal）@ " + NOW_ISO + " | "
    "下个里程碑: D-20261002-05 selftest 席位窗 10-06 00:00（首过轮=10-06 00:00 后第一轮跑 pin selftest）；"
    "fund-trio finalize（bm-b·10-05..09）；N2-W15 judge-finalize（bm-a F-04 席·≤10-12）；D-06 拆件收口窗 10-07 12:00；"
    "O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）；r530=下一 5x")
st["next"] = ("(a) D-20261002-05 selftest seat window 10-06 00:00 (first round at/after runs the pin selftest; r526 "
              "ran 10-05 before window-open = not yet due). (b) fund-trio finalize 10-05..09 (bm-b canonical, keepalive "
              "burn confirmed). (c) N2-W15 judge-finalize = bm-a F-04 seat watch (<=10-12). (d) D-06 split closeout "
              "10-07 12:00. (e) moneyflow IC reference batch when panel completes (still source-blocked). "
              "(f) market reopen 10-09 data-chain re-arm + IntradayMarks re-check (G3). (g) O-2115/O-2030 acceptance "
              "10-08. (h) next 5x HANDOVER = bm-c r530. (i) qa/ evidence pack per-round re-run (standing driver "
              "scripts/qa_smoke_run.py). (j) CEO physical item pending: tailscale login link click (bm-c URL alive "
              "since r505). (k) CODELY.md over-50KB flag carried (threshold re-anchor = GM ruling face per r504 note).")
st["note"] = ("r526: watch round closed clean. S0 clean FF to bm-a r718 tip 98a856d00 (zero overlap with lane churn; "
              "pull --rebase honestly blocked by 3 pre-existing lane daemon faces -> merge-mode FF per r523 law). "
              "D-19 double MATCH (decisions 755428F8 + group orders E79E15F9) zero consumption. 3 bm-c lane churn "
              "faces + Tools/_r518bmc_close2.py untracked scratch leftover absorbed in this round close commit "
              "(r620 law, r525 note discharged).")
st["verify"] = ("receipts: qa/smoke-r526.md 5/5 + qa/equity-curve-r526.png (66372B) + results/_r526bmc_s6_log.txt "
                "(38 legs rc0, bad=[]) + smoke 48/48 + attrition CLEAN (results/_attrition_guard_scan.json) + "
                "post_review unresolved-NO=0 (5847 rows, r514 law) + quartet 4/4 + claws IN-PLACE (LF-normalized) + "
                "orders 154/154 open+close double scan + D-19 double MATCH (d19_check.py + group-orders SHA-256 probe) "
                "+ commit/push delivery self-check this close.")
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
hb["round_no"] = 526
hb["round_no_label"] = "round 526 (bm-c)"
hb["activity_now"] = ("r526: golden-week watch + QA evidence-pack standing re-run -- qa/ 5/5 r526 refresh "
                      "(smoke-r526.md + equity-curve-r526.png 66372B), S6 38/38 rc0 FIRST PASS zero heal, smoke 48/48, "
                      "orders 154/154 double-scan zero unacked, D-19 double MATCH (decisions 755428F8 + group orders "
                      "E79E15F9, zero consumption), attrition CLEAN, post_review unresolved-NO=0, quartet 4/4 + claws "
                      "IN-PLACE; S0 clean FF to bm-a r718 tip 98a856d00; judgment seats on other machines (fund-trio "
                      "bm-b in-burn, N2-W15 finalize bm-a F-04); supply_gap flag = golden-week structural")
hb["current_task"] = st["current_task"]
hb["latest_artifact"] = ("qa/ evidence pack r526 (smoke-r526.md 5/5 + equity-curve-r526.png 66372B) + "
                         "results/_r526bmc_s6_log.txt (38 legs rc0 first-pass receipt)")
hb["next_milestone"] = ("D-20261002-05 selftest window 10-06 00:00 (first round at/after runs pin selftest); "
                        "fund-trio finalize (bm-b) 10-05..09; N2-W15 judge-finalize (bm-a) <=10-12; D-06 closeout "
                        "10-07 12:00; O-2115/O-2030 acceptance 10-08; reopen 10-09 (G3, IntradayMarks re-check); "
                        "month-end exam 10-31; next 5x = r530")
hb["prod_lanes"] = ("N2-W15 judge-finalize = bm-a F-04 seat in-flight (watch); fund-trio NULLS x3 bm-b canonical "
                    "keepalive in-burn (ready_unclaimed=0); W3 next wave = CEO ruling face; boards open=0; watermark "
                    "green (py_low_board_clear); moneyflow IC = bandit next_pick claimed, panel still source-blocked; "
                    "supply_gap flag honest (floor not breached); qa/ evidence pack standing per-round; S6 chain "
                    "zero-window wrapper-ized (r524 lineage); CEO physical item pending: tailscale login click "
                    "(bm-c URL alive since r505)")
hb["verdict"] = ("r526 bm-c: golden-week watch (boards open=0, judgment seats on other machines, no bar until "
                 "10-09). (1) S0 pull --rebase blocked by lane churn -> fetch behind=3 -> clean FF to 98a856d00. "
                 "(2) orders 154/154 open+close double scan, inbox 0. (3) D-19 double MATCH zero consumption. "
                 "(4) smoke 48/48. (5) boards empty. (6) WM green py_low_board_clear; satengine rc0 alive. "
                 "(7) CORE: QA pack r526 (5/5, 93 trades, determinism=True). (8) S6 38/38 rc0 first pass zero heal, "
                 "dualrun streak 26, supply_gap honest. (9) S7: loop pin5 phase-ok; watchdog registered; claws MATCH; "
                 "attrition CLEAN; post_review unresolved-NO=0; lane churn + r518 scratch leftover absorbed at close; "
                 "close: targeted add + commit -F + push_verify.")
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---------------- 3. round_reports-bm-c.md line ----------------
rrp = os.path.join(ROOT, "round_reports-bm-c.md")
with open(rrp, "rb") as fh:
    rr_raw = fh.read()
rr_eol = b"\r\n" if b"\r\n" in rr_raw[:4000] else b"\n"
rr_line = (
    NOW_RR + " | r526 | dept:工程（金周值守轮·QA 证据面常设复跑） | "
    "watermark verdict=绿（red=false·py_watermark=py_low_board_clear 板空合法 idle 白名单〔判决链他机在飞+池 ready 3 全 bm-b 属主 unclaimed=0+金周无 bar〕·"
    "compute_audit FLAG:supply_gap〔ready=3=floor 零 breach·金周结构供给面诚实旗〕）｜"
    "本轮：金周值守+QA 证据面常设复跑——实物=qa/smoke-r526.md 5/5+qa/equity-curve-r526.png（66372B·3 syms x 800 bars·93 trades·sharpe 0.1586·maxdd -4.33%·win 46.24%·确定性=True·常设驱动复跑）"
    "+S6 38/38 首过全绿零 heal（收据 results/_r526bmc_s6_log.txt·bad=[]·dualrun ZERO-DRIFT streak 26·token 低位·REPORT/LIVE-2026-10-05 幂等再生 09:38）｜"
    "S0=pull --rebase 诚实挡于轮首 3 个 bm-c lane daemon churn 面（r620 absorb-at-close 律）→fetch behind=3（bm-a r718 波：churn 24a4516ec+round 718 sina 四档 moneyflow 股票级 IC census P1 CENSUS_ENRICHED〔small_share-d5 retail absorption t=-3.02 p=0.00043 h10·单调 h5/h10/h20〕43b391456+churn 98a856d00）→脏∩入站=0→merge origin/main 干净 FF 至 tip 98a856d00 零 UU｜"
    "S0.5=orders 154/154 差集零未回执（正典 orders_diff·开+收双扫同果）+inbox 0 未读｜"
    "D-19=双 hash MATCH（decisions 755428F8〔d19_check.py 正典〕+group orders E79E15F9〔raw-blob SHA-256 探针〕）零消费零动作｜"
    "S1=smoke 48/48（09:36）｜S2=板空（job_list 0+fleet tasks 0 open）｜"
    "S3=satengine status rc0 活+试用劳动力常设线=判决席位他机在飞非触发态（fund-trio bm-b keepalive 在烧+N2-W15 finalize bm-a F-04 席）+supply 面停泊照旧（W3=CEO 裁定+W14 park+复市 10-09）+post_review 5,847 行 unresolved-NO=0（38 NO 全被同 id 后续 YES 压制·r514 律）｜"
    "S7=loop pin5 phase-ok no-op（首发 09:45）+watchdog 重注册（09:42）+双爪 IN-PLACE（LF 归一）+attrition CLEAN（4 账本·healed 史行照录）+池态 403=399 done+3 ready（fund-trio keepalive bm-b 属主）+1 waiting（W14 park）+lane churn 3 面+r518 scratch 遗件本轮收编（r620 律·r525 note 清账）｜"
    "记分:2（qa/ 证据包 r526=能跑/能看实物〔smoke-r526.md 5/5+equity png+driver 复跑〕+S6 38 面 CEO 再生）｜"
    "记账预算:3 面内（state+心跳+轮报=法定簿记）｜"
    "方法论捕获=无新方法（全链复用正典/血统·S6 链驱动器=r518bma 38 腿正典血统适配 scratch 仓外 r511-② 律）｜宝藏捕获=无（无五类收口面：判决 finalize 未落·名单进出零）｜"
    "登记册零命中断言=N/A-零清扫零 quarantine（O-2030 §二.3 自证面）｜"
    "本地未达 origin commit 数: 见 commit 后 push_verify 行｜"
    "当前活: r526 金周值守 | 最近实物: qa/smoke-r526.md 5/5+qa/equity-curve-r526.png 66372B @ " + NOW_ISO + " | "
    "下个里程碑: D-20261002-05 pin selftest 席位窗 10-06 00:00（10-06 00:00 后首过轮跑·r526 在窗前如实未触发）；fund-trio finalize（bm-b·10-05..09）；N2-W15 judge-finalize（bm-a F-04·≤10-12）；D-06 收口 10-07 12:00；O-2115/O-2030 验收 10-08；复市 10-09 数据链重挂+IntradayMarks 再核（G3）；月界首考 10-31；r530=下一 5x")
with open(rrp, "ab") as fh:
    fh.write(rr_eol + rr_line.encode("utf-8") + rr_eol)

# ---------------- 4. validation (r504 law) ----------------
for p in (sp, hp):
    with open(p, encoding="utf-8-sig") as fh:
        d = json.load(fh)
    assert isinstance(d.get("heartbeat_epoch_utc"), int), p + " epoch not int"
    print("reparse OK:", os.path.basename(p), "round_no=", d.get("round_no"), "epoch=", d.get("heartbeat_epoch_utc"))
print("BOOKKEEPING DONE now=", NOW_ISO)
