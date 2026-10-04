"""r501 bm-c round-close writes: state-bm-c.json (round_no 501, absolute
value per r694-ii), heartbeat fleet/machines/bm-c.json (epoch int +
json.loads self-verify per smoke F7 law), round_reports-bm-c.md one-line
append (r679 idempotent marker gate; full-field canon format). Zero console
CJK print (GBK law)."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_LOCAL = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

try:
    import psutil
    CPU = round(psutil.cpu_percent(interval=0.8), 1)
    RAM = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    CPU, RAM = None, None

CUR = ("当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·age 85min·CPU 累积 5045s·ETA ~10-05 02:00）"
       "+N2-W15 SHARD-2 bm-b 在飞（fleet 面 11/12 done）| 最近实物: S6 38 腿 CEO 面再生"
       "（REPORT-2026-10-04+LIVE-2026-10-04·22:51）+双跑对账 ZERO-DRIFT streak 1（390 entries）"
       "@ " + NOW + " | 下个里程碑: w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟"
       "（≤10-06 晚）；SHARD-2 烧完→screen-finalize（bm-a 席·≤10-05 晚）")
DID = ("r501 bm-c: custody/maintenance round. (1) S0 daemon-treadmill alignment: "
       "absorb d6038a808 (3 bm-c lane faces) + merge clean (0 UU) + DELIVERED 2788389b7 "
       "via push_verify; one fetch ref-lock race observed = concurrent daemon fetch, "
       "benign (ref already updated by concurrent fetcher). (2) S0.5 dual-scan: orders "
       "154/154, 0 unacked (round-start + close scans, same result); D-19 dual-key MATCH "
       "(4E5BE321/68947C17). (3) S1 smoke 48/48. (4) S3: watermark green (red=false; "
       "next_pick=moneyflow IC claimed/parked self-heal); satengine Tools-face rc0 alive; "
       "W3 judge custody tri-state IN_FLIGHT healthy (r487 probe rerun: liveness pid 26052 "
       "cmdline-scan cpu_s 5044.9, ckpt 4 files/777 union/0 dup, pool 4/4 done); N2-W15 "
       "11/12 (SHARD-2 bm-b keepalive 22:44:14); fund-trio NULLS x3 bm-b keepalive "
       "(watch only); boards 0 open (45 active all claimed); in-flight judgment batches "
       "exist -> standing-lane drafting conditions NOT met, zero drafting (r500 same "
       "judgment). (5) S6 38/38 rc0 (r500 python lineage copy; daily_report + LIVE CEO "
       "faces regen, token meter, dualrun ZERO-DRIFT streak 1 = natural re-green after "
       "r500 CONTEST-RC done_at race window; py_watermark py_low_with_work_cands = legit: "
       "single-core-by-design judge finalize + pool unclaimed 0 + golden-week no bars). "
       "(6) S7 quartet 4/4 + attrition CLEAN + MSG-2245 (bm-b N2-W15 judge sec.9 seat "
       "declaration, cc ALL) consumed to processed (bm-c non-party, W3 custody zero-touch "
       "seat boundary confirmed).")
VER = ("r501: receipts _r501bmc_s05.json (dual-key MATCH x2 scans, 0 unacked) + "
       "_r501bmc_s3probe.json (boards 0 open/watermark green/seats full face) + "
       "_r501bmc_s6_log.txt (38 legs rc0, NON-ZERO none) + _r487bmc_w3_judge_verify.json "
       "(IN_FLIGHT, liveness cpu_s 5044.9, ckpt 777/0dup, pool 4/4) + smoke 48/48 + "
       "attrition CLEAN (4 ledgers, healed history rows) ; delivery: absorb+merge tip "
       "2788389b7 push_verify DELIVERED, round commit + push_verify this close.")
NXT = ("(a) W3 judge product ~10-05 02:00 -> first product-check round after landing: "
       "python results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS -> treasure question + "
       "prereg sec.7/8 backfill + pool flip recheck (r668) + 48h CEO clock (<=10-06 "
       "evening). (b) N2-W15: SHARD-2 (bm-b) -> 12/12 -> bm-a screen-finalize seat "
       "(MSG-2215); judge sec.9 placeholder drafted by bm-b (MSG-2245 consumed). (c) "
       "fund-trio finalize 10-05..10-09 (bm-b, watch only). (d) O-2115/O-2030 acceptance "
       "10-08. (e) market reopen 10-09 data-chain re-arm. Next 5x = bm-c r505.")
ACT = ("r501 custody/maintenance: S0 absorb+merge DELIVERED 2788389b7 (0 UU) + S0.5 "
       "154/154 + D-19 dual MATCH + smoke 48/48 + W3 judge IN_FLIGHT healthy watch + S6 "
       "38/38 CEO faces regen + S7 quartet 4/4")
DEPT = ("dept:研究（W3 judge 看护·舰队维护·N2/fund 池面观察）")
WMLINE = ("watermark verdict=绿（red=false·next_pick=moneyflow IC claimed/parked 自愈面"
          "·S6 22:51 probe py_low_with_work_cands 合法面=W3 判决批在飞 local_batch_running"
          "·top_proc 1.09 核=judge 单核 finalize〔r487 标定〕+池可领 0+金周无 bar）")
S0LINE = ("S0: 开轮树脏 3 面（bm-c daemon lane=autofill_state+satengine 双面）→absorb "
          "d6038a808→merge 2788389b7 零 UU→push_verify DELIVERED 首推即达（一例 fetch "
          "ref-lock race=并发 daemon fetch 良性·ref 已由并发方更新到 59bb9193b）")
S05LINE = ("S0.5: 令差集 0 未回执（154/154 同形态 r477 律·开+收双扫同果）+D-19 双键 MATCH"
           "（decisions 4E5BE321/orders 68947C17 不变·r660 原字节律）+MSG-2245（bm-b "
           "N2-W15 judge §9 占位起草席声明·cc ALL）读毕入 processed（bm-c 非当事·W3 值守"
           "面零触碰=席位边界确认）")
S3LINE = ("S3: satengine rc0 活（Tools 面 r467 律）+W3 verify IN_FLIGHT 三态健康（ckpt 4 "
          "files/777 union/0 dup·池 4/4 done·r497 三态律）+N2-W15 11/12（SHARD-2 bm-b "
          "keepalive 22:44:14）+fund-trio NULLS ×3 bm-b keepalive（watch only）+CONTEST-RC "
          "done bm-a 22:32:33+常设线条件非零（W3/N2 两判决链在飞）零起草")
S6LINE = ("S6 38/38 rc0 NON-ZERO=none（r500 python 血统复用·REPORT/LIVE/市场钟 CALL 再生"
          "·金周 no-op 诚实·dualrun ZERO-DRIFT streak 1=r500 CONTEST-RC done_at 竞态窗后"
          "自然回绿·token meter 增量照录）")
S7LINE = ("S7: 四件套 4/4（loop pin=5 no-op·watchdog rc0 在位·双 claw in-place）+attrition "
          "CLEAN（4 账本·healed 史行照录）+state/心跳程序化写（epoch int+T 钟自证 r694）")
NXTLINE = ("下轮指针=r502 ①W3 judge 产品首查（~10-05 02:00 落地后首轮：python "
           "results/_r487bmc_w3_judge_verify.py→ADOPT_PASS→宝藏捕获问+prereg §7/§8 回填+"
           "池翻面复核〔r668 律〕+48h CEO 报告钟）②N2-W15 SHARD-2（bm-b）烧完→12/12→"
           "bm-a screen-finalize 席（MSG-2215）③fund-trio finalize 10-05..10-09（bm-b "
           "watch）④O-2115/O-2030 验收 10-08⑤开市 10-09 数据链 re-arm")


def main():
    # --- state-bm-c.json ---
    st = json.load(open(STATE, encoding="utf-8-sig"))
    assert st["round_no"] == 500, "unexpected base round_no %s" % st["round_no"]
    st["round_no"] = 501
    st["clock_read"] = NOW
    st["current_task"] = CUR
    st["did"] = DID
    st["last_round"] = ("r501 bm-c: custody/maintenance round -- S0 absorb+merge "
                        "DELIVERED 2788389b7 (0 UU), S0.5 154/154 + D-19 dual MATCH, "
                        "smoke 48/48, W3 judge IN_FLIGHT watch, S6 38/38, S7 quartet "
                        "4/4, MSG-2245 consumed.")
    st["last_round_at"] = NOW
    st["last_round_ts"] = NOW_LOCAL
    st["last_seen"] = NOW
    st["last_ts"] = NOW_LOCAL
    st["next"] = NXT
    st["verify"] = VER
    st["updated"] = NOW
    st["updated_at"] = NOW
    if CPU is not None:
        st["cpu_pct"] = CPU
        st["cpu_util_pct"] = CPU
    if RAM is not None:
        st["idle_ram_gb"] = RAM
        st["ram_free_gb"] = RAM
        st["free_ram_gb"] = RAM
    with open(STATE, "w", encoding="utf-8", newline="") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    json.loads(open(STATE, encoding="utf-8").read())  # self-verify (r645 law)
    assert json.load(open(STATE, encoding="utf-8"))["round_no"] == 501

    # --- heartbeat fleet/machines/bm-c.json ---
    hb = json.load(open(HEART, encoding="utf-8-sig"))
    hb["machine_id"] = "bm-c"
    hb["round_no"] = 501
    hb["round_no_label"] = "r501"
    hb["health"] = "healthy"
    hb["last_seen"] = NOW
    hb["last_seen_at"] = NOW
    hb["updated"] = NOW
    hb["updated_at"] = NOW
    hb["ts"] = NOW_LOCAL
    hb["clock_read"] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["current_task"] = CUR
    hb["current_task_at"] = NOW
    hb["activity_now"] = ACT
    hb["latest_artifact"] = ("S6 38 legs rc0 CEO faces regen 22:51 (REPORT-2026-10-04 + "
                             "LIVE-2026-10-04 + _r501bmc_s6_log.txt) + W3 custody receipt "
                             "refresh (_r487bmc_w3_judge_verify.json IN_FLIGHT)")
    hb["next_milestone"] = ("W3 judge product ~10-05 02:00 -> ADOPT_PASS -> 48h CEO clock "
                            "(<=10-06 evening); N2-W15 SHARD-2 (bm-b) -> 12/12 -> bm-a "
                            "screen-finalize; fund-trio finalize 10-05..09; acceptance "
                            "10-08; market 10-09")
    hb["prod_lanes"] = ("W3-JUDGE: finalize wave-3 IN_FLIGHT on bm-c (pid 26052, spawn "
                        "21:25:28, cpu_s 5045, ETA ~10-05 02:00, custody _r487bmc); N2-W15 "
                        "SCREEN fleet 11/12 done (SHARD-2 bm-b keepalive in-flight; judge "
                        "sec.9 placeholder = bm-b seat MSG-2245); fund-trio NULLS bm-b "
                        "canonical keepalive; CONTEST-RC done bm-a; boards empty; 0 new "
                        "orders; watermark green")
    hb["verdict"] = DID
    if CPU is not None:
        hb["cpu_pct"] = CPU
        hb["cpu_util_pct"] = CPU
        hb["cpu_idle_pct"] = round(100 - CPU, 1)
    if RAM is not None:
        for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
            hb[k] = RAM
    with open(HEART, "w", encoding="utf-8", newline="") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)
    hb2 = json.loads(open(HEART, encoding="utf-8").read())
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (F7 law)"
    assert hb2["round_no"] == 501

    # --- round_reports-bm-c.md one-line append (r679 marker gate) ---
    with open(REPORT, "r", encoding="utf-8", errors="replace") as f:
        body = f.read()
    assert body.count("| r501 |") == 0, "r501 marker already present (idempotent gate)"
    line = " | ".join([
        NOW, "r501", DEPT, WMLINE, CUR, S0LINE, S05LINE, "S1 smoke 48/48",
        "S2 板空（job_list 0·fleet 45 active 全 claimed·0 open）", S3LINE, S6LINE,
        S7LINE,
        "记分:1（S6 38 面 CEO 面再生+看护证据面=文件改动；等待态轮如实计）",
        "记账预算:4（state+心跳+轮报+MSG 移动=法定面内）",
        "方法论捕获=无新方法（全链复用正典范式）·宝藏捕获=无（无判决面收口）",
        "本地未达 origin commit 数: 收口 push 后自证", NXTLINE,
    ]) + "\n"
    with open(REPORT, "a", encoding="utf-8", newline="\n") as f:
        f.write(line)
    with open(REPORT, "r", encoding="utf-8", errors="replace") as f:
        assert f.read().count("| r501 |") == 1, "r501 marker must be exactly 1"
    print("WRITES OK; epoch=%d round=501 cpu=%s ram=%s" % (EPOCH, CPU, RAM))


if __name__ == "__main__":
    main()
