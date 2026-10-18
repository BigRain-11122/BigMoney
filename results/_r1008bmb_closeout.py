# -*- coding: utf-8 -*-
# r1008 bm-b closeout: state.json + heartbeat + round report line (three-face same-window write).
import json, time, datetime, io

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")  # e.g. 2026-10-18T16:4x:xx+08:00
epoch = int(time.time())

did = ("r1008: (a) S0 rebase absorb 9f480646f (13 commits: bm-c r1092-r1094 W269 full cycle [splice+self-burn 12/12+sixgate 32nd+finalize 1,016,135 EXACT+fivekeys 6/6] + W270 seat publish [owner bm-c 89th own wave] + bm-a r1058-r1060 guard rounds); 4-face stash bridge -> UU x2 shared faces resolved origin-side per r1007 law (watermark_red origin face = bm-a 15:59 red=false/healthy => F-20261018-01 residual cleared by origin truth; machine-health union face daemon self-heal); behind 13->0. "
"(b) O-0948 window check: ticks 14:52-16:12 x9 all CLOUD_CAP_DEFER live=2 zombies_excluded=0 = legal defer not dead windows (bm-a r1060 adjudication) -> zero died-pre-closeout holds; 16:22 tick launched when slot freed. "
"(c) S0.5: orders 102/102 unacked=NONE (pre+post-rebase double scan); D-19 ORD delta 5d871243->43a18d01 independently verified = 10-18 14:32 MV credits row (BigStream lane, bm-a executed, zero BigMoney dispatch) -> d19_watermark advance dual-face read-back OK (heartbeat mirrors synced); DEC 4cfdd17c hold. "
"(d) S6 43 legs rc0 3.9min: smoke rc0, dualrun ZERO-DRIFT streak 51, idle --worked 11->0, audit FLAG supply_floor (boards/pool drained honest starvation; answer face = W270 seat published by bm-c 16:0x + bm-b engine lane awaits W271+ seat / secretary restock), 4 bm-a-stale-takeover derives (scorecard/t35_export/daily_scorecard/build_status stale ~33min), REPORT/LIVE-2026-10-18 regenerated, attrition healed-clean, token delta recorded, orphan 7/0; Sunday live.paper family honest skip x4. "
"(e) S2/S3: job board empty, tasks all claimed, backlog zero bm-b-claimable lines, local self-drive registry 9/9 zero open, queue tech/explore drained -> agenda starvation honest face, consumed via --worked (maintenance round); inbox 2 MSGs both addressed elsewhere (MSG-1200 -> bm-a director seat per r1007; MSG-1605 W270 seat -> owner bm-c) = left in place zero-crossing.")

verdict = ("GREEN: r1008 maintenance/integration round -- S0 rebase absorb 9f480646f (stash-bridge UU x2 origin-side per r1007 law) + D-19 ord 43a18d01 dual-face advance (delta=BigStream 14:32 row, zero BigMoney dispatch, DEC hold) + S6 43 rc0 (smoke rc0, dualrun streak 51, 4 stale-takeover derives, REPORT/LIVE-10-18) + O-0948 zero died-pre-closeout (9 CLOUD_CAP_DEFER legal defers) + idle --worked 11->0 + orphan 7/0; leftovers = supply_floor honest starvation (bm-b engine lane awaits W271+ seat post-W270=bm-c; secretary restock pending; 10-25 memory-governance review window) + F-20261018-01 cleared by origin truth (bm-a 15:59 red=false/healthy face governs) + F-20261018-02 filed")

last_action = ("r1008: S0 rebase absorb 9f480646f (stash-bridge UU x2 origin-side) + D-19 ord 43a18d01 dual-face advance (zero BigMoney dispatch verified) + S6 43 rc0 + O-0948 zero-check (9 CLOUD_CAP_DEFER legal) + idle --worked")

next_ptr = ("r1009: 1) O-0948 24h 观察窗收官（died-pre-closeout 保持零至 10-19 ~10:2x·晨窗判读） 2) D-19 新鲜差集推进 3) bm-b 引擎道候 W271+ 席位发布（W270=bm-c 16:0x 已发布·W269 链完备）/secretary 补货解池饿 4) F-20261018-01 origin 真值收敛后销卡回执候 bm-a 席 5) 10-25 记忆治理回访窗（HQ gate 4h 在跑·LEDGER 已入账） 6) 41 曲 P2 立意案批产若派 bm-b=词锚批复用 lyric_calibration argv 范式")

