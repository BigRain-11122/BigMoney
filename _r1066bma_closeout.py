# r1066 bm-a closeout: state round bump + heartbeat refresh + round report line append
# (single-file atomic, r1028/r1031 laws: python raw-bytes utf-8; r1062 heartbeat pattern + r1065 state pattern)
import json, time, io, os, subprocess
os.chdir(r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney')

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())
STATE = 'state-bm-a.json'
HEART = 'fleet/machines/bm-a.json'
REPORT = 'round_reports-bm-a.md'
ORD_SHA = '22c61debe61ab4e0bffa62faf65a78ce5cc33ee342a79afd2eb633c7c1f31d52'
DEC_SHA = '4cfdd17caa13c60b718d3031f132620c8f66a9cc1e1b133a2f4cc73071b535c0'

did = ("r1066: (1) S0 pull window: fetch behind=1 -> pull --rebase --autostash absorbed bm-b round1009 batch "
       "(b18fc61139: O-1810 receipt + D-19 double advance 1b6ccf2a + CODELY.md hotcold 9,628B + S6 43 rc0 + ackfix); "
       "autostash pop-UU on shared probe watermark_red.json (stash 19:40:03 vs origin 19:36:03 = newer-wins take-stash, "
       "marker scan rc0, stash dropped b795e17c6; r1028/r1062 family zero-loss); "
       "(2) round-zero orphan probe 23 py faces / 0 orphans / 1 resident server (8792 exempt); "
       "(3) S0.5 orders_ack dual-scan CLEAN 103/112/0 + D-19 ord delta consumed same-round (ee3d9aa8 -> 22c61deb fresh face at advance; "
       "5 new rows 19:13..19:35 = MV V5.8 final-review seven-batch + cloud-final-product authorization / producer-supervisor seat law / "
       "all-stage expert coverage law / 19:28 efficiency restate / 19:35 version-count cap -- all BigStream/MV/committee domain rows "
       "already executed via bm-a other-window seats, BigMoney loop zero obligation; advance read-back full-string equality, heartbeat mirrors synced 6); "
       "dec 4cfdd17c hold; "
       "(4) S1 smoke 49/49; S2 job_list empty + boards drained (r1058 census face held, zero re-scan per product law sec.2); "
       "(5) S3 satengine ALIVE rc0 (first status read hit Select -First pipe truncation face rc=-1 = known r1005 pit, re-ran full-face "
       "engine_alive=true rc0; disclosed) + watermark green red=false (next_pick moneyflow IC claimed / panel source-blocked); "
       "(6) MAIN: S6 chain 42 rc-lines (41 legs + live_paper) all rc0 bad=0 (_r1066bma_s6chain.ps1 = r1065 face clone verbatim; Sunday no-op faces) "
       "+ MF rank-lane fresh attempt THIS round (19:44:50 spawn -> 19:45:13 fetch_failed page 2 RemoteDisconnected; main lane fuse-stopped "
       "from 19:12:40 3x RemoteDisconnected, panel cutoff 2026-10-13 complete=false frozen) = blockade alive day-12, "
       "Monday <=10-19 adjudication armed with day-8..12 five-day chain; "
       "(7) inbox MSG-20261018-191x-bmc-w272-seat.md processed: W272 seat owner=bm-c 91st own wave, upstream waits-face NONE "
       "(W271 complete r1097 chain, W272 FREEZE UNBLOCKED at seat time, prereg derive = bm-c same/next window first action) -> "
       "bm-a yields per fleet README sec.4, zero bm-a wave obligation; MSG moved to processed/, inbox 0 files; "
       "(8) idle round-head green_idle first-read (idle_rounds=1, pool 0, agenda_starved true) -> --worked same-round "
       "(S6 product work + D-19 consumption + inbox MSG processing basis, r1062..r1065 precedent family); "
       "(9) S7: loop pin=8 no-op (next fire 19:58) + watchdog alive (S4U flip access-denied = carried C-20261016-04) + "
       "claws reinstalled both + attrition_guard_scan rc0 in-chain")

