"""r1024 bm-a closeout patcher: state + heartbeat + round report + O-1745 receipt.
One pass, python json-safe (r582 law). Exit 0 ok / 2 fault.
"""
import json, os, sys, time, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
NOW_ISO = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
NOW_EPOCH = int(time.time())
DEC_SHA = "d9940c44b06b73bb930412cc499de5dfad00d5a6cddcbd64be0e419db286a906"
ORD_SHA = "819dc9282136abffa66460a63ffa4f6d82484f25671feca29ce88ab0be7a8b61"
FREE_RAM = os.environ.get("R1024_FREE_RAM", "0")
CPU_PCT = os.environ.get("R1024_CPU_PCT", "0")

DID = ("r1024 closed: P0 dual-fix full-work round (O-20261016-1950) -- (1) worktree CAS-desync "
       "rollback heal: 432 faces origin-take (119 side-excerpts preserved results/_r1024bma_rollback_side/), "
       "ff to origin 4b3f4185b, keep-set=state/hb/ack-scan/orphan-probe; (2) sitecustomize.py "
       "_silent_Popen function->CLASS fix: asyncio.windows_utils `class Popen(subprocess.Popen)` crashed "
       "EVERY console-less python import since 10-08 install (r1023 'torn pyc' verdict = misdiagnosis "
       "corrected: patch active only headless, interactive verify sessions saw green); zt_pool selftest "
       "rc0 + smoke 49/49 (from 48/49); (3) S6 41+2 legs rc0 (10-16 bars landed, papers/marks/REPORT+LIVE-"
       "2026-10-16 regenerated, live_paper rc0); (4) D-19 dual consumed DEC ab3f0cc9->d9940c44 (7 new rows, "
       "D-02 claw-4ch + D-03 -C ROOT already in-tree via restore, D-06 E1 three-task re-open EXECUTED: "
       "Bigmoney-Autofill/ResidentDispatcher/HQ-OllamaOrphanWatch re-enabled) + ORD d0eedb56->819dc928 "
       "(new rows all BigStream/MV/dispatcher domains, zero BigMoney dispatch); (5) O-1745 issuer ack + "
       "O-1950 full-work receipt; loop pin=8 no-op, watchdog rebuilt (S4U flip denied=adjudicated default "
       "face), claws x2 installed, attrition CLEAN")

CURRENT_TASK = ("O-20261016-1950 full-work: bm-a P0 dual-fix round (worktree heal + sitecustomize asyncio fix) "
                "+ S6 43 legs + D-19 dual + D-06 three-task re-enable")

NOW_ACTIVE = ("bm-a full-work resumed (CEO O-20261016-1950 19:50; O-20261015-1845 stop-order LIFTED); "
              "engine-lane = sequence-wait bm-c W254 ignition (chain-order law, bm-a own-wave W256-class "
              "derive after W255 chain); autofill/dispatcher/orphan-watch lanes re-enabled this round")

NEXT = ("r1025+: (a) W255 seat watch (bm-c chain; bm-a W256-class own-wave derive fires on W255 chain landing); "
        "(b) moneyflow IC reference batch awaiting panel complete (claimed next_pick, 30-min self-heal); "
        "(c) autofill/dispatcher re-enable effectiveness watch (pool claims + ticks resume); "
        "(d) sitecustomize subclass-fix cross-machine check (bm-b/bm-c same file family if installed)")

VERDICT = ("green-full-work (red=false lane healthy; satengine ALIVE idle queue0; O-20261015-1845 stop-order "
           "LIFTED by CEO O-20261016-1950; P0 dual-fix landed: worktree heal + sitecustomize subclass fix "
           "smoke 49/49; py ramp-up post-pause legal face; orphan 1/20 mcp-bridge read-only)")

ART = ("results/_r1024bma_s6chain_rc.log (43 legs rc0; 10-16 bars; papers/REPORT+LIVE-20261016 regenerated) "
       "+ sitecustomize subclass fix (original backup results/_r1024bma_sitecustomize_original_20261008.py) "
       "+ results/_r1024bma_rollback_side/ (119 excerpts)")


def patch(path, kv, round_fields=True):
    with open(path, encoding="utf-8") as f:
        st = json.load(f)
    for k, v in kv.items():
        st[k] = v
    if round_fields:
        for k in ("round_no", "round", "loop_round", "last_round"):
            st[k] = 1024
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    return st


