# -*- coding: utf-8 -*-
"""r810 bm-a S7 closeout faces writer (fresh-read-modify-write per multi-writer
append-only law; single-file python surgery, zero replace-tool on ledgers)."""
import json, time, datetime, io, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
iso_short = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

# --- 1) HANDOVER 5x window entry (r801-r810, r805 stamp missed disclosed) -----
hand = io.open("research/HANDOVER.md", encoding="utf-8", newline="").read()
assert "round 810 五倍数核对" not in hand, "5x entry already present"
assert hand.endswith("\n"), "HANDOVER must end with newline before append"
h_entry = (
    "> bm-a round 810 五倍数核对（2026-10-07 05:5x·增量窗 r801-810 十轮·OVERDUE-BACKLOG DISCLOSED: "
    "r805 5x stamp missed（r805 窗=W167 freeze 落地窗·state 精确续作点已写但 5x 条漏记）——本条覆盖全窗）："
    "增量窗=r801-810 bm-a 面——r801〔W167 seat 链：pre-seat probe rc0 ADMIT A 382_204..384_203 阶梯 26 例 E36"
    "+seat MSG-0056 push 982424c5f+band gate ADMIT〕；r802/r803〔死会话·r804 双收〕；"
    "r804〔W167 prereg build 落地 xform W166→W167·push 02617eb93〕；"
    "r805〔W167 freeze LANDED f61835690 五面注册·157th wave bm-a 83rd owned·本窗 5x 漏记如实披露〕；"
    "r806〔W167 finalize one-pass ledger 770,612→772,812/K 363,120→365,320 双投影精确命中"
    "+W168 seat 链首发 probe+seat MSG-0259 push ceaf58908+gate ADMIT〕；"
    "r807〔W168 prereg build xform W167→W168 46 针断言·push 62bc99927·dec 水位消费 acc32216"
    "（D-20261007-01/02/03 零本司派单）·CODELY 主件判据回线 27,396B〕；"
    "r808〔S0 crash-recovery surgery：死 r807 stale rebase 治愈（sequencer 假拦截手动 commit 三步法入律）"
    "+W168 prereg 送达 03838491a+bm-b r794 接管面 rebase 25-face newer-wins〕；"
    "r809〔W168 全生命周期一窗收口：死会话遗产收养 freeze 8d8842b61 五面注册〔158th wave bm-a 84th owned〕"
    "+engine 自燃 12/12 shards+r752 三恒等门 PASS+preflight 3 绿+finalize one-pass abb7c0517"
    " ledger 772,812→775,012/K 365,320→367,520 双投影精确命中·K-lift −0.0002 诚实实测"
    "（prereg 描述面 +0.0000·零显著性宣称）+S6 38/38+state 808→809〕；"
    "r810〔死 r809 stale-state forensics 吸收（state 叙述面仍指 freeze 续作而 origin 已载全生命周期"
    "——freeze_edits 重跑被 pre-edit live-registry parity assert 当场拦=既有法正确执法零新坑律）"
    "+W169 seat 链全落地：pre-seat probe rc0 ADMIT〔A 386_604..388_603 阶梯 28 例 E36 hops=1 被 W168 B 带"
    " 386_404..386_603 恰拒=W168 块 W169+ 投影 prose+gate leg3 双面预言命中〕+seat MSG-0547 push e51edfcbc"
    "〔bm-c r657 撞拒后一次净 rebase〕+band gate rc0 ADMIT 双窗 parity·W170+ 投影 A 388_604..390_603"
    "/B 388_804..389_003〕。窗内旗面=引擎 idle verdict（金周停市合法 idle 白名单·复市 10-09 后 re-arm）"
    "+D-06 收口窗 10-07 12:00。指针：**W169 prereg build+freeze+finalize（proj ledger 777,212/K 369,720）"
    "+复市 10-09 数据链 re-arm+月界首考 10-31**；下一 5x=bm-a r815。\n"
)
io.open("research/HANDOVER.md", "a", encoding="utf-8", newline="").write(h_entry)
print("HANDOVER 5x entry appended:", len(h_entry), "bytes")

