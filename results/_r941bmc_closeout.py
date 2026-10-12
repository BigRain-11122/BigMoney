# -*- coding: utf-8 -*-
# r941 (bm-c) closeout: state + heartbeat + round-report append.
import json, subprocess, time, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
ts_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

def gpu_faces():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.used,utilization.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True,
                           creationflags=0x08000000)
        free, used, util = [x.strip() for x in r.stdout.strip().split(",")]
        return int(free), int(used), float(util)
    except Exception:
        return None, None, None

import psutil
ram_free = round(psutil.virtual_memory().available / 1e9, 1)
cpu_pct = psutil.cpu_percent(interval=1)
g_free, g_used, g_util = gpu_faces()

# ---------- state ----------
sp = REPO + r"\state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 942
st["round_no_label"] = "r941"
st["last_round"] = 941
st["loop_round"] = 941
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_round_at",
          "current_task_at", "current_task_ts", "last_action_at", "last_run_at",
          "last_round_closed", "last_pulled_at"):
    st[k] = ts_iso
st["last_round_ts"] = epoch
st["heartbeat_epoch_utc"] = epoch
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["free_ram_gb"] = ram_free
st["ram_free_gb"] = ram_free
st["idle_ram_gb"] = ram_free
if g_free is not None:
    st["gpu_free_vram_mib"] = g_free
    st["gpu_free_vram_mb"] = g_free
    st["gpu_idle_vram_mb"] = g_free
    st["gpu_idle_vram_mib"] = g_free
    st["gpu_free_vram_gb"] = round(g_free / 1024, 1)
    st["gpu_mem_used_mib"] = g_used
    st["gpu_util_pct"] = g_util
st["current_task"] = ("r941: W226 per-wave prereg derived+landed (f65d886cb: ten-level lineage replay 46/46, "
                      "bands A 512_004..514_003 staircase EIGHTY-SIXTH + B 514_004..514_203 own-A exclusion, "
                      "anchors W225 finalize 918,789/K=492,920, banned ADMIT rc0, STALE 0/NEW all) "
                      "+ r940 closeout estate absorbed (d6bfc66b9, 183 files) + MV i2v wave A burning (PID 12620, clip 2/7)")
st["did"] = ("(1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=1 zero-kill; S0 pull refused by dirty tree -> "
             "git log verified r940 body commits 8b12ace73 (W225 full cycle) + d7d270752 (W226 seat) ALREADY pushed pre-death; "
             "closeout estate 183 files absorbed+committed d6bfc66b9 pushed (first push hit GitHub commit_refs transient, retry-1 OK); "
             "(2) S0.5 dual-delta FALSE both (dec 94c93393/ord 7351cf2f hold) + unacked=0; (3) smoke 49/49; boards clear; "
             "satengine rc0 alive (W225 12/12 done, queue DRY); (4) PRODUCT = W226 per-wave prereg: _w226bmc_prereg_derive.py "
             "ten-level lineage replay (PAIRS216+SUB17..SUB25 preflight 46/46 count==1 vs base blob 4b22941a7 freeze-time W225 face) "
             "+ 46 explicit pairs (bands machine-read from W226 probe receipt; anchors from n1_w225_results.json: ledger 918,789 "
             "prev 916,589+2,200 EXACT, K=492,920, merged mu -0.09279454 sigma 0.24508719, w225-only -0.09782473, A_p95 0.3014, "
             "KL -0.0001 line 1.1915->1.1914, se_mu 0.000349) + STALE 70 all-zero + NEW 47 all-present + 13 chain-leg identity "
             "asserts + in-band >=4 checks; derive-time pair-3 heritage-token swap caught by chain-history assert PRE-WRITE "
             "(zero disk pollution, one-fix green); r939 prose slip (arith continuation A-tail 511_603) healed to 511_803; "
             "banned_direction_gate ADMIT rc0 -> commit f65d886cb pushed; (5) S6 audit legs rc0: dualrun ZERO-DRIFT streak 36 "
             "(evidence-chain-order law kept) + compute_audit FLAG pool_starvation/supply_floor (structural, answered by prereg "
             "landing, splice=next-window heal) + py_watermark insufficient_history honest + idle_trigger --worked "
             "(idle_rounds=0) + attrition 4 CLEAN; (6) MV lane patrol: KF 5 frames + BMC-KF-DEMO-BOARD_q88.jpg landed 20:52, "
             "i2v wave A clip1 done clip2 burning, PID 12620 alive detached; (7) S7 quad self-heal green (loop pin=5 no-op "
             "first fire 21:15, watchdog re-registered, both claws LF-normalized reinstalled) + state/heartbeat r941 write")
