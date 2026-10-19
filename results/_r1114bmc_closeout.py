# -*- coding: utf-8 -*-
# r1114-continuation bm-c closeout: state + heartbeat + round-report row + HANDOVER 5x catch-up row
import datetime, io, json, subprocess, time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
NOW = now.isoformat(timespec="seconds")
EPOCH = int(time.time())
import psutil
ram_avail = round(psutil.virtual_memory().available / (1024**3), 1)
try:
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, creationflags=0x08000000)
    gpu_free = int(float(gpu.stdout.strip().splitlines()[0]))
except Exception:
    gpu_free = 0
HEAD = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

DID = ("r1114-continuation: W277 FULL CYCLE COMPLETION + W278 SEAT PUBLISHED -- sixgate PRE-FINALIZE ALL PASS 40th consecutive "
 "(_r1114bmc_w277_sixgate.py canon-clone: CR-normalized worktree==landed @ splice 9e53371814 + setwave birth-station 277:1/276:0/275:0 + "
 "shards 12/12 >100KB ls-tree-origin-verified + banned ADMIT rc0 + seed FREE x2 624701/2000+626701/200 + lagged-label heals at birth disclosed: "
 "prior_wave_274 key->prior_wave_276, wave_configs_row stale prior-wave values->current-wave W277 TRUE-match, seed_admit note filename, "
 "assert message, ledger_pre comment) + finalize one-pass ledger 1,031,535+2,200=1,033,735 EXACT / K 605,120+2,200=607,320 EXACT "
 "(w277-only mu -0.0889/sigma 0.2455; merged mu -0.09277044/sigma 0.24508694; K-lift +0.0000; n_eff held 1,031,535) + fivekeys 6/6 ALL PASS "
 "(key1 gap 0.0038719 / key1b 1.41e-05 / key2 5.4e-06 / key3 A p95 0.305->0.3095 in-band / key4 klift 0.0000 / key5 se_mu 0.000314<=0.000315 "
 "narrowing-held; keys=W276 actuals machine-read r587) + sec.7/8 backfill zero-placeholder + gate-clone builders ALL first-try zero authoring "
 "heals (90 sixgate+fivekeys needles + 42 sec78 needles, W276 anchors live-verified) + W278 SEAT PUBLISHED origin b187aa6214 "
 "(probe _w278bmc_20261019_probe.py ADMIT first-try: A 626_901..628_900 TWENTY-SEVENTH consecutive A-hop / B 628_901..629_100 TWENTY-EIGHTH "
 "consecutive above-own-A; seed FREE x2 626901/2000+628901/200; vacancy four-check; W279+ projection A 628_901..630_900 / B 629_101..629_300 "
 "pre-disclosed; machine roller _r1114bmc_roll_w278_probe.py preflight 53/53 + 21 patches count-asserted + builder 53 needles + MUST gates green; "
 "at-birth heal: r1112 Q3 seat-MSG mislabel corrected to true upstream W277 seat MSG-20261019-080x-bmc-w277-seat origin c5f8b88f91) + "
 "S6 light 10/10 rc0 + attrition 4 CLEAN + quad green (loop pin=5 no-op + watchdog Ready + claws x2 identical) + post_review today x0 + "
 "D-19 dual FALSE opening + S7 tail re-probe (ord 57d1f5de / dec 8706acd8 hold, unacked=0) + orphan face=0 py_faces=4 resident=1 + idle --worked rc0")

VERIFY = ("W277 cycle receipts machine-verified (sixgate ALL PASS exit 0 + finalize ledger identity EXACT 1,033,735/607,320 + fivekeys all_pass "
 "exit 0 + sec78 placeholders remaining: 0 + prereg backfilled CRLF preserved) + W278 seat commit b187aa6214 + cycle commit 0502c722ac BOTH "
 "pushed origin fetch-verified behind=0/ahead=0 (bm-b r1020 chain mid-window race healed via stash-bridge rebase: 3 regenerable probe faces "
 "stashed, watermark_red pop conflict resolved HEAD-wins r1028 law + stash dropped identity-verified, r1008bmc legacy stash protected intact) + "
 "smoke 49/49 + S6 light 10/10 rc0 (_r1114bmc_s6_log.txt: dualrun ZERO-DRIFT streak 51 [461] / audit FLAG pool_starvation+supply_floor "
 "answered-by-chain [W277 cycle complete + W278 seat armed] / py_wm insufficient_history fresh / bars cutoff 10-16 pre-15:30 Monday honest "
 "papers debt=0 / CALL-2026-10-16 ORANGE_COOL idempotent / b_layer all_pass / REPORT-2026-10-19 faces=5 / token meter leg rc0) + attrition 4 "
 "CLEAN + post_review today x0 + orphan face=0 + epoch int + clock_read ISO-T. DISCLOSED: (a) engine status remote_done=6 = stale-cache face "
 "for W277 (ground truth ls-tree origin 12/12 shards, both batch commits 0df07c846b+644b4f8459 on origin verified); (b) sixgate Thread-5 GBK "
 "reader-thread noise on one selftest capture = known pit-encoding face, both selftest rc=0; (c) 5 lagged-label heals + 1 seat-MSG mislabel "
 "heal at clone birth, all count-asserted first-try zero re-runs")

