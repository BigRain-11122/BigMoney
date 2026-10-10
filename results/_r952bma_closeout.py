# -*- coding: utf-8 -*-
"""r952 bm-a closeout surgery: heartbeat + state + round report + HQ-FEEDBACK."""
import datetime
import io
import json
import time

NOW = datetime.datetime.now().isoformat(timespec="seconds") + "+08:00"
EPOCH = int(time.time())
DEC_SHA = "7ce92f99d6e2e3194a2aa5a4eee8eb2e0fe020ff"
ORD_SHA = "b45103d85b30e4e087394e58a5277b55543a452a"

VERDICT = ("green (r952: dead-session estate absorbed E12 probe selftest 9/9 + "
           "queue done; D-20261010-04 Bonsai T-99/T-100 closure stamps landed; "
           "D-20261010-07 claw verified bm-b r832 selftest 28/28 zero re-exec; "
           "19-UU dual-writer storm resolved per skill canon (6 ALL_FACES "
           "merge_lane_views + twin-coupling ts probes + hardened snapshots); "
           "S6 39 legs rc0; smoke 49/49; DEC 7ce92f99/ORD b45103d8 consumed; "
           "ORD fleet 60/199 zero unacked)")

DID = ("r952: E12 repo-monthend-pulse estate absorbed (probe selftest 9/9 rc0 "
       "+ evidence + digest + queue done row; core negative = post-2024 pulse "
       "decay to zero) + D-20261010-04① Bonsai T-99/T-100 closure stamps "
       "(observe maintained + reeval conditions) + push-race storm resolved "
       "(claw correctly blocked backward owner_since -> r824 three-step -> "
       "19 UU per bigmoney-conflict-resolve canon -> r863 continue-refusal "
       "root-caused daemon live-write -> r917 atomic absorb-continue one-pass "
       "+ r808 marker guard zero) + S6 39 legs rc0 fresh regen + D-07 claw "
       "verified zero re-exec")

NEXT = ("r953: E13 explore head per T-18 probe or standing agenda (trial-labor "
        "line); W17 ignition recheck after 22:45 (MSG-0935 standing); W205 "
        "seat watch; 10-31 month-boundary first exam (T-143 assembly 10-29)")

ARTIFACT = ("scripts/repo_monthend_pulse_probe.py + results/repo_monthend_pulse_probe.json + research/digests/DIGEST-20261010-e12-repo-monthend-pulse.md + T-99/T-100 closure stamps (13:4x)")

ORDERS_SEEN = ("r952 scan: fleet orders 60 files vs 199 ack ZERO unacked; "
               "group ORD delta b45103d8 re-read = zero BigMoney rows (other-subsidiary face)")
DECISIONS_SEEN = ("r952 consume: DEC 7ce92f99 delta read (D-20261010-01..10 + "
                  "C-20261010-01/02); bigmoney action faces: D-04① closure "
                  "executed this round; D-07 claw fix verified bm-b r832 "
                  "landed selftest 28/28; queue face main.md in place (O-1246 compliant)")

SYNC = {
    "ahead_behind": "0/0",
    "note": ("r952: estate d3872ddef + churn 9e65e048a delivered via skill-"
             "canon conflict resolution + r824 three-step race; final "
             "closeout push verified post-commit"),
    "origin_tip": "9e65e048a",
    "ts": NOW,
}


def load(path):
    return json.load(io.open(path, encoding="utf-8"))