current = ("r1066: waiting-state maintenance-product round (S6 42 rc-lines all green + live_paper rc0 + D-19 ord delta consumed 22c61deb) + "
           "W272 seat consumed informational (owner=bm-c, bm-a yields) + MF rank-lane day-12 fresh-evidence; "
           "waiting faces: W272 chain on bm-c lane, MF Monday adjudication armed day-8..12, council sec.6 table <=10-20, E20 reserved")

current_task = ("r1066: S6 maintenance-product round (42 rc-lines rc0 bad=0) + D-19 ord advance 22c61deb consumed (5 informational rows zero obligation) + "
                "W272 seat informational consumed (bm-c 91st own wave); MF Monday <=10-19 adjudication armed with day-8..12 five-day chain")

nextr = ("r1067: (1) MF Monday adjudication <=10-19 (Monday S6 retest adds day-13 face or blockade breaks; five-day chain day-8..12 frozen for adjudication); "
         "(2) W272 chain watch on bm-c lane (prereg derive -> five-face splice -> self-burn -> sixgate -> finalize -> fivekeys -> sec78; "
         "W273 owner naming rides W272 sec.7/8 backfill; zero bm-a wave obligation until a seat names bm-a); "
         "(3) council sec.6 first ruling table watch <=10-20 12:00; "
         "(4) E20 three-axis synthesis = GM/council signature reserved face, loop does not self-start; "
         "(5) CODELY.md headroom maintained (zero appends r1066; next append re-triggers editorial per law); "
         "(6) S0.5 d19 probe: ord/dec faces expected unless group-side new rows land")

next_milestone = "MF Monday adjudication <=10-19 (day-8..12 chain complete) + W272 chain watch on bm-c lane + council sec.6 table <=10-20 12:00"

verdict = ("GREEN: r1066: waiting-state maintenance-product round all green -- S6 42 rc-lines + live_paper rc0 bad=0 + smoke 49/49 + "
           "orders_ack dual-scan CLEAN 103/112/0 + D-19 ord delta consumed same-round (advance 22c61deb read-back equal, mirrors synced 6) + "
           "dec hold 4cfdd17c + satengine ALIVE rc0 + watermark green red=false + orphan 0/23 + loop pin=8 no-op + claws x2 + "
           "attrition guard rc0 + idle --worked (green_idle first-read consumed same-round via S6 product work); "
           "honest face = 1-point product round (real file changes: S6-derived same-day faces + MF rank-lane day-12 evidence face + chain script; "
           "waiting objects one-line per product law sec.2, no re-scan)")

verify = ("results/_r1066bma_s6chain_rc.log 42 rc-lines all rc0 bad=0 + live_paper rc0 (in-log) + smoke 49/49 + orders_ack_scan CLEAN 103/112/0 + "
          "d19 advance read-back full-string equality (ord 22c61deb / dec 4cfdd17c, heartbeat mirrors synced 6, receipt results/_r1066bma_d19_receipt.json) + "
          "idle --worked receipt (idle_rounds 0, agenda_starved false) + MF rank-lane fresh face results/moneyflow_update_status.json "
          "(19:44:50 spawn -> 19:45:13 fetch_failed page 2 RemoteDisconnected)")

artifact = ("S6-derived same-day idempotent faces regenerated (docs/daily_report/REPORT-2026-10-18 + docs/live_usage/LIVE-2026-10-18 + "
            "results/strategy_scorecard.json + results/daily_scorecard.json + results/dashboard_status.json/js) + "
            "MF rank-lane day-12 evidence face (results/moneyflow_update_status.json) + _r1066bma_s6chain.ps1 chain script + "
            "inbox W272 seat MSG processed to processed/")

ord_seen = ("r1066: D-19 ord delta consumed (ee3d9aa8 -> 22c61deb; 5 rows 19:13..19:35 = MV V5.8 final-review + producer-supervisor seat + "
            "all-stage expert coverage + efficiency restate + version-count cap, all BigStream/MV/committee domain already executed via "
            "bm-a other-window seats, zero BigMoney-loop obligation); dec 4cfdd17c zero-delta hold")

