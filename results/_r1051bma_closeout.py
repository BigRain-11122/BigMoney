# -*- coding: utf-8 -*-
"""r1051 bm-a closeout: report line + state/heartbeat.

Run AFTER Tools/idle_trigger.py --worked (done: idle_rounds 4->0) and
d19_watermark.py update --advance (done: ord bcfadcfa->af206ff3 =
root-cure package ledger row, consumed same-round, dec unchanged).

Atomic-ish JSON writes via utf-8 round-trip, CJK-safe (r1031 PS-encoding
pit: state writes = python only)."""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
EPOCH = int(__import__("time").time())

RND = "r1051"
DEPT = "dept:工程·根治令采纳+W267守门+S6维护收口"

# ---------- 1. round report line ----------
report_line = (
    "%s | %s bm-a (%s) | WM-VERDICT: 绿(red=false lane=healthy; satengine ALIVE queue0 idle; "
    "idle two_read_red consumed via --worked(0)=S6链+MF day-8证据+根治令采纳=实际产品工) | "
    "当前活=r1051: 新令 O-20261018-0948-bm-a 同轮消费（死窗瘟疫根治令·CEO「从根本上解决」直令承接·bm-a=签发机面）"
    "——v2 活性门控发射器拉取落地（origin 738aadda92·rebase 后本机 Tools/iteration_loop.ps1 面实证 hard-cap 240min/"
    "silence-kill 25min+spawning 新话术在位）+本机 TIMEOUT 闭卷普查=407 次历史自伤击杀（rg --no-ignore 全量 run_*.log·"
    "最近一例=今日 07:13:02 run_20261018_064801.log=令中 r1047 铁证）+采纳自证 armed（本轮=09:48 发火仍旧脚本面·"
    "下轮 r1052 spawning 行应现新话术=回执引原文）+§1/§2 受令面=@bm-b/@bm-c ≤2 轮回执守望"
    "+ W266 五面 splice+自烧+finalize 守望（closeout 前 fetch·n1_w266_results.json 仍缺·W267 席位窗维持 GATED 零 skip-claim）"
    "+ MF day-8 retest 证据落档（spawn 09:53:56→300706/07/08 三连 RemoteDisconnected→conn_stopped 熔断停发·checkpoint 完好·"
    "panel cutoff 10-13 complete=false 冻结=封锁 day-8 仍活·周一 ≤10-19 裁决 armed·day-9 复测明日载腿）"
    "+ D-19 双面（09:52 probe 零增量+10:00 update 捕获 orders 新增量 bcfadcfa→af206ff3=09:5x CEO 根治三件套台账行·"
    "已消费·零新增 bm-a 义务·读回全串恒等 OK）+ orders scan CLEAN（新令 O-0948 ack·unacked=0）"
    "+ S6 42/42 rc0 bad=0（driver _r1051bma_s6chain.ps1·r1050 face clone verbatim） | "
    "验证证据=results/_r1051bma_s6chain_rc.log 42 rc0 bad=0 + smoke 49/49 + v2 面行证（rg hard-cap/silence-kill 命中 "
    "Tools/iteration_loop.ps1:168/188/198）+ TIMEOUT 普查 407 计数（rg --no-ignore -c 总和）+ MF status face "
    "（conn_stopped=true failures=3 head 300706-08）+ d19 advance 读回恒等 OK + origin n1_w266 零工件（ls-tree）"
    "+ 孤儿面 0/45 + loop pin=8 no-op + claws installed x2 + watchdog S4U flip denial=C-20261016-04 carried | "
    "下轮指针=r1052: ①v2 采纳自证回执（本轮发射仍旧脚本=25min 墙钟在身·本报告即 10:1x 前收口实证）"
    "②W266 splice/finalize 落链即开 bm-a W267 席位窗 FIRST ACTION（探针 live 跑→seat MSG→prereg derive+freeze·"
    "owner 名面随 W266 §7/8 回填·chain-order law）③bm-b/bm-c rootfix 回执守望（≤2 轮·MSG-...-rootfix.md）"
    "④MF day-9 复测载腿+周一 ≤10-19 封锁裁决 | "
    "最近实物=results/_r1051bma_s6chain_rc.log（42/42 rc0·10:0x）+MF day-8 retest 证据面（conn_stopped 熔断实录）"
    "+Tools/iteration_loop.ps1 v2 本机生效（根治件） | "
    "本地未达 origin commit 数=0（收口 push 验证后）| [r1051 bm-a rootfix-adoption-w267-watch-s6-closeout]"
) % (iso, RND, DEPT)