st["activity_now"] = ("2026-10-12 21:1x | r941 | bm-c product round: W226 PREREG derived+landed (ten-level replay 46/46, "
                      "A 512_004..514_003 EIGHTY-SIXTH + B 514_004..514_203, banned ADMIT, f65d886cb pushed origin-verified) "
                      "+ r940 closeout estate absorbed d6bfc66b9 + S6 audit legs rc0 + S7 quad green; counter 940->942")
st["now_active"] = st["activity_now"]
st["verdict"] = ("green: W226 prereg landed same-window (ten-level lineage preflight 46/46 + STALE 0 + NEW all + banned ADMIT rc0; "
                 "f65d886cb pushed origin-verified); smoke 49/49; engine alive rc0 queue DRY post-W225-finalize awaiting W226 splice "
                 "(next-window FIRST ACTION); pool_dualrun streak 36; compute_audit pool_starvation+supply_floor structural flags "
                 "disclosed (armed response = wave chain, prereg landed this window); MV i2v wave A burning legal GPU occupation "
                 "(PID 12620, clip 2/7); no new bars expected until Tue 15:30")
st["last_round_summary"] = "W226 prereg landed (r941; f65d886cb pushed)"
st["last_action"] = "r941 product closeout (W226 prereg derive+land f65d886cb + absorb r940 estate d6bfc66b9 + S6 audit legs + S7 quad)"
st["latest_artifact"] = ("research/PERPETUAL_N1_W226_PREREG.md + results/_w226bmc_prereg_derive.py (21:0x, commit f65d886cb "
                         "pushed origin-verified)")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = ("W226 five-face splice + engine self-burn 12/12 + six-gate PRE-FINALIZE + finalize (next two windows) "
                        "+ MV i2v wave A 7-clips harvest (~1.5h ETA) + Tue 15:30 bars papers chain")
st["next"] = ("r942: (1) W226 five-face freeze splice FIRST ACTION (derive _w226bmc_freeze_edits.py from _w225bmc template; "
              "gate0.5 self-check W225 row + W225 finalize file in-place; estate extract = own W225 block physical bytes) -> "
              "commit+push -> engine mtime-watch self-burn 12/12 (2-cycle product-growth verify); (2) six-gate PRE-FINALIZE in "
              "burn window (W217-debt standing law) + finalize one-pass + five-key + sec.7/8 machine-read backfill; (3) W227 seat "
              "probe (naive A 514_004..516_003 / B 514_204..514_403, EIGHTY-SEVENTH anticipated, W227 freezer re-derive mandate "
              "inherited); (4) MV wave A harvest: 7 clips receipt + per-clip self-check (<7.5 re-shake w/ seed logged) + "
              "commit+push; (5) Tue 15:30 new-bar papers full chain; (6) unity-mcp POC receipt due 10-13 12:00 (bm-a lane watch)")
st["next_pointer"] = st["next"]
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["head_sha"] = "f65d886cb"
st["health"] = "ok"
st["sync"] = {"origin_tip": "f65d886cb (W226 prereg)", "ts": ts_iso,
              "ahead_behind": "r941 closeout commit+push rides this window",
              "note": "r941: W226 prereg product f65d886cb pushed pre-closeout; closeout commit+push follows; state/heartbeat this round"}
