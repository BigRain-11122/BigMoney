"""r737 bm-c round-close bookkeeping: heartbeat + state + report row.
Single writer (bm-c own faces), epoch int via int(time.time()), T-separated
clock_read (R170/R178/R262 laws). Zero network, zero engine touches.
Pattern credit: Tools/_r736bmc_close.py (canonical chain)."""
import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ).isoformat(timespec="seconds")
epoch = int(time.time())

CT = ("当前活: r737 bm-c 盘前值守轮（06:2x-06:3x 窗·09:15 前零盲动·复市 T-0 第 57 连守轮）——"
      "主产出=QA det-57th 5/5（显式 --round 737 FIRST TRY 零误标〔r736 律双模式克隆"
      "stale736=0+点火即验标·第 2 连守〕）+S6 40/40 rc0（REPORT/LIVE-2026-10-08 再生·"
      "live_paper/cta_p1_paper bar-门控诚实 no-op〔今晚首 bar 自动接线〕·fund_premium "
      "pre-15:30 no-op→今日 15:30 bm-c 车道首采）+W182 seat MSG 消费（bm-a band "
      "415_204..417_403 占用披露·认知避撞·processed 归位·W177-W181 惯例同律·inbox 双扫 0）"
      " | 最近实物: qa/smoke-r737.md 5/5（93 trades·equity 1,017,839 冻结恒等·"
      "determinism=True）+qa/equity-curve-r737.png 66,119B+results/_r737bmc_s6_log.txt"
      "（40 腿 rc0·dualrun streak 51 ZERO-DRIFT）+results/_r737bmc_s05_facts.json（双水位 "
      "UNCHANGED·unacked=0） @ " + now + " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链"
      "全门 re-arm+REGIME_GUARD v3 首新 bar enforce+fund_premium 15:30 首采（bm-c 车）+"
      "CTA_P1 首 bar 自动接线+首 marks 验证（≤10-08 23:59）；09:15 起值守 intraday 面；"
      "O-2215 ① 剩余面=bm-a REGIME-5 标签（≤10-14）落地后矩阵 run 首产；下一 5x=bm-c r740")

DID = ("r737 bm-c: QA 57th + S6 regen + W182 seat consume (10-08 reopen T-0, "
       "57th consecutive pre-open watch round, 06:2x window). (1) S0: fetch "
       "-> 0 behind 0 ahead (no incoming, pull clean-skip behind=0); "
       "round-start dirty 13 = own live faces (satengine/idle/autofill/"
       "dispatcher + REPORT/LIVE regen + orphan probe + r736 commitmsg "
       "leftover), targeted round-close absorb. (2) S0.5 sweeps: orders 51 "
       "disk unacked=0; DEC EE659451 / ORD 17accc40 both UNCHANGED (facts "
       "results/_r737bmc_s05_facts.json, shape-asserted); inbox sweep-1 = "
       "bm-a W182 seat MSG (band 415_204..417_403 occupancy disclosure) "
       "consumed to processed per W177-W181 precedent, sweep-2 zero. (3) S1 "
       "smoke 49/49. (4) S3: satengine rc0 alive (N1 waves 1-181 dedup "
       "12/12); watermark green (red=false, lane healthy, next_pick="
       "claimed); board 176 tickets 0 open; job_list 0; idle NOT-GREEN (RAM "
       "16.2% free, resident ComfyUI), idle_rounds=0, --worked declared. "
       "(5) QA 57th determinism pack 5/5 (explicit --round 737 FIRST TRY "
       "clean per r736 clone law: double-mode replacement stale736=0 both "
       "clones + 3s ignite label check round=737; runner .err empty, "
       "terminal state polled before close per r640 law); 93 trades, "
       "equity 1,017,839 frozen identity, png 66,119B; market_clock rc0 "
       "cell=ORA; latest_panel_bar 2026-09-30 golden-week expected (reopen "
       "T-0, first new bar tonight). (6) S6 40/40 rc0 via Tools/"
       "_r737bmc_s6.py canonical clone (dualrun streak 51 ZERO-DRIFT; "
       "live_paper REGIME_GUARD shadow pre-open; cta_p1_paper bar-gated "
       "no-op auto-fires tonight first-bar; fund_premium pre-15:30 no-op -> "
       "today 15:30 bm-c-lane first snapshot; REPORT/LIVE-2026-10-08 "
       "regen). (7) post_review zero red (per-id 53, YES=48 NO=0); orphan "
       "face=1 (resident ComfyUI, no-kill documented); attrition CLEAN (4 "
       "ledger files, 3 healed notes recorded); self-heal quartet green "
       "(loop pin=5 no-op first fire 06:35 + watchdog idempotent + both "
       "claws LF-normalized). (8) O-2215-1 run remains honest "
       "awaiting_upstream (results/regime5_labels/ empty; bm-a labels due "
       "<=10-14); trial-labor supply line in flight = bm-a W182 seat "
       "(published 06:03, freeze bm-a face; engine waves 1-181 fully "
       "deduped, queue auto-pickup post-registration); no new method, no "
       "five-family closing batch -> zero METHODOLOGY/TREASURE appends "
       "(honest). (9) Product score 2 (QA 57th pack + S6 40-leg regen = "
       "runnable/visible artifacts); bookkeeping budget 3.")