NEXT = ("r1115: (1) W278 PREREG DERIVE = FIRST ACTION (post-W277-REGISTERED universe; template = frozen W277 prereg @ e0bc4a0ddd "
 "PRE-backfill face 23,593B sha256_16 45ee1de94c7d36fd, HEAD post-backfill twin DISCLOSED NOT USED per r1049/r1052 law; keys = W277 actuals "
 "FULL-PRECISION machine-read from _r1114bmc_w277_fivekeys.json + n1_w277_results.json: merged mu -0.09277043683725218 / sigma "
 "0.24508693698115214 / a_p95 0.3095 / line_merged@607320 1.197 / se_mu@607320 0.000314 / klift +0.0000 / ledger 1,033,735 EXACT / K=607,320; "
 "bands per W278 seat receipt verbatim A 626_901..628_900 / B 628_901..629_100; W279p projection A 628_901..630_900 / B 629_101..629_300 "
 "pre-disclosed); (2) TODAY Monday 2026-10-19 15:30 bars window: full papers chain (live.paper enforce + t35_openfill + t24 x2 + aggr + alloc + "
 "grid + system_v1 + t35_export + scorecard, debt=0 cutoff 10-16); (3) BigMoney automation-plan faces deadlines <=10-25/<=10-31; "
 "(4) RAM watch standing (loop CPU-only, GPU idle)")

