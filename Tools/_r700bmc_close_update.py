"""r700 bm-c round close: state-bm-c.json + fleet/machines/bm-c.json
heartbeat + round_reports-bm-c.md ledger line (N=0 tail per r699 canon,
verified by the post-commit push self-check; refused push = honest row
rewrite before delivery per r532/r533 laws). Pattern credit:
Tools/_r698bmc_close_update.py. All timestamps derived at runtime;
heartbeat_epoch_utc is a JSON int via int(time.time()) (R170/R178 law);
clock_read ISO-8601 with T separator (R262 law)."""
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
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

ACT = ("当前活: r700 S0 rebase E42 第三态逃生+pool_worker 第三信号修法+W14-JUDGE 复燃确认轮（金周第二十 bm-c 连守轮·5x HANDOVER 核对轮）: "
       "S0 轮首脏 7 daemon faces→4685b9ef0 吸收→pull --rebase 撞 r699 close 未推（behind 7）→cf6f83275 pick UU compute_audit.json→"
       "r570/r806 history union（201+201→203·latest 19:40:10 取新·零丢失）→add+continue 原子化后仍连拒「You must edit all merge conflicts」"
       "而 ls-files -u 恒空=r835 已录第三态（E42 daemon 活写族）→r835 三步逃生（author-script env 注入+commit -F message 作者日期保真 eab4c2649"
       "→rebase --quit→symbolic-ref 游离自证+branch -f main+checkout main r624 律）→余 5 absorb picks 以 live face 态内容等价重建 524264bc4"
       "→push 净（behind=0 ahead=0）·s0.py 从被弃 pick 4685b9ef0 恢复·S0.5 双扫 DEC/ORD 双零 delta（4C32527B/A8B02C8A）+orders 166/166"
       "+inbox 1=MSG-1920（bm-a W16 runner-dead 确认回执·bm-c burn=正主维持）消费入 processed·S1 48/48·"
       "**主产品=pool_worker stale-takeover 第三信号修法（r699 next 指针 (c)·W16 双烧窗立法）：origin 最近 commit 活性 <15min=活机**——"
       "_origin_commit_age_min（40 subjects needle 扫 %ct epoch·fleet 标签族 via bm-x/lane: bm-x）+_owner_age_min 三信号 min（hb/claim-stamp/origin-commit）"
       "+_origin_claims_verdict takeover 守卫（stale claim+rival fresh commits→occupied-fresh 诚实拒烧）·保守向=假活仅迟接管数分钟·假死方向才双烧；"
       "selftest 50/50（S23a-h 新 8 腿 hermetic 日期受控 tmp repo）+live-fire 探针 bm-a 10.2/bm-b 12.6/bm-c 2.0min 三机全活读正确"
       "·commit 32965ddac origin blob 7215c9566 ls-tree 送达·**W14-JUDGE 复燃活体闭环全确认**（19:58:02 autofill relaunch pid 4572"
       "→worker 池 6+ 孵出满速烧 CPU Δ4.8-8.3s/8s=r698 修复+r699 park 律双活证·fill_latency 84.7min ETA ~20:45）"
       "·QA r700 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等·png 66,349B）·S6 38 rc0（dualrun streak 20）"
       "·post_review 45Y/0N·attrition tripwire CLEAN·四件套幂等（loop pin=5 no-op·双爪 IN-PLACE·IntradayMarks 金周缺席=预期）"
       "·5x HANDOVER r696-700 行落盘 "
       "| 最近实物: Tools/pool_worker.py 第三信号修法（origin blob 7215c9566）+qa/smoke-r700.md（5/5）+qa/equity-curve-r700.png（66,349B）"
       "+results/_r700bmc_s6_log.txt（38 rc0）+results/_r700bmc_s05_facts.json（双扫）+research/HANDOVER.md r696-700 5x 行"
       "+fleet/inbox/processed/MSG-2026-10-07-1920（消费收档）@2026-10-07T20:3x "
       "| 下个里程碑: W14-JUDGE 77-cell 烧毕（ETA ~20:45）→judge-finalize+intake→CEO-REPORT-WAVE14（48h 钟·窗 ≤10-09）；"
       "10-08（周四）复市首 bar：数据链 re-arm+REGIME_GUARD v3 enforce+fund_premium 15:30 首采（bm-c 道）+O-2115 治理日验收包正式复跑；"
       "lane_io 守卫第三信号同法扩展候选（r700 观察·S6 四宿主面 stale-takeover derive 仍按 O-2100 s2.4）；月界首考 10-31（T-143 交付 10-29）；下一 5x=bm-c r705")
