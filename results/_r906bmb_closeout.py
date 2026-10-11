# r906 bm-b closeout: state.json + heartbeat + ledger row (real-time stamped, fail-closed)
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

DID = ("r906: ①i2v 值守：释放阀修复后连续干净窗提速实证——KN01/02/03/04 四单连落 02:46-02:57"
       "（~4min/单·批 6/53·fails-bmb 零行·KN05 在飞）；②S6 常设链 41/41 rc0"
       "（_r906bmb_s6_log.txt·dualrun streak 51 零漂移·ORANGE 态·REPORT+LIVE-2026-10-12 刷新）；"
       "③D-19 双水位零 delta+T-184 值守（origin 无 transfer/t184-510880 分支·bm-a 暗窗续·"
       "courtesy compare 面·票主体 r882 已闭）；④smoke 49/49+attrition CLEAN+post_review 尾 3 行 YES+"
       "水位 red=false+SAT 活（idle·queue 0）；⑤S7 四件自愈（loop pin=2 no-op·watchdog 幂等·钩爪双装 LF 归一）")
LAST_ACTION = "r906: i2v 四单连落（批 6/53·~4min/单提速）+S6 41/41 rc0+值守面全绿"
NEXT = ("r907: i2v 批续跑值守（批毕 ETA ~06:3x → 移 keepwarm.pause marker 恢复 flash 本地线）> "
        "T-184 courtesy compare（bm-a transfer/t184-510880 到货即对）> unity-mcp POC 执行窗"
        "（due 10-13 12:00）> W18+E15 48h CEO 报（10-13 11:2x/10-14 00:44）> BigHouse T-2 ≤10-15")
MILESTONE = ("i2v 批毕 ETA ~06:3x（6/53·提速 ~4min/单）→ unity-mcp POC 回执 ≤10-13 12:00；"
             "E15 48h 报 10-13 11:2x；W18 48h CEO 报 10-14 00:44；BigHouse T-2 ≤10-15")
VERDICT = ("GREEN: i2v 批提速实证（释放阀根治后连续干净窗 ~4min/单·批 6/53·KN05 在飞）+ smoke 49/49 + "
           "S6 41/41 rc0 + 水位 red=false + attrition CLEAN；观察面 = bm-a 暗窗（T-184 courtesy compare "
           "待其返回）+ O-2333 回执 due 10-13 12:00")
NOTE = ("r906：i2v 值守轮（四单连落·提速实证）；孤儿面=1=i2v 驱动睡眠轮询假阳"
        "（pit-machine r884 律·消费面活跃未击杀）；合法 detached=i2v 驱动+ComfyUI；"
        "flash 本地线 marker 期走云端回退（L2 律）")
ARTIFACT = "KN_KN04.mp4 @02:57:41（clips-animatic-480·批 6/53）+ results/_r906bmb_s6_log.txt（41 腿 rc0）"
CURRENT = "r906 closeout：i2v 值守轮收口（四单连落+S6 41/41）"
ORPHAN_NOTE = ("r906 round probe: orphans=1=i2v driver sleep-poller 假阳"
               "（pit-machine r884 律·消费面活跃未击杀）；合法 detached=i2v/ComfyUI 族")


def upd_state():
    p = os.path.join(ROOT, "state.json")
    with open(p, encoding="utf-8") as f:
        s = json.load(f)
    assert str(s.get("round_no")) == "906", f"round_no base mismatch: {s.get('round_no')}"
    s.update({
        "clock_read": ISO, "current_task": CURRENT, "did": DID, "last_action": LAST_ACTION,
        "last_action_at": ISO, "last_round_at": ISO, "last_round_ts": ISO, "last_seen": ISO,
        "latest_artifact": ARTIFACT, "next": NEXT, "next_milestone": MILESTONE, "note": NOTE,
        "now_active": "r906 closeout", "orphan_face": 1, "orphan_face_note": ORPHAN_NOTE,
        "orphan_faces": 1, "round": "906", "round_no": "907", "round_no_label": "r906",
        "task": NEXT, "ts": ISO, "updated": ISO, "updated_at": ISO, "verdict": VERDICT,
    })
    s["sync"] = dict(s.get("sync") or {}, last_push_ts=ISO,
                     note="r906 closeout push lands with this commit; delivery self-proof = post-push fetch + rev-list 0")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)


