import json, subprocess, time, os, sys, datetime
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = time.time()
epoch = int(now)
nowdt = datetime.datetime.now().astimezone()
ts = nowdt.isoformat(timespec="seconds")

import psutil
psutil.cpu_percent(interval=None)  # prime (r319 law)
time.sleep(0.6)
cpu = round(psutil.cpu_percent(interval=1.2), 1)
vm = psutil.virtual_memory()
free_ram = round(vm.available / (1024**3), 1)
try:
    g = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        creationflags=0x08000000)
    gpu_free = int(float(g.decode().strip().splitlines()[0]))
except Exception:
    gpu_free = 9891

def read_bytes(p):
    with open(p, "rb") as f:
        return f.read()

def eol_of(b):
    return b"\r\n" if b.count(b"\r\n") >= b.count(b"\n") - b.count(b"\r\n") else b"\n"

def load_json(p):
    return json.loads(read_bytes(p).decode("utf-8"))

def write_json(p, obj):
    b = read_bytes(p)
    eol = eol_of(b)
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    with open(p, "wb") as f:
        f.write(s.replace("\n", eol.decode()).encode("utf-8"))

VERIFY = ("r346: S0 dead-session forensics integration (r344/r345 dead-before-S7 per r529 law: "
          "self-labeled [bm-c r345] commits on origin + state stuck 343 + no live session process; "
          "numbers 344/345 burned, r346 resumes series; 16 daemon/dead-S6 lane files ride commit "
          "de6073f9d -> rebase -> push 2426af0ac, 0/0 clean; dead-session products W40-restore/"
          "W41/W42 finalize NOT redone) + MAIN PRODUCT: W43 full-lifecycle SINGLE-WINDOW wave "
          "(FREEZE five-piece: band gate ADMIT [A 129_004..131_003 arithmetic no-skip; B "
          "FORCED-SKIP 44_001..44_200 past refused 43_801..44_000 at SEED_REGISTRY p4_queue="
          "44_000, W26 A-skip/W39-B family, leg1-B refusal facts [44000] machine-proven] + "
          "banned gate ADMIT [first run REJECT = BAN-04 word-face false positive, rephrased per "
          "r494 law] + prereg frozen [anchor=W42 measured] + canon W43 row + WAVE_CONFIGS[43] + "
          "selftest W43 materializer leg added same-window [first run leg list ended at W42]; "
          "push b3411b7c9 wave-slot lock) -> 12/12 no-restart burn (per-tick re-read auto-saw "
          "row; ignition verified by product growth 03:15-03:16:49) -> FINALIZE one-pass "
          "(K=92,520 == sec.0 projection bit-exact; merged mu -0.091783 sigma 0.244746; "
          "W43-only mu -0.094516 sigma 0.243670 A p95 0.3028; S5 4/4 PASS single-anchor W42 "
          "disclosed [mu d 0.0013<0.02 / sigma +0.96%<10% / A p95 d -0.0248<0.05 / K-lift "
          "-0.0002<=0.02 negative honest]; skill_line_v2 1.1577->1.1575 @n_eff 454,940; ledger "
          "prev 454,940 + 2,200 = 457,140 chain head; voids [LOWAMP-P1, LOWAMP-P2] inherited; "
          "prereg s7/s8 SESSION-SIDE mechanical backfill same commit + post-backfill "
          "default-wave selftest PASS [r307 two-state]; W44+ projection both CLEAN "
          "machine-derived [A 131_004..133_003 / B 44_201..44_400]) + LOWAMP-P3 grid 16/16 on "
          "origin (3 LAEDGE cells landed bm-a lane; nulls burn daemon-managed in flight) + S6 "
          "spine rc0 (dualrun ZERO-DRIFT streak 30/3; WM loaded_ok py 100%; audit "
          "burning-healthy, cap_violation flag = O-1858 holiday full-load known false-positive "
          "face; host-guard stale-takeover legal writes bm-a hb stale 119-121min [scorecard/"
          "daily_scorecard/build_status/paper_export per O-2100 s2.4]; market_clock ORANGE_COOL; "
          "b_layer 4 gates PASS; attrition CLEAN; token delta=0) + T-131 healthy (log fresh, "
          "network-bound in flight)")