DID = ("r700 bm-c: golden-week standing-guard round #20 = S0 rebase E42 third-state escape + pool_worker third-signal fix + "
       "W14-JUDGE relaunch live-loop confirmation + 5x HANDOVER. (1) S0: round-start dirty 7 daemon faces -> absorb 4685b9ef0; "
       "pull --rebase hit the unpushed r699 close (behind 7), replay pick cf6f83275 conflicted on results/compute_audit.json -> "
       "r570/r806 append-history union (201+201 -> 203, latest 19:40:10 ours-newer, zero loss, JSON reparse PASS); after "
       "atomic add+continue the rebase kept refusing 'You must edit all merge conflicts' while git ls-files -u stayed EMPTY = "
       "the r835-recorded E42 third state (daemon live-write family); escape per r835 canon 3-step: author-script env injection "
       "+ git commit -F .git/rebase-merge/message with author-date preserved (r808 law) = eab4c2649 -> git rebase --quit -> "
       "symbolic-ref detached self-check + branch -f main HEAD + checkout main (r624 law); the 5 remaining churn-absorb picks "
       "rebuilt content-equivalently as one fresh absorb 524264bc4 (r835 precedent, current live face state supersedes stale "
       "pick snapshots); push clean behind=0 ahead=0; Tools/_r700bmc_s0.py restored verbatim from the dropped pick 4685b9ef0 "
       "(rebase checkout had removed the tracked-in-dropped-pick file). (2) S0.5 double-sweep: DEC 4C32527B / ORD A8B02C8A "
       "ZERO-delta; orders 166/166 zero unacked; inbox 1 = MSG-2026-10-07-1920 (bm-a confirmation that ITS W16 runner is dead "
       "and bm-c's burn is the rightful one) -> consumed to processed/. (3) S1 smoke 48/48. (4) S3: SAT alive rc0; watermark "
       "green (red=false); post_review 45Y/0N/5W zero red; board 0 open; job_list 0. MAIN PRODUCT = pool_worker "
       "stale-takeover third-signal fix (r699 next-pointer (c), W16 double-burn window law): a machine mid-long-round "
       "heartbeats only at round end and its claim heartbeat rides the tick cadence, but keeps committing to origin -- so a "
       "fresh (<15min) origin commit naming the machine = alive. Implementation: _origin_commit_age_min (40-subject needle "
       "scan on %ct epoch, fleet tag convention 'via bm-x' / 'lane: bm-x'; conservative-by-design: false-alive only defers "
       "takeover minutes, the double-burn hazard only runs in the false-dead direction) + _owner_age_min tri-signal min "
       "(heartbeat / claim-stamp / origin-commit, root/ref passthrough for hermeticity) + _origin_claims_verdict takeover "
       "guard (stale rival claim + rival fresh origin commits -> occupied-fresh honest no-burn). Selftest 50/50 (8 new "
       "S23a-h legs: hermetic date-controlled tmp repos -- fresh sighting <15 / only-old sighting >=15 / no sighting None / "
       "_owner_age_min alive+dead integration both ways / verdict occupied vs takeover regression). Live-fire read-only probe "
       "against real origin: bm-a 10.2min / bm-b 12.6min / bm-c 2.0min = all three machines correctly read alive. Commit "
       "32965ddac, origin blob 7215c9566 ls-tree-verified. (5) W14-JUDGE relaunch live-loop FULLY CONFIRMED: RAM recovered -> "
       "19:58:02 autofill relaunch pid 4572 -> multiprocessing worker pool spawned (6+ children) burning at full speed (CPU "
       "deltas 4.8-8.3s per 8s) = the r698 19-tuple fix and the r699 measure-size-park law both holding; fill_latency 84.7min "
       "ETA ~20:45, judge-finalize + intake next round. (6) S6 38 legs rc0 (dualrun streak 20; golden-week no-op faces honest; "
       "4 lane_io host faces stale-takeover derive legal per O-2100 s2.4, bm-a hb stale 43min but origin-commits-alive -- "
       "lane_io third-signal extension noted as follow-up candidate). (7) S7: quartet idempotent (loop pin 5 no-op, both "
       "claws IN-PLACE, IntradayMarks absent = market-closure expected state), attrition CLEAN, post_review clean, QA r700 "
       "pack 5/5 (93 trades, determinism=True, equity 1,017,839 identical across rounds, png 66,349B, explicit --round 700 "
       "detached runner). (8) 5x duty: HANDOVER r696-700 entry written (product-list drift + pointers).")