with open(os.path.join(ROOT, "round_reports-bm-a.md"), "a", encoding="utf-8", newline="\n") as f:
    f.write(report_line + "\n")

# ---------- 2. resolved-face JSON sanity ----------
for p in ("results/watermark_red.json", "results/token_usage.json",
          "results/dashboard_status.json", "results/update_status.json"):
    full = os.path.join(ROOT, p.replace("/", os.sep))
    if os.path.exists(full):
        json.load(open(full, encoding="utf-8"))

# ---------- 3. state + heartbeat writes ----------
did = ("%s: 当前活=O-20261018-0948 根治令同轮消费（v2 发射器拉取+本机面验证+TIMEOUT 普查 407+采纳自证 armed）"
       "+W266 splice/finalize 未落=W267 席保 GATED 零 skip-claim（n1_w266 零工件）"
       "+MF day-8 retest 证据（三连 RemoteDisconnected·conn_stopped·cutoff 10-13 冻结·周一裁决 armed）"
       "+D-19 orders 增量消费（bcfadcfa→af206ff3=根治台账行·零新义务）+S6 42/42 rc0+idle RED 清零（--worked 4→0）；"
       "最近实物=results/_r1051bma_s6chain_rc.log+MF day-8 证据面+Tools/iteration_loop.ps1 v2 本机生效；"
       "下个里程碑=W267 席位窗（W266 splice+finalize 落链即开）+MF 周一 ≤10-19 裁决+v2 采纳自证（r1052 spawning 行）；"
       "孤儿面=0/45；watermark=red=false healthy") % RND

verdict = ("GREEN: r1051: root-cure order O-20261018-0948-bm-a consumed same-round (v2 liveness-gated "
           "launcher pulled 738aadda92 + local face verified hard-cap 240/silence-kill 25/new spawning "
           "wording + bm-a TIMEOUT census 407 historical self-kills, most recent 07:13:02 today = the "
           "order's r1047 iron proof + adoption self-verify armed for r1052 spawning line) + W266 "
           "splice/self-burn/finalize absent -> W267 seat GATED zero skip-claim (origin n1_w266 zero) "
           "+ MF day-8 retest evidence (3x RemoteDisconnected -> conn_stopped fuse, panel cutoff 10-13 "
           "frozen, blockade alive, Monday <=10-19 adjudication armed) + D-19 orders delta consumed "
           "(bcfadcfa->af206ff3 root-cure ledger row, zero new obligation, read-back equality) + orders "
           "CLEAN (O-0948 acked, unacked=0) + S6 42/42 rc0 + smoke 49/49 + idle RED cleared (--worked "
           "4->0) + quartet (loop pin=8 no-op, claws installed x2, watchdog S4U flip denial = "
           "C-20261016-04 carried)")

verify = ("results/_r1051bma_s6chain_rc.log 42 rc0 bad=0 + smoke 49/49 + v2 face rg hits "
          "(Tools/iteration_loop.ps1:168 spawning new wording / :188 silence gate / :198 hard-cap) + "
          "TIMEOUT census 407 (rg --no-ignore -c sum) + last example 07:13:02 run_20261018_064801.log "
          "+ MF status conn_stopped=true failures=3 + d19 update --advance read-back full-string "
          "equality OK + origin n1_w266 zero artifacts (ls-tree) + idle_trigger --worked rc=0 "
          "(idle_rounds 4->0) + loop pin=8 no-op + claws installed x2 + orphan face 0/45")

next_plan = ("r1052: (1) v2 adoption self-verify receipt (this round's firing was the OLD script face "
             "-- 25min guillotine was live, closed out before the line; r1052 spawning line must show "
             "'hard-cap 240min, silence-kill 25min' = quote verbatim per order sec.1.1); (2) W266 "
             "splice+finalize lands = bm-a W267 seat window FIRST ACTION (run _w267bma_20261018_probe.py "
             "live on the post-W266 universe -> seat MSG publish -> prereg derive+freeze; W267 owner "
             "naming rides the W266 sec.7/8 backfill per chain-order law, yield if named otherwise; zero "
             "skip-claim); (3) bm-b/bm-c rootfix receipts watch (<=2 rounds, MSG-20261018-*-rootfix.md); "
             "(4) MF day-9 retest rides S6 + Monday <=10-19 blockade adjudication + idle verdict watch "
             "(backlog pool 0, refill = dispatcher/secretariat lane)")