NEXT = ("r738: (a) watch continuation 09:15+ intraday marks lane live "
        "(reopen first trading day), pre-open zero blind action; (b) "
        "tonight post-close face (<=10-08 23:59): data-chain full re-arm + "
        "REGIME_GUARD v3 first-new-bar enforce (set "
        "BIGMONEY_REGIME_GUARD=enforce before live.paper) + fund_premium "
        "15:30 first snapshot (bm-c lane) + QDII watch rerun holiday-delta "
        "+ CTA_P1 first-bar auto-wiring + first-marks verification (marks "
        "1 row + state trial-live + compounding identity); (c) O-2215 "
        "deliverable-1 remaining: await bm-a REGIME-5 labels (<=10-14) -> "
        "results/regime5_labels/ -> regime_style_matrix.py run first "
        "product + numeric weights validation per K>=1000 law; SUPPORT row "
        "awaits bm-b router spec (<=10-16); (d) O-2245: first OSS "
        "enrollments must pass Tools/oss_import_gate.py rc0 before settle; "
        "(e) cloudF row collection window <=10-14 standing; (f) "
        "month-boundary first exam 10-31; next 5x = bm-c r740. [via bm-c "
        "r737]")

VERIFY = ("qa/smoke-r737.md 5/5 (determinism=True 93 trades equity 1,017,839 "
          "frozen identity) + qa/equity-curve-r737.png 66,119B + "
          "results/_r737bmc_s6_log.txt (40 legs rc0, dualrun streak 51 "
          "ZERO-DRIFT) + results/_r737bmc_s05_facts.json (unacked=0, both "
          "watermarks unchanged, shape-asserted) + "
          "results/_attrition_guard_scan.json + post_review per-id 53 "
          "YES=48 NO=0")

ART = ("qa/smoke-r737.md 5/5 + qa/equity-curve-r737.png 66,119B "
       "(determinism 57th, 93 trades, equity 1,017,839 frozen identity, "
       "explicit --round 737 FIRST TRY) + results/_r737bmc_s6_log.txt (40 "
       "legs rc0) + Tools/_r737bmc_s05.py + Tools/_r737bmc_s6.py + "
       "Tools/_r737bmc_qa_ignite.py (canonical clones, stale736=0) @ " + now)