# --- 2) round report r810 line -------------------------------------------------
rr_path = "logs/iteration-loop/round_reports-bm-a.md"
rr = io.open(rr_path, encoding="utf-8", newline="").read()
assert " | r810 | " not in rr, "r810 line already present"
rr_entry = (
    "| " + iso_short + " | r810 | watermark verdict: 绿 (red=false; engine idle verdict = "
    "golden-week legal idle whitelist: 0 open tickets + queue empty + W169 seat published never-dry held) "
    "| 当前活: W169 seat chain 本窗全落地 (pre-seat probe rc0 ADMIT + seat MSG-2026-10-07-0547 push e51edfcbc "
    "+ band gate rc0 ADMIT) | 最近实物: results/_r810bma_w169_band_gate.json @" + iso[:16]
    + " (origin 5a0228cd4; A 386_604..388_603 阶梯 28 例 E36 / B 388_604..388_803 own-A leg2; "
    "W170+ 投影 A 388_604..390_603 / B 388_804..389_003) | 下个里程碑: W169 prereg build + freeze + finalize "
    "(窗≤48h; proj ledger 775,012+2,200=777,212 / K 367,520+2,200=369,720) + 10-07 12:00 D-06 收口窗 "
    "| did: S0 churn-absorb 活塞 4 连 (r788 族 daemon 竞速) + rebase onto bm-c r657 590ba0fe0 干净零 UU "
    "+ 死 r809 stale-state forensics 吸收 (state 叙述面仍指 W168 freeze 续作而 origin 已载 freeze 8d8842b61 "
    "+ finalize abb7c0517 全生命周期 -- freeze_edits 重跑被 pre-edit live-registry parity assert 当场拦 "
    "= 既有法正确执法零新坑) + W168 finalize 完成态机读复核 (ledger 775,012 / K 367,520 / 12/12 shards "
    "/ K-lift -0.0002 与 r809 实况一致) + S0.5 令差集 163/163 双扫零未回执 + 双水位恒等零动作 "
    "(dec 635c3024=origin / ord 9be6a74f=origin) + S1 smoke 48/48 + S2 双板 0 open + S3 主产=W169 席位链 "
    "(probe→seat→push→gate 全链 band-for-band parity · origin vacancy · r374 双向扫 · W141 own-A 互斥 "
    "· r587 never-transcribe) + S6 38/38 rc0 127s (dualrun ZERO-DRIFT streak 51 · scorecard/REPORT/"
    "LIVE-2026-10-07 再生 · build_status 432combos · token L2 0 today) + S7 四件套绿 (loop pin=8 no-op "
    "+ watchdog 重装 + 双爪重装) + attrition CLEAN×4 账本 + HANDOVER 5x 窗口条 (r801-810 · r805 stamp "
    "missed 如实披露) + state 809→810 + 心跳 epoch int 自证 | verify: smoke 48/48; W169 probe+gate 双 "
    "ADMIT receipts 在仓; seat 送达自证 (push 后 fetch ahead=0 · e51edfcbc→5a0228cd4); orders 163/163 双扫; "
    "本地未达 origin commit 数=0 (收尾 push 后 fetch+rev-list 复核) | next: (1) W169 prereg build "
    "(xform W168→W169 · facts=gate receipt _r810bma_w169_band_gate.json + seat e51edfcbc) (2) freeze "
    "5-face + verify 8 legs + commit + 2-tick ignite (3) finalize (proj 777,212/369,720) (4) 10-07 12:00 "
    "D-06 收口窗 | [r810 bm-a]\n"
)
io.open(rr_path, "a", encoding="utf-8", newline="").write(rr_entry)
print("round report r810 appended:", len(rr_entry), "bytes")

