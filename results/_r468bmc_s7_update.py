"""r468 bm-c S7 updater: state-bm-c.json + heartbeat + round report line.
Programmatic json writes + json.loads self-verify (state write-back law),
epoch int + clock T-sep (R170/R178/R262 laws). File-out for report append."""
import datetime
import json
import os
import re
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(REPO, "round_reports-bm-c.md")
NOW = datetime.datetime.now()
NOW_T = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
NOW_S = NOW.strftime("%Y-%m-%dT%H:%M:%S")
NOW_SP = NOW.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
DEC_SHA = "4E5BE321F9B7A15D7F58BAB3771ECF329534EED8D30B090CDAC4E9F151D911DC"

CT = ("当前活: golden-week watch + D-19 consumption batch (group D-20261004-03..06; D-20261004-05 "
      "dispatched BigMoney receipts) + D-02-03 fix-1 scripts-face port COMPLETED same round | "
      "最近实物: HQ-FEEDBACK F-20261004-01 (four-row receipt) + scripts/saturation_engine.py "
      "fix-1 port (T-168 done; selftest 11 legs + stale-N4 leg heal) + results/_r468bmc_s6_log.txt "
      f"(S6 38/38 rc0) @ {NOW_T} | 下个里程碑: fund-trio finalize window 10-05 10:30 (bm-b owner; "
      "QUALITY long-pole 567/2000); D-20261004-02①②③ receipt window 10-06 00:00; market reopen "
      "10-09; next 5x=r470")

DID = ("r468 bm-c golden-week watch round + D-19 CHANGED consumption batch + T-168 port same-round: "
       "(1) S0: no rebase leftovers; round-start dirty = 2 own satengine daemon lane faces; "
       "HEAD==origin/main zero-diff. (2) S0.5: orders 153/153 zero un-acked; inbox 0; D-19 CHANGED "
       "EB14B510 -> 4E5BE321: consumed D-20261004-03/04/05/06 -- 05 = BigMoney receipt dispatch. "
       "(3) CORE PRODUCT 1: HQ-FEEDBACK.md F-20261004-01 receipt (D-02-02 principal complete w/ "
       "3-task XML InteractiveToken evidence + r576 S4U-first retirement; D-02-06 13 pit-files "
       "314,851B byte+md5 reconciliation lines + main 62,651B rebound honest + line 16,719B, "
       "closeout 10-07 kept; D-02-05 perpetual_faces selftest 9/9 leg-9 pin evidence presented "
       "early). (4) CORE PRODUCT 2: D-02-03 fix-1 scripts-face port (T-2026-10-04-168-P1 opened "
       "-> WM RED FLAG fired (py_low_with_work_cands: unclaimed ticket = CEO immediate-law "
       "violation caught by the watermark system as designed) -> claimed+ported SAME ROUND: "
       "_MOD_WATCH + _mtime_stale + _refresh_family_modules (tick-start, reload+rebind FAMILIES, "
       "mid-surgery keep-view retry) + selftest leg-9 (9 assertions) -> scripts-face selftest 11 "
       "legs PASS + Tools-face regression 46/46 + AST rc0; BONUS pre-existing red healed: stale "
       "N4 real-tree assertion 12(B1+B2)->18(B1+B2+B3) -- registrar-side miss (B3 registered in "
       "n4 module S11 leg, engine selftest leg not updated); reload-spec fixture pit documented "
       "pit-engine.md; py_watermark re-probe = py_low_board_clear (red self-healed). (5) S1 "
       "smoke 48/48 (bare re-run after my own pipeline truncation slip, r460 law self-applied). "
       "(6) S2: boards empty before T-168. (7) S3: fund-trio NULLS V734/Q567/D418 of 2000 (delta "
       "0 vs r467, owners=bm-b claims healthy age 11.0min). (8) S6 38/38 rc0 NON-ZERO=none "
       "(dualrun streak 51; update_daily golden-week 0 new rows; market_regime ORANGE shadow "
       "days=2; REPORT/LIVE idempotent regen). (9) S7: loop pin5 in place + watchdog in place; "
       "claws parity TRUE x2; attrition CLEAN rc0.")

NEXT = ("(a) r469 watch rounds (finalize window opens 10-05 10:30, bm-b owner; QUALITY long-pole "
        "567/2000). (b) D-20261004-02①②③ receipt window 10-06 00:00 (data_deps local-presence "
        "gate + probe-seed siting law + S4U D-19 real-path fallback wiring). (c) O-2115/O-2030 "
        "acceptance 10-08; market reopen 10-09. (d) Next 5x = r470.")

VERIFY = ("S6 38/38 rc0 NON-ZERO=none (results/_r468bmc_s6_log.txt, PARITY PASS + chain-end); "
          "smoke 48/48; orders 153/153 zero-diff; D-19 consumed EB14B510->4E5BE321 raw-blob; "
          "satengine Tools-face selftest 46/46 + scripts-face selftest 11 legs PASS (fix-1 port "
          "leg-9 + CAS legs; stale-N4 leg healed 12->18) + Tools regression 46/46 + AST rc0; "
          "perpetual_faces selftest 9/9 (leg-9 skip-semantics-pin D-20261002-05); py_watermark "
          "re-probe py_low_board_clear (WM red self-healed after same-round claim+port); "
          "attrition CLEAN; claws parity TRUE x2; loop pin5 + watchdog in place; heartbeat "
          "epoch int + clock T-sep self-checked")