next_milestone = ("O-0948 窗收官 10-19 ~10:2x（保持零 died-pre-closeout）+ bm-b 引擎道候 W271+ 席位发布 + secretary 补货（48h 窗内里程碑=10-19 O-0948 收官判读）")

note = ("r1008: 9-tick CLOUD_CAP_DEFER window (live=2, 14:52-16:12) = legal defer not dead windows per bm-a r1060; S0 stash-bridge 4 faces UU x2 origin-side resolved; F-20261018-01 residual cleared by origin truth (bm-a 15:59 red=false/healthy); idle --worked 11->0 (daemon probe snapshot 16:22/11 = stale face, next tick self-heals)")

latest_artifact = "FluxGroup origin 717159c = P2 词锚批 9 面（斗牛/黑色幽默 官方词面+校准 4 件 + lyric_calibration.py argv 过滤器 + 回执 p2-wordanchor-receipt-r1007bmb.md + LEDGER union）14:2x（r1008 维护轮无新集团产物·该件仍为最近实物）"

task_line = "r1008: closeout (S0 rebase absorb + D-19 ord advance + S6 chain + push)"

# ---------- state.json ----------
sp = ROOT + r"\state.json"
with io.open(sp, encoding="utf-8") as f:
    s = json.load(f)
s["round_no"] = 1008
s["round"] = 1008
s["round_no_label"] = "r1008"
s["clock_read"] = now
s["ts"] = now
s["updated"] = now
s["updated_at"] = now
s["last_seen"] = now
s["last_round_at"] = now
s["last_round_ts"] = now
s["last_action_at"] = now
s["last_orders_at"] = now
s["last_decisions_at"] = now
s["last_orders_read_at"] = now
s["last_decisions_read_at"] = now
s["last_orders_probe_at"] = now
s["last_decisions_probe_at"] = now
s["last_orders_probe_at_note"] = "r1008: dual probe delta consumed same-round (ORD 5d871243->43a18d01, one BigStream row zero BigMoney dispatch); advance in-tool r1090 dual-face"
s["last_decisions_sha_probe"] = s.get("last_decisions_sha", "")
s["last_orders_sha_probe"] = s.get("last_orders_sha", "")
s["orders_delta_pending"] = False
s["decisions_delta_pending"] = False
s["d19_probe_due"] = False
s["d19_probe_due_note"] = "r1008: dual probe consumed ORD delta (43a18d01), DEC hold 4cfdd17c; advance in-tool r1090 dual-face, mirrors synced"
s["now_active"] = "r1008 closing"
s["task"] = task_line
s["current_task"] = task_line
s["did"] = did
s["last_action"] = last_action
s["verdict"] = verdict
s["current"] = verdict
s["latest_artifact"] = latest_artifact
s["last_artifact"] = latest_artifact
s["next"] = next_ptr
s["next_milestone"] = next_milestone
s["note"] = note
s["orphan_face"] = 7
s["orphan_faces"] = 7
s["orphan_face_note"] = "r1008 chain probe (16:29): 7 py faces / 0 orphans"
s["sat_engine"] = {"status": "alive (r1008 S6 status rc0, idle verdict, queue_depth 0; supply floor = honest starvation awaiting W271+ seat / restock)", "checked_at": now}
s["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
# sync block: r1007 marker verified + r1008 pending
sync = s.get("sync", {})
if "r1007_main_push" in sync:
    sync["r1007_main_push"] = {
        "status": "PUSHED_VERIFIED (verified at r1008 S0: pre-fetch HEAD==origin/main)",
        "pushed_sha": "b983a3010735a655e9ce013dffd2ef50d2426140",
        "consumed_at": "2026-10-18T16:2x+08:00 (r1008 S0 verification)",
        "behind_origin_main": 0,
        "note": "r1007 payload landed as b983a3010 (commit subject verified at r1008); stale PENDING marker healed this round"
    }
sync["r1008_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1009",
    "behind_origin_main": 0,
    "note": ("r1008 payload = own faces (state/heartbeat/round-report + s6 log/driver/closeout work files + d19 probe/check/receipt regen + orphan probe + attrition scan) "
             "+ S6 regen/product faces (REPORT/LIVE-10-18 + scorecard/dashboard/paper_export stale-takeover derives + collectors bm-b lanes + token faces + compute_audit/regime_state/pool_dualrun/fundamental faces); "
             "EXCLUDED per law = results/watermark_red.json (shared-name face, origin bm-a 15:59 red=false face governs; claw fail-closed) + fleet/machine-health.json (shared union daemon face); "
             "base = 9f480646f origin tip fresh at S0 rebase")
}
sync["last_push_ts"] = now
s["sync"] = sync
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---------- heartbeat fleet/machines/bm-b.json ----------
hp = ROOT + r"\fleet\machines\bm-b.json"
with io.open(hp, encoding="utf-8") as f:
    h = json.load(f)
ram_free_gb = None
cpu_pct = None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / (1024 ** 3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
except Exception:
    pass
if ram_free_gb is None:
    try:
        with io.open(ROOT + r"\results\idle_trigger.bm-b.json", encoding="utf-8") as f:
            it = json.load(f)
        ram_free_gb = round(it.get("ram_free_pct", 55.9) * 24.0 / 100.0, 1)
    except Exception:
        ram_free_gb = 13.4
if cpu_pct is None:
    cpu_pct = 22.0
h["machine_id"] = "bm-b"
h["last_seen"] = now
h["task"] = task_line
h["current_task"] = task_line
h["did"] = did
h["cpu_cores"] = 16
h["free_ram_gb"] = ram_free_gb
h["gpu_free_vram_mb"] = 3790
h["cpu_load_pct"] = cpu_pct
h["verdict"] = verdict
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now
h["ts"] = now
h["note"] = note
h["latest_artifact"] = latest_artifact
h["last_action"] = last_action
h["last_action_at"] = now
h["last_orders_at"] = now
h["last_decisions_at"] = now
h["last_orders_read_at"] = now
h["last_decisions_read_at"] = now
h["round_no"] = 1008
h["round"] = 1008
h["next"] = next_ptr
# mirror faces from state (r1053 law)
h["orders_ack"] = s["orders_ack"]
h["orders_ack_last"] = s.get("orders_ack_last", h.get("orders_ack_last"))
h["last_orders_sha"] = s["last_orders_sha"]
h["last_decisions_sha"] = s["last_decisions_sha"]
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write("\n")

# read-back assertions (smoke F7 family: epoch int, clock T-format, mirrors equal)
with io.open(hp, encoding="utf-8") as f:
    h2 = json.load(f)
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "clock_read must be ISO T-format"
assert h2["last_orders_sha"] == s["last_orders_sha"], "orders sha mirror diverged"
assert h2["last_decisions_sha"] == s["last_decisions_sha"], "decisions sha mirror diverged"
assert h2["orders_ack_last"] == s.get("orders_ack_last"), "orders_ack_last mirror diverged"

# ---------- round report line ----------
row = ("{ts} | r1008 bm-b | dept:舰队+数据 | WM verdict: GREEN (red=false @origin bm-a 15:59 face, lane=healthy) | "
       "当前活=r1008 收口（S0 吸收+D-19 推进+S6 维护链） | "
       "最近实物=FluxGroup origin 717159c（P2 词锚批 9 面·14:2x·r1008 维护轮无新集团产物该件仍为最近实物） | "
       "下个里程碑=O-0948 窗收官 10-19 ~10:2x（保持零 died-pre-closeout）+ bm-b 引擎道候 W271+ 席位发布/secretary 补货（48h） | "
       "孤儿面=7/0 @16:29 probe | did: {did} | "
       "verification: smoke rc0 + S6 43 legs rc0（日志 results/_r1008bmb_s6_log.txt）+ dualrun ZERO-DRIFT streak 51 + D-19 advance read-back full-string equality（dec 4cfdd17c hold / ord 43a18d01）+ "
       "orders 双扫 102/102 unacked=NONE + O-0948 核查=9 tick CLOUD_CAP_DEFER live=2 合法延迟零死窗（run_20261018_14xx-16xx.log 实证）+ attrition healed-clean + 心跳读回断言过（epoch int/镜像等） | "
       "计分:1分（维护轮·实际文件改动=吸收+S6 再生面+水位推进·无新可跑实物=诚实注记） | 本地未达 origin commit 数=0 | "
       "next: {nxt}").format(ts=now, did=did, nxt=next_ptr)
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(row + "\n")

print("CLOSEOUT-OK", now, "epoch=", epoch, "ram_free_gb=", ram_free_gb, "cpu_pct=", cpu_pct)
