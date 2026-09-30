# r261 bm-c closeout: round report line + state 260->261 flip + heartbeat (R170/R178 epoch-int law).
import io, json, time, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

DID = ("r261: (a) SLOT-9 step-6 runner build FULL SAME-ROUND LOOP (W5 r249 pattern, "
       "W7 r256 mirror): scripts/innovation_quota_w9.py built (W1-W7 skeleton "
       "parameterization; verbatim-import _r260bmc_w9_d6_cells_probe.py "
       "crowd_positions/cell_returns r456 zero-drift paradigm parity-asserted + "
       "_r259bmc_w9_crowding_probe.py load_core48/build_faces; G-ANCHOR battery "
       "from berth+freeze facts) -> selftest 27/27 -> real-panel verify bit-exact "
       "(1635x48, decidable 1616, votes 1525/1599/715/824, crowd_ge3 860, asym/sym "
       "flips 71/77, author-verbatim threshold constants zero-drift) -> catalog "
       "runner_note BUILT flip -> fill_ladder enqueue (two gates + three checks "
       "pass) -> dispatcher same-window claim-launch (r199 law) -> **CROWD-VOTE-P1 "
       "judged verdict landed 09:38:29: 0/4 G1+G2 judged-negative family closure per "
       "s5 prediction-1 mainline [0,1]/4 low band** (ASYM-X1 0.1177/SYM-X1 0.2084 vs "
       "line 0.4081/0.4115 passive-term dominant; ASYM-X2 -0.0068/SYM-X2 0.0845; "
       "DSR~0; PBO 0.4286; entries 36/39 both >= F6 30 = berth marginal-carry "
       "resolved; ledger 357,383->359,387 +2004 linear; nulls_w9 16 shards; "
       "attrition bm-c lane row verified) -> pool SLOT-9 done flip same round "
       "(SLOT-8 churn lesson applied same day); (b) SLOT-8 W8 COV-SHRINK-AB-P1 "
       "harvest face per r244 landed-marker law: prereg s7/s8 backfilled (paired "
       "G1' FAIL 0.3716<1.1952 null-term dominant, CI contains zero, DSR 7.4e-05, "
       "12m B-beat-A 0.487 neutral band center, x2-dir OK +0.074 tiny, 4 cells 0/4, "
       "turnover 3.27/2.58 vs predicted [8,20] miss disclosed, worst-12m-dd "
       "-1.6%..-3.6% vs prior -0.30..-0.45 over-pessimistic lesson) + zoo #89 "
       "A/B route tested-and-closed annotated + pool SLOT-8 done flip with "
       "guard-bounce note (bm-a pool_worker 09:37 fail-close + bm-c dispatcher "
       "09:38 invoke both bounced by r450 single-shot guard, zero duplicate burn "
       "W5 precedent) + 48h CEO clock 09:09:22 -> 10-02 09:09. Rebase window: "
       "origin 3-commit storm (bm-a r464/r465 + bm-b r452) resolved via "
       "crash_fuse union blob-merge (r446 law) + take-ours runtime state; "
       "rebase-continue phantom-refusal pit recorded to CODELY.md + hot-cold "
       "reorg done same window (10,132B+2 new pits -> 10,154B <= 10KB line, "
       "r459/r460 verbatim to archive, zero-loss verified). S6 37-leg chain "
       "detached ALL GREEN non_green=[]. Orders 122/122 zero-diff, tasks zero "
       "open, WM red=false, decisions zero new lines, attrition guard CLEAN, "
       "smoke 26/26.")
VERIFY = ("smoke 26/26; W9 selftest 27/27 + verify bit-exact (twice: pre-commit + "
          "post-rebase); CROWD-VOTE-P1.json judged product in-tree (ledger "
          "359,387 + attrition row verified); W8 s7/s8 backfill in-tree; zoo #89 "
          "annotated; pool SLOT-8/SLOT-9 both done-flipped shared+lane double-file; "
          "push LANDED origin (29fed9c6c); CODELY hot-cold reorg zero-loss "
          "verified (r459/r460 verbatim in archive); attrition guard CLEAN 4 "
          "ledgers; heartbeat epoch int self-verified; S6 chain non_green=[]")