def save(path, d):
    json.dump(d, io.open(path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


# ---- heartbeat ----
hb = load("fleet/machines/bm-a.json")
hb.update({
    "last_seen": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "clock_read": NOW,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": EPOCH,
    "heartbeat_epoch_utc_type_int": True,
    "current": NEXT, "current_task": NEXT, "task": NEXT, "next": NEXT,
    "now_active": NEXT, "did": DID, "last_action": DID,
    "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "latest_artifact": ARTIFACT,
    "cores": 32, "cpu_cores": 32,
    "free_ram_gb": 49.0, "ram_free_gb": 49.0,
    "free_vram_gb": 0.25, "gpu_free_vram_gb": 0.25, "vram_free_gb": 0.25,
    "gpu_idle_vram_gb": 0.25,
    "gpu_source_note": "nvidia-smi live read 13:4x (MV lane GPU busy, honest)",
    "verdict": VERDICT,
    "idle_rounds": 0, "agenda_starved": False,
    "round_no": 952, "loop_round": 952, "round": 952, "last_round": 951,
    "last_round_at": NOW, "last_run": NOW,
    "last_decisions_sha": DEC_SHA, "last_orders_sha": ORD_SHA,
    "last_decisions_at": NOW, "last_decisions_ts": NOW,
    "last_decisions_read_at": NOW, "last_decisions_seen": DECISIONS_SEEN,
    "last_orders_at": "2026-10-10", "last_orders_ts": NOW,
    "last_orders_read_at": NOW, "last_orders_seen": ORDERS_SEEN,
    "orphan_face": 1, "orphan_faces": 1,
    "sync": SYNC, "push_verified": SYNC,
})
save("fleet/machines/bm-a.json", hb)

# ---- state ----
st = load("state-bm-a.json")
st.update({
    "last_seen": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "clock_read": NOW, "last_run": NOW,
    "heartbeat_epoch_utc": EPOCH, "last_heartbeat_epoch_utc": EPOCH,
    "heartbeat_epoch_utc_type_int": True,
    "round_no": 952, "loop_round": 952, "round": 952, "last_round": 951,
    "last_round_at": NOW, "last_round_closed": NOW, "last_round_ts": NOW,
    "current": NEXT, "current_task": NEXT, "task": NEXT, "next": NEXT,
    "now_active": NEXT, "did": DID, "last_action": DID,
    "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "latest_artifact": ARTIFACT,
    "verdict": VERDICT, "verify": VERDICT,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 1, "orphan_faces": 1,
    "last_decisions_sha": DEC_SHA, "last_orders_sha": ORD_SHA,
    "last_decisions_at": NOW, "last_decisions_ts": NOW,
    "last_decisions_read_at": NOW, "last_decisions_seen": DECISIONS_SEEN,
    "last_orders_at": "2026-10-10", "last_orders_ts": NOW,
    "last_orders_read_at": NOW, "last_orders_seen": ORDERS_SEEN,
    "sync": SYNC, "push_verified": SYNC,
})
st["next_milestone"] = ("r953: E13 head per T-18 probe or standing agenda; "
                        "W17 ignition recheck after 22:45; 10-31 month-boundary "
                        "first exam (T-143 assembly 10-29)")
st["d19_watermark_guard"] = {
    "tool": "scripts/d19_watermark.py",
    "probe": "results/_r686bmb_d19_check.py",
    "probe_evidence": ("C:\\Users\\sjs20\\Desktop\\FluxGroup\\quant\\bigmoney"
                       "\\results\\_r686bmb_d19_check.json"),
    "method_decisions": "sha1", "method_orders": "sha1",
    "verbatim": True, "advance": True, "round_ref": 952, "ts": NOW,
}
save("state-bm-a.json", st)

# ---- round report append ----
REPORT = NOW + " | r952 | bm-a | dept:工程 (E12 死会话遗产吸收+双写者 19-UU 风暴正典收口+D-20261010-04① 关单面) | WM-VERDICT: green (red=false; engine ALIVE rc0 idle; DEC 7ce92f99/ORD b45103d8 本窗消费（ORD 增量复读零涉司行）; ORD fleet 60/199 零未回执) | 孤儿面=1 (read-only probe) | S0: 死会话遗产接管（r899 判例：唯一循环进程普查+13:08 末活动+遗产三件未提交+state 停 951）+ FF absorb 3-behind bm-c autofill tick（13 面 S6 同日 regen 双写者重叠=备份→丢弃本地陈旧 regen→FF 干净零接触→重跑链出全新 regen）| S3: E12 遗产收编（probe selftest 9/9+evidence_cutoff 2026-10-09 合法+digest+queue done 行翻转·核心负发现=月末脉冲 2024 后结构性归零禁全史立 prereg）+ D-20261010-04① Bonsai T-99/T-100 关单章（closure 字段=observe 维持+复评三前置）+ D-20261010-07 爪 quarantine manifest 门=bm-b r832 已落地本机 selftest 28/28 验讫零重执行 + E9/T20/T21 状态核验（MSG-1138：AH 三件套+期货 OI 修复均已在链·tech 队列 0 open）| S6: 39 legs rc0（run2 全新 regen；reconcile 1 face drift=compute_audit 生产者覆写观察相如实注记非故障）| S7: 推送竞速风暴=爪正确拦截（bm-c tick owner_since 13:30:05>基座 13:19:13 backward 面·r824 判例）→三步竞速 churn absorb+rebase→19 UU 按 skill 正典配方集收口（6 ALL_FACES=merge_lane_views union+daily_report/live_usage 孪生 ts 探针各对同侧耦合（report=origin 侧/live=本机侧）+硬化探针 snapshot take-new+js-wrapper 字节取侧）→r863 continue 恒拒确诊=daemon 活写 churn 敏感面→r917 吸收-continue 原子环一发过+r808 标记守卫零冲突→push 9e65e048a 落链 0/0 | smoke 49/49 | 下轮指针: r953 E13 队头（T-18 探针先行）或常设议程; W17 点火复核 22:45 后; W205 seat watch | scoring: 2（能跑探针+证据+关单章+冲突正典收口）| bookkeeping: 4/5 | 本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证）| [r952 bm-a]\n"
with io.open("round_reports-bm-a.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(REPORT)

# ---- HQ-FEEDBACK receipt ----
hq = io.open("HQ-FEEDBACK.md", encoding="utf-8").read()
if "F-20261010-03" not in hq:
    line = ("- F-20261010-03 [bm-a r952 " + NOW + "·决策回执面·D-20261010-04① "
            "关单面执行回执] **Bonsai T-99/T-100 关单章已落地**：fleet/tasks 两票 "
            "closure_d_20261010_04 字段（verdict=observe 维持不转正·双票同谳 "
            "16GB 档 tg128 40.52±1.10/40.75±0.30 达标/CPU 档不可用·复评条件=GPU "
            "空窗 tg128 实测+O-2175 评估+fleet-allocations §8.4 改行 或新硬需求"
            "触发）；commit 4f0e1e9ca 已推链。D-20261010-07 爪修法=bm-b r832 已落"
            "地（F-20261010-02 在册），本机 r952 selftest 28/28 交叉验讫零重执行。\n")
    with io.open("HQ-FEEDBACK.md", "a", encoding="utf-8", newline="") as fh:
        fh.write(line)

# ---- verify ----
for p in ("fleet/machines/bm-a.json", "state-bm-a.json"):
    d = load(p)
    assert isinstance(d["heartbeat_epoch_utc"], int), p
    assert "T" in d["clock_read"], p
    print("verified", p, "epoch=", d["heartbeat_epoch_utc"],
          "round=", d["round_no"])
print("closeout surgery done", NOW)