# --- 3) state-bm-a.json ---------------------------------------------------------
st = json.load(io.open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 810
st["round"] = 810
st["loop_round"] = 810
st["last_round"] = 809
st["current_task"] = ("r811: W169 prereg build (xform W168->W169; facts-source = band gate "
                      "results/_r810bma_w169_band_gate.json ADMIT + seat MSG-2026-10-07-0547-bma-w169-seat "
                      "on origin e51edfcbc; anchor = W168 finalize one-pass r809 abb7c0517 ledger 775,012 "
                      "K 367,520 n1_w168_results.json)")
st["did"] = ("r810 W169 seat chain landed one-window (probe rc0 ADMIT A 386_604..388_603 staircase 28th "
             "E36 hops=1 + B 388_604..388_803 own-A leg2 hops=1; seat MSG-0547 pushed e51edfcbc after one "
             "clean rebase onto bm-c r657; band gate rc0 ADMIT dual-window parity; W170+ projection "
             "A 388_604..390_603 / B 388_804..389_003): dead-r809 stale-state absorbed (origin already "
             "carried W168 full lifecycle freeze 8d8842b61 + finalize abb7c0517, ledger 775,012 K 367,520 "
             "machine-read; freeze_edits re-run caught by pre-edit parity assert = existing law correct "
             "enforcement, zero new pits); S0.5 163/163 + dual watermarks identical zero action; smoke "
             "48/48; S6 38/38 rc0 127s; S7 four-piece green + attrition CLEAN + HANDOVER 5x r801-810 "
             "(r805 stamp missed disclosed)")
st["last_action"] = "r810: W169 seat chain landed+pushed; W169 prereg build = next window"
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["last_run"] = iso
st["last_seen"] = iso
st["updated"] = iso
st["ts"] = iso
st["clock_read"] = iso
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
st["next"] = ("r811 = W169 prereg build (facts in-repo: gate ADMIT + seat e51edfcbc) -> freeze 5-face "
              "(two-session law) -> freeze_verify 8 legs -> commit push -> 2-tick ignite -> finalize "
              "(proj ledger 777,212 / K 369,720); 10-07 12:00 D-06 closeout window")
st["notes"] = ("r810 = first session of the 05:3x-06:0x window; dead-r809 stale-state forensics absorbed "
               "pre-work (state narrative vs origin truth reconciled by machine-read receipts); "
               "golden-week: engine idle verdict legal, market re-opens 10-09")
st["verify"] = ("smoke 48/48; W169 probe+gate dual ADMIT; seat delivery self-verified ahead=0 "
                "(e51edfcbc -> 5a0228cd4); orders 163/163 double-sweep; watermarks dec 635c3024 "
                "= ord 9be6a74f both identical zero action; heartbeat epoch int + clock T-sep "
                "self-checked")
st["latest_artifact"] = "results/_r810bma_w169_band_gate.json @" + iso
io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))
print("state-bm-a.json: round_no 809->810")

# --- 4) heartbeat fleet/machines/bm-a.json -------------------------------------
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["machine_id"] = "bm-a"
hb["clock_read"] = iso
hb["ts"] = iso
hb["last_seen"] = iso
hb["last_run"] = iso
hb["last_heartbeat_epoch_utc"] = hb.get("heartbeat_epoch_utc", epoch)
hb["heartbeat_epoch_utc"] = epoch
hb["round_no"] = 810
hb["round"] = 810
hb["last_round"] = 809
hb["last_action"] = st["last_action"]
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
hb["current"] = st["current_task"]
hb["verdict"] = ("green: W169 seat chain landed (probe+seat+gate ADMIT, origin 5a0228cd4); "
                 "engine idle verdict = golden-week legal idle; 0 open tickets; S6 38/38 rc0")
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = ("W169 prereg+freeze+finalize (proj ledger 777,212 / K 369,720, window<=48h); "
                        "D-06 closeout window 10-07 12:00")
try:
    import psutil
    hb["cpu_pct"] = psutil.cpu_percent(interval=1)
    hb["cpu_util_pct"] = hb["cpu_pct"]
    hb["cpu_load_pct"] = hb["cpu_pct"]
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1024**3, 2)
    hb["idle_ram_gb"] = hb["free_ram_gb"]
    hb["idle_ram_mb"] = int(vm.available / 1024**2)
    hb["ram_free_gb"] = hb["free_ram_gb"]
    print("heartbeat sampled: cpu", hb["cpu_pct"], "ram", hb["free_ram_gb"], "GB")
except Exception as e:
    print("psutil sample skipped:", e)
io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock must be T-separated (R262 law)"
print("heartbeat written: epoch int self-verified", chk["heartbeat_epoch_utc"])
print("ALL FOUR CLOSEOUT FACES LANDED")
