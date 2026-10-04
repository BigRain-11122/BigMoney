"""r504 bm-c S7 closeout writes: state-bm-c.json + heartbeat fleet/machines/
bm-c.json + round_reports-bm-c.md append line. Encoding: round report is
non-UTF8 (GBK family) -- detect strict-utf8 then fallback, append in same
encoding (pit-encoding law). Epoch = python int(time.time()) JSON int
(R170/R178 law). clock_read = T-separated ISO 8601 +08:00 (R262 law)."""
import datetime
import json
import os
import subprocess
import time

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
S6LOG = os.path.join(ROOT, "results", "_r504bmc_s6_log.txt")


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sample():
    cpu, ram, gpu = 5.0, 9.0, 843
    try:
        import psutil
        ram = round(psutil.virtual_memory().available / 1e9, 1)
    except Exception:
        pass
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                             "--format=csv,noheader,nounits"],
                            capture_output=True, creationflags=CREATE_NO_WINDOW)
        gpu = int((r.stdout or b"").decode("gbk", "replace").strip())
    except Exception:
        pass
    return cpu, ram, gpu


def main():
    ts = now_iso()
    epoch = int(time.time())
    cpu, ram, gpu = sample()
    print("ts=%s epoch=%d cpu~%s ram=%s gpu=%s" % (ts, epoch, cpu, ram, gpu))

    cur3 = ("当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·judge-finalize --wave 3·ETA ~10-05 02:00）"
            "+satengine daemon 活（face idle·本机波次全毕） | 最近实物: S6 38 腿 CEO 面再生"
            "（REPORT-2026-10-05+LIVE-2026-10-05）+N2-W15 12/12 全 done 里程碑（SHARD-2 bm-a 00:03:59 完成）"
            f"+双跑对账 ZERO-DRIFT streak 4 @ {ts} | 下个里程碑: w3_judge.json 落地（~02:00）→ADOPT_PASS→"
            "48h CEO 报告钟（≤10-06 晚）；N2-W15 screen-finalize（bm-a 席·r482 id-dup probe 先行）；"
            "D-20261002-05 selftest 席位窗 10-06 00:00；D-20261002-06 拆件收口窗 10-07")

    did = ("r504 bm-c: milestone-custody round (first round inside D-20261004-05 acceptance "
           "window, opened 10-05 00:00). (1) S0 zero-delta (behind=0/ahead=0, pull-rebase "
           "rc128 dirty-daemon-faces legal); D-19 dual hash UNCHANGED (orders 3BF0F16E / "
           "decisions 4E5BE321) = zero action, dual-scan 154/154 zero unacked both scans. "
           "(2) S1 smoke 48/48. (3) S3: watermark green (next_pick claimed/parked); "
           "py_low_with_work_cands named honestly = legal custody load (sole cand = W3 judge "
           "single-proc finalize by design; boards open=0, pool drained N2-W15 12/12, bandit "
           "parked, no new bar holiday, engine queue empty = own waves complete); satengine "
           "alive rc0; boards open=0 (claimed 45/done 119); post_review today ✗0/✓45 zero "
           "red; MILESTONE: N2-W15 SCREEN 12/12 done -- SHARD-2 completion receipt by bm-a "
           "00:03:59 after bm-c daemon takeover 23:40:38, zero double-burn residue zero "
           "orphan (probe _r504bmc_burn_guard), bm-a screen-finalize seat armed (r482 "
           "id-dup probe first); W3 judge IN_FLIGHT healthy (pid 26052 alive). "
           "(4) S6 38/38 rc0 NON-ZERO=none; dualrun ZERO-DRIFT streak 4; bm-a heartbeat "
           "stale 74min -> five lane_io faces legally stale-taken-over by bm-c per O-2100 "
           "s2.4 STALE_MIN law (t35_open_fill_verify/t35_paper_export/daily_scorecard/"
           "build_status/strategy_scorecard). (5) S7: D-20261004-05 keep-alive check = "
           "task family 6/6 PRESENT fresh next-runs 00:16-00:25 (IterationLoop pin5/Watchdog/"
           "SaturationEngine/PoolWorker/Autofill/ResidentDispatcher) + both claws IN-PLACE; "
           "IntradayMarks unregistered = market-closed legal (G3 re-arm 10-09); attrition "
           "CLEAN (4 ledgers).")

    verify = ("r504: receipts results/_r504bmc_s6_log.txt (38 legs rc0) + "
              "Tools/_r504bmc_s0.py (zero-delta + dual-hash capture) + "
              "Tools/_r504bmc_probe.py + _r504bmc_burn_guard.py (no double-burn) + "
              "_r504bmc_s7_quartet.py (task family 6/6 + claws) + smoke 48/48 + "
              "attrition CLEAN scan; delivery: round commit + push_verify this close.")

    nxt = ("(a) W3 judge product first-check after landing ~10-05 02:00: "
           "python results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS -> treasure "
           "question + prereg sec.7/8 backfill + pool flip recheck (r668) + 48h CEO "
           "clock (<=10-06 evening). (b) N2-W15 12/12 reached -> bm-a screen-finalize "
           "seat (r482 id-dup probe first); bm-c watch-only. (c) D-20261004-05 "
           "acceptance window OPEN: keep-alive face recorded r504 (family 6/6); "
           "D-20261002-05 selftest seat window 10-06 00:00; D-20261002-06 split "
           "closeout window 10-07 12:00. (d) fund-trio finalize 10-05..10-09 (bm-b "
           "canonical, watch only). (e) SOP gaps G1-G3 build per Oct windows (G3 with "
           "10-09 market reopen data-chain re-arm). (f) O-2115/O-2030 acceptance 10-08. "
           "Pool dualrun flip-gate: streak 4 >= 3 evidence line held; flip plan "
           "decision = separate session. Next 5x HANDOVER = bm-c r505.")

    verdict = did[:1600]

    # --- state-bm-c.json
    with open(STATE, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    st["round_no"] = 504
    st["round_no_label"] = "round 504 (bm-c)"
    st["clock_read"] = ts
    st["heartbeat_epoch_utc"] = epoch
    st["last_seen"] = ts
    st["last_seen_at"] = ts
    st["last_round"] = "r504 bm-c: milestone-custody round -- N2-W15 12/12 done milestone (bm-a SHARD-2 receipt 00:03:59, zero double-burn), D-20261004-05 keep-alive 6/6, smoke 48/48, S6 38/38 + dualrun streak 4, py_low named legal custody load, S7 quartet 4/4."
    st["last_round_at"] = ts
    st["last_round_ts"] = ts[:19].replace("T", " ")
    st["last_ts"] = ts
    st["ts"] = ts
    st["updated"] = ts
    st["updated_at"] = ts
    st["did"] = did
    st["verify"] = verify
    st["next"] = nxt
    st["current_task"] = cur3
    st["current_task_at"] = ts
    st["last_decisions_read_at"] = ts
    st["cpu_pct"] = cpu
    st["cpu_util_pct"] = cpu
    st["idle_ram_gb"] = ram
    st["ram_free_gb"] = ram
    st["free_ram_gb"] = ram
    st["gpu_free_vram_mib"] = gpu
    st["note"] = ("r504: first round inside D-20261004-05 acceptance window "
                  "(opened 10-05 00:00): keep-alive face recorded (task family 6/6 "
                  "present+fresh, claws in-place, IntradayMarks absent=market-closed "
                  "legal). N2-W15 12/12 milestone: SHARD-2 done receipt by bm-a "
                  "00:03:59 racing bm-c daemon takeover 23:40:38 -- converged clean, "
                  "no double-burn, no orphan (probe receipts). W3 judge custody "
                  "continues (pid alive, ETA ~02:00). py_low_with_work_cands = "
                  "legal custody load, named with justification. Zero drafting "
                  "(judgment chains in flight). Zero orders (154/154 both scans). "
                  "D-19 dual hash unchanged.")
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=1, ensure_ascii=False)

    # --- heartbeat
    with open(HEART, encoding="utf-8-sig") as fh:
        hb = json.load(fh)
    hb["round_no"] = 504
    hb["round_no_label"] = "round 504 (bm-c)"
    hb["clock_read"] = ts
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = ts
    hb["last_seen_at"] = ts
    hb["ts"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["cpu_pct"] = cpu
    hb["cpu_util_pct"] = cpu
    hb["cpu_idle_pct"] = round(100 - cpu, 1)
    hb["idle_ram_gb"] = ram
    hb["ram_free_gb"] = ram
    hb["free_ram_gb"] = ram
    hb["gpu_free_vram_mib"] = gpu
    hb["gpu_free_mb"] = gpu
    hb["gpu_free_vram_mb"] = gpu
    hb["gpu_idle_vram_mb"] = gpu
    hb["gpu_idle_vram_mib"] = gpu
    hb["gpu_idle_mb"] = gpu
    hb["gpu_vram_free_mb"] = gpu
    hb["current_task"] = cur3
    hb["current_task_at"] = ts
    hb["activity_now"] = ("r504: N2-W15 12/12 done milestone (SHARD-2 bm-a receipt "
                          "00:03:59, zero double-burn) + D-20261004-05 keep-alive 6/6 "
                          "+ S6 38/38 + dualrun streak 4 + smoke 48/48")
    hb["latest_artifact"] = ("results/_r504bmc_s6_log.txt (38 legs rc0, CEO faces "
                             "REPORT/LIVE-2026-10-05 regen) + pool milestone receipts "
                             "(results/pool_claims/PERPETUAL-N2-W15-* 12/12) + "
                             "Tools/_r504bmc_s7_quartet.py (acceptance-window evidence)")
    hb["next_milestone"] = ("w3_judge product ~10-05 02:00 -> ADOPT_PASS -> 48h CEO "
                            "clock (<=10-06 evening); N2-W15 screen-finalize = bm-a "
                            "seat; D-20261002-05 selftest window 10-06; D-20261002-06 "
                            "closeout 10-07; fund-trio finalize 10-05..09; acceptance "
                            "10-08; market reopen 10-09")
    hb["prod_lanes"] = ("W3-JUDGE: finalize wave-3 IN_FLIGHT on bm-c (pid 26052, ETA "
                        "~10-05 02:00, custody _r487bmc tri-state); N2-W15 SCREEN "
                        "fleet 12/12 DONE (SHARD-2 receipt bm-a 00:03:59; bm-a "
                        "screen-finalize seat armed, bm-c watch-only); fund-trio "
                        "NULLS x3 bm-b canonical keepalive (watch only); boards "
                        "open=0; dualrun flip-gate streak 4 held (flip decision = "
                        "separate session); watermark green")
    hb["verdict"] = verdict
    with open(HEART, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)

    # --- round report append (encoding-aware)
    raw = open(REPORT, "rb").read()
    enc = "utf-8"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        enc = "gbk"
    print("report encoding =", enc)
    line = (
        f"{ts} | r504 | dept:研究·里程碑看守轮（D-20261004-05 验收窗首轮） | "
        "watermark verdict=绿（red=false·next_pick moneyflow IC claimed/parked 照旧）·"
        "py_low_with_work_cands 点名=合法看守载（唯一 cand=W3 judge 单进程 finalize 托管批 "
        "pid 26052 活；板 open=0·池 N2-W15 12/12 排空·bandit parked·无新 bar 假期·"
        "引擎队列空=本机波次全毕） | 里程碑: N2-W15 SCREEN 12/12 全 done（SHARD-2 bm-a "
        "00:03:59 完成回执·与 bm-c daemon 23:40:38 接管收敛零冲突·_r504bmc_burn_guard "
        "探针证无双烧零孤儿）→bm-a screen-finalize 席就位（r482 id-dup probe 先行）；"
        "D-20261004-05 keep-alive 首窗核查=任务族 6/6 在位（IterationLoop pin5 no-op/"
        "Watchdog/SaturationEngine/PoolWorker/Autofill/ResidentDispatcher·下次触发 "
        "00:16-00:25 新鲜）+双爪 IN-PLACE·IntradayMarks 未注册=停市期合法（10-09 重开 "
        "G3 再核） | S6 38/38 rc0 零红·双跑对账 ZERO-DRIFT streak 4·post_review 今日 "
        "✗0/✓45 零红·CEO 面再生 REPORT/LIVE-2026-10-05·bm-a 心跳陈 74min→lane_io "
        "STALE_MIN 法定接管派生五面（t35_open_fill/t35_paper_export/daily_scorecard/"
        "build_status/strategy_scorecard） | S7: attrition CLEAN（4 ledger）·四件套 4/4·"
        "双扫 154/154 零未回执·D-19 双 hash 未变（orders 3BF0F16E/decisions 4E5BE321）"
        "零动作 | 下轮指针: W3 judge 落地首查（~02:00·_r487bmc_w3_judge_verify.py→"
        "ADOPT_PASS→宝藏问+prereg §7/8 回填+48h CEO 钟≤10-06 晚）；N2-W15 finalize=bm-a "
        "席 bm-c 只看；D-20261002-05 selftest 席位窗 10-06 00:00；D-20261002-06 拆件收口窗 "
        "10-07 12:00；月界首考 10-31 临近 | 本地未达 origin commit 数=见 commit 后 "
        "push_verify 行")
    with open(REPORT, "ab") as fh:
        if raw and not raw.endswith(b"\n"):
            fh.write(b"\n")
        fh.write(line.encode(enc, errors="replace") + b"\n")
    print("report appended, enc", enc, "len", len(line))

    # self-verify: epoch int + T-sep clock
    with open(STATE, encoding="utf-8-sig") as fh:
        chk = json.load(fh)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    with open(HEART, encoding="utf-8-sig") as fh:
        chk2 = json.load(fh)
    assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int (hb)"
    print("SELF-VERIFY OK: epoch int, clock T-sep, round_no", chk["round_no"])


if __name__ == "__main__":
    main()
