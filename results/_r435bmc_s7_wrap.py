"""_r435bmc_s7_wrap.py -- r435 emergency wrap (round budget exhausted).

S0 surgery main product already PUSHED (T=4de95e7f). This wrap: state 435,
heartbeat (int epoch), ledger line, targeted commit+push+verify, orders
double-scan. S6 chain deferred to r436 (legs idempotent; round killed at
budget would leave partial chain -- cleaner to run full next round).
"""
import datetime
import json
import os
import subprocess
import sys
import time

CREATE = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
ROUND = 435


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=CREATE, cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace").strip(), (p.stderr or b"").decode("utf-8", "replace").strip()


def jload(p):
    with open(os.path.join(ROOT, p), "r", encoding="utf-8") as f:
        return json.load(f)


def jdump(p, obj):
    with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def main():
    # --- state-bm-c.json ---
    st = jload("state-bm-c.json")
    st["round_no"] = ROUND
    st["clock_read"] = NOW
    st["last_seen"] = NOW
    st["last_round_at"] = NOW
    st["last_round_ts"] = NOW
    st["updated"] = NOW
    st["updated_at"] = NOW
    st["last_decisions_read_at"] = NOW
    st["current_task"] = ("r435: S0 redelivery surgery DONE (r434 2 commits onto bm-a r646, 15-face newer-wins, "
                           "push verified origin/main==4de95e7f); W2 finalize RESPAWNED pid 31336 (silent-kill "
                           "forensics negative: no traceback/no WER/no fuse/no watchdog kill); S6 deferred r436 "
                           "(budget); next: r436 full S6 + W2 poll")
    st["did"] = ("r435 bm-c: WM 绿 (watermark_red=false, lane healthy; py_low legality=W2 burn in flight). "
                 "(1) S0 重大发现=r434 两 commit 从未达 origin (r434 state 假送达声明=r502 族假回执) -- 本轮隔离 "
                 "worktree cherry-pick 手术重放 ca9c3a009+b4ab54ba0 onto e74c79c95 (bm-a r646), 15 冲突面逐面 "
                 "newer-wins 裁定 (14 origin/bm-a 23:0x 新 + 1 mine lhb 22:55>22:48), 收据 "
                 "results/_r435bmc_rebase_resolve.{py,json}; push 后 fetch+rev-parse+ls-tree 三证 "
                 "origin/main==4de95e7fb80886b07c98e72b3a68b20d739e11ef, canon_sweep.py 送达自证, marker 扫描 "
                 "0 hits; O-2030 焊面交付物 (canon_sweep driver+31 capture comments) 现已全员在册. "
                 "(2) W2 judge-finalize 静默死亡诊断 (pid 31276, 19:28:59 spawn, 4.5h 满核, 22:59-23:15 窗灭, "
                 "日志零追加=零 traceback): 四查全阴 (WER 零事件/watchdog.log 零 kill+白名单不含 "
                 "mass_train/timeout 树杀无记录/crash_fuse 无该 sig) -- 同窗 22:45 轮 codely(pid 3104)+launcher "
                 "亦无声死 (run log 无 finished 行, 23:15 lock takeover 实证) = 同一外部杀手不可考, 按 "
                 "r422/r426 设计重跑净重拉 pid 31336 (23:34:14, log line 2, deadline <=10-06). "
                 "(3) S0.5 orders 152/152 零差集 (bm-a 23:30 MSG-163 认领声明已读无撞车); D-19 "
                 "4167B784 MATCH + GORDERS 68947C17 MATCH 双水位零消费; S1 smoke 47/47 "
                 "(_r435bmc_smoke_log.txt); satengine rc0 活 (last_epoch 23:30:26). S6 链顺延 r436 (轮预算 "
                 "25min 尽, 各腿幂等周末多 no-op, 全链 r436 跑净优于半链被杀); S7 claws/loop/watchdog 检查+"
                 "attrition+HANDOVER 顺延 r436. 本地未达 origin commit 数=见 push 自证 (三证).")
    st["next"] = ("(a) r436: 全 S6 37 腿链 (adapt->run->restore r429 律) + S7 全套 (claws/loop pin=5/watchdog/"
                 "attrition scan/heartbeat int-epoch 自证); (b) W2 poll: python Tools/_r426bmc_w2_judge_"
                 "finalize.py status -> w2_judge.json 落地即收养 (adapt _r426bmc_close.py 模板, count->replace->"
                 "assert 三段律) + 延迟烧日志原子 commit, deadline <=10-06; 若 31336 再度静默死 (同窗 ~4.5h) "
                 "=确定性灭门 -> 升级呈报 (防再烧三连浪费); (c) O-2030 验收证据包 10-08; (d) D-06 收口 10-07 "
                 "(pit-git 107KB sub-split + pit-data CRLF 裁定); (e) r434 S7 wrap 假送达缺陷回查 "
                 "(_r434bmc_s7_wrap.py 的 push 验证腿 vs r502 律) -- 下轮工程小活.")
    st["last_round"] = "r435 bm-c: S0 redelivery surgery (r434 undelivered commits onto bm-a r646, 15-face newer-wins, delivered 4de95e7f); W2 finalize respawned pid 31336; smoke 47/47; S6 deferred r436"
    jdump("state-bm-c.json", st)

    # --- heartbeat fleet/machines/bm-c.json ---
    hb = jload("fleet/machines/bm-c.json")
    hb["round_no"] = ROUND
    hb["clock_read"] = NOW
    hb["last_seen"] = NOW
    hb["last_seen_at"] = NOW
    hb["updated_at"] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["activity_now"] = "r435: S0 redelivery surgery pushed (4de95e7f, 15-face newer-wins receipts); W2 finalize respawned pid 31336 (silent-kill forensics negative); S6 deferred r436 (budget)"
    hb["current_task"] = "r435: S0 surgery DONE+W2 respawned; next r436: full S6 chain + W2 poll (deadline <=10-06)"
    hb["latest_artifact"] = "results/_r435bmc_rebase_resolve.json (15-face newer-wins surgery receipt) + canon_sweep.py delivered on origin/main @ " + NOW
    hb["next_milestone"] = "W2 w2_judge.json landing -> adoption (deadline <=10-06, first capture-point example); O-2030 acceptance evidence pack 10-08; D-06 closure 10-07"
    hb["prod_lanes"] = "S0 redelivery complete r435 (r434 weld-face deliverables on origin/main 4de95e7f); MASS_TRIAL_W2-JUDGE finalize respawned (pid 31336, first burn silently killed 22:59-23:15 window, forensics negative)"
    jdump("fleet/machines/bm-c.json", hb)
    assert isinstance(jload("fleet/machines/bm-c.json")["heartbeat_epoch_utc"], int), "epoch must be int"

    # --- ledger line ---
    line = (f"{NOW} | r435 | S0 重送达手术 (r434 两 commit 假送达修复: cherry-pick onto bm-a r646, 15面 newer-wins, "
            f"origin/main==4de95e7f 三证) + W2 finalize 重拉 pid 31336 (31276 静默灭门四查全阴) | 证据: "
            f"_r435bmc_rebase_resolve.json + push fetch/rev-parse/ls-tree 自证 + smoke 47/47 _r435bmc_smoke_log.txt | "
            f"下轮: r436 全 S6 链 + W2 poll + S7 补全 (预算耗尽顺延)\n")
    with open(os.path.join(ROOT, "round_reports-bm-c.md"), "a", encoding="utf-8") as f:
        f.write(line)

    # --- orders double-scan (S7) ---
    ack = set(hb.get("orders_ack", []))
    orders_dir = os.path.join(ROOT, "fleet", "orders")
    on_disk = set(os.listdir(orders_dir))
    unacked = sorted(on_disk - ack)
    print("ORDERS_DOUBLE_SCAN unacked=%d %s" % (len(unacked), unacked if unacked else "(zero)"))

    # --- targeted commit + push + verify ---
    rc, out, err = git("status", "--porcelain")
    print("DIRTY_BEFORE:\n" + out)
    targets = [
        "results/_r435bmc_rebase_resolve.py", "results/_r435bmc_rebase_resolve.json",
        "results/_r435bmc_smoke_log.txt", "results/_r435bmc_s7_wrap.py",
        "round_reports-bm-c.md", "state-bm-c.json", "fleet/machines/bm-c.json",
        "results/watermark_red.json",
        "results/autofill_state.bm-c.json", "results/dispatcher_state.bm-c.json",
        "results/saturation_engine/face_bm-c.json", "results/saturation_engine_state.bm-c.json",
    ]
    for t in targets:
        if os.path.exists(os.path.join(ROOT, t)):
            git("add", "--", t)
    rc, out, err = git("commit", "-m",
                       "round 435: S0 redelivery surgery (r434 false-push repaired: 2 commits cherry-picked onto bm-a r646, 15-face newer-wins receipts, origin/main==4de95e7f triple-verified) + W2 finalize respawn pid 31336 (silent-kill forensics negative) + smoke 47/47; S6 deferred r436 (budget)")
    print("COMMIT rc=%d %s %s" % (rc, out, err))
    rc, out, err = git("push", "origin", "main")
    ptxt = out + " " + err
    ok = rc == 0 and not any(k in ptxt for k in ("fatal", "rejected", "failed", "error"))
    print("PUSH rc=%d ok=%s %s %s" % (rc, ok, out, err))
    git("fetch", "origin")
    rc2, tip, _ = git("rev-parse", "HEAD")
    rc3, om, _ = git("rev-parse", "origin/main")
    rc4, behind, _ = git("rev-list", "--count", "HEAD..origin/main")
    rc5, ahead, _ = git("rev-list", "--count", "origin/main..HEAD")
    print("VERIFY tip=%s origin_main=%s behind=%s ahead=%s undelivered=%s" % (tip, om, behind, ahead, ahead))
    return 0


if __name__ == "__main__":
    sys.exit(main())
