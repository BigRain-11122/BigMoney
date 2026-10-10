"""r840 bm-b closeout driver: state.json + heartbeat + round report line.

Load-modify-field-write law (r818: heartbeat big-list fields never hand-
retyped wholesale); epoch int law (R170/R178); clock ISO8601 T-separator
law (R262)."""
import json
import datetime as dt
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(dt.datetime.now().timestamp())

R = lambda *p: os.path.join(ROOT, *p)

NOTE = ("r840: astock_daily gate disk-truth guard P0 fix (status-face-only "
        "freshness deadlock after r834 tree deletion killed gitignored "
        "per/*.csv; _disk_truth_override + per_files_on_disk disclosure + "
        "selftest 6 legs + live-fire spawned detached full-universe rebuild "
        "5,229 in flight); T23 alphagen paradigm census slice-1 = "
        "POSITIVE-with-riders (grammar pin distinct from N2 axis-gate pin -> "
        "N2 U3 channel-1 new-syntax drafting window legal to open; riders: "
        "A158 lineage negative prior + corpus rebuild in flight + RL claims "
        "unverified -> slice-2 random-grammar cheap census before RL "
        "commitment); pit-data.md r840 pit line; 5x HANDOVER r840 row "
        "(window r826-r840, r830-r835 ledger-absent P0 window disclosed).")

DID = ("r840: astock gate disk-truth guard fix + universe rebuild spawned + "
       "T23 alphagen census (POSITIVE-with-riders) + tech.md T23 done + "
       "pit-data r840 line + 5x HANDOVER row + S6 41 legs")

VERDICT = ("r840: GREEN; smoke 49/49; gate P0 fix live-fired (rebuild pid "
           "alive); dualrun ZERO-DRIFT streak 25; supply_gap standing flag "
           "(O-1645); alloc rc=2 known P5 stale-leg 510880; zero double-burn")

CURRENT_TASK = ("r841 queue: astock rebuild progress verify (completion "
                "window ~10-11 00:30) -> T23 slice-2 random-grammar cheap "
                "census (gated on panel completion) -> N2 U3 drafting-window "
                "prereg if census holds + S6 chain")

LATEST_ARTIFACT = ("r840: scripts/update_astock_daily.py (gate disk-truth "
                   "guard + selftest 6 legs, live-fired rebuild spawn) + "
                   "research/digests/DIGEST-20261010-t23-alphagen-paradigm-"
                   "census.md + results/_r840bmb_t23_alphagen_census.json, "
                   "2026-10-10 21:0x")

NEXT_MILESTONE = ("r841 (<=10-10 21:3x): astock rebuild verify; T23 slice-2 "
                  "prep; W18 legs stay drain-gated (bm-a owns w17-judge)")

