"""r865 bm-b books: round report line + state.json + heartbeat + S7 orders rescan."""
import io
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_EPOCH = int(time.time())
R = "r865"

DID = (
    "r865: S0 stash daemon faces + pull --rebase fast-forward "
    "(be3ad243b..4996ca7f2, bm-c r855 batch + daily faces) + orders diff 0 "
    "(67/192/0, S7 rescan 0) + D19 dual watermark identical "
    "(dec caca0c6e/ord f90233c7 zero delta) + smoke 49/49 + orphan face=0 "
    "(round probe 16 py faces alive) + boards clear (job 0, asks 0, open 0) "
    "+ SAT alive rc0 idle; PRIMARY PRODUCT = N2-W20 REPLICATION WAVE "
    "slice-1 (draft window): research/PERPETUAL_N2_W20_PREREG.md DRAFT "
    "(replication wave -- 2nd independent readout of the feedback-search "
    "lever; RP1 band [0.20,0.45] / RP2 leverage-vs-census-0.353 readout "
    "faces pre-declared sec.4; zero band values in draft per r702 law; "
    "meaning-gate answers in sec.0) + draft probe "
    "results/_r865bmb_n2w20_draft_probe.py (9 faces green: W19 consumed "
    "face 51 enrolled = 48 ok + 3 h1-skip reconciles 48x7=336 observed "
    "pooled; chain head 877,227 match; band derive read-only X=739,500 "
    "trio walk 14 slots forced past W19 family halo top 739,000; "
    "B-arithmetic B=7 the ONLY feasible budget under the 500 cap "
    "(B=8 envelope 558>500), survival requirement 69.12% vs empirical "
    "faces census 75.0% / W19 77.4%, envelope 496<=500; census-union "
    "99 formulas overlap 0) + runner clone scripts/alphagen_beam_w20.py "
    "(r836 clone law all params explicit in selftest L1c; NEW "
    "W19-result dedup source _w19_consumed_formulas (anti-dredge "
    "zero-formula-re-burn face, 51 formulas union census 48 + ledger "
    "text belt); hermetic selftest 28/28 PASS incl NEW L5c W19-source "
    "parse leg + L13 FREEZE-GATE refuse machine proof rc2 zero-writes; "
    "probe 11/11 PASS incl NEW w19_source check) + F-04 "
    "MSG-20261011-0628-bmb-n2w20-draft.md; freeze+burn = next round "
    "(W19 cadence r864 precedent: freeze five-condition + judged burn "
    "same round); S6 41 legs 40 rc0 + alloc rc2 known 510880 "
    "stale-leg carried; S7 loop task no-op pin=2 + watchdog registered "
    "+ both claws installed + attrition guard CLEAN + idle --worked; "
    "zero burn zero ledger append zero seed consumption this round"
)

VERDICT = (
    "GREEN: r865 (W20 replication-wave slice-1 landed: prereg DRAFT + "
    "9-face draft probe + runner clone selftest 28/28 + probe 11/11; "
    "smoke 49/49; S6 40/41 rc0 alloc-known; orders diff 0; D19 "
    "identical; SAT alive; attrition CLEAN; orphan face=0)"
)

NEXT = (
    "r866 queue: N2-W20 FREEZE WINDOW (five-condition machine proof + "
    "band gate live derive walk past W18+W19 halos + seed_admit_gate "
    "rc0 x3 + banned_direction_gate rc0 + SEED_REGISTRY three-band "
    "registration same commit + FROZEN flip per R250 one-step law) + "
    "same-window slice-3 JUDGED BURN (runner ready; W19 r864 "
    "freeze+burn same-round precedent; RP1/RP2 replication readout = "
    "the 2/2 or 1/2 leverage verdict) + W210 freeze watch (bm-a "
    "W208/W209 chain, seats blocked) + moneyflow IC panel-ready watch "
    "(bm-a lane) + material-pool consumption prereg evaluation window "
    "<=10-13 (separate lane) + O-20261011-0012 CPU-max maintained"
)

NOW_ACTIVE = (
    "r865 closeout: N2-W20 replication-wave slice-1 landed (prereg "
    "DRAFT + draft probe 9 faces + runner selftest 28/28), freeze+burn "
    "queued next round"
)

LATEST_ARTIFACT = (
    "r865: research/PERPETUAL_N2_W20_PREREG.md (DRAFT) + "
    "scripts/alphagen_beam_w20.py (selftest 28/28, probe 11/11) + "
    "results/_r865bmb_n2w20_draft_probe.json (9-face receipt)"
)

NEXT_MILESTONE = (
    "N2-W20 freeze + judged replication burn <=10-12 (next round r866; "
    "RP1/RP2 = 2/2 or 1/2 leverage verdict face), material-pool "
    "consumption prereg evaluation window <=10-13, chain head 877,227 "
    "monotone (zero append this round)"
)

ORPHAN_NOTE = (
    "r865 round probe: py_faces=16 alive, orphans=0 (zero live seats; "
    "W20 slice-1 = draft window, zero detached burns)"
)