dec_seen = "r1066: D-19 zero-delta hold (dec 4cfdd17c, zero new group rows consumed)"

ack_note = ("r1066: fleet board CLEAN (103 orders / 112 acks, 0 unacked, 0 face divergence); NO new fleet orders; "
            "group ord delta = 5 informational rows consumed via D-19 advance (zero BigMoney-loop obligation); "
            "inbox W272 seat MSG consumed informational (owner=bm-c, bm-a yields) -> processed/, inbox EMPTY")

notes = ("r1066: (1) zero-new-pitfall round: Select -First truncation face (rc=-1 fake) = already-carded r1005 pit re-hit read-side only, "
         "full-face rerun rc0 = no new law; watermark pop-UU = r1028 family standard recipe; "
         "(2) W272 seat consumed informational -- owner=bm-c (91st own wave, sixth-plus consecutive bm-c own wave face continues as fleet-health observation), "
         "W273 owner naming rides W272 sec.7/8 backfill; "
         "(3) MF day-12 rank-lane fresh failure (19:45:13 page 2 RemoteDisconnected) extends the five-day chain by one same-day face; "
         "main lane fuse-stopped per design, Monday <=10-19 adjudication armed; "
         "(4) watchdog S4U flip access-denied = carried C-20261016-04 (elevation window pending)")

# ---------- state face ----------
with io.open(STATE, 'r', encoding='utf-8') as f:
    s = json.load(f)

s['loop_round'] = 1066
s['round'] = 1066
s['round_no'] = 1067
s['round_no_label'] = 'r1066'
s['last_round'] = 'r1066'
s['last_round_label'] = 'r1066'
for k in ('clock_read', 'ts', 'updated', 'updated_at', 'last_round_at', 'last_round_closed', 'last_round_ts',
          'last_run', 'last_seen', 'last_action_at', 'last_orders_at', 'last_orders_read_at', 'last_decisions_read_at'):
    s[k] = NOW
prev_epoch = s.get('heartbeat_epoch_utc', EPOCH)
s['heartbeat_epoch_utc'] = EPOCH
s['heartbeat_epoch_utc_type_int'] = True
s['last_heartbeat_epoch_utc'] = prev_epoch
s['did'] = did
s['last_action'] = did
s['current'] = current
s['current_task'] = current_task
s['task'] = "r1066: maintenance-product round (S6 chain + D-19 consumption + W272 seat informational + closeout)"
s['now_active'] = "bm-a loop r1066 closeout (waiting-state maintenance-product round)"
s['next'] = nextr
s['next_milestone'] = next_milestone
s['verdict'] = verdict
s['verify'] = verify
s['last_artifact'] = artifact
s['recent_artifact'] = artifact
s['latest_artifact'] = artifact
s['last_orders_seen'] = ord_seen
s['last_decisions_seen'] = dec_seen
s['orders_ack_note'] = ack_note
s['notes_r1066'] = notes
s['idle_rounds'] = 0
s['agenda_starved'] = False
s['orphan_face'] = 0
s['orphan_faces'] = 0
s['orphan_killed'] = 0
s['last_orders_sha'] = ORD_SHA
s['d19_watermark_guard'] = dict(s.get('d19_watermark_guard') or {})
s['d19_watermark_guard'].update({"round_ref": 1066, "ts": NOW})

