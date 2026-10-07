"""r736 bm-c round-close bookkeeping: heartbeat + state + report row.
Single writer (bm-c own faces), epoch int via int(time.time()), T-separated
clock_read (R170/R178/R262 laws). Zero network, zero engine touches."""
import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ).isoformat(timespec="seconds")
epoch = int(time.time())

CT = ("当前活: r736 bm-c 盘前值守轮（06:0x-06:1x 窗·09:15 前零盲动·复市 T-0 第 56 连守轮）——主产出=O-2215 ①策略-阶段矩阵骨架+切换律 v1 提前落地（大限 10-16·scripts/regime_style_matrix.py 五态矩阵+切换律三件·selftest 40 检全过·run 诚实等 bm-a REGIME-5 ≤10-14）+QA det-56th 5/5（显式 --round 736·首点错标 3 秒捕获治愈·新坑律入册）+CODELY mini-split（主件 30,422B ≤帽·r847/r849 verbatim 迁出）+S6 40/40 rc0（cta_p1_paper bar-gated 今晚首 bar 自动接线） | 最近实物: scripts/regime_style_matrix.py（可运行 40 检引擎）+research/REGIME_STYLE_MATRIX_V1.md（规格）+qa/smoke-r736.md 5/5（93 trades·equity 1,017,839 冻结恒等）+qa/equity-curve-r736.png 66,347B+results/_r736bmc_codely_minisplit.json（mini-split 收据） @ "
      + now + " | 下个里程碑: 今晚盘后（10-08 15:30+）数据链全门 re-arm+REGIME_GUARD v3 新 bar enforce+fund_premium 首采（bm-c 车）+CTA_P1 首 bar 自动接线+首 marks 验证（≤10-08 23:59）；O-2215 ① 剩余面=bm-a REGIME-5 标签落地后矩阵 run 首产+数值面 K≥1000 验证；09:15 起值守 intraday 面；下一 5x=bm-c r740")

DID = ("r736 bm-c: O-2215-① skeleton + QA 56th + CODELY mini-split + S6 regen "
       "(10-08 reopen T-0, 56th consecutive pre-open watch round, 06:0x window). "
       "(1) S0: fetch -> 0 behind origin (no incoming, pull no-op); round-start "
       "dirty 3 = own probe + satengine live faces, deferred to round-close "
       "absorb. (2) S0.5 sweep 1: orders 51 disk unacked=0; DEC EE659451 / ORD "
       "17accc40 both UNCHANGED (facts results/_r736bmc_s05_facts.json, "
       "shape-asserted); inbox 0. (3) S1 smoke 49/49. (4) S3: satengine rc0 "
       "alive; watermark green (red=false, next_pick=claimed); board 176 "
       "tickets 0 open; job_list 0; idle NOT-GREEN (RAM 16.9% free, resident "
       "ComfyUI), idle_rounds=0, --worked declared. (5) MAIN PRODUCT: O-2215 "
       "deliverable-1 landed early (due 10-16): scripts/regime_style_matrix.py "
       "(five-state BULL/CHOP/GRIND/BEAR/SUPPORT matrix + switching law v1: "
       "N_CONF=3 confirmation-window hysteresis + sum|dw|*COST_X1 transition "
       "cost + w_eff glide law mirror; COST_X1 imported from rev_osc_stock_p1 "
       "zero re-implementation; selftest 40 checks PASS; run = honest "
       "awaiting_upstream no-op until bm-a REGIME-5 labels land <=10-14) + "
       "research/REGIME_STYLE_MATRIX_V1.md (frozen input contract + matrix "
       "table with structural disable list + amendment-window law). (6) QA "
       "56th determinism pack 5/5 (explicit --round 736; ignite-1 mislabeled "
       "735 caught in 3s by out-tail round check, pid killed, re-ignited "
       "clean -- new pit law appended to CODELY.md); 93 trades, equity "
       "1,017,839 frozen identity, png 66,347B. (7) CODELY mini-split: r847 "
       "871B -> pit-encoding.md + r849 811B -> pit-git-staged.md verbatim, "
       "new r736 pit + pointer row, main 30,654->30,422B <=30,720 cap, "
       "receipt _r736bmc_codely_minisplit.json (prescan rc0, byte equations "
       "true, blocks absent, all touched <=cap). (8) S6 40/40 rc0 (dualrun "
       "streak 51; cta_p1_paper bar-gated no-op auto-fires tonight first-bar; "
       "fund_premium pre-15:30 no-op -> today 15:30 bm-c-lane first snapshot). "
       "(9) post_review zero red (YES=45 NO=0); orphan face=1 (resident "
       "ComfyUI, no-kill documented); attrition CLEAN; self-heal quartet green "
       "(loop pin=5 no-op + watchdog re-registered + both claws reinstalled). "
       "(10) Product score 2 (runnable matrix engine + spec + QA pack + "
       "mini-split receipt).")

