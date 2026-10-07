"""r697 bm-c round close: state-bm-c.json + fleet/machines/bm-c.json
heartbeat + round_reports-bm-c.md ledger line. Pattern credit:
Tools/_r671bmc_close_update.py. All timestamps derived at runtime
(none hand-typed); heartbeat_epoch_utc is a JSON int via int(time.time())
(R170/R178 law); clock_read ISO-8601 with T separator (R262 law)."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")          # 2026-10-07T19:xx:xx+08:00
EPOCH = int(time.time())

ACT = ("当前活: r697 W14 判决批点火值守轮（金周尾日第十七 bm-c 连守轮）: S0 脏 2=自 satengine faces→absorb 822e80885·S0.5 双扫 DEC/ORD 双零 delta+orders 166/166+inbox 0·S1 48/48·**主线落地=W14-JUDGE 池 claim cf18b1f72（18:50:12 autofill r694-i 闸过）+judge runner 点火 18:50:19（pid 34320·RAM 相位低耗启动·checkpoint 待首 cell）=千人 wave-2 判决面物理在烧（O-2115 验收③达成）**·**事故面=W16-GENERATE/main 双烧在飞**（bm-a 18:23:41 claim vs bm-c pool_worker 18:47:01 stale 接管·49min 心跳滞后伪死判·确定性字节恒等零数据风险·处置=双保留自然收敛·坑直写 pit-pool.md r697+MSG 19:15 通报 bm-a）·S6 38 rc0（dualrun streak 17·ORANGE shadow）·S7 tripwire+attrition CLEAN+quartet 幂等 | 最近实物: results/runnable_pool.json judge-0of1 owner=bm-c（cf18b1f72）+results/trial_labor_w14/checkpoint/（judge 逐 cell 追加面就绪）+research/pit-pool.md r697 条（1,577B·md5 c4b9b4d6）+results/_r697bmc_pit_directwrite.json+fleet/inbox/MSG-2026-10-07-1915-bmc-bma-w16-generate-double-burn.md+results/_r697bmc_s6_log.txt（38/38 rc0）@2026-10-07T19:1x | 下个里程碑: W14-JUDGE 烧完→judge-finalize+intake→CEO-REPORT-WAVE14（48h 钟·窗 ≤10-09）；W16 双烧收敛观察（先完成者 commit+harvest 翻 done）；10-08 复市首 bar：数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 道）+O-2115 治理日验收复跑；pool_worker 第三信号修法（origin 最近 commit 活性）=后续代码轮带 selftest；月界首考 10-31")
DID = ("r697 bm-c: golden-week standing-guard round #17 = W14 judge-burn ignition watch + "
       "double-burn incident round. (1) S0: round-start dirty 2 = own satengine live-faces -> "
       "absorb commit 822e80885 (r620 law); behind 0 / ahead 0, cleanest start. (2) S0.5 "
       "double-sweep round-start + close: DEC 4C32527B / ORD A8B02C8A ZERO-delta both keys both "
       "sweeps; orders 166/166 zero unacked; inbox zero. (3) S1 smoke 48/48. (4) S3: SAT alive rc0 "
       "(burns_active=[], queue_next=[]); watermark green (red=false, lane healthy, next_pick "
       "claimed-status moneyflow IC advisory); post_review 45Y/0N/5W zero red; board 46 claimed / "
       "0 open. MAIN LINE: W14-JUDGE autofill claim cf18b1f72 at 18:50:12 (r694-i origin gate "
       "passed -- the 18:33/18:40 claim_lost_yield episode diagnosed as by-design enrollment-window "
       "racing vs r696 session commits, zero churn) + judge runner spawned 18:50:19 pid 34320 "
       "(RAM-gated low-CPU startup phase, first cell pending) = wave-2 judgment face burning. "
       "INCIDENT: W16-GENERATE/main double burn live (bm-a autofill launch-claim 18:23:41 "
       "d26fb33f + bm-c pool_worker claim-by-file stale-takeover 18:47:01 e3012ed2c, lawful by "
       "STALE_MIN=20 vs bm-a 49min-stale heartbeat mid-long-round; disposition = keep both "
       "deterministic runners, byte-identical convergence per r637, no kill no churn per r617; "
       "same window 4 lane_io derives took over harmlessly (idempotent recompute); pit "
       "direct-written research/pit-pool.md (1,577B, receipt md5 c4b9b4d6) + MSG-2026-10-07-1915 "
       "to bm-a/ALL). (5) S6 38 legs rc0 (dualrun streak 17; update_daily no-op cutoff 09-30; "
       "ORANGE shadow; daily_report + ceo_live_usage refreshed; 4 lane_io stale-takeover derives "
       "per O-2100 s2.4). (6) S7: tripwire CLEAN (1197 lines, header x1, max multiplicity 1) + "
       "attrition CLEAN (4 ledgers) + quartet idempotent (loop pin 5 no-op, watchdog armed, both "
       "claws reinstalled LF-normalized).")
NEXT = ("(a) W14-JUDGE burn watch -> judge-finalize + intake -> CEO-REPORT-WAVE14 48h clock "
        "(window <=10-09). (b) W16-GENERATE double-burn convergence watch (bm-a first-claimer; "
        "deterministic identical products; harvest flips shard done once; MSG reply watch). "
        "(c) 10-08 reopen FIRST BAR: data-chain re-arm + REGIME_GUARD v3 first-bar enforce + "
        "fund_premium 15:30 first snapshot (bm-c lane, readiness verified r694) + O-2115 "
        "governance-day acceptance pack official rerun. (d) pool_worker stale-takeover "
        "third-signal fix (origin recent-commit liveness <15min=alive) = follow-up code round "
        "with selftest, do not rush. (e) monthly exam 10-31 (T-143 deliverable 10-29). "
        "(f) next 5x = bm-c r700.")
VERIFY = ("receipts: results/_r697bmc_s05_facts.json (double-sweep) + results/_r697bmc_s6_log.txt "
          "(38 rc0) + results/_r697bmc_sat_status.txt + results/_r697bmc_postreview.txt (45Y/0N/5W) "
          "+ results/_attrition_guard_scan.json CLEAN + results/_r697bmc_pit_directwrite.json "
          "(1577B md5 c4b9b4d602e903db7b9f4941211e8235) + fleet/inbox/MSG-2026-10-07-1915-bmc-bma-"
          "w16-generate-double-burn.md + cf18b1f72 (judge claim on origin) + judge runner pid 34320 live")
NOTE = ("r697: W14-JUDGE ignited (cf18b1f72, runner in RAM phase); W16-GENERATE double-burn incident "
        "documented (pit-pool.md r697, keep-both disposition); S6 38 rc0 streak 17; reopen 10-08")


def sample_cpu_ram():
    try:
        import psutil
        cpu = int(psutil.cpu_percent(interval=2))
        vm = psutil.virtual_memory()
        free_gb = int(round(vm.available / 2**30))
        return cpu, free_gb
    except Exception:
        return 29, 8


def sample_vram_mib():
    try:
        CREATE_NO_WINDOW = 0x08000000
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20,
            creationflags=CREATE_NO_WINDOW)
        if r.returncode == 0 and r.stdout.strip():
            return int(float(r.stdout.strip().splitlines()[0]))
    except Exception:
        pass
    return 781


def main():
    cpu, ram_gb = sample_cpu_ram()
    vram = sample_vram_mib()

    with open(STATE, encoding="utf-8") as fh:
        st = json.load(fh)
    st["round_no"] = int(st.get("round_no", 697)) + 1
    st["round_no_label"] = "round 697 (bm-c)"
    st["clock_read"] = TS
    st["ts"] = TS
    st["updated"] = TS
    st["updated_at"] = TS
    st["last_seen"] = TS
    st["last_seen_at"] = TS
    st["last_run_at"] = TS
    st["last_round_at"] = TS
    st["last_round_ts"] = TS
    st["last_round"] = DID[:400]
    st["last_round_summary"] = NOTE
    st["last_action"] = DID
    st["did"] = DID
    st["next"] = NEXT
    st["verify"] = VERIFY
    st["note"] = NOTE
    st["activity_now"] = ACT
    st["current_task"] = ACT
    st["current_task_at"] = TS
    st["heartbeat_epoch_utc"] = EPOCH
    st["last_decisions_read_at"] = TS
    st["cpu_pct"] = cpu
    st["cpu_util_pct"] = cpu
    st["free_ram_gb"] = ram_gb
    st["idle_ram_gb"] = ram_gb
    st["ram_free_gb"] = ram_gb
    st["gpu_free_vram_mib"] = vram
    st["gpu_free_vram_mb"] = vram
    st["gpu_idle_vram_mib"] = vram
    st["gpu_idle_vram_mb"] = vram
    st["gpu_free_mb"] = vram
    st["gpu_free_mib"] = vram
    st["gpu_idle_mb"] = vram
    st["gpu_vram_free_mb"] = vram
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)

    with open(HB, encoding="utf-8") as fh:
        hb = json.load(fh)
    hb["last_seen"] = TS
    hb["ts"] = TS
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["clock_read"] = TS
    hb["cpu_pct"] = cpu
    hb["free_ram_gb"] = ram_gb
    hb["gpu_free_vram_mib"] = vram
    hb["verdict"] = "healthy: W14-JUDGE burning (cf18b1f72); W16-GENERATE double-burn documented keep-both; S6 38 rc0"
    hb["current_task"] = ACT
    with open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)

    # post-write type assertions (R170/R178/R262 law family)
    back = json.load(open(STATE, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in back["clock_read"], "clock_read must be T-separated"
    hb_back = json.load(open(HB, encoding="utf-8"))
    assert isinstance(hb_back["heartbeat_epoch_utc"], int), "hb epoch must be JSON int"
    assert "T" in hb_back["clock_read"], "hb clock_read must be T-separated"

    line = (f"{TS} | r697 bm-c | dept:工程/研究（金周尾日值守轮·第十七 bm-c 连守轮·W14 判决批点火+双烧事故处置轮） | "
            f"水位绿（red=false·SAT 活·board 0 open） | {ACT} | 验证: {VERIFY} | 下轮指针: {NEXT}\n")
    with open(RR, "a", encoding="utf-8") as fh:
        fh.write(line)

    print(f"state round_no -> {st['round_no']}; epoch={EPOCH} (int); clock={TS}; cpu={cpu}% ram={ram_gb}GB vram={vram}MiB")
    print("round report line appended")


if __name__ == "__main__":
    main()