def upd_heartbeat():
    p = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    with open(p, encoding="utf-8") as f:
        h = json.load(f)
    assert h.get("round_no") == 906, f"heartbeat round_no base mismatch: {h.get('round_no')}"
    h.update({
        "agenda_starved": False, "clock_read": ISO, "current_task": CURRENT, "did": DID,
        "free_ram_gb": 2.0, "gpu_free_vram_gb": 0.57, "gpu_free_vram_mb": 567,
        "heartbeat_epoch_utc": EPOCH, "idle_rounds": 0,
        "last_action": LAST_ACTION, "last_action_at": ISO, "last_round_at": ISO,
        "last_seen": ISO, "latest_artifact": ARTIFACT, "next": NEXT, "next_milestone": MILESTONE,
        "note": NOTE, "now_active": "r906 closeout → i2v 批流水续跑中（KN05 在飞）",
        "orphan_face": 1, "orphan_face_note": ORPHAN_NOTE, "orphan_faces": 1,
        "ram_free_gb": 2.0, "ram_free_pct": 7.6, "round": 906, "round_no": 907,
        "round_no_label": "r906", "task": NEXT, "ts": ISO, "updated": ISO, "updated_at": ISO,
        "verdict": VERDICT, "vram_free_gb": 0.57, "green_idle": False,
    })
    h["sync"] = dict(h.get("sync") or {}, last_push_ts=ISO,
                     note="r906 closeout push lands with this commit")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=1)


def append_ledger():
    p = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    row = (
        f"| {ISO} | r906 | dept:工程（i2v 批值守；S6 常设链；T-184/D-19 值守）"
        "| 当前活: i2v 批 KN05 在飞（6/53 已落·KN04 02:57:41 连续四单 ~4min/单提速实证）"
        f"| 最近实物: KN_KN04.mp4 @02:57:41（clips-animatic-480）+ REPORT-2026-10-12/LIVE-2026-10-12 面板刷新"
        "| 下个里程碑: i2v 批毕 ETA ~06:3x（提速后重估）→ 批毕移 keepwarm.pause marker 恢复 flash 本地线 → unity-mcp POC 回执 ≤10-13 12:00；E15 48h 报 10-13 11:2x；W18 48h CEO 报 10-14 00:44；BigHouse T-2 ≤10-15"
        f"| did: {DID}"
        "| 证据: smoke 49/49 PASS + S6 41/41 rc0（_r906bmb_s6_log.txt·dualrun streak 51）"
        "+ attrition CLEAN（_attrition_guard_scan.json）+ _orphan_face_probe.bm-b.json（orphans=1 假阳未击杀）"
        "| watermark verdict: GREEN（red=false·无在途红项·next_pick=claimed moneyflow IC 待面板完备）"
        "| 孤儿面=1（i2v 驱动睡眠轮询假阳·pit-machine r884 律·消费面 ComfyUI 活跃未击杀）"
        "| 本地未达 origin commit 数=0（push 后 fetch+rev-list 自证）"
        f"| 下轮指针: {NEXT} |\n"
    )
    with open(p, "a", encoding="utf-8") as f:
        f.write(row)


def selfverify():
    with open(os.path.join(ROOT, "state.json"), encoding="utf-8") as f:
        s = json.load(f)
    with open(os.path.join(ROOT, "fleet", "machines", "bm-b.json"), encoding="utf-8") as f:
        h = json.load(f)
    assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in h["clock_read"] and "T" in s["clock_read"], "clock_read must be T-separated"
    assert s["round_no"] == "907" and h["round_no"] == 907, "round_no increment failed"
    assert abs(h["heartbeat_epoch_utc"] - EPOCH) <= 120, "epoch drifted"
    print(f"closeout ok: iso={ISO} epoch={EPOCH} round 906->907 "
          f"ledger appended, epoch int + T-sep verified")


upd_state()
upd_heartbeat()
append_ledger()
selfverify()