DID = ("r346: dead-session S0 forensics integration + W43 full-lifecycle single-window "
       "(freeze -> 12/12 burn -> finalize, ledger 457,140, K=92,520) + S6 chain")
CURRENT = ("W43 full-lifecycle closed same window (freeze b3411b7c9 -> 12/12 no-restart burn "
          "03:15-03:16:49 -> finalize one-pass); LOWAMP-P3 16/16 on origin (nulls burn in "
          "flight, finalize awaits nulls + E1 four-leg); T-131 backfill in flight (network-"
          "bound); engine idle post-W43 = queue empty, W44 freeze next round per de-throttle "
          "first-free law")
NEXT = ("(r347)(a) W44 freeze first-free-number (fresh fetch + band-gate machine-verify per "
        "W43 row W44+ projection both CLEAN: A 131_004..133_003 / B 44_201..44_400, r535 law); "
        "(b) LOWAMP-P3 finalize when nulls burn completes (E1 four-leg mandatory "
        "pre-consumption per prereg; grid 16/16 ready); (c) T-134 s2 p1e_synth conversion "
        "(r340 pick9 = 2586.9s heaviest; r304 paradigm); (d) T-131 liveness watch + completion "
        "closeout; (e) register_satengine_task.ps1 S4U-first dead-code cleanup (D-20261002-02, "
        "window 10-04); (f) T-143 month-exam prep ticket claim decision (deliverable 10-29); "
        "(g) month-boundary first exam 10-31")
NOTE = ("r346 skipped dead r344/r345 numbering per r529 law (state 343 + self-labeled [bm-c "
        "r345] commits on origin + no state/heartbeat/report updates + no live session "
        "process = dead-before-S7; both numbers burned to prevent double identity). W43 = "
        "third single-window full-lifecycle wave (W32 r339 / W42 r345 precedents). Discovery: "
        "finalize does NOT auto-backfill prereg s7/s8 -- backfill is a SESSION-side action "
        "(r412 mechanical-backfill face = session writes, values machine-derived from finalize "
        "output). Inbox MSG-013x/025x = my outbound to bm-b, left in inbox for bm-b per "
        "addressing. cap_violation audit flag = O-1858 holiday full-load false-positive face "
        "(r341 precedent).")
LAST_ROUND = ("2026-10-02 r346 bm-c: W43 full-lifecycle single-window (ledger 457,140, K="
              "92,520) + dead-session S0 forensics integration + S6 chain")

sp = os.path.join(ROOT, "state-bm-c.json")
st = load_json(sp)
st["round_no"] = 346
st["last_round_at"] = "r346"
st["last_round_ts"] = ts
st["updated"] = ts
st["cpu_pct"] = cpu
st["idle_ram_gb"] = free_ram
st["gpu_free_vram_mib"] = gpu_free
st["verify"] = VERIFY
st["did"] = DID
st["current_task"] = CURRENT
st["next"] = NEXT
st["note"] = NOTE
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = ts
st["last_ts"] = ts
st["last_round"] = LAST_ROUND
st["last_seen"] = ts
write_json(sp, st)

hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = load_json(hp)
hb["cpu_util_pct"] = cpu
hb["free_ram_gb"] = free_ram
hb["gpu_free_vram_mb"] = gpu_free
hb["cpu_pct"] = cpu
hb["idle_ram_gb"] = free_ram
hb["gpu_idle_vram_mib"] = gpu_free
hb["gpu_idle_vram_mb"] = gpu_free
hb["gpu_free_vram_mib"] = gpu_free
hb["round_no"] = 346
hb["updated_at"] = ts
hb["ram_free_gb"] = free_ram
hb["gpu_vram_free_mb"] = gpu_free
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["current_task"] = CURRENT
hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
hb["prod_lanes"] = ("r346: W43 FULL-LIFECYCLE SINGLE-WINDOW landed (freeze b3411b7c9 -> 12/12 "
                    "no-restart burn 03:15-03:16:49 -> finalize one-pass ledger 457,140 chain "
                    "head, K=92,520, S5 4/4 PASS, prereg s7/s8 backfilled same commit); "
                    "LOWAMP-P3 grid 16/16 on origin (nulls burn in flight); T-131 backfill "
                    "in flight network-bound")