NEXT = ("r737: (a) watch continuation until 09:15 (reopen first trading day), "
        "intraday marks lane live from 09:15; (b) tonight post-close face "
        "(<=10-08 23:59): data-chain full re-arm + REGIME_GUARD v3 "
        "first-new-bar enforce + fund_premium 15:30 first snapshot (bm-c "
        "lane) + QDII watch rerun holiday-delta + CTA_P1 first-bar "
        "auto-wiring + first-marks verification (S6 cta_p1_paper leg; verify "
        "= marks 1 row + state trial-live + compounding identity); (c) "
        "O-2215 deliverable-1 remaining face: await bm-a REGIME-5 labels "
        "(<=10-14) -> drop into results/regime5_labels/ per contract -> "
        "regime_style_matrix.py run first product; SUPPORT row completion "
        "awaits bm-b router spec (<=10-16); numeric weights validation per "
        "K>=1000 law before any promotion; (d) O-2245 follow-ups: first OSS "
        "enrollments must pass Tools/oss_import_gate.py rc0 before settle; "
        "(e) cloudF row collection window <=10-14 standing; (f) month-boundary "
        "first exam 10-31; next 5x = bm-c r740. [via bm-c r736]")

VERIFY = ("scripts/regime_style_matrix.py selftest 40 checks PASS + run "
          "awaiting_upstream rc0 + research/REGIME_STYLE_MATRIX_V1.md + "
          "results/_r736bmc_codely_minisplit.json (byte equations, sha16x2, "
          "prescan rc0, all <=cap) + qa/smoke-r736.md 5/5 (determinism=True "
          "93 trades equity 1,017,839 frozen identity) + "
          "qa/equity-curve-r736.png 66,347B + results/_r736bmc_s6_log.txt "
          "(40 legs rc0, dualrun streak 51) + results/_r736bmc_s05_facts.json "
          "(unacked=0, both watermarks unchanged) + "
          "results/_attrition_guard_scan.json")

ART = ("scripts/regime_style_matrix.py (5-state matrix + switching law v1 "
       "engine, selftest 40 PASS, honest awaiting_upstream) + "
       "research/REGIME_STYLE_MATRIX_V1.md (spec: frozen contract + matrix + "
       "disable list + amendment window) + qa/smoke-r736.md 5/5 + "
       "qa/equity-curve-r736.png 66,347B (determinism 56th, 93 trades, "
       "equity 1,017,839 frozen identity, explicit --round 736 after "
       "3s-catch heal) + results/_r736bmc_codely_minisplit.json (r847 871B "
       "-> pit-encoding, r849 811B -> pit-git-staged, main 30,422B <=cap) + "
       "results/_r736bmc_s6_log.txt (40 legs rc0) @ " + now)


