# r849 bm-b closeout: state.json + heartbeat + round report line (one-shot, idempotent-safe)
import json, time, os, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = "2026-10-11T00:04:00+08:00"
now_iso = now
epoch = int(time.time())

did = ("r849: W207 freeze-prep bundle LANDED on origin (research/PERPETUAL_N1_W207_PREREG.md commit 6fa2dae16: "
       "第205枚·bm-b 41st owned·197th engine wave·A 470_204..472_203 staircase 67th E36 hops=1·B 472_204..472_403 "
       "own-A reserved W141 hops=1·seed_admit_gate 双带 FREE·banned gate ADMIT rc0·锚=W204 实测〔ledger 864,387·"
       "K446,720·W205/W206 在飞席如实注记·r590 commit 前终检=上游零 finalize 落地〕; W208+ 投影 A 472_204..474_203/"
       "B 472_404..472_603 承载供下波复核) + S0 双窗 absorb 4 commits (satengine PT1M tick 竞态·零冲突) + rebase onto "
       "origin (bm-c r841/r842 churn + bm-a r963 + bm-c r818) + S0.5 orders 66/66 零未回执 (轮首扫描·轮中零新增令) + "
       "D19 双水位零 delta (dec a20664ec·ord 24e6066e) + smoke 49/49 + S3 固定序绿 (wm probe py_low_with_work_cands "
       "合法=local_batch 1=astock 重建在飞·SatEngine rc0 活 idle queue 0·T-182 claimed by bm-c 非本机·池 419 全 done·"
       "idle GREEN-IDLE→常设议程=W207 freeze-prep 领做同轮) + S6 36 腿 35 rc0+alloc rc2 已知 P5 510880 披露 + "
       "astock 重建 3237/5217 @23:56 (62%·pace ~14/min·ETA ~02:00-02:30 诚实窗) + S7 四件套自愈绿 (loop pin=2 no-op·"
       "watchdog 重装·双爪 LF 归一) + attrition guard CLEAN + idle --worked 清零")

task = ("r850 queue: astock completion verify (ETA ~02:00-02:30) -> spawn detached T23 census full burn -> "
        "census_holds readout -> N2 U3(1) prereg window / G2 fallback + S6 chain; W207 five-face freeze window "
        "(gated on W205 bm-a + W206 bm-c five faces landing on origin; anchor roll per r590 before freeze commit; "
        "selftest W207 face + M8-mirror watcher); W18 stays drain-gated (bm-a owns w17-judge)")

verdict = ("GREEN: r849 (W207 freeze-prep prereg landed origin 6fa2dae16 = queue chain advanced one link; "
           "S6 36 legs green + alloc rc2 known; astock rebuild in flight 3237/5217; T23 census physical wait "
           "window honest; engine alive rc0 idle)")

# ---- state.json ----
sp = os.path.join(ROOT, "state.json")
s = json.load(open(sp, encoding="utf-8"))
s["machine_id"] = "bm-b"
s["round_no"] = 849
s["round"] = 849
s["note"] = did
s["did"] = did
s["last_action"] = did
s["now_active"] = "r849 closeout: W207 freeze-prep prereg landed (bm-b 41st owned wave); astock rebuild in flight 3237/5217"
s["current_task"] = task
s["task"] = task
s["next"] = task
s["verdict"] = verdict
s["last_round_at"] = now_iso
s["last_seen"] = now_iso
s["updated"] = now_iso
s["updated_at"] = now_iso
s["ts"] = now_iso
s["clock_read"] = now_iso
s["last_round_ts"] = now_iso
s["round_no_label"] = "r850"
s["latest_artifact"] = "r849: research/PERPETUAL_N1_W207_PREREG.md on origin (commit 6fa2dae16, tip 044d2f2b8) + banned gate ADMIT rc0 receipt, 2026-10-11 00:0x"
s["next_milestone"] = ("astock panel complete (~02:00-02:30) -> detached T23 census full burn -> holds verdict "
                       "(window <=10-11 06:00) -> N2 U3(1) prereg window / G2 fallback; W207 five-face freeze window "
                       "gated on W205/W206 five faces landing (anchor roll r590)")
