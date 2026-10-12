import json, time, datetime, subprocess, os

NOW = datetime.datetime.now().astimezone()
EPOCH = int(time.time())
CLOCK = NOW.isoformat(timespec="seconds")

# --- state-bm-c.json: round_no advance + ORD watermark + face fields ---
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 940
st["last_round"] = 940
st["last_round_at"] = CLOCK
st["last_round_ts"] = EPOCH
st["clock_read"] = CLOCK
st["last_seen"] = CLOCK
st["last_orders_sha"] = "7351cf2f4c3e55a43b0f5412a3f8fcea4e78c03629959defd335a6affec768e8"
st["last_orders_sha_method"] = "sha256 origin blob fresh-read r940 closeout"
st["current_task"] = "r940: W225 full cycle landed (finalize 918,789/K=492,920 five-key ALL PASS sec.7/8 backfilled) + W226 seat published + @bm-c ORD consumed O-20261012-2020/2025 (jman LoRA pulled+KF demo chain ignited PID 12620 + i2v wave A queued) + Monday bars landed papers legs run"
st["current_task_at"] = CLOCK
st["did"] = "W225 six-gate PRE-FINALIZE all-green run 3 consecutive (family-6 first zero-repair window) + finalize one-pass ledger identity EXACT + five-key ALL PASS + prereg sec.7/8 machine-read backfill + W226 seat probe derive rc0 ADMIT (A 512_004..514_003 staircase 86th + B 514_004..514_203) + MSG seat publish + S6 39 legs ALL rc0 (dualrun streak 35; update_daily Monday bar landed cutoff 10-12 +35 rows; LHB +83 rows; futures +1; fund_prem exit2 healed snapshot 1683 rows; REPORT/LIVE-2026-10-12 regenerated) + papers legs (live.paper enforce OK; t35 NO_EVIDENCE zero-pending marks-gap disclosed; t24 prospect 22/22 drift 0; promotion 0/22 honest) + ORD delta consumed (3 @bm-c MV-lane rows: O-20261012-2020 LoRA KF demo accepted-dead-window resumed + O-20261012-2025 CEO off-hours full-power handover + i2v wave A whitelist) + GPU idle caught -> fill-order law: jman LoRA CDN pull size-check PASS 469,315,352 + bmc_kf_i2v_chain.py detached ignite (KF 5-frame seed 9011 jman 0.8 -> i2v wave A 7 clips INT8 768P length 124) + attrition 4 CLEAN + quad self-heal (loop pin=5 no-op, watchdog 20:46, claws installed)"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no ->", st["round_no"])

# --- heartbeat fleet/machines/bm-c.json ---
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = CLOCK
hb["ts"] = CLOCK
hb["clock_read"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = 940
hb["cpu_cores"] = 32
try:
    fr = os.popen("wmic OS get FreePhysicalMemory /value").read()
    free_kb = int([l for l in fr.splitlines() if "FreePhysicalMemory" in l][0].split("=")[1])
    hb["free_ram_gb"] = round(free_kb / 1048576.0, 1)
except Exception:
    pass
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    u, mu, mt = [x.strip() for x in g.stdout.split(",")]
    hb["gpu_util_pct"] = int(u)
    hb["gpu_used_vram_mib"] = int(mu)
    hb["gpu_total_vram_mib"] = int(mt)
    hb["gpu_free_vram_mib"] = int(mt) - int(mu)
except Exception as e:
    hb["gpu_probe_error"] = repr(e)[:80]
hb["verdict"] = ("green: W225 FULL CYCLE landed (six-gate run-3 all-green + finalize 918,789/K=492,920 EXACT "
                 "five-key ALL PASS + sec.7/8 backfilled) + W226 seat published ADMIT A 512_004..514_003/B 514_004..514_203; "
                 "Monday bars landed cutoff 10-12 papers legs run; engine DRY post-W225 -> W226 chain armed; "
                 "@bm-c MV lane ignited PID 12620 (jman LoRA KF demo seed 9011 -> i2v wave A 7 clips INT8 768P)")
hb["now_active"] = ("2026-10-12 21:0x | r940 | bm-c absorb r938/r939 dead-window estates (seat+prereg+splice all landed by r938/r939; "
                    "sixgate/fivekey tools prepared unrun) -> this window full-cycle closeout + supply: W225 finalize one-pass "
                    "ledger 916,589+2,200=918,789 EXACT merged K=492,920 EXACT mu -0.09279 sigma 0.24509 w225-only -0.09782 "
                    "skill_line 1.1915->1.1914 delta -0.0001 five-key ALL PASS (key1 0.0050/key2 +0.0011pct/key3 0.0154/key4 -0.0001) "
                    "se_mu 0.000349 chain head; six-gate PRE-FINALIZE all-green = correct-phase run 3 consecutive + splice integrity "
                    "BOTH faces clean-equal = family-6 upgrade executed at r939 derive first zero-repair window; prereg sec.7/8 "
                    "machine-read backfilled | PRODUCT-2: W226 seat published (probe derive checked-rep rc0 ADMIT A 512_004..514_003 "
                    "staircase EIGHTY-SIXTH hops=1 + B 514_004..514_203 own-A exclusion hops=1; seed_admit FREE x2 512004/2000+514004/200; "
                    "origin vacancy 4-check; naive 511_804 projection correctly REFUSED by registered W225 B band) | S0.5 ORD delta TRUE "
                    "consumed 4d1986f7->7351cf2f: three @bm-c MV-lane rows O-20261012-2020 (jman LoRA 5-frame KF demo seed 9011 -- "
                    "accepted-dead-window 20:13 resumed this window: LoRA CDN pull size PASS 469,315,352 + chain ignited) + "
                    "O-20261012-2025 (CEO off-hours full-power handover, night window opened early) + @bm-c i2v wave A (7-frame "
                    "whitelist INT8 768P length 124, queued behind KF batch in chain PID 12620); DEC watermark 67403afa-sibling "
                    "match TRUE zero action | S1 smoke 49/49 | S6 39 legs ALL rc0: dualrun ZERO-DRIFT streak 35 + compute_audit "
                    "pool_starvation/supply_floor structural flags (armed response = W226 seat landed) + update_daily MONDAY BAR "
                    "LANDED cutoff 10-12 +35 rows/48 sym + LHB +83 rows cutoff 10-12 + futures SC +1 10-12 + fund_prem exit2 HEALED "
                    "snapshot 1683 rows + aggr_paper 20/20 marked through 10-12 + REPORT/LIVE-2026-10-12 + token delta 0 | papers "
                    "legs: live.paper enforce OK (x2 watch 2 PROBATION faces) + t35_open_fill NO_EVIDENCE zero-pending marks-lane "
                    "gap disclosed (bm-a dark) + t24 prospect 22/22 drift 0 + promotion 0/22 honest | GPU fill-order: idle caught "
                    "(0%/1.3GB queue empty) -> claimed @bm-c lane items per O-20261012-1505 self-claim engine law")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
v = json.load(open(hp, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written epoch int OK:", v["heartbeat_epoch_utc"])
