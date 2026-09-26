# _r252bmb_close.py -- R252 bm-b round closeout (state/heartbeat/report/CODELY)
import json, time, datetime, io, os

TS = "2026-09-26 13:5x"
EPOCH = int(time.time())

# ---- state.json (bm-b ledger state)
sp = "logs/iteration-loop/state.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 252
st["did"] = ("r252: CEO triple-order same-round execution -- T-79 RETRO-PAPER-2026 full arc "
             "(prereg freeze f70c0054 -> batch 20.3s 17 accounts A6/B4/C7 window 2026-01-05->09-24 "
             "-> LEADERBOARD one-pager to CEO -> CEO_APPROVALS.md append-only ledger + sim-gateway queue, "
             "done commit b9946140) + T-80 claim+start (T-54 full-pool face 121,528 cells verified in place, "
             "battery runner spec = resume point) + T-81 claim+start (per-state raw material landed in retro "
             "ledgers, inputs verified); S6 28 legs all exit 0 (weekend no-ops, cutoff 09-24); smoke 25/25")
st["verdict"] = "GREEN"
st["next"] = ("R253+: T-80 battery runner build (scripts/aggr_fullpool_battery.py per ticket progress_r252, "
              "pool-submit 400 cells) + T-81 profile-card runner (scripts/applicability_profile.py, consume "
              "retro ledgers per-state) + CN-REV-TILT-P1 pool harvest (bm-a autofill in flight) + "
              "09-28 Monday new-bar chain + 10-01 month-boundary trio + REGIME_GUARD v3 date gate")
st["current_task"] = ("r252 closed: CEO triple-order executed same-round; next face = T-80 battery runner "
                      "build + T-81 profile cards (resume specs in tickets progress_r252)")
st["last_round_ts"] = "2026-09-26 13:55"
st["updated_at"] = "2026-09-26 13:55"
st["last_tick"] = "13:55"
with io.open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat bm-b
hp = "fleet/machines/bm-b.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = "2026-09-26 13:55"
hb["round_no"] = 252
hb["current_task"] = ("CEO triple-order executed (T-79 done / T-80+T-81 claimed+started); next=T-80 battery "
                      "runner + T-81 profile cards")
hb["cpu_cores"] = 16
hb["cores"] = 16
hb["free_ram_gb"] = 11.8
hb["idle_ram_gb"] = 11.8
hb["gpu_free_vram_gb"] = 2.2
hb["cpu_util_pct"] = 3.6
hb["verdict"] = "GREEN"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
ack = hb["orders_ack"]
for o in ("O-20260926-1326-bm-a.md", "O-20260926-1332-bm-a.md", "O-20260926-1342-bm-a.md"):
    if o not in ack.split():
        ack = ack + " " + o
hb["orders_ack"] = ack
with io.open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# verify epoch int (R170/R178 law)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat epoch int-verified:", chk["heartbeat_epoch_utc"])
print("orders_ack n =", len(chk["orders_ack"].split()))

