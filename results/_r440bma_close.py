# r440 bm-a close: round-report rows (r438/r439 posthumous backfill + r440) + state numbering repair + heartbeat.
# Encoding-safe UTF-8 writes per PS-encoding pit family; run once from repo root.
import json
import time

NOW = "2026-09-29T18:2x+08:00"
NOW_FULL = "2026-09-29T18:2x:00+08:00"
EPOCH = int(time.time())
CLOCK = time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] + ":" + time.strftime("%z")[3:]

R438 = ("| 2026-09-29 17:2x | r438（死后补账·S7 前会话亡） | A158-TSGATE-P1 314 门普查烧批落地：1,724 员·PASS 48/PARTIAL 142/FAIL 117/NA 7·"
        "五员 top=STD20_q90(5/5 OOS 正)+RSQR20_q90 | 正典=commit 44c5fc747(prereg FROZEN)+ad57d5782(遗产吸收)"
        "+results/a158_tsgate_p1.json+research/A158_TSGATE_P1.md | 已被 GATE-RECHECK-A158 消费（r439） |")
R439 = ("| 2026-09-29 17:5x | r439（死后补账·S6 中段会话亡） | GATE-RECHECK-A158 独立复核落地：48 PASS→27 簇 27 代表·"
        "RECHECK-CONFIRM 17/CLUSTER-COLLAPSED 21/FAIL 10·SUM*/VSUM* 构造恒等塌缩·17 门机读库+10 降格 C1 | "
        "正典=commit fa5b3cd73(prereg FROZEN)+07bbfdd6e(verdicts)+results/gate_recheck_a158.json+research/A158_GATE_RECHECK.md | "
        "已被 bm-c r231 GATE-TIMING-PRESCREEN 消费（85 格 19 SURVIVE） |")
R440 = ("| 2026-09-29 18:2x | r440 | WM-VERDICT:绿（red=false；probe 18:11 py_low_board_clear 合法闲=板 0 open/bandit 0/池 120/120 done；"
        "audit FLAG supply_floor ready 0<3=W10 候选 gated 于 bm-c 草作者·W9 收口 18:04 触发冻结窗已开·bm-a 抢跑即违撞批三查律故让路）。"
        "当前活=r438/r439 死窗遗产吸收+撞批让路+S6 收口；最近实物=DECISION_CHAIN_BENCHMARKS.md A2/A6/A7 三臂判决行回写"
        "（commit 523580f3b→rebase 后 368c4bc0f·18:1x）；下个里程碑=①bm-c W10 收编冻结与 v4 臂预注册观察（窗≤48h）"
        "②09-29 bar 落地→触发链（REGIME_GUARD enforce+t35/t24）③10-01 月首轮三件套（science_audit+monthly_briefing+self_review）。"
        "did：S0 11 件死窗遗产吸收（commit e9ad7487a→rebase 1-UU=compute_audit canon resolve 203 行 union→reconcile ZERO-DRIFT→push）；"
        "S0.5 orders 122/122 文件名级差集 0 未回执+decisions D-20260929-07 产品优先律=loop prompt 顶部块已接线回执合规；"
        "S1 smoke 26/26；S2 双板 0 open；S3=A158 17 门择时初筛起草中被撞批三查拦下（bm-c r231 18:02:44 同窗冻结+30.4s 烧完 85 格）"
        "→按 fleet/README §4 后到让路零重复件→转产出 v4 臂表三判决行回写（A2 线关闭 r433/434 CORRSOURCE·A6 as-spec'd 判负 r437 探针·"
        "A7 初筛 0/10 r435/436）=r437 next(e) 指针债窗内清偿；A7 死窗遗产核实=已由 r436 pre commit 4c6970a29 落地无欠账；"
        "S4 坑律=撞批三查律入 CODELY.md；S6 29 腿全 rc=0（无新 bar→live.paper/t35_open_fill/t24_prospect 三触发腿合法跳过；"
        "moneyflow spawn rank pass 自愈续；ah spawn refresh；CEO 面 LIVE-2026-09-29/REPORT-0929/dashboard/scorecard 全再生；token delta 0）；"
        "S7 schtasks Loop Running pin 合格+Watchdog Ready+state 编号修复 438→441（r438/r439 死于 S7 前·按 git round 标签接续）。"
        "verify：smoke 26/26；S6 腿 rc 全 0；dualrun ZERO-DRIFT 120 条 streak 21/3；WM py_low_board_clear；orders 122/122；"
        "D-07 回执；心跳 epoch int 自证过 | 下轮=里程碑①②③观察窗+10-01 月首轮三件套备件 |")