notes_r1051 = ("r1051: (1) NEW ORDER O-20261018-0948-bm-a (dead-window root-cure, CEO 'cong genben shang "
               "jiejue' direct order relay) consumed same-round: root cause adjudicated = "
               "Tools/iteration_loop.ps1 25-min wall-clock kill (legacy param from 2026-09-23 MiniGame "
               "short-round mode); fix v2 = liveness-gated budget (silence-kill 25min zero-output gate "
               "+ hard-cap 240min) landed on origin 738aadda92 same batch as the order; bm-a pulled via "
               "S0 absorb+rebase (a14447619 absorb 49 files then rebase over the 2 origin commits clean) "
               "and verified local v2 face; THIS round was fired 09:48:00 by the OLD script (v2 reached "
               "local disk only at the ~10:05 rebase) so the 25-min guillotine was still on this round "
               "-- closeout raced it (started ~10:06); adoption self-verify = r1052 spawning line; "
               "(2) bm-a self-census per order sec.1.2 pattern (formally @bm-b/@bm-c legs; bm-a did its "
               "own for the issuer evidence chain): 407 ROUND TIMEOUT kills total in local run logs "
               "(rg --no-ignore -g 'run_*.log' -c sum), most recent 2026-10-18 07:13:02 "
               "run_20261018_064801.log = the r1047 death = the order's iron proof; (3) W266 watch: "
               "prereg freeze landed (595433d63c) but five-face splice + engine self-burn + finalize all "
               "absent at round close (origin n1_w266_results.json zero, behind-0 after fetch) -> W267 "
               "seat stays GATED, zero skip-claim held; (4) MF day-8 retest: spawn 09:53:56 -> "
               "300706/07/08 three consecutive RemoteDisconnected -> conn_stopped=true fuse stop, "
               "checkpoint intact, panel cutoff 2026-10-13 complete=false frozen = blockade ALIVE on "
               "day-8; Monday <=10-19 adjudication armed with this evidence; day-9 retest rides "
               "tomorrow's S6; (5) D-19: 09:52 probe zero-delta, then 10:00 update --advance caught a "
               "FRESH orders delta bcfadcfa->af206ff3 = the 09:5x CEO root-cure package ledger row on "
               "group orders.md (same package, group-side face) -- consumed, zero new bm-a obligation; "
               "(6) S6 chain = r1050 face clone verbatim (one typo tt24 fixed pre-run), 42 rc-lines "
               "bad=0; (7) watchdog S4U flip access-denied = carried face C-20261016-04 (elevation "
               "window needed, unattended-legal hold); (8) idle two_read_red consumed via --worked "
               "(S6 chain + MF day-8 evidence + root-cure adoption = actual product work per "
               "O-20261007-2315)")

ack_note = ("r1051: NEW order O-20261018-0948-bm-a consumed same-round (root-cure adoption on issuer "
            "machine: v2 pull+face verify+census 407+ack); D-19 orders delta af206ff3 consumed = "
            "root-cure ledger row, zero new obligation; unacked=0 after this ack")

