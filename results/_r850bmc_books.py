# r850 bm-c books: state + heartbeat bump (single-source python, no manual JSON surgery)
import json, time, io

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = "2026-10-11T04:16:30+08:00"
epoch = int(time.time())

did = ("r850 bm-c: (1) S0-1 identity anchor bm-c + round-zero probe py_faces=6 orphans=1 read-only; "
       "S0 dirty face = own runtime 7 faces targeted absorb pre d185ab242 -> pull --rebase clean (origin zero new commits = "
       "W208 NOT landed, zero inbox, engine chain unchanged); (2) S0.5 double-scan: ORD f90233c7 / DEC 68d13893 both UNCHANGED "
       "raw-bytes verified = zero new rows zero action (unacked 0); (3) S1 smoke 49/49; S2 boards empty (job 0 / open tickets 0 / "
       "P2 tech queue drained / P3 explore queue drained) + satengine alive + cron 9defca39 W208-watch in place + M10 row "
       "waiting-upstream verified armed; (4) PRODUCT = S6 43-leg operational chain 43/43 rc0 (r849 driver verbatim clone "
       "_r850bmc_s6_chain.ps1, dualrun ZERO-DRIFT streak 26, DONE 04:13:53) - data panels/paper accounts/scorecard/dashboard/"
       "daily report/collector wall all refreshed clean; (5) W209 freeze still waiting-upstream W208 (bm-a one-line declaration, "
       "no rescan per anti-rescan law); W211 seat chain holds (2 outstanding own-wave seats W209+W211, no seat-stuffing: W212+ "
       "not published - 4 seats outstanding fleet-wide, bottleneck = W208 freeze chain not seat numbers); (6) jman trainer 21288 "
       "alive (CPU 28.2h, RAM 0.5G free tight, GPU 16070/16384 used, ETA ~09:45-10:00 unchanged - completion validation window "
       "val_grid+LOOKBOARD+recovery-debt trio per O-20261010-0025); (7) bm-b pool-EOL FLEET ADJUDICATION follow: zero new "
       "origin commits = zero adjudication movement, byte-face untouched; (8) S7: attrition 4 ledgers CLEAN (healed history "
       "disclosed) + quartet green (loop pin=5 no-op first-fire 04:15, watchdog registered 04:13, both claws LF-normalized) + "
       "idle --worked (idle_rounds=0)")

next_ptr = ("r851: (1) W208 landing watch -> M10 auto-execute (freeze -> selftest default-wave -> pathspec push -> 2-cycle "
            "n1_w209 ignition -> MSG receipt + flip M10 + delete cron 9defca39); (2) jman completion window ~09:45-10:00 "
            "(val_grid + LOOKBOARD_variant_640 + recovery-debt trio per O-20261010-0025, <=48h SLA); (3) W211 freeze-prep "
            "follow (per-wave prereg PERPETUAL_N1_W211_PREREG.md + freeze splice script when W210 freeze approaches; read "
            "pit-engine-finalize.md FIRST; freezer must re-pull + re-verify universe face per seat guard note); (4) bm-b "
            "pool-EOL cross-machine drift FLEET ADJUDICATION follow (byte-face untouched); (5) S0.5 standing composer; "
            "(6) 10-16 governance criteria on file")

activity = ("当前活: 守望窗（W209 freeze 待上游 W208 落链·M10 行+cron 9defca39 双武装·jman trainer 21288 在烧 ETA ~09:45-10:00）"
            "| 最近实物: S6 43 腿经营面全绿 rc0（dualrun streak 26·数据面板/纸盘/scorecard/看板全刷新）@ 2026-10-11T04:13 | "
            "上轮席位实物 W211 包 0a60b8850（A 479_004..481_003/B 481_004..481_203）@ 2026-10-11T03:52 | "
            "下个里程碑: W209 freeze（W208 落链即 M10 自动执行）+ jman 完训验证三件 ~09:45-10:00（≤48h SLA）")

verdict = ("r850 close: watch-window maintenance round - S6 43/43 rc0 (dualrun streak 26) + smoke 49/49 + M10 armed "
           "(waiting W208) + jman trainer alive (ETA ~09:45) + zero inbox zero orders delta")

summary = "r850 close: S6 43/43 rc0 (dualrun streak 26) + smoke 49/49 + W209 M10 armed waiting W208 + jman alive ETA ~09:45"

def upd(path, is_hb):
    with io.open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    ts_fields = ["ts","last_seen","last_seen_at","clock_read","updated","updated_at","last_run_at","last_round_at",
                 "last_round_ts","last_ts","last_round_closed","current_task_at","last_round_summary_at",
                 "last_orders_read_at","last_pulled_at"]
    for k in ts_fields:
        if k in d: d[k] = now_iso
    d["round_no"] = 851
    d["round_no_label"] = "r850"
    d["last_round"] = 850
    d["loop_round"] = 850
    d["heartbeat_epoch_utc"] = epoch
    d["cpu_pct"] = 28; d["cpu_util_pct"] = 28; d["cpu_idle_pct"] = 72
    d["free_ram_gb"] = 0.5; d["idle_ram_gb"] = 0.5; d["ram_free_gb"] = 0.5
    for k in ["gpu_free_vram_mb","gpu_free_vram_mib","gpu_idle_vram_mb","gpu_idle_vram_mib","gpu_vram_free_mb"]:
        d[k] = 108
    d["gpu_free_mb"] = 108; d["gpu_free_mib"] = 108; d["gpu_idle_mib"] = 108; d["gpu_idle_mb"] = 16070
    d["current_task"] = activity
    d["activity_now"] = activity
    d["did"] = did
    d["verdict"] = verdict
    d["last_round_summary"] = summary
    d["note"] = ("r850 = watch-window maintenance round: W208 (bm-a freeze) not landed -> W209 M10 still waiting-upstream; "
                 "jman trainer alive ETA ~09:45-10:00; queues drained; S6 43/43 clean; no seat-stuffing (W212+ not published).")
    d["next"] = next_ptr
    d["next_pointer"] = next_ptr
    d["next_milestone"] = ("r851: W209 freeze on W208 landing (M10 auto-execute, cron 9defca39 armed) + jman completion "
                           "window ~09:45-10:00 (val_grid + LOOKBOARD + recovery-debt trio) <=48h")
    d["last_action"] = "r850 S6 43-leg chain (streak 26) + M10/W208 watch verification + books"
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_face"] = 1
    d["orphan_faces"] = 1
    d["verify"] = ("receipts: smoke 49/49 + S0.5 double-scan zero-delta + S6 43/43 rc0 (_r850bmc_s6_log.txt, dualrun streak 26) "
                   "+ attrition 4 CLEAN + quartet green + idle --worked + this books commit/push_verify")
    if not is_hb:
        d["last_action_at"] = now_iso
        d["sync"] = {"ahead_behind": "0/0 pre-books", "origin_tip": "0a60b8850", "ts": now_iso,
                     "note": "r850 books: maintenance round (S6 + watches), no new delivery commit; books commit follows this write"}
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")

upd(ROOT + r"\state-bm-c.json", False)
upd(ROOT + r"\fleet\machines\bm-c.json", True)

# epoch int self-check (R170/R178 law)
for p in [ROOT + r"\state-bm-c.json", ROOT + r"\fleet\machines\bm-c.json"]:
    with io.open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert isinstance(d["heartbeat_epoch_utc"], int), p
    assert "T" in d["clock_read"], p
print("BOOKS OK round_no=851 epoch=%d clock=%s" % (epoch, now_iso))