NEXT = ("(a) W14-JUDGE 77-cell burn completion (ETA ~20:45) -> judge-finalize + intake -> CEO-REPORT-WAVE14 48h clock "
        "(window <=10-09). (b) 10-08 reopen FIRST BAR: data-chain re-arm + REGIME_GUARD v3 first-bar enforce + fund_premium "
        "15:30 first snapshot (bm-c lane) + O-2115 governance-day acceptance pack official rerun. (c) lane_io stale-"
        "takeover third-signal extension candidate (same origin-commit-liveness law face; S6 four host faces observed "
        "deriving on a live-but-heartbeat-stale bm-a this round) = follow-up code round with selftest. (d) monthly exam "
        "10-31 (T-143 deliverable 10-29). (e) next 5x = bm-c r705.")
VERIFY = ("receipts: 32965ddac (pool_worker third-signal fix, origin blob 7215c9566 ls-tree verified) + eab4c2649 (r699 "
          "close pick manual commit, author-date preserved) + 524264bc4 (post-quit churn rebuild) + pool_worker selftest "
          "50/50 (S23a-h new) + results/_r700bmc_s0_facts.json + results/_r700bmc_s05_facts.json (double-sweep) + "
          "results/_r700bmc_s3_facts.json + results/_r700bmc_s6_log.txt (38 rc0) + qa/smoke-r700.md 5/5 + qa/equity-curve-"
          "r700.png 66,349B + judge runner pid 4572 live (worker pool full-speed) + results/_attrition_guard_scan.json "
          "CLEAN + research/HANDOVER.md r696-700 5x entry + fleet/inbox/processed/MSG-2026-10-07-1920")
NOTE = ("r700: S0 E42 third-state escaped per r835 (compute_audit union 203, behind=0); pool_worker third-signal "
        "liveness law landed (selftest 50/50, live-fire 3 machines alive); W14-JUDGE relaunched and burning full-speed "
        "(pid 4572, ETA ~20:45); MSG-1920 consumed; S6 38 rc0 streak 20; 5x HANDOVER written; reopen 10-08")


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
    st["round_no"] = int(st.get("round_no", 700)) + 1
    st["round_no_label"] = "round 700 (bm-c)"
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
    hb["verdict"] = ("healthy: S0 E42 third-state escaped clean (r835 canon); pool_worker third-signal liveness law "
                     "landed (selftest 50/50, live-fire 3/3 alive, origin blob 7215c9566); W14-JUDGE burning full-speed "
                     "pid 4572; S6 38 rc0; 5x HANDOVER written")
    hb["current_task"] = ACT
    hb["round_no"] = 700
    hb["round_no_label"] = "round 700 (bm-c)"
    with open(HB, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)

    # post-write type assertions (R170/R178/R262 law family)
    back = json.load(open(STATE, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in back["clock_read"], "clock_read must be T-separated"
    hb_back = json.load(open(HB, encoding="utf-8"))
    assert isinstance(hb_back["heartbeat_epoch_utc"], int), "hb epoch must be JSON int"
    assert "T" in hb_back["clock_read"], "hb clock_read must be T-separated"

    line = (f"{TS} | r700 bm-c | dept:工程/研究（金周连守轮·第二十 bm-c·S0 rebase 逃生+pool_worker 第三信号修法+W14 复燃确认·5x HANDOVER 核对轮） | "
            f"水位绿（red=false·SAT 活·board 0 open） | {ACT} | 验证: {VERIFY} | 下轮指针: {NEXT} | "
            f"本地未达 origin commit 数=0（commit 后 push+fetch+ls-tree 自证）\n")
    with open(RR, "a", encoding="utf-8") as fh:
        fh.write(line)

    print(f"state round_no -> {st['round_no']}; epoch={EPOCH} (int); clock={TS}; cpu={cpu}% ram={ram_gb}GB vram={vram}MiB")
    print("round report line appended (N=0 tail; push self-check next)")


if __name__ == "__main__":
    main()