with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write("\n" + R438 + "\n" + R439 + "\n" + R440 + "\n")

# ---- state-bm-a.json: numbering repair 438 -> 441 (r440 done; r438/r439 died pre-S7) ----
with open("state-bm-a.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 441
st["round"] = 440
st["loop_round"] = 440
st["last_round"] = 439
st["last_round_ts"] = "2026-09-29T17:51:10+08:00"
st["did"] = ("r440: S0 absorbed dead r438/r439 resident state (11 files) + rebase 1-UU canon-resolved + ZERO-DRIFT; "
             "orders 122/122 zero unacked; D-20260929-07 receipt (product-priority law wired in loop prompt); "
             "PRODUCT = v4 arm table 3 verdict rows (A2 LINE_CLOSED r433/434 CORRSOURCE BETA_SAME_SOURCE + alpha-insig; "
             "A6 as-spec'd negative r437 probe; A7 prescreen 0/10 r435/436) = r437 next(e) debt closed in-window; "
             "A158 17-gate timing prescreen YIELDED to bm-c r231 per anti-dup law (collision caught at seed-registry "
             "live-read pre-draft, zero duplicate written, pit entry '撞批三查律' landed in CODELY.md); "
             "S6 29 legs rc=0 (no new bar: live.paper/t35_open_fill/t24_prospect legit-skip; CEO faces regen); "
             "state numbering repaired 438->441 (r438/r439 died pre-S7, git round labels authoritative)")
st["verify"] = ("smoke 26/26; S6 legs all rc=0; dualrun ZERO-DRIFT 120 entries streak 21/3; "
                "audit FLAG supply_floor ready 0<3 honest (W10 gated at bm-c draft-author, freeze window open, "
                "not a fault); WM py_low_board_clear legal idle; orders 122/122; "
                "schtasks Loop Running pin ok + Watchdog Ready; heartbeat epoch int self-verified")
st["next"] = ("r441: (a) bm-c W10 adoption-freeze + v4 arm prereg watch (window <=48h from 18:04); "
              "(b) 09-29 bar landing -> trigger chain (REGIME_GUARD enforce + t35/t24 legs); "
              "(c) moneyflow panel self-heal watch -> IC batch when complete; "
              "(d) 10-01 month-first triple (science_audit + monthly_briefing + self_review); "
              "(e) eCloud reconfig = CEO physical item (standing); next 5x = bm-a r445 HANDOVER check")
st["last_round_at"] = NOW_FULL
st["current_task"] = "r440 closed: dead-window harvest + anti-dup yield + arm-table verdict rows + S6 green; next=r441 watch faces"
st["updated"] = NOW_FULL
st["last_ts"] = NOW_FULL
with open("state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-a.json ----
with open("fleet/machines/bm-a.json", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = NOW_FULL
hb["current_task"] = st["current_task"]
hb["verdict"] = ("r440 ok: dead-session harvest + ZERO-DRIFT + anti-dup yield (bm-c r231) + arm-table verdict rows + "
                 "S6 29 legs green; WM py_low_board_clear legal idle; supply_floor breach = W10 gated at bm-c "
                 "(freeze window open, in-flight response)")
try:
    import psutil
    hb["cpu_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
    hb["free_ram_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["cpu_util_pct"] = hb["cpu_pct"]
except Exception:
    pass
try:
    with open("results/compute_audit.json", encoding="utf-8") as f:
        au = json.load(f)
    mem_used = au.get("gpu", {}).get("mem_used_mb")
    if isinstance(mem_used, (int, float)):
        free_mib = int(12282 - mem_used)
        hb["gpu_free_vram_mib"] = free_mib
        hb["gpu_free_vram_gb"] = round(free_mib / 1024, 1)
except Exception:
    pass
hb["round_no"] = 441
hb["round"] = 440
hb["loop_round"] = 440
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
hb["task"] = "r440-deadwindow-harvest-antidup-yield-armtable-verdicts"
with open("fleet/machines/bm-a.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- self-verification ----
with open("fleet/machines/bm-a.json", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 with T and offset"
assert len(hb2["orders_ack"]) == 122, f"orders_ack expected 122, got {len(hb2['orders_ack'])}"
with open("state-bm-a.json", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 441 and st2["round"] == 440
print("close-ok: report rows +3, state 438->441 (round=440), heartbeat epoch=%d clock=%s ack=122"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"]))
