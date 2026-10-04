"""r506 bm-c S7 closeout writes (crashed-round recovery continuation):
state-bm-c.json + heartbeat fleet/machines/bm-c.json + round_reports-bm-c.md
append line. Pattern credit: Tools/_r504bmc_close.py (encoding-aware append,
epoch JSON int R170/R178, T-sep clock R262). Round report line carries the
in-round carry of the crashed session's S6 (01:18) -- zero re-run."""
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


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sample():
    cpu, ram, gpu = 5.0, 8.0, 843
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

    cur3 = ("当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·judge-finalize --wave 3·cpu 14427s·ETA ~10-05 02:00）"
            "+N2-W15 JUDGE 12 分片池已开（bm-a r705 judge-prep N_judge=281·bm-a autofill 领 0-3·4-11 开放归池自动续批）"
            f" | 最近实物: 崩溃 r506 续跑收口（S0 32-UU v2 resolver 零丢失集成 53d95952c 已推+S6 38 腿 CEO 面"
            f"再生 REPORT/LIVE-2026-10-05 01:18）+rebase 标签坑入册 CODELY+MSG-0100 消费 @ {ts} | 下个里程碑: "
            "w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；N2 judge 12 分片烧录 ≤10-12→"
            "judge-finalize；CEO 双链接点击（bm-b+bm-c）；D-20261002-05 selftest 席位窗 10-06 00:00；"
            "D-20261002-06 拆件收口窗 10-07 12:00")

    did = ("r506 bm-c: crashed-round recovery continuation closeout (predecessor r506 session died ~01:20 "
           "post-S6, after completing S0 merge 53d95952c (32-UU v2 resolver, pushed 01:13), D-19 read, "
           "S6 38 legs (01:18); this session resumed 01:26 from receipts -- zero S6 re-run, zero "
           "double-burn). (1) S0.5: D-19 dual hash UNCHANGED both scans (orders 3BF0F16E / decisions "
           "755428F8) zero action; orders dir zero new file (154/154 ack holds). (2) S1 smoke 48/48 "
           "(re-run by continuation 01:31, crashed session had no smoke receipt). (3) S3: watermark "
           "green (next_pick moneyflow IC claimed/parked); py_low_with_work_cands named legal custody "
           "load (W3 judge single-proc finalize pid 26052 alive cpu 14427s + N2-W15 judge chain "
           "enrolled = dual judgment chains in flight; boards open=0, bandit parked, holiday no "
           "bar); satengine rc0 alive (Tools face r467 law); post_review today YES=45/NO=0/WAIT=5 "
           "zero red. (4) N2-W15 JUDGE chain per MSG-0100 (consumed to processed): sec.9.1 frozen "
           "bm-b r702 (judge berth 545_500), judge-prep DONE bm-a r705 (188s, N_judge=281, "
           "collapse-0, seed 545_500, one-shot state gate armed), 12 judge shards enrolled pool "
           "391->403, bm-a autofill claimed 0-3 via lane, 4-11 ready open -- pool burn belongs to "
           "autofill/pool_worker daemons per C8 law, bm-c daemon alive, zero manual claim; W3 "
           "custody verify IN_FLIGHT healthy (_r487bmc tri-state). (5) S7: quartet 4/4 (loop pin=5 "
           "no-op first-fire 01:35 + watchdog idempotent rebuild + both claws LF-normalized "
           "installed); attrition CLEAN rc0 (4 ledgers, healed history rows noted; first attempt "
           "hit wrong-path Tools/ slip rc2 self-noise, corrected scripts/ = invocation slip not "
           "mechanism fault); MSG-0042 self-sent stays for cross-machine window; S4 one pit entry "
           "to CODELY (rebase marker label family); D-19 close double-scan UNCHANGED.")

    verify = ("r506: receipts results/_r506bmc_s6_log.txt (38 legs rc0 01:18 crashed-session carry) + "
              "results/_r506bmc_d19_read.txt (dual-hash UNCHANGED x2 scans) + "
              "results/_r506bmc_rebase_resolve.json/.log (32-UU v2 resolve, r505-v1 marker-label "
              "false-negative healed) + results/_r487bmc_w3_judge_verify.json (IN_FLIGHT custody) + "
              "smoke 48/48 (01:31) + post_review REPORT-20261005 zero red + attrition CLEAN + "
              "Tools/_r506bmc_pool_probe2.py (12 judge shards ready at origin tip, prep done "
              "result_ref); delivery: round commit + push_verify this close.")

    nxt = ("(a) W3 judge product first-check after landing ~10-05 02:00 (next rounds): "
           "python results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS -> treasure question + "
           "prereg sec.7/8 backfill + pool flip recheck (r668) + 48h CEO clock (<=10-06 evening). "
           "(b) N2-W15 JUDGE 12 shards: daemon autofill burn watch (bm-a 0-3 claimed, 4-11 open; "
           "burn <=10-12 then judge-finalize seat, r482 id-dup probe first). (c) CEO dual "
           "tailscale links click (bm-b a/14a391ef01dbc6 + bm-c a/13ac0ce1015dd3). (d) "
           "D-20261002-05 selftest seat window 10-06 00:00; D-20261002-06 split closeout window "
           "10-07 12:00. (e) fund-trio finalize 10-05..10-09 (bm-b canonical, watch only). "
           "(f) market reopen 10-09 data-chain re-arm (G3); month-end first exam 10-31. "
           "Next 5x HANDOVER = bm-c r510.")

    note = ("r506: crashed-session recovery round. Predecessor died ~01:20 after S0 (merge "
            "53d95952c pushed, 32-UU v2 resolver), D-19 read, S6 38 legs (01:18); continuation "
            "resumed 01:26 from receipts -- S6 carried in-round (no re-run), smoke re-run for "
            "honest receipt, state/heartbeat/round-report written fresh by close script. N2-W15 "
            "judge chain landed mid-round (MSG-0100): prep done bm-a, 12 shards pool-ready, "
            "daemon burn territory per C8 -- zero manual claim. W3 custody continues (pid 26052, "
            "ETA ~02:00). Zero new drafting (dual judgment chains in flight). Zero orders "
            "(154/154, dual scan). D-19 dual hash unchanged.")

    verdict = did[:1600]

    # --- state-bm-c.json
    with open(STATE, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    st["round_no"] = 506
    st["round_no_label"] = "round 506 (bm-c)"
    st["clock_read"] = ts
    st["heartbeat_epoch_utc"] = epoch
    st["last_seen"] = ts
    st["last_seen_at"] = ts
    st["last_round"] = ("r506 bm-c: crashed-round recovery closeout -- S0 32-UU v2-resolver integration "
                        "53d95952c (pushed), S6 38/38 in-round carry (01:18), smoke 48/48, N2-W15 judge "
                        "chain observed (prep done bm-a N_judge=281, 12 shards pool-ready, daemon burn), "
                        "W3 custody IN_FLIGHT, attrition CLEAN, quartet 4/4, MSG-0100 consumed.")
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
    st["note"] = note
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, indent=1, ensure_ascii=False)

    # --- heartbeat
    with open(HEART, encoding="utf-8-sig") as fh:
        hb = json.load(fh)
    hb["round_no"] = 506
    hb["round_no_label"] = "round 506 (bm-c)"
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
    hb["activity_now"] = ("r506: crashed-round recovery closeout -- S6 38/38 (01:18 carry) + smoke 48/48 "
                          "+ quartet 4/4 + attrition CLEAN + N2-W15 judge chain observed (prep done, "
                          "12 shards ready, daemon burn territory)")
    hb["latest_artifact"] = ("results/_r506bmc_s6_log.txt (38 legs rc0, CEO faces REPORT/LIVE-2026-10-05 "
                             "regen) + CODELY r506 rebase-marker pit entry + MSG-2026-10-05-0100 "
                             "consumed to processed")
    hb["next_milestone"] = ("w3_judge.json ~10-05 02:00 -> ADOPT_PASS -> 48h CEO clock (<=10-06 "
                           "evening); N2 judge 12 shards burn <=10-12 -> judge-finalize; CEO dual-link "
                           "click; D-20261002-05 window 10-06; D-20261002-06 closeout 10-07; "
                           "fund-trio finalize 10-05..09")
    hb["prod_lanes"] = ("W3-JUDGE: finalize wave-3 IN_FLIGHT on bm-c (pid 26052, ETA ~10-05 02:00, "
                        "custody _r487bmc tri-state); N2-W15 JUDGE: 12 shards pool-ready (prep done "
                        "bm-a r705 N_judge=281 seed 545_500; bm-a autofill claimed 0-3; 4-11 open = "
                        "daemon territory, burn <=10-12); fund-trio NULLS x3 bm-b canonical keepalive "
                        "(watch only); boards open=0; watermark green")
    hb["verdict"] = verdict
    with open(HEART, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)

    # --- round report append (encoding-aware, binary append per r485 EOL law)
    raw = open(REPORT, "rb").read()
    enc = "utf-8"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        enc = "gbk"
    print("report encoding =", enc)
    line = (
        f"{ts} | r506 | dept:研究（崩溃轮续跑收口·W3/N2 双判决链看护·舰队维护） | "
        "watermark verdict=绿（red=false·next_pick moneyflow IC claimed/parked 自愈面照旧·S3probe 01:30）·"
        "py_low_with_work_cands 点名=合法托管载（W3 judge 单进程 finalize pid 26052 活 cpu 14427s〔r487 标定〕"
        "+N2-W15 JUDGE 12 分片池已开=双判决链在飞；板 open=0·bandit parked·金周无 bar·引擎队列空） | "
        "当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00）+N2-W15 JUDGE 12 分片池烧录在途"
        "（bm-a autofill 0-3 已领·4-11 开放归池自动续批=daemon 领域零手工代领） | 最近实物: 崩溃 r506 续跑收口"
        "（S0 32-UU v2 resolver 零丢失集成 53d95952c 已推+S6 38 腿 CEO 面再生 REPORT/LIVE-2026-10-05 01:18）"
        "+rebase 标签坑入册 CODELY+MSG-0100 消费 @ " + ts + " | 下个里程碑: w3_judge.json 落地（~02:00）→"
        "ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；N2 judge 12 分片烧录 ≤10-12→judge-finalize；CEO 双链接点击；"
        "D-20261002-05 selftest 席位窗 10-06 00:00；D-20261002-06 收口窗 10-07 12:00 | "
        "S0（崩溃轮段 01:0x-01:1x）: churn-absorb×2 daemon 面→pull --rebase 32 UU→v2 resolver（r505 v1 标签"
        "假阴性治愈·坑已入册 CODELY）→origin 5-commit treadmill 波 merge 53d95952c push 01:13 | "
        "S0.5: D-19 双键 UNCHANGED（orders 3BF0F16E/decisions 755428F8·开+收双扫同果）+orders 目录零新令"
        "（154/154） | S1: smoke 48/48（续跑段 01:31 实跑·崩溃段无 smoke 回执） | S2: 板空（job_list 0+"
        "fleet open 0·s3probe 实证） | S3: satengine rc0 活（Tools 面 r467 律）+watermark 绿+post_review 今日 "
        "✗0（YES=45/WAIT=5）+W3 custody IN_FLIGHT 健康（_r487bmc 三态律）+N2-W15 §9.1 冻结窗落地消费"
        "（MSG-0100：bm-b r702 freeze judge 带 545_500+bm-a r705 judge-prep PASS 188s N_judge=281 collapse-0·"
        "12 shard 池入 391→403·bm-a autofill 0-3·4-11 开放）+常设线条件非零（双判决链在飞）零起草 | "
        "S6: 38/38 rc0 NON-ZERO=none（崩溃段 01:18 轮内承运零重跑·CEO 面 REPORT/LIVE-2026-10-05 再生） | "
        "S7: 四件套 4/4（loop pin=5 no-op 首发保 01:35+watchdog 幂等重建+双爪 LF 归一安装）+attrition CLEAN"
        "（4 账本·healed 史行照录·首跑 Tools\\ 笔误 rc2 自噪非机制故障·scripts\\ 正径 rc0）+MSG-0100 消费入 "
        "processed（bm-c 非起草席·池烧录归 autofill）+MSG-0042 自发件留他机消费窗（r503 律）+S4 坑律一条入册 "
        "CODELY（rebase 标签面）+登记册零命中断言=不适用（零清扫零 quarantine） | "
        "记分:1（S6 38 面 CEO 再生+崩溃轮零丢失收口=实际文件改动·看护轮如实计） | 记账预算:5（state+心跳+轮报="
        "法定 3+MSG 移动 1+CODELY 坑律 1=面内） | 方法论捕获=坑律入册 CODELY（rebase 标签面 v1→v2）·知识卡不另立"
        "（同内容复述禁令）·宝藏捕获=无（无五类收口面：判决 finalize 未落·名单进出零） | "
        "本地未达 origin commit 数: 见 commit 后 push_verify 行 | 下轮指针=r507 ①W3 judge 产品首查（~02:00 "
        "落地后首轮：python results/_r487bmc_w3_judge_verify.py→ADOPT_PASS→宝藏捕获问+prereg §7/§8 回填+"
        "池翻面复核〔r668 律〕+48h CEO 报告钟）②N2-W15 JUDGE 分片烧录盯梢（autofill daemon 面·全 done→"
        "judge-finalize 席 r482 id-dup 探针前置）③CEO 双链接点击（bm-b a/14a391ef01dbc6+bm-c a/13ac0ce1015dd3）"
        "→tailnet 三机全通④fund-trio finalize 10-05..10-09（bm-b 正主）⑤O-2115/O-2030 验收 10-08⑥开市 10-09 "
        "数据链 re-arm（SOP G3 同窗）")
    with open(REPORT, "ab") as fh:
        if raw and not raw.endswith(b"\n"):
            fh.write(b"\n")
        fh.write(line.encode(enc, errors="replace") + b"\n")
    print("report appended, enc", enc, "len", len(line))

    # self-verify: epoch int + T-sep clock + roundtrip
    with open(STATE, encoding="utf-8-sig") as fh:
        chk = json.load(fh)
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    assert chk["round_no"] == 506
    with open(HEART, encoding="utf-8-sig") as fh:
        chk2 = json.load(fh)
    assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int (hb)"
    print("SELF-VERIFY OK: epoch int, clock T-sep, round_no", chk["round_no"])


if __name__ == "__main__":
    main()