ROUND_SHORT = ("r468 bm-c: D-19 consumption -> F-20261004-01 four-row receipt + D-02-03 fix-1 "
               "scripts-face port SAME ROUND (T-168 done; WM red fired on open-unclaimed -> "
               "claimed+ported+11-leg selftest + stale-N4 heal) + fund-trio V734/Q567/D418 watch "
               "+ S6 38/38 rc0; smoke 48/48; orders 153/153")


def sample():
    d = {"cpu_pct": None, "idle_ram_gb": None, "gpu_free_mb": None}
    try:
        import psutil
        d["cpu_pct"] = round(psutil.cpu_percent(interval=1.0), 1)
        d["idle_ram_gb"] = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                           capture_output=True, creationflags=0x08000000, timeout=15)
        d["gpu_free_mb"] = int(r.stdout.decode("utf-8", "replace").strip().splitlines()[0])
    except Exception:
        pass
    return d


def main():
    smp = sample()
    # --- state-bm-c.json
    st = json.load(open(STATE, encoding="utf-8"))
    st["clock_read"] = NOW_T
    st["current_task"] = CT
    st["did"] = DID
    st["heartbeat_epoch_utc"] = EPOCH
    st["last_decisions_read_at"] = NOW_T
    st["last_decisions_sha"] = DEC_SHA
    st["last_round"] = ROUND_SHORT
    st["last_round_at"] = NOW_S
    st["last_round_ts"] = NOW_SP
    st["last_seen"] = NOW_S
    st["last_ts"] = NOW_SP
    st["round_no"] = 468
    st["updated"] = NOW_S
    st["updated_at"] = NOW_S
    st["verify"] = VERIFY
    st["next"] = NEXT
    if smp["cpu_pct"] is not None:
        st["cpu_pct"] = smp["cpu_pct"]
    if smp["idle_ram_gb"] is not None:
        st["idle_ram_gb"] = smp["idle_ram_gb"]
        st["ram_free_gb"] = smp["idle_ram_gb"]
        st["free_ram_gb"] = smp["idle_ram_gb"]
    with open(STATE, "w", encoding="utf-8", newline="") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    chk = json.loads(open(STATE, encoding="utf-8").read())
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$", chk["clock_read"]), "clock T-sep"

    # --- heartbeat fleet/machines/bm-c.json
    hb = json.load(open(HB, encoding="utf-8"))
    hb["activity_now"] = ("golden-week watch; D-19 consumption batch landed: F-20261004-01 four-row "
                          "receipt (D-20261002-02/03/05/06); D-02-03 fix-1 scripts-face port COMPLETED "
                          "same round (T-168 done; WM red fired on open-unclaimed -> claimed+ported, "
                          "11-leg selftest + stale-N4 heal); fund-trio NULLS V734/Q567/D418 of 2000 "
                          "(delta 0 vs r467), owners=bm-b claims healthy; finalize window opens "
                          "10-05 10:30 (bm-b owner); N1 closed per O-2115 sec-2")
    hb["clock_read"] = NOW_S
    if smp["cpu_pct"] is not None:
        hb["cpu_pct"] = smp["cpu_pct"]
        hb["cpu_util_pct"] = smp["cpu_pct"]
        hb["cpu_idle_pct"] = round(100 - smp["cpu_pct"], 1)
    if smp["idle_ram_gb"] is not None:
        for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
            hb[k] = smp["idle_ram_gb"]
    if smp["gpu_free_mb"] is not None:
        for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
                  "gpu_vram_free_mb", "gpu_idle_mb"):
            hb[k] = smp["gpu_free_mb"]
    hb["current_task"] = CT
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["last_seen"] = NOW_S
    hb["last_seen_at"] = NOW_S
    hb["latest_artifact"] = (f"HQ-FEEDBACK.md F-20261004-01 (four-row receipt) + "
                             f"scripts/saturation_engine.py fix-1 port (T-168 done, selftest 11 legs) + "
                             f"results/_r468bmc_s6_log.txt (S6 38/38 rc0) @ {NOW_S}")
    hb["next_milestone"] = ("fund-trio finalize window 10-05 10:30 (QUALITY long-pole 567/2000); "
                            "D-20261004-02①②③ receipt window 10-06 00:00; O-2115/O-2030 "
                            "acceptance 10-08; market reopen 10-09; next 5x=r470")
    hb["prod_lanes"] = ("FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2; "
                        "D-19 receipt batch landed (F-20261004-01); T-168 port DONE same round")
    hb["round_no"] = 468
    hb["round_no_label"] = "round 468 (bm-c)"
    hb["ts"] = NOW_S
    hb["updated"] = NOW_S
    hb["updated_at"] = NOW_S
    hb["verdict"] = ("GREEN (smoke 48/48; orders 153/153 zero delta; D-19 consumed EB14B510->4E5BE321; "
                     "WM red self-healed after same-round T-168 claim+port (re-probe "
                     "py_low_board_clear); satengine alive rc0 Tools face + scripts-face selftest 11 "
                     "legs + Tools 46/46; S6 38 legs rc0 fail=0 dualrun streak 51; attrition CLEAN; "
                     "trio owners healthy; PF selftest 9/9 leg-9 pin; zero cloud token)")
    with open(HB, "w", encoding="utf-8", newline="") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    chk2 = json.loads(open(HB, encoding="utf-8").read())
    assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch must be int"
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", chk2["clock_read"]), "hb clock"
    print("S7_UPDATE_DONE epoch", EPOCH, "cpu", smp["cpu_pct"], "ram", smp["idle_ram_gb"],
          "gpu_free", smp["gpu_free_mb"])


if __name__ == "__main__":
    main()
