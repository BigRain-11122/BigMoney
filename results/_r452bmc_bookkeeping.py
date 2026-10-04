"""r452 bm-c bookkeeping updater: state-bm-c.json + fleet/machines/bm-c.json.
Programmatic json.dump write + json.loads self-verify + isinstance(epoch,int)
per r645/r170 laws. Regenerable probe form; single-writer own files only."""
import json
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CPU = 5.0
RAM = 8.8
GPU = 14132

STATE_PATH = ROOT + r"\state-bm-c.json"
HB_PATH = ROOT + r"\fleet\machines\bm-c.json"

st = json.load(open(STATE_PATH, encoding="utf-8"))
st["round_no"] = 452
st["clock_read"] = NOW
st["cpu_pct"] = CPU
st["idle_ram_gb"] = RAM
st["gpu_free_vram_mib"] = GPU
st["heartbeat_epoch_utc"] = EPOCH
st["last_decisions_read_at"] = NOW
st["last_seen"] = NOW
st["last_ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["updated"] = NOW.replace("T", " ")
st["updated_at"] = NOW
st["current_task"] = ("r452 done (S6 37/37 rc0 per-round driver, self-caught double-run of chain "
                      "idempotent-zero-harm; FUND NULLS watch V629/Q477/D339; zero board/pool "
                      "claimable, N1 closed per O-2115 sec-2); next: fund-trio finalize window "
                      "opens 10-05 10:30 watchers, O-2115+O-2030 acceptance 10-08, HANDOVER 5x at r455")
st["did"] = ("r452 bm-c golden-week watch round: (1) S0: fetch behind=0 (origin==HEAD, no pull needed); "
             "round-start 4 dirty faces = bm-c own lane daemon faces (treadmill normal). (2) S0.5 orders "
             "152/152 first+second scan zero un-acked (canonical Tools/orders_diff.py) + D-19 MATCH "
             "EB14B510 (decisions watermark unchanged, zero consumption) + group orders.md SHA-1 MATCH "
             "68947C17 (first-probe SHA-256-vs-SHA-1 method mismatch false alarm self-refuted per "
             "r641/r645 prove-before-report law) + inbox 0. (3) S1 smoke 47/47; S2 boards: job_list empty "
             "+ fleet tickets 0 open (45 claimed); S3 satengine rc0 alive; watermark red=false "
             "next_pick=claimed moneyflow-IC other-lane; post_review zero new rows since 07:26:51 "
             "(bm-a R4 THEME_PERSIST_P1 prereg row last), zero new red; N1 W116+ held closed per "
             "O-2115 sec-2; pool ready x3 = FUND trio NULLS other-machine-owner faces (r622/r629 "
             "division law, watch-only). (4) MAIN OUTPUT: S6 37/37 rc0 NON-ZERO=none, full-leg log "
             "results/_r452bmc_s6_log.txt (dualrun ZERO-DRIFT streak 51; compute_audit zero flags; "
             "py_watermark py_low_board_clear legal idle; REPORT/LIVE-2026-10-04 faces regenerated; "
             "4 stale-takeover derives per O-2100 s2.4 STALE_MIN law, bm-a heartbeat stale 81min) -- "
             "per-round driver form results/_r452bmc_s6_chain.py (canon Tools driver untouched; driver "
             "parity guard AST+37-leg byte-equal PASS results/_r452bmc_driver_parity.py; self-caught: "
             "phantom --noop flag in evidence-extract command re-ran whole chain once = idempotent "
             "legs+lane guards so zero data harm, dualrun +1 honest green line; logged as round "
             "inefficiency). (5) FUND trio NULLS watch: V629/Q477/D339 of 2000 (+6/+6/+4 vs r451), "
             "three nulls.jsonl same-window fresh 07:34, cells 401x2 per family (VALUE dual-factor "
             "1604) + sens 500x3 all landed; evidence results/_r452bmc_fundnulls_watch.json. "
             "(6) S7 self-heal 4x green (loop pin5 no-op first-fire 07:45, watchdog registered "
             "first-fire 07:46, dual claws installed LF-normalized) + attrition CLEAN (4 ledgers, "
             "2 bm-a healed historical notes) + S7 orders second scan zero-diff.")
st["last_round"] = ("r452 bm-c: golden-week watch round: S6 37/37 rc0 _r452bmc_s6_log.txt (streak 51, "
                    "per-round driver form, canon untouched, self-caught double-run idempotent-zero-harm); "
                    "FUND NULLS watch V629/Q477/D339 (+6/+6/+4); orders/D19 MATCH; smoke 47/47; "
                    "group orders.md false-alarm self-refuted (SHA-1 MATCH)")
st["next"] = ("(a) FUND trio finalize window 10-05..10-09 watchers (D ETA 10-05 10:30 per bm-b r652; "
              "readiness probe bm-b r651/654 in-register do-not-rebuild; G-SEG GM ruling + VALUE passive "
              "crash bm-b fix pending). (b) O-2115 acceptance pack final run + O-2030 "
              "treasure-protection acceptance 10-08. (c) W116+ N1 supply reassess after fund-trio "
              "finalize. (d) HANDOVER 5x at r455. (e) Market reopen 10-09: data lanes resume "
              "verification.")
st["verify"] = ("S6 37/37 rc0 NON-ZERO=none (results/_r452bmc_s6_log.txt in-repo); smoke 47/47; "
                "orders 152/152 double-scan zero-diff; D-19 EB14B510 raw-bytes MATCH; group orders.md "
                "SHA-1 68947C17 MATCH; attrition CLEAN; dual claws in place; FUND watch evidence "
                "results/_r452bmc_fundnulls_watch.json")

with open(STATE_PATH, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
chk = json.loads(open(STATE_PATH, encoding="utf-8").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk["round_no"] == 452

hb = json.load(open(HB_PATH, encoding="utf-8"))
hb["round_no"] = 452
hb["clock_read"] = NOW
hb["cpu_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["cpu_idle_pct"] = 100 - CPU
hb["free_ram_gb"] = RAM
hb["idle_ram_gb"] = RAM
hb["ram_free_gb"] = RAM
for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
          "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb"):
    hb[k] = GPU
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["updated_at"] = NOW
hb["current_task"] = st["current_task"]
hb["activity_now"] = ("FUND trio NULLS burn watch (bm-b canonical, V629/Q477/D339 rising, finalize "
                      "window opens 10-05 10:30); N1 W116+ closed per O-2115 sec-2; golden-week "
                      "maintenance all-green")
hb["latest_artifact"] = ("results/_r452bmc_s6_log.txt (S6 37/37 rc0 full-leg evidence; streak 51) + "
                         "results/_r452bmc_fundnulls_watch.json @ " + NOW)
hb["next_milestone"] = ("FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30; G-SEG GM + VALUE "
                        "passive pre-rulings); O-2115/O-2030 acceptance 10-08; market reopen 10-09")
hb["verdict"] = ("green (golden-week maintenance all-green; S6 evidence chain continuous; "
                 "board/pool/orders lawful; lane divisions respected; waiting state declared: "
                 "finalize window opens 10-05)")

with open(HB_PATH, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1, sort_keys=True)
chk2 = json.loads(open(HB_PATH, encoding="utf-8").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
assert chk2["round_no"] == 452
print("BOOKKEEPING OK", NOW, "epoch", EPOCH)