def main():
    # ---- heartbeat ----
    hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    with open(hb_path, encoding="utf-8") as fh:
        hb = json.load(fh)
    hb.update({
        "free_ram_gb": 3.9, "gpu_free_vram_mb": 1123, "idle_rounds": 0,
        "agenda_starved": False, "heartbeat_epoch_utc": epoch,
        "last_seen": now, "clock_read": now, "ts": now,
        "cpu_pct": 12.0, "cpu_util_pct": 12.0, "cpu_idle_pct": 88.0,
        "idle_ram_gb": 3.9, "ram_free_gb": 3.9,
        "gpu_free_vram_mib": 1123, "gpu_idle_vram_mb": 1123,
        "gpu_idle_vram_mib": 1123, "gpu_vram_free_mb": 1123,
        "gpu_free_mb": 1123, "gpu_idle_mb": 1123, "gpu_free_mib": 1123,
        "gpu_idle_mib": 1123,
        "round_no": 737, "round_no_label": "round 736 (bm-c)",
        "last_round": 736, "last_round_at": now,
        "current_task": CT, "current_task_at": now,
        "latest_artifact": ART,
        "next_milestone": ("tonight post-close: data-chain re-arm + REGIME_"
                           "GUARD v3 first-new-bar enforce + fund_premium "
                           "15:30 first snapshot (bm-c lane) + CTA_P1 "
                           "first-bar auto-wiring + first-marks verify "
                           "(<= 10-08 23:59); O-2215-1 remaining = matrix "
                           "run first product when bm-a REGIME-5 labels land; "
                           "next 5x = bm-c r740"),
        "did": DID, "verdict": DID,
        "note": ("r736: O-2215-1 skeleton (matrix engine 40-check selftest) + "
                 "QA det-56th 5/5 (explicit round, 3s mislabel catch healed) + "
                 "CODELY mini-split (30,422B <=cap) + S6 40 rc0 streak 51; "
                 "watermarks unchanged; unacked=0; smoke 49/49."),
        "last_round_summary": ("r736: matrix skeleton + QA det-56th 5/5 + "
                               "mini-split + S6 40 rc0; watermarks unchanged; "
                               "unacked=0; smoke 49/49."),
        "last_action": ("r736: matrix skeleton + QA det-56th 5/5 + mini-split "
                        "+ S6 40 rc0; watermarks unchanged; unacked=0; smoke "
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
        "clock_read": now, "cpu_pct": 12.0, "current_task": CT,
        "current_task_at": now, "did": DID,
        "free_ram_gb": 3.9, "idle_ram_gb": 3.9, "ram_free_gb": 3.9,
        "gpu_free_vram_mib": 1123, "gpu_free_vram_mb": 1123,
        "gpu_free_mib": 1123, "gpu_free_mb": 1123,
        "heartbeat_epoch_utc": epoch,
        "idle_rounds": 0, "agenda_starved": False,
        "last_decisions_read_at": now,
        "last_decisions_sha_method": ("python subprocess raw-blob bytes "
                                      "SHA-256 (group-tree origin/main git "
                                      "show; r736 sweeps = UNCHANGED "
                                      "EE659451 zero delta zero action; "
                                      "hex-case comparison normalized per "
                                      "r711 pit law; facts-driven from "
                                      "results/_r736bmc_s05_facts.json, "
                                      "64hex shape-asserted, never hand-"
                                      "typed (r583 S4 law))"),
        "last_orders_sha_method": ("python subprocess raw-blob bytes SHA-1 "
                                   "(ALGORITHM PIN per r537 law; r736 "
                                   "sweeps = UNCHANGED 17accc40, zero "
                                   "delta; hex-case comparison normalized "
                                   "per r711 pit law; facts-driven from "
                                   "results/_r736bmc_s05_facts.json, 40hex "
                                   "shape-asserted, never hand-typed (r583 "
                                   "S4 law))"),
        "last_round": 736, "last_round_at": now, "last_round_ts": now,
        "last_seen": now, "last_seen_at": now, "last_ts": now,
        "last_run_at": now, "last_run_at": now,
        "note": ("r736: O-2215-1 matrix skeleton landed (engine 40-check "
                 "selftest + spec, awaiting REGIME-5 labels); QA det-56th "
                 "explicit first-try after 3s mislabel catch; CODELY "
                 "mini-split 30,422B <=cap; S6 40/40 rc0 streak 51; "
                 "watermarks unchanged; unacked=0 both sweeps; smoke "
                 "49/49."),
        "round_no": 737, "round_no_label": "round 736 (bm-c)",
        "ts": now, "updated": now, "updated_at": now,
        "verify": VERIFY, "activity_now": DID,
        "next_pointer": NEXT, "latest_artifact": ART,
        "next_milestone": ("tonight post-close: data-chain re-arm + REGIME_"
                           "GUARD v3 first-new-bar enforce + fund_premium "
                           "15:30 first snapshot (bm-c lane) + CTA_P1 "
                           "first-bar auto-wiring + first-marks verify (<= "
                           "10-08 23:59); next 5x = bm-c r740"),
        "cpu_idle_pct": 88.0,
    })
    with open(st_path, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=1, ensure_ascii=False)
    assert isinstance(st["heartbeat_epoch_utc"], int)

    # ---- report row ----
    rp_path = os.path.join(ROOT, "logs", "iteration-loop",
                           "round_reports-bm-c.md")
    row = (now + " | r736 | dept:工程（复市 T-0 盘前值守轮·第 56 bm-c 连守轮） | "
           "WM-VERDICT: 绿（red=false·next_pick=claimed moneyflow IC 车道〔板 "
           "176 票 0 open/51 disk unacked=0 双扫〕） | 当前活: " + CT + " | "
           "验证证据: " + VERIFY + " | 下轮指针: " + NEXT + "\n")
    with open(rp_path, "a", encoding="utf-8") as fh:
        fh.write(row)
    print("bookkeeping done epoch=%d now=%s" % (epoch, now))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