NEXT = ("(a) r262 = W9 CROWD-VOTE-P1 harvest face (W7 r256->r257 mirror): prereg "
        "s7/s8 backfill (s5 five predictions vs live: G1 [0,1]/4 hit, variant "
        "maxdd ASYM -25.5% vs SYM -19.2% = prediction-2 asym>=sym MISSED reversed "
        "direction honest, D6 merge <50% hit zero-trigger, turnover <50 budget "
        "hit, extreme-day COVID/2021-top clusters vs maxdd>=0.5x-passive check) "
        "+ zoo #84 tested-and-closed annotation + 48h CEO face clock from "
        "09:38:29 (due 10-02 09:38) + supply floor: W1-W9 nine consecutive "
        "judged-negative = A-layer quota inventory exhausted -> next berth scan "
        "wave (B-layer stock-domain bm-b lane or new family candidates per "
        "STANDBY_POOL_SUPPLY B2-B4); (b) 10-01 month-first trio (science_audit + "
        "monthly_briefing + self_review) + REGIME_GUARD v3 date-gate "
        "auto-activation hands-off; (c) SLOT-7 48h CEO clock due 10-02 07:26 + "
        "SLOT-8 48h due 10-02 09:09 (O-1116 dual-column); (d) supply floor "
        "breach standing: ready=0 after both done-flips -> next supply line = "
        "r262 berth scan obligation.")

report = (
    now + " | r261 bm-c (dept:研究+工程·SLOT-9 runner 建+判决同窗落地+SLOT-8 W8 收割) | "
    "WM-VERDICT: 绿 (red=false lane=healthy; 判决批在窗=满载合法; S6 chain "
    "detached 37 腿全绿 non_green=[]) | CEO 可见面: 当前活=SLOT-9 step-6 全闭环单轮完成"
    "（runner 建→selftest 27/27→verify 逐位→入池→dispatcher 同窗点火→judged 判决 09:38:29）"
    "+SLOT-8 W8 收割面（s7/s8 回填+zoo #89 关单注记+池翻面+48h 钟起算）; 最近实物=results/"
    "innovation_quota/CROWD-VOTE-P1.json（CROWD-VOTE-P1 判决面 0/4 G1+G2 judged-negative "
    "族关单·账本 357,383→359,387）+scripts/innovation_quota_w9.py（runner·r450 守卫+2004 "
    "计数律）+research/INNOVATION_QUOTA_W8_PREREG.md §7/§8（W8 收割回填·paired G1' FAIL "
    "0.3716<1.1952）+commit 29fed9c6c push LANDED; 下个里程碑=r262 W9 收割面（s7/s8 回填+"
    "zoo #84 注记+48h CEO 面 10-02 09:38 到期）+10-01 月首轮三件套+供给地板 ready=0→新泊位"
    "扫描义务（W1-W9 九连判负=A 层配额存货耗尽·B 层/新族候选） | did: " + DID +
    " | verify: " + VERIFY + " | next: " + NEXT)
with io.open(r"logs\iteration-loop\round_reports-bm-c.md", "a",
             encoding="utf-8") as f:
    f.write("\n" + report + "\n")
print("round report line appended")

# state-bm-c.json 260->261
with io.open(r"state-bm-c.json", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 261
st["last_round_at"] = "r261"
st["last_round_ts"] = now
st["updated"] = now
st["did"] = DID
st["verify"] = VERIFY
st["next"] = NEXT
st["current_task"] = ("r261 closed (SLOT-9 runner+verdict same-round + SLOT-8 W8 "
                      "harvest); next = r262 W9 harvest + berth scan (A-layer "
                      "exhausted)")
with io.open(r"state-bm-c.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state flipped 260->261")

# heartbeat (epoch int law)
with io.open(r"fleet\machines\bm-c.json", encoding="utf-8") as f:
    hb = json.load(f)
epoch = int(time.time())
hb["last_seen"] = now
hb["current_task"] = ("r261 closed: SLOT-9 CROWD-VOTE-P1 judged 0/4 family "
                      "closure same-round + SLOT-8 W8 harvest; r262 = W9 "
                      "harvest + berth scan (A-layer exhausted)")
hb["round_no"] = 261
hb["verdict"] = ("alive: r261 closed (W9 verdict landed 09:38:29 + W8 harvest "
                 "complete), r262 = W9 s7/s8 + supply berth scan")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now
hb["health"] = "ok"
hb["updated_at"] = now
with io.open(r"fleet\machines\bm-c.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with io.open(r"fleet\machines\bm-c.json", encoding="utf-8") as f:
    back = json.load(f)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in back["clock_read"], "clock_read not ISO-T"
print("heartbeat written, epoch", epoch, "int self-verified")