# ---- round report line
rp = "logs/iteration-loop/round_reports.md"
line = ("2026-09-26 13:55 | r252 bm-b | dept:交易+组合与资金+总经办+工程 | "
        "WM-VERDICT: py_low_with_work_cands RESOLVED same-round (probe 13:41 py 0.5-1.0% + board: 3 CEO "
        "immediate tickets claimed+executed this round; pool ready 1 = CN-REV-TILT-P1 claimed by bm-a autofill "
        "in flight; red=false) | did: S0 stash-pull-pop FF + S0.5 双扫 3 unacked CEO orders (O-1326/O-1332 "
        "mid-round + O-1342 discovered at S7 double-scan = law working) all executed same-round per O-1730; "
        "T-79 FULL ARC (dept:交易): s0 prereg frozen f70c0054 (17-account family A6/B4/C7, window "
        "2026-01-05->09-24, paper semantics, sort key frozen) -> s1 batch 20.3s R41-exempt (selftest 13/13, "
        "B_MAXDIV canon sha + AGGR top-3 sha gates, ALLOC 7 cells frozen s2 mechanics incl. pinned P5 slot "
        "bm-b lane) -> s2 LEADERBOARD one-pager to CEO (sort: #1 COMPOSITE-CE-02 71%/+4.46%, cum-top "
        "COMPOSITE-CE-01 +5.71%; honest annotation verbatim window-overlap; negatives as-is: ALLOC 5/7 neg) "
        "-> s3 CEO_APPROVALS.md append-only ledger + sim-gateway wiring queue; predictions 5/5 reconciled "
        "prereg s7; ledger +0 (replay face zero claims); T-80 (dept:组合) claim b84f8636 + inputs verified "
        "(T-54 full-pool grid 121,528 cells/22 members in place = the face that cures CE-6 restriction) + "
        "runner spec precise in ticket; T-81 (dept:策略) claim 0b4cd1a1 + inputs verified (per-state raw "
        "material already in retro ledgers daily shadow_regime_states; v3/heat/three-card/decay live); "
        "S6 28 legs all exit 0 (weekend no-ops cutoff 09-24: regime breadth 0.77 ORANGE shadow, clock "
        "ORANGE_COOL idempotent, paper 6 anchors OK, t35 zero-pending PASS, t24 22/22 drift=0, promotion "
        "0/22 legal, aggr/alloc/grid marks no-op, scorecard 6, daily_report 4 faces, build_status "
        "432combos/6traders, token delta=0 L1-only + retro 6135 est); push-collision window resolved (bm-a "
        "r247 window: stash/watchdog race -> discard superseded snapshots, rebase replay clean 7daef6c3) | "
        "evidence: commits b84f8636/f70c0054/b9946140/af322241/0b4cd1a1 + results/retro_paper_2026/ 17 "
        "ledgers + LEADERBOARD.{md,json} + docs/CEO_APPROVALS.md + smoke 25/25 + S6 28 exit-0 legs + "
        "heartbeat epoch int-verified | next: T-80 battery runner build+pool-submit (400 cells), T-81 "
        "applicability_profile.py, CN-REV harvest, 09-28 Monday new-bar chain, 10-01 month trio\n")
with io.open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# ---- CODELY.md two lines (S0.5 execution record + S4 pit)
cp = "CODELY.md"
lines = (
    " - [2026-09-26 13:5x] 执行记录（bm-b r252·CEO 三连令同轮执行）：O-1326 T-79 年内回放纸盘全弧交付"
    "（prereg 冻结 f70c0054→批 20.3s 17 台账→一页榜呈 CEO→CEO_APPROVALS.md 认可台账+模拟盘网关队列；"
    "排序 #1 COMPOSITE-CE-02 月正率 71%/+4.46%、累计榜首 COMPOSITE-CE-01 +5.71%；诚实标注=窗与 OOS 开发窗"
    "重叠非前向新证据；判负照报 ALLOC 5/7 负）；O-1332 T-80 认领+开动（T-54 全池面 121,528 cells 实勘在位、"
    "电池 runner 规格=精确续作点）；O-1342 T-81 认领+开动（逐政体原料已随 retro 台账落盘、输入面全验）。"
    "指针=results/retro_paper_2026/LEADERBOARD.md+三票 progress_r252+commits b9946140/af322241/0b4cd1a1\n"
    " - [2026-09-26 13:4x] 坑律（bm-b r252·S0 stash-vs-watchdog 并发写竞态面·R245 家族新参·E1 自捕）："
    "**stash push→pull→pop 窗内被 autofill watchdog 活写手（~10s tick）掺搅=pop 撞键悄悄失败（2>$null 吞掉"
    "冲突输出、stash entry 静默保留）且树仍脏阻 rebase**；正解=快照族让路三步——①比 tick 新鲜度定新旧面"
    "（工作树 tick vs stash 快照 vs 远端已提交面），②弃被超越面（checkout -- 旧 tick+stash drop，"
    "take-remote-committed 新面），③rebase 重放后让 watchdog 下一 tick 自愈重写；连带=push 被拒先看远端"
    "新 commit 是否携带同文件新面（本轮 bm-a tick commit 已含 cnrev launch-claim=远端面最新）。"
    "指针=R252 S0 实录（autofill_state.json 三面竞态）+commit 7daef6c3\n")
with io.open(cp, "a", encoding="utf-8", newline="\n") as f:
    f.write(lines)
print("closeout written: state 252 + heartbeat + report + CODELY x2")