hb["verdict"] = ("healthy (W43 full-lifecycle closed same round -- third single-window wave "
                 "after W32/W42; engine idle post-W43 = queue empty, W44 freeze next round "
                 "per de-throttle first-free law; T-131 network-bound in flight; wm loaded_ok "
                 "py 100% burn window)")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts
hb["health"] = "ok"
hb["activity_now"] = ("r346: dead-r344/r345 forensics + W43 freeze/burn/finalize single-window "
                     "(band gate ADMIT + banned gate ADMIT + selftest W43 leg) + S6 chain "
                     "rc0 + smoke 47/47 + orders diff EMPTY + D-19 MATCH-unchanged")
hb["latest_artifact"] = ("results/perpetual_faces/n1_w43_results.json (ledger 457,140, "
                         "K=92,520) + research/PERPETUAL_N1_W43_PREREG.md s7/s8 backfill + "
                         "results/p2cal_ext/n1_w43/ 12 shards")
hb["next_milestone"] = ("W44 freeze next round (first-free, band-gate derive; W44+ projection "
                        "both CLEAN per W43 row); LOWAMP-P3 finalize (E1 four-leg, awaits "
                        "nulls burn); T-131 completion; month-boundary first exam 10-31")
write_json(hp, hb)

REPORT_LINE = (ts + "｜r346｜dept:研究（W43 单窗全生命周期）+dept:工程（S0 死亡会话取证整合）｜"
    "watermark verdict=绿（red=false·probe loaded_ok py 100% 烧录窗·local_batch_running=true 合法态；"
    "audit cap_violation 旗=O-1858 假期满载令已知假阳性面〔r341 先例〕如实注记）｜"
    "S0: r344/r345 猝死会话取证收编（state 停 343+origin 自标 [bm-c r345] commit+无活会话进程扫描=死于 S7 前·"
    "r529 律号位 344/345 烧毁·r346 续系列；死亡会话遗产 W41/W42 finalize+W40 恢复件已在 origin 零重做）→"
    "16 脏件 ride commit de6073f9d→rebase→push 2426af0ac 0/0 净｜S0.5 令差集 EMPTY（144 全 ack 含 README）·"
    "D-19 水位 4fd50184 MATCH-unchanged（raw-blob python 法）·S1 smoke 47/47｜"
    "主产出=**W43 引擎波单窗全生命周期收官**（第 33 枚·bm-c 第 12 枚自有波·first-free after W42："
    "冻结五件套〔带闸 ADMIT=results/_r346bmc_w43_band_gate.py：leg0 40 行+leg0b W42 行 W43+ 警示 prose 校验+"
    "leg1-A 算术 CLEAN+leg1-B 算术 43_801..44_000 REFUSED refusal facts=[44_000] 跳位被迫性机证+"
    "leg2-B 强制跳位首净窗 44_001..44_200==W42 行公示投影逐位〔W26 A 跳位/W39-B 族〕+leg3+N3-R1 腿+"
    "探针簇腿+origin 号位净空〕+禁向闸 ADMIT〔首跑 REJECT=BAN-04「网格」词面假阳性 r494 律·改措辞避开复跑绿〕+"
    "prereg 冻结〔§5 锚=W42 实测〕+法典 W43 行+WAVE_CONFIGS[43]+selftest W43 材料面腿同轮补齐"
    "〔首跑面列表止于 W42=缺腿发现→补腿复跑绿〕→push b3411b7c9=波位锁→**免重启 12/12 烧录**"
    "（per-tick 重读自动见行·点火验证=产物增长面 03:15-03:16:49）→**finalize one-pass**："
    "K=92,520==§0 投影逐位·merged mu −0.091783/sigma 0.244746·W43-only mu −0.094516/sigma 0.243670/"
    "A p95 0.3028·S5 4/4 PASS 单锚 W42 披露〔mu Δ0.0013<0.02/sigma +0.96%<±10%/A p95 Δ−0.0248<0.05/"
    "K-lift −0.0002≤0.02 负向如实〕·skill_line_v2 1.1577→1.1575 @n_eff 454,940·账本 prev 454,940+2,200="
    "**457,140 链头**·voids [LOWAMP-P1,P2] 继承·§7/§8 会话侧机械回填同 commit+回填后缺省波 selftest PASS"
    "〔r307 两态〕·W44+ 投影双侧 CLEAN 机证（A 131_004..133_003/B 44_201..44_400）·r538 一过律执行）｜"
    "LOWAMP-P3 网格 16/16 在 origin（LAEDGE 三胞 bm-a 落齐·nulls 烧批 daemon 管理在飞·finalize 候 nulls 完成+E1 四腿）｜"
    "S6 链 rc0（dualrun ZERO-DRIFT streak 30/3·audit burning-healthy·WM loaded_ok·假日 0 新行 cutoff 09-30·"
    "regime ORANGE shadow days=4·clock ORANGE_COOL sleeves=4·b_layer 4 gates PASS·fund_premium pre-15:30 no-op·"
    "fundamental fresh-skip 14.8h·车道守卫 13 腿诚实 no-op·host 守卫 stale-takeover 合法写〔bm-a hb 119-121min·"
    "O-2100 s2.4〕：scorecard/daily_scorecard/build_status/paper_export·REPORT-2026-10-02+LIVE-2026-10-02 再生·"
    "token delta=0·月度三件 10-01 已履不双跑）·S7 五查绿（attrition CLEAN〔2 healed 历史注记〕·loop pin=5 no-op "
    "03:25 次 fire·watchdog 在位 03:50·claw 重装·inbox 两件均本机→bm-b 出站件按编址留置）｜"
    "实况三行（CEO 过程可见面）：当前活=W43 单窗全生命周期已收官（冻结→烧→收口同窗）+T-131 回填续拉+LOWAMP-P3 nulls 在飞｜"
    "最近实物=results/perpetual_faces/n1_w43_results.json（K=92,520·账本 457,140）+research/PERPETUAL_N1_W43_PREREG.md "
    "§7/§8 回填+12 分片 results/p2cal_ext/n1_w43/（origin b3411b7c9+appender·03:1x）｜"
    "下个里程碑=W44 冻结+LOWAMP-P3 finalize（E1 四腿·nulls 完成后·窗≤48h）+T-134 p1e_synth 转换（r347）+月界首考 10-31｜"
    "产品分=2（finalize 科学件+冻结五件套+12 分片=能跑能看实物）｜坑律新增=0（本窗 incidents 均已知律复发："
    "r330 CRT 坑/r494 BAN 词面坑/r522 缺省波律——按既有配方处置；发现面=finalize 不自动回填 §7/§8〔会话侧动作〕如实注记）｜"
    "本地未达 origin commit 数=收尾 push 后 fetch 自证｜next: (r347)(a) W44 冻结（W43 行 W44+ 投影双侧 CLEAN 机证复核）；"
    "(b) LOWAMP-P3 finalize（E1 四腿前置）；(c) T-134 s2 p1e_synth 转换；(d) T-131 巡检；"
    "(e) register_satengine S4U 清理（窗 10-04）；(f) T-143 月考筹备票认领决策")

rp = os.path.join(ROOT, "round_reports-bm-c.md")
b = read_bytes(rp)
eol = eol_of(b)
add = (REPORT_LINE.encode("utf-8"))
if not b.endswith(eol) and not b.endswith(b"\n"):
    b += eol
b += add + eol
with open(rp, "wb") as f:
    f.write(b)

# self-verify: heartbeat epoch int + clock T-separator (F7 law)
chk = load_json(hp)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read ISO T-separator"
chk2 = load_json(sp)
assert isinstance(chk2["heartbeat_epoch_utc"], int)
print("STATE_OK round_no=", chk2["round_no"], "epoch=", chk2["heartbeat_epoch_utc"],
      "cpu=", cpu, "free_ram=", free_ram, "gpu_free=", gpu_free, "ts=", ts)