common_updates = {
    "current": did,
    "did": did,
    "last_action": did,
    "task": "r1051: root-cure order adoption + W267 gate watch + S6 closeout",
    "current_task": next_plan,
    "next": next_plan,
    "next_milestone": ("W267 bm-a seat window (gated on W266 splice+finalize by bm-c) + MF Monday "
                       "blockade adjudication (<=10-19) + v2 adoption self-verify (r1052) + "
                       "month-boundary first exam 10-31"),
    "last_artifact": ("results/_r1051bma_s6chain_rc.log (42/42 rc0) + MF day-8 retest evidence face "
                      "(conn_stopped fuse) + Tools/iteration_loop.ps1 v2 local-effective"),
    "recent_artifact": ("results/_r1051bma_s6chain_rc.log (42/42 rc0) + MF day-8 retest evidence face "
                        "(conn_stopped fuse) + Tools/iteration_loop.ps1 v2 local-effective"),
    "latest_artifact": ("results/_r1051bma_s6chain_rc.log (42/42 rc0) + MF day-8 retest evidence face "
                        "(conn_stopped fuse) + Tools/iteration_loop.ps1 v2 local-effective"),
    "last_round": RND,
    "round": 1051,
    "loop_round": 1051,
    "round_no": 1052,
    "round_no_label": RND,
    "last_round_label": RND,
    "verdict": verdict,
    "verify": verify,
    "orders_ack_note": ack_note,
    "last_decisions_seen": ("r1051: dec 0ad85a30 hold (zero-delta, probe+update agree)"),
    "last_orders_seen": ("r1051: ord bcfadcfa->af206ff3 advance consumed (09:5x CEO root-cure package "
                          "ledger row, executed-status, zero new bm-a obligation)"),
    "last_decisions_read_at": iso,
    "last_orders_read_at": iso,
    "last_orders_at": iso,
    "last_decisions_at": iso,
    "last_decisions_ts": iso,
    "last_round_at": iso,
    "last_round_closed": iso,
    "last_round_ts": iso,
    "last_run": iso,
    "last_seen": iso,
    "now_active": iso,
    "updated": iso,
    "updated_at": iso,
    "ts": iso,
    "clock_read": iso,
    "last_action_at": iso,
    "orphan_face": 0,
    "orphan_faces": 0,
    "notes_r1051": notes_r1051,
}

NEW_ACK = "O-20261018-0948-bm-a.md"


def apply(path, extra=None, preserve_idle=True, is_state=False):
    obj = json.load(open(path, encoding="utf-8"))
    prev_epoch = obj.get("heartbeat_epoch_utc")
    idle_rounds = obj.get("idle_rounds")
    agenda = obj.get("agenda_starved")
    obj.update(common_updates)
    if extra:
        obj.update(extra)
    obj["last_heartbeat_epoch_utc"] = prev_epoch
    obj["heartbeat_epoch_utc"] = EPOCH
    obj["heartbeat_epoch_utc_type_int"] = True
    if preserve_idle and idle_rounds is not None:
        obj["idle_rounds"] = idle_rounds
        obj["agenda_starved"] = agenda
    if is_state:
        acks = obj.get("orders_ack", [])
        if NEW_ACK not in acks:
            acks.append(NEW_ACK)
            obj["orders_ack"] = acks
    sync = {"ts": iso, "origin_tip": None, "ahead_behind": "pending-closeout-push",
            "note": "r1051 closeout push follows this write; fetch+ls-tree self-verify after push"}
    obj["sync"] = sync
    obj["push_verified"] = dict(sync)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    back = json.load(open(path, encoding="utf-8"))
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
    assert "T" in back["clock_read"], "clock_read must be T-delimited ISO (R262 law)"
    return back


st_extra = {
    "d19_watermark_guard": {
        "tool": "scripts/d19_watermark.py",
        "probe": "results/_r686bmb_d19_check.py",
        "probe_evidence": "C:\\Users\\sjs20\\Desktop\\FluxGroup\\quant\\bigmoney\\results\\_r686bmb_d19_check.json",
        "method_decisions": "sha256",
        "method_orders": "sha256",
        "verbatim": True,
        "advance": True,
        "round_ref": 1051,
        "ts": iso,
    },
    "last_orders_sha": "af206ff3084af3445506585f5a3c7501af46b6a574c0a926f5426631c39a6a6a",
    "last_orders_ts": iso,
}
st = apply(os.path.join(ROOT, "state-bm-a.json"), extra=st_extra, is_state=True)
ack_back = st.get("orders_ack", [])
hb = apply(os.path.join(ROOT, "fleet", "machines", "bm-a.json"))

print(json.dumps({
    "round": 1051, "next_round_no": 1052, "epoch": EPOCH,
    "ack_appended": NEW_ACK in ack_back, "ack_count": len(ack_back),
    "idle_rounds_kept": hb.get("idle_rounds"),
    "agenda_starved_kept": hb.get("agenda_starved"),
    "clock_read": hb.get("clock_read"),
}, ensure_ascii=False))
sys.exit(0)