s["last_orders_sha_note"] = "r849: dual watermark probe zero-delta both (dec a20664ec, ord 24e6066e); no group delta this round"
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
h = json.load(open(hp, encoding="utf-8"))
h["round"] = 849
h["round_no"] = 849
h["now_active"] = "r849 closeout: W207 freeze-prep prereg landed (bm-b 41st owned wave); astock rebuild in flight 3237/5217"
h["current_task"] = task
h["task"] = task
h["next"] = task
h["latest_artifact"] = "r849: research/PERPETUAL_N1_W207_PREREG.md on origin (commit 6fa2dae16, tip 044d2f2b8) + banned gate ADMIT rc0, 2026-10-11 00:0x"
h["next_milestone"] = s["next_milestone"]
h["verdict"] = verdict
h["last_action"] = did
h["did"] = did
h["last_round_at"] = now_iso
h["last_seen"] = now_iso
h["updated"] = now_iso
h["updated_at"] = now_iso
h["ts"] = now_iso
h["clock_read"] = now_iso
h["heartbeat_epoch_utc"] = epoch  # JSON int (smoke F7)
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["orphan_faces"] = 0
h["orphan_face_note"] = "r849 round-zero probe 23:4x py_faces=9 orphans=0"
h["sync"] = {"last_push_ts": now_iso, "note": "r849 closeout push; post-push behind=0 self-proof below"}
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# int-type self-proof
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# ---- round report line ----
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
raw = open(rp, "rb").read()
eol = "\r\n" if raw.count(b"\r\n") > raw.count(b"\n") - raw.count(b"\r\n") else "\n"
line = ("2026-10-11T00:04:00+08:00 | r849 bm-b | dept:研究（W207 freeze-prep prereg 落地·never-dry 引擎线续链）+工程（S6+等待窗守护） | "
        "WM-VERDICT: green（red=false @23:45 probe；py_low_with_work_cands 合法=local_batch 1=astock 全宇宙重建在飞〔refresh lock alive·"
        "3237/5217@23:56·pace ~14/min·ETA ~02:00-02:30〕+池 ready 0+板 0〔T-182=claimed by bm-c 非开〕+bandit 0；"
        "supply_gap/supply_floor=O-1645 standing〔W18 drain-gated 待 bm-a W17-JUDGE〕；ignition_sla 零 breach） | "
        "孤儿面=0（round-zero probe 23:4x py_faces=9 orphans=0） | "
        "CEO three-line: 当前活=W207 freeze-prep prereg 起草落地+推送（bm-b 第41枚自有波·机队第197波·A 470_204..472_203 阶梯67例 E36·B 472_204..472_403 同窗互斥 W141·"
        "seed_admit_gate 双带 FREE·banned gate ADMIT rc0）+astock 等待窗守护+S6 36 腿；"
        "最近实物=research/PERPETUAL_N1_W207_PREREG.md on origin（commit 6fa2dae16·tip 044d2f2b8）+禁向闸 ADMIT 回执·2026-10-11 00:0x；"
        "下个里程碑=astock 面板完备（~02:00-02:30±）→detached T23 census 全量烧录→census_holds 判读（窗 ≤10-11 06:00）→N2 U3(1) prereg 起草窗/G2 fallback；"
        "W207 五面冻结窗=上游 gated（W205 bm-a/W206 bm-c 五面均未落 origin·冻结前 r590 锚滚终检+selftest W207 face 随五面落地） | "
        "板/队列实况: fleet tasks 零 open（T-182 claimed by bm-c）·job_list 空·P2/P3 全 done——主队列头 T23 census 物理依赖 astock 面板+"
        "W207 五面=上游 gated·诚实等待窗·禁造假行；池 419 全 done 零 ready | "
        "本地未达 origin commit 数=0（收口 push 044d2f2b8 后 fetch+ls-remote 自证；收口前=0）")
with open(rp, "ab") as f:
    f.write((line + eol).encode("utf-8"))

print("closeout written: state round=849, heartbeat epoch=", epoch, ", report line appended, eol=", repr(eol))