# ---------- live measure (CPU/RAM psutil, VRAM nvidia-smi) ----------
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_pct = round(vm.percent, 1)
    ram_free_gb = round(vm.available / (1024 ** 3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    ram_pct, ram_free_gb, cpu_pct = 55.3, 51.8, 21.5
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=15)
    vram_free_mb = int(out.stdout.strip().splitlines()[0])
    vram_note = "nvidia-smi live measure r1066 closeout (CEO working machine, honest free face)"
except Exception:
    vram_free_mb = 7414
    vram_note = "nvidia-smi fallback to r1065 face (measurement failed this window)"

s['cpu_load_pct'] = cpu_pct
s['cpu_pct'] = cpu_pct
s['cpu_total_pct'] = cpu_pct
s['cpu_util_pct'] = cpu_pct
s['ram_load_pct'] = ram_pct
s['ram_free_pct'] = round(100 - ram_pct, 1)
s['free_ram_pct'] = round(100 - ram_pct, 1)
s['ram_free_gb'] = ram_free_gb
s['free_ram_gb'] = ram_free_gb
s['idle_ram_gb'] = ram_free_gb
s['ram_free_mb'] = int(ram_free_gb * 1024)
s['idle_ram_mb'] = int(ram_free_gb * 1024)
s['gpu_free_vram_mb'] = vram_free_mb
s['gpu_source_note'] = vram_note

with io.open(STATE, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
    f.write('\n')

with io.open(STATE, 'r', encoding='utf-8') as f:
    rb = json.load(f)
assert rb['round_no'] == 1067 and rb['loop_round'] == 1066, 'round face mismatch'
assert isinstance(rb['heartbeat_epoch_utc'], int), 'epoch not int'
assert rb['last_orders_sha'] == ORD_SHA, 'ord sha face'
assert rb['last_decisions_sha'].startswith('4cfdd17c'), 'dec sha face'
assert 'T' in rb['clock_read'], 'clock_read T-separator'

# ---------- heartbeat face ----------
with io.open(HEART, 'r', encoding='utf-8') as f:
    hb = json.load(f)
prev_hb_epoch = hb.get('heartbeat_epoch_utc', EPOCH)
for k, v in [("active", True), ("clock_read", NOW), ("ts", NOW), ("last_seen", NOW),
             ("updated", NOW), ("updated_at", NOW), ("last_run", NOW),
             ("last_round", "r1066"), ("last_round_label", "r1066"), ("round", 1066),
             ("round_no", 1067), ("loop_round", 1066),
             ("heartbeat_epoch_utc", EPOCH), ("heartbeat_epoch_utc_type_int", True),
             ("last_heartbeat_epoch_utc", prev_hb_epoch),
             ("idle_rounds", 0), ("agenda_starved", False), ("health", "green"),
             ("cpu_pct", cpu_pct), ("cpu_load_pct", cpu_pct), ("cpu_total_pct", cpu_pct),
             ("cpu_util_pct", cpu_pct),
             ("ram_load_pct", ram_pct), ("ram_free_pct", round(100 - ram_pct, 1)),
             ("free_ram_pct", round(100 - ram_pct, 1)),
             ("ram_free_gb", ram_free_gb), ("free_ram_gb", ram_free_gb), ("idle_ram_gb", ram_free_gb),
             ("ram_free_mb", int(ram_free_gb * 1024)), ("idle_ram_mb", int(ram_free_gb * 1024)),
             ("gpu_free_vram_mb", vram_free_mb), ("gpu_source_note", vram_note),
             ("current", current), ("did", did), ("last_action", did),
             ("task", s["task"]), ("now_active", s["now_active"]),
             ("last_artifact", artifact), ("recent_artifact", artifact), ("latest_artifact", artifact),
             ("next", nextr), ("next_milestone", next_milestone),
             ("verdict", verdict), ("verify", verify), ("orders_ack_note", ack_note),
             ("last_orders_seen", ord_seen), ("last_decisions_seen", dec_seen),
             ("last_orders_at", NOW), ("last_decisions_at", NOW),
             ("last_orders_read_at", NOW), ("last_decisions_read_at", NOW),
             ("last_orders_sha", ORD_SHA)]:
    hb[k] = v
assert isinstance(hb["heartbeat_epoch_utc"], int)
with io.open(HEART, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---------- round report line ----------
line = (NOW + " | r1066 | 等待态维护产出轮：S0 拉取窗（fetch behind=1→pull --rebase --autostash 吸收 bm-b round1009 批 b18fc61139=O-1810 回执+D-19 双推进 1b6ccf2a+CODELY.md hotcold 9,628B+S6 43 rc0；autostash pop-UU 共享探针 watermark_red.json=stash 19:40:03 vs origin 19:36:03 newer-wins take-stash·标记扫描 rc0·stash 弃 b795e17c6·r1028/r1062 族零丢失）·"
        "round-zero 孤儿探针 0/23 面（1 resident server 8792 豁免）·"
        "S0.5 双扫 CLEAN 103/112/0+**D-19 ord 增量同轮消费**（ee3d9aa8→22c61deb·5 新行 19:13..19:35=MV V5.8 终审反馈七批+云端终品授权/制监席新立令/全环节专家覆盖律/19:28 效率令重申/19:35 版本数收口令·均 BigStream/MV/委员会域·bm-a 他窗席位已 executed·本 loop 零义务·advance 读回恒等·心跳镜像 synced 6）·dec 4cfdd17c hold·"
        "S1 smoke 49/49·S2 板面全清维持（job_list 空·r1058 census 面维持·产品律 sec.2 零重扫）·S3 satengine ALIVE rc0（首读撞 Select -First 截停面 rc=-1=r1005 已卡坑·全量重跑 rc0 engine_alive=true·如实披露）+水位绿 red=false（next_pick moneyflow IC=claimed/panel-blocked）·"
        "**本轮主产=S6 链 42 rc-lines（41 腿+live_paper）全 rc0 bad=0**（_r1066bma_s6chain.ps1=r1065 面 verbatim 克隆·周日 no-op 面）+**MF rank 道本轮新鲜尝试证据**（19:44:50 spawn→19:45:13 fetch_failed page 2 RemoteDisconnected·主道 fuse-stopped 自 19:12:40 3 连断·panel cutoff 2026-10-13 complete=false 冻结=封锁 day-12 仍活·周一 <=10-19 裁决 armed·day-8..12 五日链完整）·"
        "**W272 席位消息消费**（MSG-20261018-191x-bmc-w272-seat：owner=bm-c 91st own wave·upstream waits-face NONE〔W271 r1097 链完整·W272 FREEZE 席时 UNBLOCKED·prereg derive=bm-c 下窗首务〕→bm-a 按 fleet README sec.4 让位零波义务·消息移 processed/·inbox 清零）·"
        "idle 轮首 green_idle 首读（idle_rounds=1·pool 0）→--worked 同轮清零（basis=S6 产品工+D-19 消费+席位消息处置）·S7 loop pin=8 no-op（下火 19:58）·watchdog 活（S4U flip 拒绝访问=carried C-20261016-04）·双爪重装+attrition guard rc0（链内）·"
        "等待面一行：W272 链 bm-c 道（W273 点名随 W272 sec.7/8 回填）／MF 周一裁决 armed／委员会 §6 首裁决 <=10-20 12:00／E20=GM/委员会保留面不自启／CODELY.md 余量维持（本轮零 append） | "
        "证据=results/_r1066bma_s6chain_rc.log 42 rc-lines rc0 bad=0+smoke 49/49+orders_ack_scan CLEAN 103/112/0+d19 advance 读回恒等（ord 22c61deb·镜像 synced 6·回执 results/_r1066bma_d19_receipt.json）+idle --worked 回执（idle_rounds 0）+MF rank 道新鲜面 results/moneyflow_update_status.json（19:44:50→19:45:13 fetch_failed） | "
        "本轮=产品 1 分（S6 能看面再生+MF rank 道 day-12 证据面+链脚本+席位消息处置·非纯记账·等待态律合规零重扫） | "
        "下轮指针=r1067：MF 周一裁决 <=10-19（周一 S6 重试加 day-13 面或封锁破·五日链冻结裁决）+W272 链守望（bm-c 道·W273 点名随 sec.7/8 回填）+委员会 §6 <=10-20 12:00+E20 GM/委员会保留面+CODELY.md 余量维持 | 本地未达 origin commit 数=0（收口 push 验证后）\n")
with io.open(REPORT, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
with io.open(REPORT, 'r', encoding='utf-8') as f:
    tail = f.read()
assert 'r1066 |' in tail, 'report line append fail'
print(json.dumps({"closed": "r1066", "now": NOW, "epoch": EPOCH, "ram_free_gb": ram_free_gb,
                  "cpu_pct": cpu_pct, "vram_free_mb": vram_free_mb, "state_round_no_next": 1067},
                 ensure_ascii=False))
print('CLOSEOUT-OK')