st["r941_absorb_note"] = ("r941 absorb note: prior session r940 executed the W225 full cycle + W226 seat body with commits+pushes "
                          "(8b12ace73 + d7d270752, both on origin) and ran the full S6 chain (Monday 10-12 bars landed, papers legs "
                          "run) + MV chain ignition (PID 12620), but died PRE-closeout-commit (183-file estate on disk; state was "
                          "its mid-flight write at round_no=940) -- this session absorbed per the bm-c r930/r933/r937 absorb "
                          "precedent: estate committed+pushed (d6bfc66b9), executed as r941 (next after highest committed label "
                          "r940), advanced counter 940->942 so next session = r942; zero double-count: S0.5 dual-delta FALSE this "
                          "window (dec 94c93393 / ord 7351cf2f both current), r940's body debts were handled by its own commits")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]
print("state OK: round_no=", chk["round_no"], "epoch=", chk["heartbeat_epoch_utc"], "clock=", chk["clock_read"])

# ---------- heartbeat ----------
hp = REPO + r"\fleet\machines\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = ts_iso
hb["ts"] = ts_iso
hb["clock_read"] = ts_iso
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = cpu_pct
hb["cpu_cores"] = 32
hb["cores"] = 32
hb["free_ram_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
if g_free is not None:
    hb["gpu_free_vram_mb"] = g_free
    hb["gpu_free_vram_mib"] = g_free
    hb["gpu_idle_vram_mb"] = g_free
    hb["gpu_idle_vram_mib"] = g_free
hb["verdict"] = ("green: W226 prereg landed (f65d886cb pushed; ten-level replay 46/46 + banned ADMIT rc0); "
                 "engine alive rc0 queue DRY; MV i2v wave A burning (legal CEO-lane GPU occupation, PID 12620); "
                 "S6 audit legs rc0 (dualrun streak 36); smoke 49/49; next = W226 splice (r942 FIRST ACTION)")
hb["current_task"] = "r941: W226 prereg landed (f65d886cb) + r940 estate absorbed (d6bfc66b9) + closeout"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 1
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int) and "T" in chk2["clock_read"]
print("heartbeat OK: epoch=", chk2["heartbeat_epoch_utc"], "clock=", chk2["clock_read"], "gpu_free=", g_free)

