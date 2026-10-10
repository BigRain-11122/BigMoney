"""r866 bm-b S7 books: round report line + state.json (bm-b) round 866 +
heartbeat fleet/machines/bm-b.json + idle_trigger --worked (real product
this round -> counters cleared per O-20261007-2315). Zero console CJK.
"""
import io
import json
import subprocess
import time
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

REPORT = "logs/iteration-loop/round_reports.md"
STATE = "state.json"
HEART = "fleet/machines/bm-b.json"

DID = (
    "r866: S0 stash daemon faces + pull up-to-date then mid-round rebase onto "
    "bm-c r856/r857 close (161bd57c2->3a498f2d3->239887fc4, zero code-dir "
    "changes) + orders diff 0 (67/192/0, S7 rescan 0) + D19 dual watermark "
    "identical (dec caca0c6e/ord f90233c7) + smoke 49/49 + orphan face=0 "
    "(11 py faces) + boards clear + SAT alive rc0 idle; PRIMARY PRODUCT = "
    "N2-W20 REPLICATION WAVE slice-2 FREEZE WINDOW: SEED_REGISTRY three-band "
    "registration (gen=739_500/scrnull=740_000/unc=740_500, r682 live derive "
    "walk 14 slots past W18+W19 halo chain, X=739,500 bit-identical to r865 "
    "draft-probe readout) + band gate ADMIT (trio CLEAN vs 624 reserved "
    "intervals; NEW self-face classification law E53: first run REFUSE on "
    "own-wave r865 HANDOVER readout citation -> SELF disclosed-not-blocking, "
    "foreign zero-hit) + seed_admit rc0 x3 span=500 + banned_direction rc0 + "
    "r687 pre-write check (origin three keys absent, prereg origin-side "
    "DRAFT) + prereg FROZEN flip (five-condition machine proof, R250 "
    "one-step same commit 526f3d4d3) + slice-3 JUDGED BURN same round (W19 "
    "r864 cadence): V1=HOLDS (family max |ICIR| 0.478 > pooled null p95 "
    "0.087, pooled 336>=300 one-shot, elapsed 153.2s/300s cap) + RP2 "
    "LEVERAGE REPLICATION TRUE (0.478>=0.353 -> 2/2 independent readings -> "
    "N2 feedback-leverage claim UPGRADED citable) + RP1 band replication "
    "FAILS honestly disclosed (0.478 above [0.20,0.45], no re-tune) + M1 "
    "0/48 positive-direction (negative |t|>=3 27/48 descriptive face) + "
    "attrition decomposition (10 t84s3 + 3 in-batch dup = 13 excluded -> 49 "
    "enrolled -> 1 skip 2.0%<10% -> 48 ok -> 336 pooled; survival 77.4% "
    "W19 bit-same) + ledger 877,227->877,723 (+496 envelope, 398 consumed + "
    "98 berth identity) + attrition row ic_judgment guard CLEAN (entries "
    "112) + sec.7/sec.8 one-shot backfill + TREASURE row (material pool +48 "
    "W20-tagged) + METHODOLOGY E53 card (commit 37dd75bae -> origin "
    "5439bcceb post-rebase); S6 41 legs 40 rc0 + alloc rc2 known 510880 "
    "stale-leg carried; S7 quartet green (loop pin=2 no-op, watchdog, both "
    "claws) + idle --worked; zero registration zero engine runs"
)

LINE = (
    ts + " | r866 bm-b | dept:研究（N2-W20 复现波 slice-2 冻结窗+slice-3 判读"
    "烧录同轮）+工程（S6 链·S7 收口）| 实况三行：当前活=N2-W20 冻结+判读复现烧录"
    "同轮落地（V1=HOLDS 0.478>0.087·RP2=2/2 杠杆复现成立=N2 反馈杠杆宣称升级"
    "可引用·RP1 带复现带外上方如实披露）/最近实物=results/alphagen_w20/"
    "W20-2026-10-09.json + research/PERPETUAL_N2_W20_PREREG.md FROZEN"
    "（freeze 526f3d4d3+burn 37dd75bae→origin 5439bcceb·06:4x-07:0x）/"
    "下个里程碑=素材池消费预注册评估窗 ≤10-13（独立轨道）+N2 同族防换皮重跑"
    "护栏（RP2=2/2 后 z 轴/期限/阈值变体=禁开面）+W210 冻结候 W209 落链守望"
    "（bm-a M9 链）| WM-VERDICT: green（red=false·py_low_board_clear 合法"
    "白名单·板空=W20 链后常设线供给步·compute_audit pool_starvation/"
    "supply_floor 旗=波后正常态·下轮供给决策=素材池消费 prereg 评估窗轨道）| "
    "S0: stash→rebase 快进（bm-c r856/r857 close·scripts/research 零改动）·"
    "orders 差集 0（67/192/0·S7 复扫 0）·D19 双水位恒等（dec caca0c6e/ord "
    "f90233c7）·smoke 49/49·孤儿面=0（11 py faces）| S3: SAT alive rc0 "
    "idle·boards clear·五条件机证（selftest 28/28 复跑+probe 11/11 复跑+band "
    "gate ADMIT X=739,500 与 r865 只读候选逐位一致+seed_admit rc0×3+"
    "banned_direction rc0）| 主产出=W20 三带登记+prereg FROZEN（R250 一步律"
    "同 commit）+判读烧录 V1=HOLDS+RP2=2/2 定谳+RP1 带外如实披露+损耗分解"
    "（10+3=13 排除→49 enrolled→1 skip 2.0%→48 ok→336 pooled·存活率 77.4%"
    "与 W19 逐位同值）+账本 877,227→877,723（+496·398+98 恒等）+attrition "
    "行 guard CLEAN+§7/§8 一次定稿回填+TREASURE 行+方法论 E53 新卡（band-"
    "gate self-face 分类律·首跑 REFUSE→分类律→ADMIT live 实证）| PUSH: 首推"
    "拒（bm-c r857 face 同窗推进）→全量 stash+rebase+pop→push 239887fc4.."
    "5439bcceb·behind=0 送达自证 | S6: 41 腿 40 rc0+alloc rc2 已知 510880"
    "（P5 TRANSFER 待件）·lane-guard 诚实跳过面 7 腿（scorecard/live_paper/"
    "t35/t24×2/build_status/daily_scorecard·host=bm-a）·dualarm streak 21 "
    "零漂移 | S7: 四件套 ALIVE（loop pin=2 no-op·watchdog 幂等重注·双爪在位）"
    "+attrition guard CLEAN+idle --worked | 本地未达 origin commit 数=0"
    "（books push 后 fetch+rev-list 自证）| 零注册零引擎零策略宣称\n"
)

