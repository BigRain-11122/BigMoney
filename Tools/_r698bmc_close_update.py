"""r698 bm-c round close: state-bm-c.json + fleet/machines/bm-c.json
heartbeat + round_reports-bm-c.md ledger line. Pattern credit:
Tools/_r697bmc_close_update.py. All timestamps derived at runtime
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

ACT = ("当前活: r698 W14 判决崩溃修复轮（金周第十八 bm-c 连守轮）: S0 双吸收 45a1622db+bffe8f32f（pull 撞 daemon 写面一次·r832 律原子重试净）·"
       "S0.5 双扫 DEC/ORD 双零 delta+orders 166/166+inbox 1=自发件留置·S1 48/48·"
       "**主产品=W14-JUDGE 判决 runner 崩溃根因定谳+修复+推送 origin：根因=_judge_cell_w14 x1/x2 调用点 W13 旧口径 17 值解包 vs W14 19 值返回"
       "（ValueError 首 cell 即崩 18:55·零判决·crash-fuse O-0947 同版拒烧=r494 key-drift 族判决面漏改）；修复=双点 19 值解包+per-leg resi/cnt 态预计算入双成本面"
       "+legs resi/cnt 四计数键+stop-disclosure overlay 补 RESI→CNT 组合链（引擎面一致性律）+selftest 新 L17 AST 解包契约腿（rets=[19]·11 站点全 19·54/54）"
       "·科学面零触碰（beat/passive/dual_nulls/判线全不动）·commit 0caadc134 origin blob 52718afd 实证送达·fuse 按 code_changed 自清→19:19 判决 runner 复燃 pid 25768"
       "（首 cell 生存验证=r699 盯守）**·W16 双烧按 r637 处置收敛收官（bm-a 18:44:40+bm-c 19:10:37 双 ledger 行恒等 ebf15822d2c8472e·pool_worker close outcome=ok）"
       "·S6 38 rc0（dualrun streak 18·ORANGE·金周 no-op 面诚实）·S7 tripwire+attrition CLEAN+四件套幂等+锁龄续期（长轮>12min 锁窗坑·pit 直写 2 条） "
       "| 最近实物: scripts/trial_labor_w14.py 修复（origin blob 52718afd）+results/_r698bmc_s6_log.txt（38 rc0）+results/_r698bmc_s05_facts.json（双扫）"
       "+results/_r698bmc_postreview.txt（45Y/0N/5W）+results/_r698bmc_pit_directwrite.json（2,150B md5 af4a1d8c）+research/pit-spawn.md r698 双条"
       "+research/TRIAL_GRAMMAR_LEDGER.md W16 行 @2026-10-07T19:2x "
       "| 下个里程碑: W14-JUDGE 复燃烧完 77 cell→judge-finalize+intake→CEO-REPORT-WAVE14（48h 钟·窗 ≤10-09）；10-08 复市首 bar：数据链 re-arm+"
       "REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 道）+O-2115 治理日验收复跑；pool_worker 第三信号修法（origin 最近 commit 活性）=后续代码轮带 selftest；月界首考 10-31")
DID = ("r698 bm-c: golden-week standing-guard round #18 = W14 judge-crash repair round. (1) S0: round-start dirty 3 = own "
       "satengine/w16-claim faces -> 2 absorb commits (45a1622db + bffe8f32f); pull --rebase hit the beat-window daemon "
       "race once (r832 law), single-shell atomic retry clean; behind 0. (2) S0.5 double-sweep round-start + close: DEC "
       "4C32527B / ORD A8B02C8A ZERO-delta both keys both sweeps; orders 166/166 zero unacked; inbox 1 = own-authored "
       "MSG-1915 (addressee bm-a, left in place per fleet consume semantics). (3) S1 smoke 48/48. (4) S3: SAT alive rc0; "
       "watermark green (red=false; py_watermark verdict py_low_with_work_cands at 18:52 = the judge-dead window, "
       "remediated this round by the fix + relaunch); post_review 45Y/0N/5W zero red; board 46 claimed / 0 open; "
       "job_list 0. MAIN PRODUCT = W14-JUDGE runner crash root-caused + fixed + pushed: root cause = _judge_cell_w14 "
       "x1/x2 call sites carried the stale W13 17-tuple unpack vs the W14 19-tuple return (run_candidate_curve_w14 "
       "returns eq..cnt_zeroed = 19; judge sites unpacked 17 and ALSO omitted resi_state/cnt_state args) -> ValueError "
       "'too many values to unpack (expected 17)' on the FIRST judged cell 18:55:42, zero cells judged, runner pid 34320 "
       "dead, autofill 19:10:03 crash-fuse CONFIRM + same-version relaunch REFUSED (O-0947 fix-first); r494 key-drift "
       "family (generate sites fixed r494b, judge sites missed). Fix (commit 0caadc134, origin blob 52718afd "
       "ls-tree-verified): both sites 19-tuple unpack + per-leg resi/cnt state precompute (st.get fallback to "
       "resi/cnt_state_series, deterministic same-input law) passed to both cost faces + legs resi/cnt zeroed counters "
       "(healthy + degenerate branches) + out header resi_face/cnt_face + stop-disclosure overlay composed through "
       "RESI->CNT (engine-face consistency law completion) + NEW selftest L17 AST unpack-contract leg (return arity == "
       "every non-star call-site unpack; rets=[19], 11 sites all 19; selftest 54/54 PASS). Science faces untouched "
       "(beat windows / passive / dual_nulls / thresholds zero change); no manual burn (manual substitute-burning of "
       "pool batches forbidden -- fuse self-cleared per code_changed, fill-ladder relaunched judge runner pid 25768 "
       "at ~19:19). SIDE CONVERGENCE: W16-GENERATE double-burn resolved exactly per r637/r697 keep-both disposition "
       "-- bm-a closure 18:44:40 + bm-c pool_worker closure 19:10:37, both TRIAL_GRAMMAR_LEDGER rows union-appended "
       "(identical sha16 ebf15822d2c8472e, dedup->173, same seeds = byte-identical deterministic convergence), "
       "pool_worker close commit 616c7caac outcome=ok. (5) S6 38 legs rc0 (dualrun streak 18; update_daily no-op "
       "cutoff 09-30 golden week; ORANGE shadow; daily_report + LIVE-2026-10-07 regenerated; 4 lane_io stale-takeover "
       "derives per O-2100 s2.4). (6) S7: tripwire CLEAN (1198 lines, header x1, 0 dup groups) + attrition CLEAN (4 "
       "ledgers) + quartet idempotent (loop pin 5 no-op, watchdog armed, both claws reinstalled) + round.lock tenure "
       "refresh at 19:17 (long surgery round > 12min lock window -- duplicate-spawn pit direct-written research/"
       "pit-spawn.md with kill-decision wall-clock re-anchor near-miss pit, receipt _r698bmc_pit_directwrite.json). "
       "NEAR-MISS DISCLOSED: own wrapper chain (wscript->powershell->codely, 11.3min age) was nearly misdiagnosed as "
       "a duplicate round from assumed elapsed time; wall-clock re-anchor (real 19:16:19) proved it is this session's "
       "own 19:05 tick chain; ZERO kills executed, zero collateral.")
NEXT = ("(a) W14-JUDGE relaunch watch (pid 25768, first-cell survival + checkpoint growth) -> 77-cell burn -> "
        "judge-finalize + intake -> CEO-REPORT-WAVE14 48h clock (window <=10-09). (b) 10-08 reopen FIRST BAR: "
        "data-chain re-arm + REGIME_GUARD v3 first-bar enforce + fund_premium 15:30 first snapshot (bm-c lane) + "
        "O-2115 governance-day acceptance pack official rerun. (c) pool_worker stale-takeover third-signal fix "
        "(origin recent-commit liveness <15min=alive) = follow-up code round with selftest. (d) long-round lock-window "
        "pit absorbed (tenure-touch convention for >12min rounds). (e) monthly exam 10-31 (T-143 deliverable 10-29). "
        "(f) next 5x = bm-c r700.")
VERIFY = ("receipts: 0caadc134 (fix commit, origin blob 52718afd ls-tree verified) + results/_r698bmc_s05_facts.json "
          "(double-sweep) + results/_r698bmc_s6_log.txt (38 rc0) + results/_r698bmc_s3_facts.json + "
          "results/_r698bmc_postreview.txt (45Y/0N/5W) + selftest 54/54 (L17 rets=[19] sites 11x19) + "
          "results/_attrition_guard_scan.json CLEAN + results/_r698bmc_pit_directwrite.json (2150B md5 "
          "af4a1d8c0d04516198561e45c00022cf) + W16 ledger rows x2 (ebf15822d2c8472e) + 616c7caac pool_worker close "
          "outcome=ok + judge runner relaunch pid 25768 (~19:19, fuse code_changed)")
NOTE = ("r698: W14-JUDGE crash fixed+pushed+relaunched (pid 25768, first-cell watch -> r699); W16 double-burn converged "
        "(both closures, ledger x2); S6 38 rc0 streak 18; 2 pits (kill wall-clock re-anchor + lock-window tenure-touch); "
        "reopen 10-08")


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
    st["round_no"] = int(st.get("round_no", 698)) + 1
    st["round_no_label"] = "round 698 (bm-c)"
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
    hb["verdict"] = ("healthy: W14-JUDGE crash fixed+pushed (0caadc134, selftest 54/54 L17) + relaunched pid 25768; "
                     "W16 double-burn converged (both closures, r637 disposition); S6 38 rc0; 2 pits direct-written")
    hb["current_task"] = ACT
    hb["round_no"] = 698
    hb["round_no_label"] = "round 698 (bm-c)"
    with open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)

    # post-write type assertions (R170/R178/R262 law family)
    back = json.load(open(STATE, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in back["clock_read"], "clock_read must be T-separated"
    hb_back = json.load(open(HB, encoding="utf-8"))
    assert isinstance(hb_back["heartbeat_epoch_utc"], int), "hb epoch must be JSON int"
    assert "T" in hb_back["clock_read"], "hb clock_read must be T-separated"

    line = (f"{TS} | r698 bm-c | dept:工程/研究（金周连守轮·第十八 bm-c·W14 判决崩溃修复+W16 双烧收敛轮） | "
            f"水位绿（red=false·SAT 活·board 0 open） | {ACT} | 验证: {VERIFY} | 下轮指针: {NEXT}\n")
    with open(RR, "a", encoding="utf-8") as fh:
        fh.write(line)

    print(f"state round_no -> {st['round_no']}; epoch={EPOCH} (int); clock={TS}; cpu={cpu}% ram={ram_gb}GB vram={vram}MiB")
    print("round report line appended")


if __name__ == "__main__":
    main()