def main():
    # ---- 1. round report line (append, UTF-8 LF)
    line = (
        f"{NOW_ISO} | {R} bm-b | dept:研究（N2-W20 复现波 slice-1 起草窗·"
        "F-04 先行）| 工程面（S6 链 40/41 rc0·alloc rc2 已知面携带）| "
        "实况三行：当前活=N2-W20 复现波 slice-1 落地（草案+探针+runner "
        "克隆·冻结+烧录=下轮 r866）/最近实物=research/"
        "PERPETUAL_N2_W20_PREREG.md DRAFT + scripts/alphagen_beam_w20.py"
        f"（selftest 28/28·06:2x-06:3x）/下个里程碑=W20 冻结+判读烧录 "
        "≤10-12（RP1/RP2 复现定谳面）+素材池消费 prereg 评估窗 ≤10-13 | "
        "WM-VERDICT: green（red=false·板空=W19 链后常设线供给步·合法）| "
        "S0: stash daemon faces→pull --rebase fast-forward（be3ad243b.."
        "4996ca7f2）·orders 差集 0（67/192/0·S7 复扫 0）·D19 双水位恒等"
        "（dec caca0c6e/ord f90233c7）·smoke 49/49·孤儿面=0（16 py "
        "faces）| S3: SAT alive rc0 idle·boards clear·W20 意义门三问"
        "（复现研究问题/消费方=N2 杠杆线收口+素材池扩容/T-84s3 去重源"
        "扩容 99 式零重烧）| 主产=W20 prereg DRAFT（RP1/RP2 复现读数面"
        "预声明·零带值 r702）+起草探针 9 面全绿（X=739,500 步进过 W19 "
        "halo·B=7 闸内唯一·存活要求 69.12% vs 实证 75/77.4%）+runner "
        "克隆（L5c W19 源解析新腿·L13 拒烧机证）| 本地未达 origin "
        "commit 数=0（push 后 fetch+rev-list 自证）| 零烧录零账本零种子"
    )
    p = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
    with io.open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n" + line + "\n")

    # ---- 2. state.json (root, bm-b state)
    p = os.path.join(REPO, "state.json")
    st = json.load(io.open(p, encoding="utf-8"))
    st["round_no"] = 865
    st["round"] = 865
    st["round_no_label"] = R
    st["did"] = DID
    st["last_action"] = DID
    st["verdict"] = VERDICT
    st["next"] = NEXT
    st["task"] = NEXT
    st["current_task"] = NEXT
    st["now_active"] = NOW_ACTIVE
    st["latest_artifact"] = LATEST_ARTIFACT
    st["next_milestone"] = NEXT_MILESTONE
    st["orphan_face"] = 0
    st["orphan_face_note"] = ORPHAN_NOTE
    st["orphan_faces"] = 0
    st["clock_read"] = NOW_ISO
    st["last_round_at"] = NOW_ISO
    st["last_round_ts"] = NOW_ISO
    st["last_seen"] = NOW_ISO
    st["ts"] = NOW_ISO
    st["updated"] = NOW_ISO
    st["updated_at"] = NOW_ISO
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    # ---- 3. heartbeat fleet/machines/bm-b.json
    p = os.path.join(REPO, "fleet", "machines", "bm-b.json")
    hb = json.load(io.open(p, encoding="utf-8"))
    hb["round_no"] = 865
    hb["round"] = 865
    hb["did"] = DID
    hb["last_action"] = DID
    hb["last_action_at"] = NOW_ISO
    hb["last_round_at"] = NOW_ISO
    hb["last_seen"] = NOW_ISO
    hb["ts"] = NOW_ISO
    hb["updated"] = NOW_ISO
    hb["updated_at"] = NOW_ISO
    hb["clock_read"] = NOW_ISO
    hb["heartbeat_epoch_utc"] = NOW_EPOCH
    hb["verdict"] = VERDICT
    hb["next"] = NEXT
    hb["task"] = NEXT
    hb["current_task"] = NEXT
    hb["now_active"] = NOW_ACTIVE
    hb["latest_artifact"] = LATEST_ARTIFACT
    hb["next_milestone"] = NEXT_MILESTONE
    hb["orphan_face"] = 0
    hb["orphan_face_note"] = ORPHAN_NOTE
    hb["orphan_faces"] = 0
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")

    # ---- 4. S7 orders double-scan rescan
    orders = sorted(f for f in os.listdir(os.path.join(REPO, "fleet",
                                                      "orders"))
                    if f.startswith("O-") and f.endswith(".md"))
    ack = set(hb.get("orders_ack", []))
    missing = [o for o in orders if o not in ack]
    print(json.dumps({"round": R, "orders_total": len(orders),
                      "ack_count": len(ack), "missing": missing,
                      "epoch_int": isinstance(
                          hb["heartbeat_epoch_utc"], int)}))


if __name__ == "__main__":
    main()