with io.open(REPORT, "a", encoding="utf-8", newline="\n") as f:
    f.write(LINE)

with io.open(STATE, encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "clock_read": ts, "ts": ts, "last_round_at": ts, "last_round_ts": ts,
    "last_seen": ts, "updated": ts, "updated_at": ts,
    "round": 866, "round_no": 866, "round_no_label": "r866",
    "machine_id": "bm-b",
    "did": DID, "last_action": DID,
    "now_active": "r866 closeout: N2-W20 replication wave freeze+burn "
                  "landed (V1=HOLDS + RP2 2/2 leverage citable, RP1 "
                  "band-miss disclosed)",
    "latest_artifact": "r866: results/alphagen_w20/W20-2026-10-09.json + "
                       "research/PERPETUAL_N2_W20_PREREG.md FROZEN + "
                       "results/_r866bmb_w20_band_gate.txt (ADMIT receipt) "
                       "+ knowledge/METHODOLOGY_ASSETS.md E53 card",
    "next": "r867 queue: material-pool consumption prereg evaluation "
            "window <=10-13 (separate lane, next round primary candidate) "
            "+ N2 post-2/2 guardrail (same-family z-axis/horizon/threshold "
            "variants = banned re-open face per W20 sec.8) + W210 freeze "
            "watch (bm-a W208/W209 chain, seats blocked) + moneyflow IC "
            "panel-ready watch (bm-a lane) + O-20261011-0012 CPU-max "
            "maintained + next-wave supply decision (pool_starvation flag "
            "post-burn normal state)",
    "task": "r867 queue: material-pool consumption prereg evaluation "
            "window <=10-13 (separate lane, next round primary candidate) "
            "+ N2 post-2/2 guardrail (same-family z-axis/horizon/threshold "
            "variants = banned re-open face per W20 sec.8) + W210 freeze "
            "watch (bm-a W208/W209 chain, seats blocked) + moneyflow IC "
            "panel-ready watch (bm-a lane) + O-20261011-0012 CPU-max "
            "maintained + next-wave supply decision (pool_starvation flag "
            "post-burn normal state)",
    "current_task": "r867 queue: material-pool consumption prereg "
                    "evaluation window <=10-13 + N2 post-2/2 guardrail + "
                    "W210 freeze watch + O-20261011-0012 CPU-max maintained",
    "next_milestone": "material-pool consumption prereg evaluation window "
                      "<=10-13, chain head 877,723 monotone (zero append "
                      "until next wave), N2 leverage claim citable 2/2 "
                      "(W19+W20)",
    "verdict": "GREEN: r866 (W20 replication wave freeze+burn same round "
               "landed: V1=HOLDS 0.478>0.087 pooled 336>=300; RP2 2/2 "
               "leverage claim citable; RP1 band-miss disclosed honestly; "
               "smoke 49/49; S6 40/41 rc0 alloc-known; orders diff 0; D19 "
               "identical; SAT alive; attrition CLEAN; orphan face=0)",
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r866 round probe: py_faces=11 alive, orphans=0 "
                        "(zero live seats; W20 freeze+burn same-window "
                        "in-round, zero detached burns)",
})
with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

with io.open(HEART, encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "clock_read": ts, "ts": ts, "last_seen": ts, "updated_at": ts,
    "last_round_at": ts, "last_action_at": ts,
    "heartbeat_epoch_utc": epoch,
    "round": 866, "round_no": 866,
    "idle_rounds": 0, "agenda_starved": False,
    "did": DID, "last_action": DID,
    "current_task": st["current_task"], "task": st["task"],
    "next": st["next"],
    "now_active": st["now_active"],
    "latest_artifact": st["latest_artifact"],
    "next_milestone": st["next_milestone"],
    "verdict": st["verdict"],
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": st["orphan_face_note"],
    "sync": {
        "last_push_ts": ts,
        "note": "r866 closeout push (freeze+burn commits + S6 chain + "
                "books); post-push behind=0 self-proof via fetch+rev-list",
    },
})
assert isinstance(hb["heartbeat_epoch_utc"], int)
with io.open(HEART, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

r = subprocess.run(["python", "Tools/idle_trigger.py", "--worked"],
                   capture_output=True, text=True)
print("books done; report+state+heartbeat written; idle --worked rc=",
      r.returncode, r.stdout.strip()[-120:])