NOW_ACTIVE = ("r840 closeout: astock gate P0 fix + T23 alphagen census "
              "positive + S6 41 legs")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def main():
    # ---- state.json (bm-b canonical state file)
    sp = R("state.json")
    st = load(sp)
    assert st.get("machine_id") == "bm-b", st.get("machine_id")
    st.update({
        "round_no": 840, "round": 840, "round_no_label": "r841",
        "note": NOTE, "did": DID, "verdict": VERDICT,
        "current_task": CURRENT_TASK, "task": CURRENT_TASK,
        "next": "r841 queue per current_task",
        "now_active": NOW_ACTIVE, "last_action": DID,
        "latest_artifact": LATEST_ARTIFACT,
        "next_milestone": NEXT_MILESTONE,
        "last_round_at": NOW, "ts": NOW, "updated": NOW,
        "last_seen": NOW, "clock_read": NOW, "updated_at": NOW,
        "last_round_ts": NOW,
    })
    dump(sp, st)

    # ---- heartbeat (fleet/machines/bm-b.json) -- field-level update only
    hp = R("fleet", "machines", "bm-b.json")
    hb = load(hp)
    assert hb.get("machine_id") == "bm-b"
    ack_before = len(hb.get("orders_ack", []))
    hb.update({
        "round": 840, "round_no": 840,
        "now_active": NOW_ACTIVE, "current_task": CURRENT_TASK,
        "task": CURRENT_TASK, "next": "r841 queue per current_task",
        "latest_artifact": LATEST_ARTIFACT,
        "next_milestone": NEXT_MILESTONE, "verdict": VERDICT,
        "last_action": DID,
        "last_round_at": NOW, "last_seen": NOW, "updated": NOW,
        "ts": NOW, "clock_read": NOW, "updated_at": NOW,
        "heartbeat_epoch_utc": EPOCH,
        "idle_rounds": 0, "agenda_starved": False,
        "orphan_faces": 0,
        "orphan_face_note": "r840 orphan probe 21:0x py_faces=8 orphans=0",
        "sync": {"last_push_ts": NOW,
                 "note": "r840 closeout; post-push fetch self-proof in S7"},
    })
    assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
    assert "T" in hb["clock_read"] and "+08:00" in hb["clock_read"]
    assert len(hb.get("orders_ack", [])) == ack_before, "orders_ack mutated!"
    dump(hp, hb)

    # ---- round report line (bm-b canonical ledger)
    line = (
        f"{NOW} | r840 bm-b | dept:数据（**astock_daily gate 盘面守卫 P0 修复**："
        "13:16 P0 删除事故毁 gitignored per/*.csv 5,217 件而 tracked 状态件持续宣称 "
        "complete→gate「panel fresh」假新鲜死锁〔14:21 git 恢复只救状态面〕——修="
        "_disk_truth_override〔磁盘 per-files 计数==0 或<声明值即推翻 complete→"
        "first-pull〕+per_files_on_disk/disk_truth_override 双 disclosure+selftest 6 腿"
        "+实弹拉起分离全宇宙重建〔5,229·pid alive 实证·~3.6h 完备窗〕·坑律直写 pit-data.md r840 行）"
        "+dept:研究（**T23 alphagen 范式评估普查=slice-1 出列=正（POSITIVE-with-riders）"
        "→N2 U3「①全新语法」起草窗合法可开**：L1 语法撞号裁定=N2 18-tuple 轴门组合 pin vs "
        "alphagen 公式树+RL/MCTS 生成机制双异·非撞号〔vendored A158 基座 29 滚动算子族+9 kbar+"
        "price0·158 解析门 PASS〕；L2 语料面=astock 宽股票截面面板=alphagen 论文语料结构等价面"
        "〔P0 盘面死亡+同窗修复披露〕+可执行宇宙错配披露〔core48 门/输入特征消费路线="
        "A158-TSGATE/A10 先例〕；L3 可跑性=IC 普查机械在位+RL 件待建〔宣称未核〕·slice-2="
        "随机语法廉价普查先于 RL 承诺；L4 判读口径预演=PIT rank-IC+同语法 nulls+全起点虚拟时点+"
        "DSR 跨波累计+D6≥0.7+出场轴显式门；三骑士=R1 A158 血统负先验〔157/158+A9 0/9+A10 0/16〕+"
        "DSR 墙高/R2 语料重建在途/R3 RL 宣称未核——证据=results/_r840bmb_t23_alphagen_census."
        "{py,json}+research/digests/DIGEST-20261010-t23-alphagen-paradigm-census.md+"
        "tech.md T23 消耗记录〔队列 1→0〕）+dept:舰队（W17-JUDGE owner=bm-a 让路·W18 "
        "drain-gated 延窗·fund 三族 GM 待裁=等待面一行声明不重扫）"
        " | WM-VERDICT: green（red=false @20:33·probe py_low_with_work_cands 且 "
        "local_batch=1=astock 重建合法候选开工·supply_gap=O-1645 standing）"
        " | 孤儿面=0（probe py_faces=8）"
        " | CEO three-line: 当前活=r840 收口：astock gate P0 修复+全宇宙重建拉起+T23 范式评估正；"
        f"最近实物={LATEST_ARTIFACT}；下个里程碑={NEXT_MILESTONE}"
        " | smoke 49/49 | S6 41 腿：40×rc0+alloc rc=2（已知 P5 stale-leg 510880 披露面维持）"
        "——dualrun ZERO-DRIFT streak 25·compute_audit FLAG supply_gap 常设·D19 probe 双 MATCH "
        "零 delta·orders 双扫 CLEAN（65 orders/190 acks/unacked=[]）·SAT 活 rc0 idle"
        " | 5x HANDOVER r840 行落账（增量窗 r826-r840 合并覆盖·r830-r835 缺行=P0 事故窗如实披露）"
        " | W17-JUDGE 排水验证不可执行（bm-a 属主 w17-judge-0of1）如实注记·本机零双烧"
        " | 本地未达 origin commit 数=0（S7 post-push fetch+rev-parse 自证）\n")
    with open(R("logs", "iteration-loop", "round_reports.md"), "a",
              encoding="utf-8") as f:
        f.write(line)
    print("closeout written: state.json r840, heartbeat epoch", EPOCH,
          ", round line appended")


if __name__ == "__main__":
    main()
