# -*- coding: utf-8 -*-
"""r376 bm-c wrap: state 376 + round report + heartbeat + wrap commit/push.

Laws: r583 heartbeat carry-list law (orders_ack carried from existing file,
dynamic fields only), R170/R178 epoch int + T-format clock, targeted add
(dirty-tree law), commit -F channel (r375), push fallback = surgical (r366).
"""
import subprocess
import sys
import os
import json
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000


def git(*a, check=True):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, creationflags=NO_WINDOW)
    out = r.stdout.decode("utf-8", "replace").strip()
    err = r.stderr.decode("utf-8", "replace").strip()
    if check and r.returncode != 0:
        print("GITFAIL", list(a)[:3], err[:300])
        sys.exit(1)
    return r.returncode, out, err


def main():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    epoch = int(time.time())

    # ---- machine readings (psutil) ------------------------------------------
    cpu_pct = idle_ram = gpu_free = None
    try:
        import psutil
        psutil.cpu_percent(interval=None)  # prime (r319 law)
        time.sleep(1.0)
        cpu_pct = round(psutil.cpu_percent(interval=None), 1)
        idle_ram = round(psutil.virtual_memory().available / 1e9, 1)
    except Exception as e:
        print("psutil read fail:", e)
    hb0 = json.load(open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
    gpu_free = hb0.get("gpu_free_vram_mib")  # carry prior reading (no nvidia-smi from session shell)

    # ---- state-bm-c.json: dynamic fields only --------------------------------
    sp = os.path.join(REPO, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 376
    st["last_round_at"] = "r376"
    st["last_round_ts"] = now
    st["updated"] = now_iso
    st["last_ts"] = now_iso
    st["last_seen"] = now_iso
    st["cpu_pct"] = cpu_pct if cpu_pct is not None else st.get("cpu_pct")
    st["idle_ram_gb"] = idle_ram if idle_ram is not None else st.get("idle_ram_gb")
    st["gpu_free_vram_mib"] = gpu_free
    st["verify"] = (
        "r376: W99 finalize one-pass landed end-to-end (prev=origin face 580,148 = W98 bm-a r584 -> "
        "total 582,348 +2,200, merged K=215,720, skill_line 1.1689->1.169 K-lift +0.0001, voids LOWAMP-P1/P2, "
        "89th engine wave / bm-c 29th owned; prereg SS7/SS8 mechanical backfill W97 paradigm; n1 selftest "
        "default-wave PASS two-state legs same-window r307/r522; direct push claw-blocked on bm-a/bm-b "
        "divergence r366 family -> surgical re-parent 914272a60 4-file payload, ls-tree delivery verified; "
        "bm-b W100 finalize unblocked by this landing) + W105 FREEZE delivered end-to-end (seat "
        "MSG-20261002-1738-bmc pre-published 565a6b254 r565; band gate ADMIT rc0 A 253_004..255_003 "
        "skip-past-published W104 pub hops=1 / B 60_001..60_200 hops=2 (59_801..60_000 refused at "
        "SEED_REGISTRY div_lowvol_p1=60_000 upper-edge, past-hit restart both readings converge, W74-B/W81 "
        "edge family); banned gate ADMIT 0; 94th engine wave by machine-derive, bm-c 31st owned; five faces "
        "+ PERPETUAL_N1_W105_PREREG frozen via r584 FIX-A/B/C + AST pure-insertion generator +992/-0, "
        "selftest PASS with W105 materializer leg live; freeze commit f2db133c5 direct push clean) + W105 "
        "self-ignition verified (mtime-reload v0.4, 9/12 + 3 active at wrap, product-growth proof r325) + "
        "S0 surgical realign (r578: reset --mixed + 93 stale faces checkout-restored, 4 bm-c live-writer "
        "files kept, 4 writer tasks disable/enable window) + S6 chain 36/36 rc0 (dualrun ZERO-DRIFT streak "
        "51/3, WM green lane healthy, market clock ORANGE_COOL, lane-guarded legs honest no-ops, daily "
        "report + CEO live page regenerated) + smoke 47/47 + orders 143/143 double-scan + D-19 937A373D "
        "MATCH + attrition CLEAN + self-heal 4/4 (loop pin=5 no-op, watchdog, claws MATCH)"
    )
    st["did"] = (
        "r376: W99 finalize + prereg backfill + surgical push 914272a60 + W105 seat/gate/freeze "
        "f2db133c5 + W105 ignition + S6 all-green + stale MSG copies cleaned"
    )
    st["current_task"] = (
        "W105 burning on local engine (12/12 by wrap+minutes); W102 finalize gated on W100 bm-b + W101 bm-a "
        "landings (FAIL-CLOSED r307 chain order); W105 finalize queued behind W100-W103; T-144(c) "
        "data/protocol domains + flow-sinking due 10-04/10-07 (engine domain done by bm-a r585); T-143 "
        "month-exam prep 10-29; month-boundary first exam 10-31"
    )
    st["next"] = (
        "(r377)(a) W102 finalize when W100/W101 land on origin (fetch check -> one-pass finalize --wave 102, "
        "prev=origin chain head derive r518, no blind rerun r538); (b) W105 finalize after W102/W103 land; "
        "(c) W106 never-dry if engine queue empty (projection A 255_004..257_003 / B 60_201..60_400, "
        "re-derive never transcribe); (d) T-144(c) data-domain split; (e) T-143 month-exam prep; "
        "(f) month-boundary first exam 10-31"
    )
    st["heartbeat_epoch_utc"] = epoch
    st["clock_read"] = now_iso
    st["last_round"] = (
        "2026-10-02 r376 bm-c: W99 finalize landed (head 582,348 K=215,720) + W105 freeze+ignition + "
        "S6 all-green + smoke 47/47 + orders 143/143"
    )
    json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- round report lines (S5) ---------------------------------------------
    rp = os.path.join(REPO, "round_reports-bm-c.md")
    line1 = (
        f"{now_iso} | r376 | watermark: 绿（red=false·lane healthy·引擎面 W105 点火饱和）｜当前活=W105 12 片烧录在本地引擎（wrap 时 9/12+3 在烧）｜最近实物=results/perpetual_faces/n1_w99_results.json（W99 finalize 17:0x·链头 582,348·K=215,720）+ W105 五面冻结 f2db133c5（17:2x）｜下个里程碑=W102/W105 finalize 随上游 W100/W101 落账解锁（≤24h）→ 月界首考 10-31 ‖ 本轮双主产：W99 finalize one-pass（prev=origin 面 580,148=W98 bm-a r584→total 582,348 +2,200·merged K=215,720·K-lift +0.0001·voids LOWAMP-P1/P2·89th 波·bm-c 29th 自有）+prereg §7/§8 机械回填（W97 范式·r307 两态腿同窗复跑 PASS）+直推被爪正确拦（bm-a/bm-b 分叉 r366 族）→外科 re-parent 914272a60 四件 payload·ls-tree 送达自证·bm-b W100 finalize 链序解锁；W105 冻结全程（席位 MSG-20261002-1738-bmc 先推 565a6b254 r565→带闸 ADMIT rc0 A 253_004..255_003 skip-past-published W104 hops=1/B 60_001..60_200 hops=2〔59_801..60_000 撞 SEED_REGISTRY div_lowvol_p1=60_000 上缘→越 hit 起窗·两读法同解 W74-B/W81 族〕→banned ADMIT 0→prereg 冻结锚=W99 实测键 r576 锚滚律→五面 FIX-A/B/C+AST 纯插入 +992/-0→selftest PASS W105 腿在场→f2db133c5 直推净成）+W105 自燃 9/12+3 在烧（r325 产物增长律）+S0 手术重对齐（r578：reset --mixed+93 陈旧面 checkout 恢复·4 活写件保本地·4 写者任务窗内禁复）+S6 36 腿 rc0（dualrun 零漂 51/3·WM 绿·ORANGE_COOL·车道腿诚实 no-op·日报+CEO 页再生）+smoke 47/47+orders 143/143 双扫+D-19 MATCH+attrition CLEAN+自愈 4/4（pin=5 no-op·watchdog 在位·爪 MATCH MATCH） ‖ 验证证据：n1_w99_results.json ledger total=582,348 / gate rc0 ADMIT 回执在场 / freeze FIX-C +992/-0 / selftest PASS / ls-tree 送达四件 / 产物增长 9/12 ‖ 下轮指针：W102 finalize 候 W100/W101 落账；W105 finalize 候 W102/W103；W106 never-dry 投影 A 255_004..257_003/B 60_201..60_400 必重 derive；T-144(c) 数据域拆件；T-143 备考 [via bm-c r376]"
    )
    line2 = f"{now_iso} | r376 | 本地未达 origin commit 数=0（wrap 前取数 0/0；W105 冻结 f2db133c5 直推净成·seat 565a6b254 直推净成）"
    with open(rp, "a", encoding="utf-8") as f:
        f.write(line1 + "\n" + line2 + "\n")

    # ---- heartbeat (r583: dynamic only, carry orders_ack) ---------------------
    hb = dict(hb0)
    hb["round_no"] = 376
    hb["last_seen"] = now_iso
    hb["last_seen_at"] = now
    hb["updated_at"] = now_iso
    hb["heartbeat_epoch_utc"] = epoch
    hb["clock_read"] = now_iso
    if cpu_pct is not None:
        hb["cpu_pct"] = cpu_pct
        hb["cpu_util_pct"] = cpu_pct
    if idle_ram is not None:
        hb["idle_ram_gb"] = idle_ram
        hb["free_ram_gb"] = idle_ram
        hb["ram_free_gb"] = idle_ram
    hb["gpu_free_vram_mib"] = gpu_free
    hb["verdict"] = (
        "healthy: W99 finalize landed (head 582,348) + W105 freeze+ignition 12/12; S6 green; smoke 47/47"
    )
    hb["current_task"] = "W105 burn completing on local engine; W102/W105 finalize chain-gated on W100/W101 landings"
    hb["activity_now"] = "W105 12-shard burn on local engine (9/12 + 3 active at wrap)"
    hb["latest_artifact"] = (
        "results/perpetual_faces/n1_w99_results.json (W99 finalize 17:07, ledger head 582,348, K=215,720) "
        "+ W105 five-face freeze commit f2db133c5 (17:26)"
    )
    hb["next_milestone"] = (
        "W102/W105 finalize as upstream W100/W101 land (<=24h); T-143 month-exam prep by 10-29; first "
        "month-boundary exam 10-31"
    )
    json.dump(hb, open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # self-verify epoch int (R170/R178 law)
    chk = json.load(open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    print("heartbeat epoch int OK:", chk["heartbeat_epoch_utc"])

    # ---- wrap commit + push ---------------------------------------------------
    payload = [
        "state-bm-c.json", "round_reports-bm-c.md", "fleet/machines/bm-c.json",
        "docs/daily_report/REPORT-2026-10-02.json", "docs/daily_report/REPORT-2026-10-02.md",
        "docs/live_usage/LIVE-2026-10-02.json", "docs/live_usage/LIVE-2026-10-02.md",
        "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
        "results/_attrition_guard_scan.json", "results/autofill_state.bm-c.json",
        "results/compute_audit.bm-c.json", "results/compute_audit.json",
        "results/dispatcher_state.bm-c.json", "results/fund_premium_status.json",
        "results/fundamental_b_layer_filter.json", "results/futures_update_status.bm-c.json",
        "results/futures_update_status.json", "results/lhb_update_status.bm-c.json",
        "results/lhb_update_status.json", "results/pool_dualrun.bm-c.jsonl",
        "results/regime_state.bm-c.json", "results/regime_state.json",
        "results/saturation_engine/face_bm-c.json", "results/saturation_engine_state.bm-c.json",
        "results/token_usage.bm-c.json", "results/token_usage.json",
        "results/update_status.bm-c.json", "results/update_status.json",
        "results/_r376bmc_commit_push.py", "results/_r376bmc_s6_driver.py",
        "results/_r376bmc_surgical_push.py",
    ]
    git("add", "--", *payload)
    rc, out, _ = git("diff", "--cached", "--stat")
    print("staged:", out[-400:])
    rc, out, err = git("commit", "-F", REPO + r"\.codely-cli\scratch\msg-r376c.txt")
    print("commit rc", rc, (out or err)[:200])
    rc, out, err = git("push", "origin", "main", check=False)
    print("push rc", rc, (out or err)[:400])
    if rc != 0:
        print("WRAP PUSH BLOCKED -- surgical fallback required (r366)")


if __name__ == "__main__":
    main()
