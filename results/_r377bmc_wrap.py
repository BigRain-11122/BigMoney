# -*- coding: utf-8 -*-
"""r377 bm-c wrap: state 377 + round report + heartbeat + wrap commit/push.

Laws: r583 heartbeat carry-list (orders_ack etc. carried from existing file,
dynamic fields only), R170/R178 epoch int + T-format clock, status-driven
targeted add with allowlist guard (dirty-tree law), commit -F channel (r375),
push fallback = surgical reparent (r523, same-window race precedent r377).
"""
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000
ALLOW_PREFIXES = ("results/", "docs/")
ALLOW_EXACT = {
    "state-bm-c.json", "round_reports-bm-c.md", "fleet/machines/bm-c.json",
}


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

    # machine readings
    cpu_pct = idle_ram = None
    try:
        import psutil
        psutil.cpu_percent(interval=None)  # prime (r319 law)
        time.sleep(1.0)
        cpu_pct = round(psutil.cpu_percent(interval=None), 1)
        idle_ram = round(psutil.virtual_memory().available / 1e9, 1)
    except Exception as e:
        print("psutil read fail:", e)
    hb0 = json.load(open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
    gpu_free = hb0.get("gpu_free_vram_mib")

    # ---- state-bm-c.json dynamic fields only ----
    sp = os.path.join(REPO, "state-bm-c.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 377
    st["last_round_at"] = "r377"
    st["last_round_ts"] = now
    st["updated"] = now_iso
    st["last_ts"] = now_iso
    st["last_seen"] = now_iso
    st["cpu_pct"] = cpu_pct if cpu_pct is not None else st.get("cpu_pct")
    st["idle_ram_gb"] = idle_ram if idle_ram is not None else st.get("idle_ram_gb")
    st["gpu_free_vram_mib"] = gpu_free
    st["verify"] = (
        "r377: W105 burn products 12/12 COMPLETE delivered to origin (tail 3 shards face-ride "
        "83438cc37; first 9 landed via r376 wrap; engine dedup local12/remote0 healed) + S0 "
        "surgical realign r578 (fe191d370: reset --mixed + 39 faces checkout, 4 live-writers "
        "kept, resident engine kill+tick revive rc0, 4 writer tasks window) + same-window race "
        "handled: first push rejected non-ff (bm-b W106 FREEZE d6b2952e3 landed mid-window) -> "
        "r523 surgical reparent re-commit 83438cc37 push clean, ls-tree delivery blob 6af537689 "
        "both-sides identical + W106 five-faces synced + n1 selftest PASS (W104/W105/W106 legs "
        "live, dep head 584,548) + pf 9/9 + W106 seat MSG consumed+archived (bm-b A "
        "255_004..257_003/B 60_201..60_400; W107+ projection A 257_004..259_003/B "
        "60_401..60_600 re-derive-at-freeze note) + W102 finalize still gated (W100 landed "
        "r585 head 584,548 K=217,920; W101 bm-a pending, FAIL-CLOSED r307) + S6 33 legs rc0 "
        "(dualrun ZERO-DRIFT 51/3, WM green red=false lane healthy, ORANGE_COOL, lane-guarded "
        "honest no-ops, daily report + CEO page regenerated, scorecard/export/status "
        "stale-takeover legal O-2100 STALE_MIN 32-33min) + attrition CLEAN + self-heal 4/4 "
        "(loop pin=5 no-op, watchdog, claws MATCH) + smoke 47/47 + orders 143/143 double-scan "
        "+ D-19 937A373D MATCH"
    )
    st["did"] = (
        "r377: S0 surgery + W105 products 12/12 delivered 83438cc37 (reparent after same-window "
        "bm-b W106 freeze) + W106 seat consumed + S6 all-green + self-heal 4/4"
    )
    st["current_task"] = (
        "W105 delivered 12/12; bm-c engine queue empty (W107 seat OPEN -- rotation next=bm-a, "
        "bm-c takes if unclaimed next round); W102 finalize gated on W101 bm-a landing "
        "(FAIL-CLOSED r307); W105 finalize queued behind W102/W103; T-144(c) data/protocol "
        "domains + flow-sinking due 10-04/10-07; month-boundary first exam 10-31"
    )
    st["next"] = (
        "(r378)(a) W102 finalize when W101 bm-a lands on origin (fetch check -> one-pass "
        "finalize --wave 102, prev=origin chain head derive r518, no blind rerun r538); "
        "(b) W105 finalize after W102/W103 land; (c) W107 seat+freeze IF still unclaimed by "
        "bm-a at round start (projection from W106 registered tails A 257_004..259_003 / B "
        "60_401..60_600, re-derive never transcribe); (d) T-144(c) data-domain split due 10-04; "
        "(e) T-143 month-exam prep 10-29; (f) month-boundary first exam 10-31"
    )
    st["heartbeat_epoch_utc"] = epoch
    st["clock_read"] = now_iso
    st["last_decisions_read_at"] = now
    st["last_round"] = (
        "2026-10-02 r377 bm-c: W105 products 12/12 delivered (83438cc37) + S0 realign + "
        "W106-sync + S6 all-green + smoke 47/47 + orders 143/143"
    )
    json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- round report (S5) ----
    rp = os.path.join(REPO, "round_reports-bm-c.md")
    line1 = (
        f"{now_iso} | r377 | watermark: 绿（red=false·lane=healthy·引擎面 W105 12/12 已交付·W106 bm-b 冻结在烧）"
        "｜当前活=bm-c 引擎队列空（never-dry 下一席 W107 开放·轮转自然属 bm-a·若其未认领下轮 bm-c 接手）"
        "｜最近实物=results/saturation_engine/face_bm-c.json（W105 烧录产物 12/12 全量落 origin 83438cc37·17:5x）"
        "+ results/perpetual_faces/n1_w100_results.json（链头 584,548·K=217,920）"
        "｜下个里程碑=W102 finalize 候 W101 bm-a 落账（≤48h）→ T-144(c) 数据域拆件 10-04 → 月界首考 10-31 "
        "‖ 本轮主产：W105 产物 12/12 补齐送达（尾 3 片 face ride 提交·首 9 片 r376 wrap 已落·引擎 dedup local12/remote0 治愈）"
        "+S0 外科重对齐（r578：fe191d370 39 面 checkout·4 活写件保本地·常驻引擎 pid 验属击杀+tick 复活 rc0·4 写者任务禁复窗）"
        "+同窗竞态实证=首推被拒（bm-b W106 FREEZE d6b2952e3 窗内落 origin）→r523 外科 re-parent 83438cc37 直推净成"
        "·ls-tree 送达自证 face blob 6af537689 双面恒等+W106 面同步+n1 selftest PASS（W104/W105/W106 三腿在场·W106 dep head 584,548）+pf 9/9"
        "+W106 席位 MSG 消费归档（bm-b A 255_004..257_003/B 60_201..60_400·W107+ 投影 A 257_004..259_003/B 60_401..60_600 冻结时必重 derive）"
        "+S6 33 腿 rc0（dualrun ZERO-DRIFT 51/3·WM 绿·ORANGE_COOL·车道腿诚实 no-op·日报+CEO 页再生"
        "·scorecard/export/status 三面 bm-a 心跳 32-33min 陈旧接管合法 O-2100 STALE_MIN）"
        "+attrition CLEAN+自愈 4/4（loop pin=5 no-op·watchdog·双爪 MATCH）+smoke 47/47+orders 143/143 双扫+D-19 937A373D MATCH "
        "‖ 验证证据：push d6b2952e3..83438cc37 净成 / S6 log 51 行零败 / n1+pf rc0 / ls-tree blob 恒等 "
        "‖ 下轮指针：W102 finalize 候 W101；W105 finalize 候 W102/W103；W107 席位开放观察；T-144(c) 数据域拆件 10-04 [via bm-c r377]"
    )
    rc, out, _ = git("fetch", "origin")
    rc, out, _ = git("rev-list", "--count", "HEAD..origin/main")
    behind = out.strip()
    line2 = f"{now_iso} | r377 | 本地未达 origin commit 数={behind}（wrap 前取数；主产 83438cc37 已直推净成）"
    with open(rp, "a", encoding="utf-8") as f:
        f.write(line1 + "\n" + line2 + "\n")

    # ---- heartbeat (r583: dynamic only, carry lists) ----
    hb = dict(hb0)
    hb["round_no"] = 377
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
        "healthy: W105 products 12/12 delivered on origin (83438cc37); S6 33 legs rc0; "
        "smoke 47/47; W102 finalize gated on W101 bm-a"
    )
    hb["current_task"] = (
        "W105 delivered 12/12; engine queue empty (W107 open seat, rotation next=bm-a); "
        "W102/W105 finalize chain-gated; T-144(c) data split due 10-04"
    )
    hb["activity_now"] = "S7 wrap (state 377 + heartbeat + round report); engine idle post W105 delivery"
    hb["latest_artifact"] = (
        "results/saturation_engine/face_bm-c.json -- W105 12/12 products on origin 83438cc37 "
        "(17:52); chain head n1_w100_results.json 584,548 K=217,920"
    )
    hb["next_milestone"] = (
        "W102 finalize when W101 bm-a lands (<=48h); T-144(c) data-domain split by 10-04; "
        "month-boundary first exam 10-31"
    )
    json.dump(hb, open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    chk = json.load(open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    print("heartbeat epoch int OK:", chk["heartbeat_epoch_utc"])

    # ---- status-driven targeted add (allowlist guard) ----
    # NB: use RAW stdout here -- git()'s global .strip() eats the FIRST line's
    # leading space (" M path" -> "M path") and shifts column slicing (caught
    # by the allowlist guard this round; parse raw to fix the root cause).
    r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                       capture_output=True, creationflags=NO_WINDOW)
    out = r.stdout.decode("utf-8", "replace")
    payload = ["state-bm-c.json", "round_reports-bm-c.md",
               "fleet/machines/bm-c.json", "results/_r377bmc_wrap.py"]
    for l in out.splitlines():
        if not l.strip():
            continue
        path = l[3:].strip().strip('"')
        if path in ALLOW_EXACT or path.startswith(ALLOW_PREFIXES):
            if path not in payload:
                payload.append(path)
        else:
            print("UNEXPECTED DIRTY PATH (manual review):", path)
            sys.exit(5)
    print("payload N =", len(payload))
    git("add", "--", *payload)
    rc, out, _ = git("diff", "--cached", "--stat")
    print("staged tail:", out[-300:])
    rc, out, err = git("commit", "-F", REPO + r"\.codely-cli\scratch\msg-r377c-wrap.txt")
    print("commit rc", rc, (out or err)[:200])
    rc, out, err = git("push", "origin", "main", check=False)
    print("push rc", rc, (out or err)[:300])
    if rc != 0:
        print("WRAP PUSH BLOCKED -- reparent path required (r523, see results/_r377bmc_reparent.py pattern)")


if __name__ == "__main__":
    main()