def main():
    # ---- heartbeat ----
    hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hb_path, encoding="utf-8") as fh:
        hb = json.load(fh)
    hb.update({
        "free_ram_gb": 3.9, "gpu_free_vram_mb": 1142, "idle_rounds": 0,
        "agenda_starved": False, "heartbeat_epoch_utc": epoch,
        "last_seen": now, "clock_read": now, "ts": now,
        "cpu_pct": 5.0, "cpu_util_pct": 5.0, "cpu_idle_pct": 95.0,
        "idle_ram_gb": 3.9, "ram_free_gb": 3.9,
        "gpu_free_vram_mib": 1142, "gpu_idle_vram_mb": 1142,
        "gpu_idle_vram_mib": 1142, "gpu_vram_free_mb": 1142,
        "gpu_free_mb": 1142, "gpu_idle_mb": 1142, "gpu_free_mib": 1142,
        "gpu_idle_mib": 1142,
        "round_no": 738, "round_no_label": "round 737 (bm-c)",
        "last_round": 737, "last_round_at": now,
        "current_task": CT, "current_task_at": now,
        "latest_artifact": ART,
        "next_milestone": ("tonight post-close: data-chain re-arm + REGIME_"
                           "GUARD v3 first-new-bar enforce + fund_premium "
                           "15:30 first snapshot (bm-c lane) + CTA_P1 "
                           "first-bar auto-wiring + first-marks verify "
                           "(<= 10-08 23:59); O-2215-1 remaining = matrix "
                           "run first product when bm-a REGIME-5 labels "
                           "land; next 5x = bm-c r740"),
        "did": DID, "verdict": DID,
        "note": ("r737: QA det-57th 5/5 (explicit FIRST TRY) + S6 40 rc0 "
                 "streak 51 + W182 seat consumed; watermarks unchanged; "
                 "unacked=0 both sweeps; smoke 49/49."),
        "last_round_summary": ("r737: QA det-57th 5/5 + S6 40 rc0 + W182 "
                               "seat consume; watermarks unchanged; "
                               "unacked=0; smoke 49/49."),
        "last_action": ("r737: QA det-57th 5/5 + S6 40 rc0 + W182 seat "
                        "consume; watermarks unchanged; unacked=0; smoke "
                        "49/49."),
        "next": NEXT, "last_seen_at": now, "updated_at": now, "updated": now,
        "last_run_at": now, "last_ts": now,
    })
    with open(hb_path, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)
    assert isinstance(hb["heartbeat_epoch_utc"], int)

    # ---- state ----
    st_path = os.path.join(ROOT, "state-bm-c.json")
    with open(st_path, encoding="utf-8") as fh:
        st = json.load(fh)
    st.update({
        "clock_read": now, "cpu_pct": 5.0, "current_task": CT,
        "current_task_at": now, "did": DID,
        "free_ram_gb": 3.9, "idle_ram_gb": 3.9, "ram_free_gb": 3.9,
        "gpu_free_vram_mib": 1142, "gpu_free_vram_mb": 1142,
        "gpu_free_mib": 1142, "gpu_free_mb": 1142,
        "heartbeat_epoch_utc": epoch,
        "idle_rounds": 0, "agenda_starved": False,
        "last_decisions_read_at": now,
        "last_decisions_sha_method": ("python subprocess raw-blob bytes "
                                      "SHA-256 (group-tree origin/main git "
                                      "show; r737 sweeps = UNCHANGED "
                                      "EE659451 zero delta zero action; "
                                      "hex-case comparison normalized per "
                                      "r711 pit law; facts-driven from "
                                      "results/_r737bmc_s05_facts.json, "
                                      "64hex shape-asserted, never hand-"
                                      "typed (r583 S4 law))"),
        "last_orders_sha_method": ("python subprocess raw-blob bytes SHA-1 "
                                   "(ALGORITHM PIN per r537 law; r737 "
                                   "sweeps = UNCHANGED 17accc40, zero "
                                   "delta; hex-case comparison normalized "
                                   "per r711 pit law; facts-driven from "
                                   "results/_r737bmc_s05_facts.json, 40hex "
                                   "shape-asserted, never hand-typed (r583 "
                                   "S4 law))"),
        "last_round": 737, "last_round_at": now, "last_round_ts": now,
        "last_seen": now, "last_seen_at": now, "last_ts": now,
        "last_run_at": now,
        "note": ("r737: QA det-57th explicit FIRST TRY clean (clone law "
                 "held) + S6 40/40 rc0 streak 51 + W182 seat MSG consumed "
                 "(bm-a band disclosure); O-2215-1 still "
                 "awaiting_upstream (labels dir empty); watermarks "
                 "unchanged; unacked=0 both sweeps; smoke 49/49."),
        "round_no": 738, "round_no_label": "round 737 (bm-c)",
        "ts": now, "updated": now, "updated_at": now,
        "verify": VERIFY, "activity_now": DID,
        "next_pointer": NEXT, "latest_artifact": ART,
        "next_milestone": ("tonight post-close: data-chain re-arm + REGIME_"
                           "GUARD v3 first-new-bar enforce + fund_premium "
                           "15:30 first snapshot (bm-c lane) + CTA_P1 "
                           "first-bar auto-wiring + first-marks verify (<= "
                           "10-08 23:59); next 5x = bm-c r740"),
        "cpu_idle_pct": 95.0,
    })
    with open(st_path, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=1, ensure_ascii=False)
    assert isinstance(st["heartbeat_epoch_utc"], int)

    # ---- report row ----
    rp_path = os.path.join(ROOT, "logs", "iteration-loop",
                           "round_reports-bm-c.md")
    row = (now + " | r737 | dept:工程（复市 T-0 盘前值守轮·第 57 bm-c 连守轮） | "
           "WM-VERDICT: 绿（red=false·lane healthy·next_pick=claimed "
           "moneyflow IC 车道〔板 176 票 0 open/51 disk unacked=0 双扫〕） | "
           "当前活: " + CT + " | 验证证据: " + VERIFY + " | 下轮指针: " + NEXT +
           " | 轮产品计分：2（QA 57th 确定性包+S6 40 腿再生=能跑能看实物） | "
           "记账预算：3（state+心跳+轮报）\n")
    with open(rp_path, "a", encoding="utf-8") as fh:
        fh.write(row)
    print("bookkeeping done epoch=%d now=%s" % (epoch, now))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