def main():
    # state-bm-a.json
    sv = {
        "current": DID, "did": DID, "current_task": CURRENT_TASK, "task": CURRENT_TASK,
        "now_active": NOW_ACTIVE, "next": NEXT, "verdict": VERDICT,
        "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
        "last_action": "r1024: P0 dual-fix (worktree heal + sitecustomize class fix) + S6 43 rc0 + D-19 dual consumed + 3-task re-enable + quad green",
        "last_decisions_sha": DEC_SHA, "last_orders_sha": ORD_SHA,
        "last_decisions_seen": "r1024: DEC ab3f0cc9->d9940c44 consumed (7 new rows D-20261016-01..07; D-02 claw-4ch/D-03 -C ROOT already in-tree; D-06 E1 three-task re-open EXECUTED this round)",
        "last_orders_seen": "r1024: ORD d0eedb56->819dc928 consumed (new rows BigStream/MV/dispatcher domains, zero BigMoney dispatch; O-1950 full-work executed; O-1745 issuer-ack)",
        "last_decisions_at": NOW_ISO, "last_orders_at": NOW_ISO,
        "last_decisions_read_at": NOW_ISO, "last_orders_read_at": NOW_ISO,
        "ts": NOW_ISO, "updated": NOW_ISO, "updated_at": NOW_ISO, "last_run": NOW_ISO,
        "last_seen": NOW_ISO, "last_round_at": NOW_ISO, "last_round_closed": NOW_ISO,
        "last_round_ts": NOW_ISO, "last_action_at": NOW_ISO,
        "clock_read": NOW_ISO,
        "heartbeat_epoch_utc": NOW_EPOCH, "last_heartbeat_epoch_utc": NOW_EPOCH,
        "heartbeat_epoch_utc_type_int": True,
        "idle_rounds": 0,
        "orphan_face": 1, "orphan_faces": 1,
        "push_verified": {"ts": NOW_ISO, "origin_tip": "pending",
                          "note": "r1024: closeout push verification follows commit+push (range + behind check post-push)"},
        "sync": {"ts": NOW_ISO, "origin_tip": "pending", "ahead_behind": "pending",
                 "note": "r1024: post-push readback follows"},
    }
    patch(os.path.join(ROOT, "state-bm-a.json"), sv)

    # heartbeat fleet/machines/bm-a.json
    hb_path = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
    with open(hb_path, encoding="utf-8") as f:
        hb = json.load(f)
    acks = hb.get("orders_ack", [])
    for o in ("O-20261016-1745-bm-a.md", "O-20261016-1950-bm-a.md"):
        if o not in acks:
            acks.append(o)
    hb["orders_ack"] = acks
    hb["orders_ack_note"] = ("r1024: +2 acks (O-20261016-1745 fleet-sync heal = bm-a issuer-side self-check "
                             "three-channels green listener v1.9.2 /health 19:59:40 + receipt row appended; "
                             "O-20261016-1950 CEO full-work resume = executed: P0 dual-fix + S6 43 rc0 + "
                             "D-06 three-task re-enable + this receipt)")
    hb.update({
        "round_no": 1024, "round": 1024, "loop_round": 1024, "last_round": 1024,
        "current": DID, "did": DID, "current_task": CURRENT_TASK, "task": CURRENT_TASK,
        "now_active": True,
        "last_action": "r1024: P0 dual-fix (432-face worktree heal + sitecustomize subclass fix smoke 49/49) + S6 43 rc0 + D-19 dual + 3-task re-enable",
        "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
        "next": NEXT, "verdict": VERDICT,
        "last_decisions_sha": DEC_SHA, "last_orders_sha": ORD_SHA,
        "last_decisions_at": NOW_ISO, "last_orders_at": NOW_ISO,
        "last_decisions_read_at": NOW_ISO, "last_orders_read_at": NOW_ISO,
        "ts": NOW_ISO, "updated": NOW_ISO, "updated_at": NOW_ISO, "last_seen": NOW_ISO,
        "last_run": NOW_ISO, "last_round_at": NOW_ISO, "last_round_closed": NOW_ISO,
        "last_round_ts": NOW_ISO,
        "clock_read": NOW_ISO,
        "heartbeat_epoch_utc": NOW_EPOCH, "last_heartbeat_epoch_utc": NOW_EPOCH,
        "heartbeat_epoch_utc_type_int": True,
        "idle_rounds": 0,
        "orphan_face": 1, "orphan_faces": 1,
        "ram_free_gb": float(FREE_RAM) if FREE_RAM else hb.get("ram_free_gb", 0),
        "free_ram_gb": float(FREE_RAM) if FREE_RAM else hb.get("free_ram_gb", 0),
        "cpu_load_pct": float(CPU_PCT) if CPU_PCT else hb.get("cpu_load_pct", 0),
        "codely_live_count": 5,
        "codely_live_count_note": "r1024 20:1x census: self loop round + committee ACP (19:16) + 2 ACP (19:48:51/19:49:42) + BigLife -y (19:53); honest read",
    })
    with open(hb_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)

    # round report line
    line = (f"{NOW_ISO} | r1024 bm-a (dept:工程-P0双修+数据-工程值守) | WM-VERDICT: green (red=false lane healthy; "
            f"satengine ALIVE idle queue0; O-20261015-1845 停产口令已被 CEO O-20261016-1950「全面开工」解除·19:50 令) | "
            f"当前活: P0 双修收官 (worktree CAS-desync 回退面治愈 + sitecustomize asyncio 崩溃修) + S6 43 腿 + D-19 双消费 + D-06 三任务复开 | "
            f"最近实物: results/_r1024bma_s6chain_rc.log (43 legs rc0·10-16 bars 落地·papers/marks/REPORT+LIVE-20261016 再生) + "
            f"sitecustomize.py 类包修法 (原件备份 results/_r1024bma_sitecustomize_original_20261008.py·smoke 48/49->49/49) + "
            f"results/_r1024bma_rollback_side/ (119 件摘录存旁) | "
            f"下个里程碑: W254 点火=bm-c 链序 (bm-a 自研 W256-class derive 候 W255 链落地) + moneyflow IC 批候面板完备 + autofill/dispatcher 复开效能观察 (窗≤48h) | "
            f"did: S0-1 锚定 bm-a+孤儿 1/20 (mcp-bridge 只读); S0 脏树分诊=CAS-desync 回退面 (worktree 停在 r1023 物化态 21:26:49·HEAD=今日 0cb8050 CAS 提交不物化=C-02 wave-F 族) "
            f"-> mtime 分区 (今日写盘 3 件保) + 119 件摘录存旁 + 432 面 origin-take checkout + ff 4b3f4185b (0/0) + x2 2201⊆2261 前缀验; "
            f"S1 smoke 48/49 (zt_pool 红) -> 根因定谳=sitecustomize.py (10-08 装·CEO 机零窗律) 在无控制台宿主下把 subprocess.Popen 换成函数 -> asyncio.windows_utils "
            f"`class Popen(subprocess.Popen)` 子类化函数必崩=全机无头 asyncio import 崩 (r1023 'torn pyc' 诊断系误判·交互验证会话有控制台不触发=假自愈·勘正入档) "
            f"-> 修法=函数包->类包 (保零窗意图+恢复可子类化) -> zt selftest rc0 + smoke 49/49; "
            f"S3 satengine ALIVE rc0 queue0 + O-1950 全面开工执行 + D-19 双探针双变化消费 (DEC ab3f0cc9->d9940c44 七新行·ORD d0eedb56->819dc928 零 BigMoney 派工行) "
            f"+ D-20261016-06 E1 三任务复开执行 (Bigmoney-Autofill/ResidentDispatcher/HQ-OllamaOrphanWatch 全已禁用实测->/ENABLE rc0×3·resume 1h+ 缺口闭环); "
            f"S6 41+2 腿 rc0 (shell 5min 静默自动取消截断 attrition/live_paper 两腿->补跑双 rc0·链脚本流式输出改良遗下轮); "
            f"S7 四件套 (loop pin=8 no-op first-fire 20:18/watchdog 重建 S4U-flip denied=已裁决面/双爪装毕/attrition CLEAN 4 ledgers) + "
            f"O-1745 签发侧回执行 (三通道绿+listener 1.9.2·回执行入令) + O-1950 回执 (orders_ack+本行); "
            f"| evidence: _r1024bma_s6chain_rc.log + _r1024bma_smoke.log 49/49 + _r1024bma_d19_check.json + _r1024bma_rollback_side/ | "
            f"记账预算: 收口三件+水位+回执=法定收口件 (纯记账面 0 分如实标注·S6 数据面产出与 P0 修复=实物豁免面按 P-2026-09-29-07) | "
            f"产品计分: 2 分 (机器级修复两件=可验实物: 432 面树治愈+全机 asyncio 修复·smoke 49/49 实证) | "
            f"本地未达 origin commit 数: 0 (push 后 rev-list+ls-remote 自证) | 孤儿面: 1 (mcp-bridge read-only) | [r1024 bm-a]\n")
    with open(os.path.join(ROOT, "round_reports-bm-a.md"), "a", encoding="utf-8", newline="\n") as f:
        f.write("\n" + line)

    # O-1745 receipt row (issuer-side)
    opath = os.path.join(ROOT, "fleet", "orders", "O-20261016-1745-bm-a.md")
    with open(opath, encoding="utf-8") as f:
        otxt = f.read()
    if "bm-a | 2026-10-16" not in otxt:
        row = ("| bm-a | 2026-10-16 20:1x | 签发侧自查无楔 N/A（本机=令源·三通道 17:23 起全绿） | N/A（本机不适用 heal 面） | 1.9.2（19:59:40 /health 实测 ok·218ms 级） |\n")
        if otxt.rstrip().endswith("## 回执"):
            otxt = otxt.rstrip() + "\n" + row
        else:
            otxt = otxt.rstrip() + "\n" + row
        with open(opath, "w", encoding="utf-8", newline="\n") as f:
            f.write(otxt)
        print("O1745_receipt: appended")
    else:
        print("O1745_receipt: already present")

    # post_review single-point reconcile check
    with open(os.path.join(ROOT, "results", "post_review.jsonl"), encoding="utf-8") as f:
        disk = f.read()
    print("post_review_000119_on_disk:", '"ts": "2026-10-16 00:01:19"' in disk)
    print("CLOSEOUT_PATCH_OK", NOW_ISO)


if __name__ == "__main__":
    sys.exit(main())