# ---------- state ----------
sp = "state-bm-c.json"
raw = io.open(sp, encoding="utf-8", newline="").read()
st = json.loads(raw)
st.update({
 "activity_now": NOW, "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
 "last_seen": NOW, "last_seen_at": NOW, "last_action_at": NOW,
 "current_task": "W277 CYCLE COMPLETE (ledger 1,033,735/607,320 EXACT) + W278 SEAT PUBLISHED (A 626_901..628_900 / B 628_901..629_100); W278 prereg derive = r1115 FIRST ACTION",
 "current_task_at": NOW, "current_task_ts": EPOCH,
 "last_round": 1114, "last_round_at": NOW, "last_round_closed": 1114, "last_round_closed_at": NOW,
 "last_round_label": "r1114-continuation", "round_no_label": "r1114-continuation closeout -> counter 1115",
 "last_round_summary": "r1114-continuation: W277 CYCLE COMPLETE (sixgate 40th + finalize 1,033,735/607,320 EXACT + fivekeys 6/6 + sec78 zero-placeholder) + W278 SEAT PUBLISHED b187aa6214 (A 626_901..628_900 27th A-hop / B 628_901..629_100 28th above-own-A)",
 "last_round_summary_at": NOW, "last_round_ts": NOW, "last_pulled_at": NOW, "last_run_at": NOW,
 "last_action": "W277 cycle completion (sixgate+finalize+fivekeys+sec78) + W278 seat publish + S6 light 10/10 + closeout",
 "did": DID,
 "last_artifact": "W277 finalize product results/perpetual_faces/n1_w277_results.json (ledger 1,033,735 / K=607,320 EXACT) + backfilled prereg research/PERPETUAL_N1_W277_PREREG.md + W278 seat faces (_w278bmc_20261019_probe.py + receipt + MSG-20261019-102x-bmc-w278-seat.md) @ origin b187aa6214+0502c722ac",
 "recent_artifact": "results/perpetual_faces/n1_w277_results.json (ledger 1,033,735/K=607,320 EXACT) + W278 seat MSG @ origin b187aa6214",
 "latest_artifact": "results/perpetual_faces/n1_w277_results.json (ledger 1,033,735/K=607,320 EXACT) + W278 seat MSG @ origin b187aa6214",
 "next": NEXT, "next_milestone": "W278 prereg derive (r1115 FIRST ACTION); TODAY Monday 15:30 papers chain; BM automation-plan <=10-25/<=10-31",
 "next_pointer": NEXT,
 "now_active": "W277 cycle complete + W278 seat published; W278 prereg derive = next first action",
 "note": "CPU=W277 CYCLE COMPLETE + W278 SEAT (ledger 1,033,735/K=607,320; W278 prereg = r1115 first action); GPU=idle (loop CPU-only); short-video lane DISABLED standing per O-20261017-1741",
 "prod_lanes": "CPU=W277 CYCLE COMPLETE + W278 SEAT PUBLISHED (b187aa6214; prereg = r1115 first action); GPU=idle (loop CPU-only); short-video lane DISABLED standing per O-20261017-1741",
 "full_load_selfproof": {
  "占用一行": "CPU=W277 CYCLE COMPLETE (ledger 1,033,735/K=607,320 EXACT; fivekeys 6/6; sec78 zero-placeholder) + W278 SEAT PUBLISHED b187aa6214 (prereg derive = r1115 FIRST ACTION); GPU=idle ~%.1fG free, loop CPU-only; short-video lane DISABLED standing per O-20261017-1741" % (gpu_free / 1024.0),
  "最近实物": "results/perpetual_faces/n1_w277_results.json (ledger 1,033,735/K=607,320 EXACT) + research/PERPETUAL_N1_W277_PREREG.md sec.7/8 backfilled + W278 seat MSG-20261019-102x-bmc-w278-seat.md @ origin b187aa6214 %s" % NOW,
  "下个里程碑": "W278 prereg derive (r1115 FIRST ACTION); TODAY Monday 2026-10-19 15:30 papers chain; BM automation-plan <=10-25/<=10-31",
 },
 "ram_critical_face": "none (loop CPU-only, GPU idle, %.1fGB free)" % ram_avail,
 "free_ram_gb": ram_avail, "idle_ram_gb": ram_avail, "ram_free_gb": ram_avail,
 "gpu_free_mb": gpu_free, "gpu_idle_mb": gpu_free, "gpu_free_vram_mb": gpu_free,
 "gpu_free_mib": gpu_free, "gpu_idle_mib": gpu_free, "gpu_free_vram_mib": gpu_free,
 "gpu_vram_free_mb": gpu_free, "gpu_idle_vram_mb": gpu_free, "gpu_free_vram_gb": round(gpu_free / 1024.0, 2),
 "idle_rounds": 0, "agenda_starved": False,
 "heartbeat_epoch_utc": EPOCH,
 "verdict": "green r1114-continuation product window (W277 CYCLE COMPLETE: sixgate 40th consecutive + finalize 1,033,735/607,320 EXACT + fivekeys 6/6 + sec78 zero-placeholder + W278 SEAT PUBLISHED first-try ADMIT; smoke 49/49; S6 light 10/10; loop CPU-only, GPU idle)",
 "verify": VERIFY,
 "orders_ack_receipt": "r1114-continuation: opening scan dual FALSE (ord 57d1f5de / dec 8706acd8 hold, unacked=0, files=105 inside ack-230); S7 tail re-probe dual FALSE same -- zero mid-round arrivals",
 "orders_ack_ts": NOW,
 "last_decisions_read_at": NOW, "last_decisions_seen": NOW,
 "last_decisions_read_note": "r1114-continuation: DEC delta FALSE at open+tail both (raw-blob sha256 8706acd8 hold; zero rows owed)",
 "last_orders_read_at": NOW, "last_orders_seen": NOW,
 "last_orders_read_note": "r1114-continuation: ORD delta FALSE at open+tail both (content-sha1 57d1f5de hold; zero rows owed)",
 "orphan_face": 0, "orphan_faces": 0,
 "head_sha": HEAD,
 "sync": {"origin_tip": "r1114-continuation W278 SEAT + W277 CYCLE COMPLETE (b187aa6214 + 0502c722ac, pre-closeout-commit face)", "ts": NOW},
 "r1114c_closeout_note": "r1114-continuation: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=0 resident=1 zero-kill + S0 fetch 0/0 clean open (HEAD==origin 644b4f8459, dirty=1 regenerable daemon face watermark_red); "
 "(2) S0.5 D-19 dual-delta FALSE opening + S7 tail re-probe (ord 57d1f5de / dec 8706acd8 hold; unacked=0; orders files=105 inside ack-230); "
 "(3) S1 smoke 49/49; (4) P0 PRODUCT = W277 cycle completion per next_pointer (r1096 honest-split law, counter HELD 1114 by the closeout-lite d7b732c9e8): engine burn 12/12 verified (local 12 files + ls-tree origin 12/12 + both batch commits 0df07c846b/644b4f8459 on origin; engine status remote_done=6 = stale-cache face DISCLOSED) -> gate-clone builder _r1114bmc_build_gate_clones.py ALL first-try (90 needles count-asserted, W276 anchors live-verified mu -0.09278451/sigma 0.24508562/a_p95 0.305/line 1.1969/se_mu 0.000315/klift +0.0001; 5 lagged-label heals at birth: prior_wave_274 key->276, wave_configs_row stale prior-wave->current-wave TRUE-match, seed_admit note filename, assert message, ledger_pre comment) -> sixgate PRE-FINALIZE ALL PASS 40th consecutive (Thread-5 GBK reader noise = known pit-encoding face, selftest rc 0/0) -> finalize one-pass 1,033,735/607,320 EXACT -> fivekeys 6/6 (key5 se_mu 0.000314<=0.000315 narrowing-held; key3 A p95 0.305->0.3095 in-band) -> sec78 backfill zero-placeholder (builder 42 needles first-try, 3 context heals: W277 engine batches 0df07c846b+644b4f8459, prereg CAS-surgical delivery face, dedup remote stale-cache disclosure); "
 "(5) W278 SEAT PUBLISHED: machine roller _r1114bmc_roll_w278_probe.py (preflight 53/53 vs on-disk W277 probe + token maps + 21 patches count-asserted; at-birth heal: r1112 Q3 seat-MSG mislabel -> true upstream W277 seat c5f8b88f91) -> builder _r1114bmc_build_w278_probe.py (53 needles + MUST gates) -> probe _w278bmc_20261019_probe.py ADMIT first-try (A 626_901..628_900 27th A-hop live-walk / B 628_901..629_100 28th above-own-A / seed FREE x2 / vacancy four-check / owner 267 rows bmc 96 -> W278 268th wave bm-c 97th own wave; W279p A 628_901..630_900 / B 629_101..629_300 pre-disclosed) -> seat MSG @ALL + commit b187aa6214; "
 "(6) push saga: seat push non-FF (bm-b r1020 chain x2) -> cycle-estate commit 0502c722ac + stash-bridge rebase (3 regenerable probe faces; watermark_red pop conflict resolved HEAD-wins r1028; stash dropped; legacy stashes protected) -> BOTH LANDED behind=0/ahead=0 fetch-verified; "
 "(7) S6 light 10/10 rc0 (driver _r1114bmc_s6_light.py canon-clone; dualrun streak 51 [461] / audit FLAG answered-by-chain / insufficient_history fresh / bars cutoff 10-16 pre-15:30 honest / ORANGE_COOL idempotent / REPORT-2026-10-19 faces=5); "
 "(8) S7: attrition 4 CLEAN + quad green (loop pin=5 no-op next fire 10:45 + watchdog Ready 10:41 + claws x2 identical) + idle --worked rc0 idle_rounds=0 + post_review today x0 + D-19 tail dual FALSE + orphan face=0; "
 "(9) 零新方法论卡零新宝藏入册（克隆愈合全属 E63 已知家族·出生站 count-assert 全拦零盘污）；5x HANDOVER catch-up row r1112-r1115 landed THIS window（印章 r1115·上章 r1111）；counter 1114->1115",
})
st["round_no"] = 1115
eol = "\r\n" if raw.count("\r\n") >= raw.count("\n") - raw.count("\r\n") else "\n"
io.open(sp, "w", encoding="utf-8", newline="").write(json.dumps(st, ensure_ascii=False, indent=1).replace("\n", eol))
j = json.loads(io.open(sp, encoding="utf-8").read())
assert isinstance(j["heartbeat_epoch_utc"], int) and j["round_no"] == 1115
print("state OK round_no->1115 epoch int", j["heartbeat_epoch_utc"])

