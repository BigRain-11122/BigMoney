"""r414 bm-a S7 close: round report line + state flip + heartbeat + MSG archive."""
import datetime
import json
import os
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + NOW.strftime("%z")[:3] + ":" + NOW.strftime("%z")[3:]


def cpu_pct():
    try:
        import psutil
        return round(psutil.cpu_percent(interval=1.0), 1)
    except Exception:
        return None


def free_ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        return None


def main():
    # 1) round report line (canon face = logs/iteration-loop/round_reports-bm-a.md)
    line = (
        f"{NOW_ISO} | r414 | WATERMARK VERDICT: GREEN (red=false, lane=healthy; py tail "
        "4.9/4.8/4.8% low-load = board 0 open + pool ready_unclaimed=0 + W6 single-shard "
        "bm-b in-flight 05:00:04 = legal-wait face per O-1820 meaning-law, no fabricated burn) "
        "| did: S0.5 orders 122/122 ack zero-unprocessed + inbox MSG-0450 receipted+archived "
        "by sender (bm-b r410) + decisions.md council-pending only (no repo lines); W4 chain "
        "gap found+closed same round: intake zero-face product was missing (W4 runner "
        "half-built by design, intake subcommand never registered; judge harvest r396 closed "
        "judge face only) -> fail-closed generator results/_r414bma_w4_intake_zeroface.py "
        "landed w4_intake.json (n_eligible=0 lawful-zero, vol G1 passes wild 0/260 none 0/140 "
        "calm 0/61 = 0/461 wave-wide, schema mirror r407 W5 precedent, single-shot guard "
        "idempotent); T-97/T-98/T-114 three tickets flipped done (claimed-by-bm-a asserted, "
        "full chains verified on disk, result_ref carries merged CEO report pointer per "
        "MSG-0415 terminal-notify request; verdicts W3/W4/W5 all zero-registration honest "
        "negative, 关线=合法产出); MSG-0515 F-04 declaration sent+self-archived; W6 zero "
        "touch (generate-0of1 bm-b 05:00:04 in-flight, anti-dup law); smoke 26/26; S6 37 legs "
        "rc=0 (market_clock ORANGE_COOL sleeves=4 activated=0; t35 open_fill PASS "
        "zero-pending 6; t24 prospect 22/22; promotion 0/22; daily_report+live_usage+"
        "build_status written) | verify: w4_intake.json reload self-check + generator re-run "
        "NO-OP; three ticket JSONs reload status=done result_ref present; pool_dualrun "
        "ZERO-DRIFT streak 2/3 (108 entries); compute_audit FLAG cap_violation+supply_floor "
        "HONESTLY CARRIED (cpu_total 85% non-BigMoney load; ready 1<floor 3 with W6 chain "
        "replenishing; ignition_sla 0 breach; zombies 0); schtasks loop Running pin=8 no-op + "
        "watchdog Ready + pre-commit claw identical | next: W6 generate landing watch (bm-b "
        "lane, screen slice opens after landing); W7 prereg trigger = W6 full chain consumed "
        "+ zero in-flight verdicts (NOT met -- no premature draft); supply floor watch; "
        "r415 5x HANDOVER recon"
    )
    canon = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
    with open(canon, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    # 2) state-bm-a.json flip r413 -> r414
    sp = os.path.join(ROOT, "state-bm-a.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 414
    st["did"] = ("r414: W4 intake zero-face gap closed (fail-closed generator, n_eligible=0 "
                 "lawful) + T-97/T-98/T-114 flipped done (W3/W4/W5 full chains verified, CEO "
                 "merged report pointer appended per MSG-0415) + MSG-0515 declaration + S6 37 "
                 "legs rc=0")
    st["verify"] = ("smoke 26/26; S6 37/37 rc=0; w4_intake reload+rerun NO-OP; tickets "
                    "reload status=done; pool_dualrun ZERO-DRIFT streak 2/3; audit flags "
                    "cap_violation+supply_floor honestly carried")
    st["next"] = ("W6 generate landing watch (bm-b lane) -> screen slice; W7 prereg trigger "
                  "check (W6 consumed + zero in-flight verdicts); r415 5x HANDOVER recon")
    st["last_round_at"] = NOW_ISO
    st["current_task"] = "r414: W4 intake zero-face + three wave-ticket closes + maintenance"
    st["updated"] = NOW_ISO
    st["round"] = "414"
    st["loop_round"] = "413"
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)

    # 3) heartbeat fleet/machines/bm-a.json
    hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
    hb = json.load(open(hp, encoding="utf-8"))
    hb["last_seen"] = NOW_ISO
    hb["current_task"] = "r414: W4 intake zero-face landed + T-97/98/114 done closes"
    hb["cpu_pct"] = cpu_pct()
    hb["free_ram_gb"] = free_ram_gb()
    hb["verdict"] = ("green; r414: W4 chain gap closed (w4_intake.json zero-face lawful, "
                     "fail-closed generator r407-precedent schema); T-97/T-98/T-114 done "
                     "(W3/W4/W5 chains verified complete, honest zero-registration negatives, "
                     "CEO merged report pointers appended per MSG-0415); orders 122/122; "
                     "smoke 26/26; S6 37 legs rc=0; compute_audit FLAG cap_violation (cpu 85% "
                     "non-BM) + supply_floor (ready 1/3, W6 replenishing) honestly carried; "
                     "W6 generate in-flight bm-b (zero touch)")
    hb["heartbeat_epoch_utc"] = int(time.time())
    hb["clock_read"] = NOW_ISO
    hb["round_no"] = 414
    hb["round"] = 414
    hb["loop_round"] = 413
    hb["task"] = "round-closed"
    with open(hp, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    # heartbeat self-check: epoch must be int (R170/R178 law)
    back = json.load(open(hp, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in back["clock_read"], "clock_read must be T-separated"

    # 4) archive own MSG-0450-precedent self-receipt
    src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260929-0515-bma-ALL-w3w4w5-ticket-closes.md")
    dst = os.path.join(ROOT, "fleet", "inbox", "processed",
                       "MSG-20260929-0515-bma-ALL-w3w4w5-ticket-closes.md")
    if os.path.exists(src):
        shutil.move(src, dst)
        print("MSG-0515 archived to processed (bm-b r410 self-archive precedent)")

    print("S7 close files written: report line r414 + state round_no=414 + heartbeat "
          f"(epoch int ok, {NOW_ISO}) + inbox archived")
    print("cpu_pct:", hb["cpu_pct"], "| free_ram_gb:", hb["free_ram_gb"])


if __name__ == "__main__":
    main()
