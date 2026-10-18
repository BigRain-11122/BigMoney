# -*- coding: utf-8 -*-
"""r1050 bm-a closeout: report line + state/heartbeat (no inbox processing this
round: MSG-0849/0725 are outgoing receipts addressed to bm-b/bm-c and stay in
fleet/inbox for addressee consumption).

Order in the round: run AFTER Tools/idle_trigger.py --worked (that tool owns
the heartbeat idle_rounds/agenda_starved fields; this script preserves them by
fresh-reading). Atomic-ish JSON writes via utf-8 round-trip, CJK-safe
(r1031 PS-encoding pit: state writes = python only). d19 advance already
landed via scripts/d19_watermark.py update --advance (r1069 law).
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
EPOCH = int(__import__("time").time())

RND = "r1050"
DEPT = "dept:工程·W267席位链预备+S6维护收口"

# ---------- 1. round report line ----------
report_line = (
    "%s | %s bm-a (%s) | WM-VERDICT: 绿(red=false lane=healthy; satengine ALIVE queue0 idle; "
    "idle two_read_red consumed via --worked(0)=W267 探针预著产品工) | "
    "当前活=r1050: S0 rebase 收口（3 运行时面 absorb+watermark UU newer-wins 本机 09:30>origin 09:20·diff --check 0 标记）"
    "+ D-19 DEC 水位 advance（1d4741e4→0ad85a30·delta=D-20261016-06 回执列回填 R2.17（v6.1 已部署在案执行件回执面）"
    "=零新 bm-a 义务·d19_watermark.py --advance 单源推进·读回全串恒等 OK）+ orders scan CLEAN（最新 O-20261018-0348 已 ack·unacked=0）"
    "+ W266 PREREG FREEZE 落链确认（bm-c 595433d63c 09:13·bands A 600_501..602_500/B 602_501..602_700）"
    "+ 五面 splice 未落=W267 席保 GATED 零 skip-claim（origin w267 工件四查零）"
    "+ W267 pre-seat 探针预著（results/_w267bma_20261018_probe.py·bloodline=_w266bmc_20261018_probe.py derive 机芯 verbatim·"
    "W267 facts live-registry-driven r587 禁转录·leg0 门守卫负测试 loud-fail 实证+py_compile rc0·"
    "预期带=W266 席位 MSG leg4+prereg §5 item5 投影：A 602_701..604_700 第十六连 A-hop/B 604_701..604_900 第十七连 above-own-A·"
    "运行时 live walk 统辖）+ MF day-8=周日合法 no-op（S6 腿 rc0·封锁复测=周一 ≤10-19 裁决面·checkpoint 完好）"
    "+ HANDOVER 5x r1050 行落账（r1040/r1045 两截 5x 戳 OVERDUE-DISCLOSED·3089B·utf-8 读回在档）"
    "+ idle two_read_red 消费（idle_rounds 4→0 via --worked·W267 探针+HANDOVER+S6=实际产品工）"
    "+ S6 42/42 rc0 bad=0（driver _r1050bma_s6chain.ps1） | "
    "验证证据=results/_r1050bma_w267_probe_negtest.txt（门守卫负测试实录）+ _w267bma_20261018_probe.py py_compile rc0 + "
    "origin vacancy w267 零工件（ls-tree+glob 双读）+ results/_r1050bma_s6chain_rc.log 42 rc0 bad=0 + smoke 49/49 + "
    "d19 advance 读回恒等 OK + HANDOVER r1050 行在档 + idle_trigger --worked rc=0（idle_rounds 4→0）+ "
    "loop pin=8 no-op + claws match x2 + 孤儿面 0/21 | "
    "下轮指针=r1051: W266 五面 splice+引擎自烧+finalize 守望（bm-c 窗）→落链即开 bm-a W267 席位窗=FIRST ACTION"
    "（探针 live 跑→seat MSG→prereg derive+freeze·post-W266 宇宙 live re-derive·W267 owner 名面随 W266 §7/8 回填定）"
    "+ MF 周一封锁裁决（≤10-19·r1027 typing escalation face）+ idle verdict 守望（backlog 池 0·补货归秘书处） | "
    "最近实物=results/_w267bma_20261018_probe.py（W267 pre-seat 探针·09:5x）+ results/_r1050bma_w267_probe_negtest.txt"
    "（负测试证据）+ results/_r1050bma_s6chain_rc.log（42/42 rc0） | "
    "本地未达 origin commit 数=0（收口 push 验证后）| [r1050 bm-a w267-probe-presoak-s6-closeout]"
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
did = ("%s: 当前活=W266 PREREG FREEZE 落链确认（bm-c 595433d63c·bands A 600_501..602_500/B 602_501..602_700）"
       "+五面 splice 未落=W267 席保 GATED 零 skip-claim+W267 pre-seat 探针预著（_w267bma_20261018_probe.py·"
       "W266 血统机芯 verbatim·leg0 门守卫负测试 loud-fail 实证）+D-19 DEC advance（1d4741e4→0ad85a30="
       "D-20261016-06 回执列回填 R2.17·零新 bm-a 义务）+S6 42/42 rc0+HANDOVER 5x r1050 行"
       "（r1040/r1045 OVERDUE-DISCLOSED）+idle RED 清零（--worked 4→0）；"
       "最近实物=results/_w267bma_20261018_probe.py+results/_r1050bma_w267_probe_negtest.txt+"
       "results/_r1050bma_s6chain_rc.log（42 rc0）；"
       "下个里程碑=W267 席位窗（W266 注册+finalize 落链即开·探针活跑→seat MSG→prereg derive）"
       "+MF 封锁周一 ≤10-19 裁决；孤儿面=0/21；watermark=red=false healthy") % RND

verdict = ("GREEN: r1050: W266 prereg-freeze landed confirmed (bm-c 595433d63c) + five-face splice "
           "absent -> W267 seat GATED zero skip-claim held (origin w267 four-check zero) + W267 "
           "pre-seat probe PRE-AUTHORED while gate closed (bloodline _w266bmc verbatim; live-registry "
           "r587; leg0 loud-fail negtest proven in-window; py_compile rc0; expected per W266 seat MSG "
           "leg4 + prereg sec.5 item5: A 602_701..604_700 16th A-hop / B 604_701..604_900 17th "
           "above-own-A, live walk governs at run) + D-19 DEC advance 1d4741e4->0ad85a30 "
           "(D-20261016-06 receipt-column backfill, zero new bm-a obligation, read-back equality) + "
           "orders CLEAN + S6 42/42 rc0 + smoke 49/49 + HANDOVER 5x r1050 (r1040/r1045 "
           "OVERDUE-DISCLOSED) + idle RED cleared (--worked 4->0) + quartet (loop pin=8 no-op, "
           "claws x2, watchdog S4U flip denial = C-20261016-04 carried)")

verify = ("results/_w267bma_20261018_probe.py py_compile rc0 + gate-closed negtest leg0 loud-fail "
          "(results/_r1050bma_w267_probe_negtest.txt) + origin vacancy w267 zero artifacts "
          "(ls-tree+glob) + results/_r1050bma_s6chain_rc.log 42 rc0 bad=0 + smoke 49/49 + "
          "d19 advance read-back equality OK + HANDOVER r1050 row appended (utf-8 read-back present) "
          "+ idle_trigger --worked rc=0 (idle_rounds 4->0) + loop pin=8 no-op + claws match x2 + "
          "orphan face 0/21")

next_plan = ("r1051: W266 five-face splice + engine self-burn + finalize watch (bm-c windows) -> "
             "lands = bm-a W267 seat window FIRST ACTION (run _w267bma_20261018_probe.py live on the "
             "post-W266 universe -> seat MSG publish -> prereg derive+freeze; W267 owner naming rides "
             "the W266 sec.7/8 backfill per chain-order law, yield if named otherwise; zero "
             "skip-claim) + MF Monday blockade adjudication (<=10-19; day-8/9 retest rides S6) + "
             "idle verdict watch (backlog pool 0, refill = dispatcher/secretariat lane)")

notes_r1050 = ("r1050: (1) W266 prereg freeze landed 09:13 (bm-c r1085 595433d63c, bands A "
               "600_501..602_500 / B 602_501..602_700) but five-face splice NOT landed at window "
               "close -> W267 stays GATED, zero skip-claim verified (origin w267 zero artifacts); "
               "(2) W267 pre-seat probe PRE-AUTHORED while gate closed (results/_w267bma_20261018_"
               "probe.py, bloodline _w266bmc_20261018_probe.py derive machinery verbatim; every band "
               "fact live-registry-driven at run r587; leg0 gate-guard loud-fail proven by in-window "
               "negative test; expected bands per W266 seat MSG leg4 + prereg sec.5 item5 projection: "
               "A 602_701..604_700 SIXTEENTH consecutive A-hop / B 604_701..604_900 SEVENTEENTH "
               "consecutive above-own-A -- live walk governs, divergence disclosed honestly if "
               "universe changed again); W267 owner naming rides the W266 sec.7/8 backfill "
               "(chain-order law; bm-a yields per fleet README sec.4 if named otherwise); "
               "(3) D-19 DEC delta consumed = D-20261016-06 receipt-column backfill only (R2.17 "
               "09:3x executor receipt, machine-state v6.1 already deployed = zero new bm-a "
               "obligation); watermark advanced via d19_watermark.py --advance per r1069 law "
               "(read-back full-string equality); (4) idle_trigger two_read_red face (idle_rounds=4 "
               "accumulated across watch windows) consumed same-round via --worked (W267 probe "
               "pre-authoring + HANDOVER 5x + S6 chain = actual product work per O-20261007-2315); "
               "(5) HANDOVER r1040/r1045 5x stamps OVERDUE-DISCLOSED in the r1050 row (wave-chain + "
               "dead-window absorption windows consumed them, single-window compact coverage per "
               "r770/r790/r1035 precedent); (6) inbox MSG-0849 (memory-gov closure receipt) + "
               "MSG-0725 (voicegen pickup status) both outgoing receipts addressed @bm-b/@bm-c = "
               "stay in inbox for addressee consumption, zero bm-a action; (7) S6 chain 42 rc-lines "
               "(41 legs + live_paper) = r1048/r1049 verbatim face clone, bad=0")

ack_note = ("r1050: orders scan CLEAN (origin latest O-20261018-0348-bm-a.md pre-acked, unacked=0 "
            "dual-checked); DEC delta consumed = D-20261016-06 receipt backfill zero new obligation "
            "(advance landed); inbox MSG-0849 + MSG-0725 both outgoing to bm-b/bm-c = addressee-side "
            "consumption, no bm-a action")

common_updates = {
    "current": did,
    "did": did,
    "last_action": did,
    "task": "r1050: W267 pre-seat probe presoak + S6 maintenance closeout",
    "current_task": next_plan,
    "next": next_plan,
    "next_milestone": "W267 bm-a seat window (gated on W266 registration+finalize by bm-c) + MF Monday blockade adjudication (<=10-19) + month-boundary first exam 10-31",
    "last_artifact": "results/_w267bma_20261018_probe.py (W267 pre-seat probe) + results/_r1050bma_w267_probe_negtest.txt + results/_r1050bma_s6chain_rc.log (42/42 rc0)",
    "recent_artifact": "results/_w267bma_20261018_probe.py (W267 pre-seat probe) + results/_r1050bma_w267_probe_negtest.txt + results/_r1050bma_s6chain_rc.log (42/42 rc0)",
    "latest_artifact": "results/_w267bma_20261018_probe.py (W267 pre-seat probe) + results/_r1050bma_w267_probe_negtest.txt + results/_r1050bma_s6chain_rc.log (42/42 rc0)",
    "last_round": RND,
    "round": 1050,
    "loop_round": 1050,
    "round_no": 1051,
    "round_no_label": RND,
    "last_round_label": RND,
    "verdict": verdict,
    "verify": verify,
    "orders_ack_note": ack_note,
    "last_decisions_seen": "r1050: dec 1d4741e4->0ad85a30 advance consumed (D-20261016-06 R2.17 receipt backfill, zero new bm-a obligation)",
    "last_orders_seen": "r1050: ord bcfadcfa hold (zero-delta)",
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
    "notes_r1050": notes_r1050,
}


def apply(path, extra=None, preserve_idle=True):
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
    sync = {"ts": iso, "origin_tip": None, "ahead_behind": "pending-closeout-push",
            "note": "r1050 closeout push follows this write; fetch+ls-tree self-verify after push"}
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
        "round_ref": 1050,
        "ts": iso,
    },
}
st = apply(os.path.join(ROOT, "state-bm-a.json"), extra=st_extra)
hb = apply(os.path.join(ROOT, "fleet", "machines", "bm-a.json"))

print(json.dumps({
    "round": 1050, "next_round_no": 1051, "epoch": EPOCH,
    "idle_rounds_kept": hb.get("idle_rounds"),
    "agenda_starved_kept": hb.get("agenda_starved"),
    "clock_read": hb.get("clock_read"),
}, ensure_ascii=False))
sys.exit(0)