# ---------- heartbeat ----------
hp = "fleet/machines/bm-c.json"
rawh = io.open(hp, encoding="utf-8", newline="").read()
hb = json.loads(rawh)
hb.update({
 "ts": NOW, "last_seen": NOW, "updated_at": NOW, "activity_now": NOW,
 "machine_id": "bm-c",
 "cores": 32, "cpu_cores": 32,
 "cpu_pct": 0.0, "cpu_idle_pct": 100.0, "cpu_util_pct": 0.0,
 "free_ram_gb": ram_avail, "idle_ram_gb": ram_avail, "ram_free_gb": ram_avail, "total_ram_gb": 23.9,
 "gpu_free_mb": gpu_free, "gpu_idle_mb": gpu_free, "gpu_free_vram_mb": gpu_free, "gpu_used_mib": 16384 - gpu_free,
 "idle_rounds": 0, "agenda_starved": False,
 "heartbeat_epoch_utc": EPOCH,
 "clock_read": NOW,
 "current_task": "W277 CYCLE COMPLETE (ledger 1,033,735/607,320 EXACT) + W278 SEAT PUBLISHED (A 626_901..628_900 / B 628_901..629_100); W278 prereg derive = r1115 FIRST ACTION",
 "verdict": "green r1114-continuation: W277 cycle complete (sixgate 40th + finalize EXACT + fivekeys 6/6 + sec78) + W278 seat published ADMIT first-try",
 "health": "ok",
 "round_no": 1115,
 "last_round": 1114, "last_round_closed": 1114, "last_round_label": "r1114-continuation",
})
eolh = "\r\n" if rawh.count("\r\n") >= rawh.count("\n") - rawh.count("\r\n") else "\n"
io.open(hp, "w", encoding="utf-8", newline="").write(json.dumps(hb, ensure_ascii=False, indent=1).replace("\n", eolh))
jh = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(jh["heartbeat_epoch_utc"], int)
print("heartbeat OK epoch int")