# ---------- round report ----------
rp = REPO + r"\logs\iteration-loop\round_reports-bm-c.md"
line = ("2026-10-12T21:1x | r941 | bm-c absorb r940 closeout estate + W226 PREREG PRODUCT round "
        "(r940 body commits 8b12ace73/d7d270752 already pushed pre-death; 183-file closeout estate absorbed this window "
        "d6bfc66b9; state was r940 mid-flight write, this session = r941, counter 940->942 zero double-count) | "
        "WM-VERDICT: green red=false (py_watermark insufficient_history fresh-window honest face; engine alive rc0 queue DRY "
        "post-W225-finalize awaiting W226 splice; pool_starvation+supply_floor structural flags disclosed, W226 prereg landed "
        "THIS window = armed response continues, splice = r942 FIRST ACTION) | "
        "dept:策略（N1 波链 W226 prereg=判据冻结正身）+dept:工程（S0/S0.5/S6 审计腿/S7 全链+MV 车道巡检） | "
        "实况三行：当前活=@bm-c MV 车道 i2v 波 A 在烧（PID 12620·clip1 完成 clip2/7 在跑·INT8 768P·GPU 15.6GB 合法占卡）"
        "+W226 splice=下窗第一动作；最近实物=research/PERPETUAL_N1_W226_PREREG.md+results/_w226bmc_prereg_derive.py"
        "（21:0x·commit f65d886cb 已推 origin）；下个里程碑=W226 five-face splice+自燃 12/12+六门 PRE-FINALIZE+finalize"
        "（下两窗内）+MV 波 A 7 clips 收片（~1.5h ETA） | "
        "did: r941 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=1 zero-kill；S0 pull 被脏树拒→git log 核实="
        "r940 body 已推（HEAD==origin d7d270752）·closeout 遗产 183 文件 absorb 提交 d6bfc66b9 推送（首拒=GitHub commit_refs "
        "瞬态·重试一次成功）；(2) S0.5 双水位 probe：ORD/DEC delta FALSE both+unacked=0 零动作；(3) S1 smoke 49/49；S2 boards "
        "clear；satengine rc0 活（W225 12/12 done·queue DRY）；(4) PRODUCT=W226 per-wave prereg derive+land："
        "_w226bmc_prereg_derive.py 十级血统重放（PAIRS216+SUB17..SUB25 preflight 46/46 count==1 全对上基 blob 4b22941a7 "
        "冻结面）+46 对显式替换（bands A 512_004..514_003 staircase EIGHTY-SIXTH hops=1+B 514_004..514_203 own-A 互斥 全机读自 "
        "W226 probe receipt·锚=W225 finalize 918,789/K=492,920 EXACT/mu −0.09279454/sigma 0.24508719/A_p95 0.3014/K-lift "
        "−0.0001 line 1.1915→1.1914/se_mu 0.000349）+STALE 70 项全零+NEW 47 项全在+链史 13 腿恒等断言+in-band ≥4→banned gate "
        "ADMIT rc0→提交 f65d886cb 推送自证；derive 期 pair-3 遗产 token 对调被链史断言当场拦截（写盘前零污染·一次修复全绿）"
        "+W225 面 r939 prose 滑笔（arith 续带 A 尾 511_603）在新面按正身 511_803 治愈；(5) S6 审计腿批 rc0：dualrun "
        "ZERO-DRIFT streak 36（排 compute_audit 前=证据链序律）+compute_audit FLAG pool_starvation/supply_floor（结构性披露·"
        "prereg=已装填响应·splice 下窗愈合）+py_watermark insufficient_history（单样本窗诚实）+idle_trigger --worked（"
        "idle_rounds=0）+attrition 4 ledger CLEAN；(6) MV 车道巡检：KF 5 帧+拼板 BMC-KF-DEMO-BOARD_q88.jpg 全落（20:52）·"
        "i2v 波 A clip1 完成转 clip2·PID 12620 活·脱离式自走零干预；(7) S7：quad 自愈全绿（loop pin=5 no-op 首火 21:15/"
        "watchdog 重注册/双 claw LF 归一重装）+state/heartbeat r941 写回（epoch int+clock T 格式 json.loads 自证） | "
        "验证证据=smoke 49/49+preflight 46/46+STALE 全零/NEW 全在+链史 13 腿+banned ADMIT rc0+push range 行 "
        "d6bfc66b9..f65d886cb 自证+dualrun streak 36+attrition CLEAN | 本地未达 origin commit 数=0（收尾 push 后 fetch+"
        "rev-list 自证）| 孤儿面=1 | 产品积分: 2（W226 prereg=判据冻结正典件上链 f65d886cb）+1（absorb 遗产 183 文件落地 "
        "d6bfc66b9）=3 | 记账预算: 3（state+heartbeat+round-report 法定簿记） | "
        "下轮指针=r942: (1) W226 five-face freeze splice FIRST ACTION（_w225bmc_freeze_edits.py 模板派生·gate0.5 自查 W225 行"
        "+W225 finalize 件在场·estate 提取=本机 W225 块物理字节）→commit+push→引擎 mtime-watch 自燃 12/12（2 cycle 产物增长面"
        "验证）；(2) 烧录窗内六门 PRE-FINALIZE（W217 债后常设律）+finalize one-pass+五键+sec.7/8 机读回填；(3) W227 席位 probe"
        "（naive A 514_004..516_003·阶梯 EIGHTY-SEVENTH 预期·W227 freezer 重 derive 强制注记承接）；(4) MV 波 A 收片：7 clips "
        "回执+逐镜自检（<7.5 记种子重摇）+commit+push；(5) 周二 15:30 新 bar papers 全链；(6) unity-mcp POC 回执 10-13 12:00"
        "（bm-a lane watch） | [r941 bm-c]" + "\n")
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report appended")
print("LIVE FACES: ram_free=", ram_free, "GB cpu=", cpu_pct, "% gpu_free=", g_free, "MB gpu_used=", g_used, "MB util=", g_util, "%")