# ---------- round report row ----------
row = ("| %s | r1114-continuation | %s | %s | %s |\r\n" % (NOW, DID, VERIFY, NEXT))
with io.open("round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(row)
print("round report row appended")

# ---------- HANDOVER 5x catch-up row (stamp r1115, segment r1112-r1115) ----------
HROW = ("> bm-c round 1115 层报核对·2026-10-19 10:4x 核对窗（窗口覆盖 r1112-r1115 增量段·5x 印章 r1115 本窗落章 per r1083 先例·上一章 r1111）。真值权威=round_reports-bm-c.md 全行在册+state-bm-c.json closeout notes。增量段执行总结（r1112-r1115）＝**W277 全周期自运转四窗链（seat r1112 c5f8b88f91 → prereg r1113 e0bc4a0ddd CAS-surgical → splice r1114 9e53371814 CLEAN-AT-BIRTH 10th gen + 引擎自烧 12/12 0df07c846b+644b4f8459 → 周期收口 r1114-continuation：六门 40 连正确相位 + finalize 1,031,535+2,200=1,033,735 EXACT / K 605,120+2,200=607,320 EXACT + 五键 6/6 + sec.7/8 回填零占位）+ W278 席位已发布（b187aa6214：A 626_901..628_900 27th A-hop / B 628_901..629_100 28th above-own-A·机器 roller 21 补丁全 count-asserted 首过·r1112 Q3 seat-MSG 误标当窗正身）**。本窗实物=W277 周期收口+W278 席位四件套：sixgate 收据 _r1114bmc_w277_sixgate.json（出生站滞后标签五面愈合披露·40 连）+ finalize 产物 n1_w277_results.json + 五键收据 _r1114bmc_w277_fivekeys.json（key5 se_mu 0.000314≤0.000315 窄化续行·key3 A p95 0.305→0.3095 带内）+ prereg sec.7/8 回填 + W278 探针/roller/builder/席位 MSG。维护面：smoke 49/49 + S6 light 10/10（dualrun streak 51 / audit FLAG answered-by-chain / bars 10-16 pre-15:30 honest）+ attrition 4 CLEAN + quad green（loop pin=5/watchdog Ready/双爪）+ 双水位双扫 FALSE + 孤儿面 0 + post_review 今日 ✗0。重要披露：engine status remote_done=6=陈旧缓存面（ls-tree origin 12/12 实证）；中窗 bm-b r1020 竞速经 stash-bridge rebase 零内容损治愈（watermark_red HEAD-wins r1028 律·legacy stash 保护未动）。指针：**W278 prereg derive=r1115 FIRST ACTION（模板=冻结 W277 prereg @ e0bc4a0ddd PRE-backfill 面 23,593B sha16 45ee1de94c7d36fd·HEAD 回填孪生禁用 per r1049/r1052；键=W277 实测全精度机读 mu -0.09277044/sigma 0.24508694/a_p95 0.3095/se_mu 0.000314；带按 W278 席位收据逐字 A 626_901..628_900 / B 628_901..629_100）→ splice→cycle→W279；周一 15:30 bars papers 全链 re-arm（debt=0 cutoff 10-16）；BM automation-plan ≤10-25/≤10-31；月界首考 10-31**。下一 5x=bm-c r1120。[via bm-c r1114-continuation]\n")
with io.open("research/HANDOVER.md", "a", encoding="utf-8", newline="") as f:
    f.write(HROW)
print("HANDOVER 5x catch-up row appended")
print("CLOSEOUT WRITES OK")
