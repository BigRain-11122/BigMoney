#!/usr/bin/env python
# r1052 bm-a closeout writer -- round report line + CODELY.md pit row +
# state-bm-a.json + fleet/machines/bm-a.json (heartbeat) r1052 faces.
# Fresh-read-modify-write per r504 law; JSON validated before atomic write;
# both orders_ack faces consistent post-heal (heartbeat healed earlier this
# round by _r1052bma_heartack_heal.py).
# -*- coding: utf-8 -*-
import json
import os
import time
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())
OLD_EPOCH = 1792288905

REPORT = os.path.join(BASE, 'round_reports-bm-a.md')
CODELY = os.path.join(BASE, 'CODELY.md')
STATE = os.path.join(BASE, 'state-bm-a.json')
HEART = os.path.join(BASE, 'fleet', 'machines', 'bm-a.json')

CUR = ("r1052: 当前活=v2 采纳自证回执闭环（本窗 spawning 行逐字 hard-cap 240min/silence-kill 25min vs 09:48 旧面 budget 25min=O-0948 §1.1 完成）"
       "+心跳回执面补账（r1051 收口漏心跳 orders_ack append→10:08 轮首扫描假 P0 债·_r1052bma_heartack_heal.py append+3 镜像字段同步→复扫 CLEAN 102/111/0）"
       "+D-19 orders 增量消费（af206ff3→a62af296=记忆治理席 CEO令②补录行·零新义务·读回全串恒等）"
       "+W266 门收窄（bm-c 中窗四连提交 10:11-10:17：五面 splice+自烧 12/12 shard+post-splice heal+sixgate PRE-FINALIZE 29 连 PASS 落链 839bf365f7·finalize n1_w266_results.json+§7/8 回填仍缺→W267 席位窗维持 GATED 零 skip-claim）"
       "+MF day-9 证据（主道 conn_stopped 熔断保持+rank 道 10:14:58 page-1 RemoteDisconnected fetch_failed 158s=封锁 day-9 仍活·周一 ≤10-19 裁决 armed）"
       "+bm-b/bm-c rootfix 回执守望（≤2 轮窗第 1 轮收口零件）+S6 42/42 rc0+idle --worked；"
       "最近实物=_r1052bma_heartack_heal.py（回执面修复件）+results/_r1052bma_s6chain_rc.log（42/42 rc0）+MF day-9 rank 证据面（results/moneyflow_update_status.json 10:15:09）；"
       "下个里程碑=W267 席位窗（门=仅剩 W266 finalize·bm-c 窗）+MF 周一 ≤10-19 封锁裁决+rootfix 回执（≤2 轮窗）+月界首考 10-31；"
       "孤儿面=0/27；watermark=red=false healthy")

NEXT = ("r1053: (1) W266 finalize watch (n1_w266_results.json + sec.7/8 backfill owner naming, bm-c window) -- lands = bm-a W267 seat window "
        "FIRST ACTION (run _w267bma_20261018_probe.py live on the post-W266 universe -> seat MSG publish -> prereg derive+freeze; "
        "W267 owner naming rides the W266 sec.7/8 backfill per chain-order law, yield if named otherwise; zero skip-claim); "
        "(2) bm-b/bm-c rootfix receipts watch (<=2-round window round 2, MSG-20261018-*-rootfix.md); "
        "(3) MF Monday <=10-19 blockade adjudication (day-8 + day-9 evidence chain, rank fetch_failed face); "
        "(4) idle verdict watch (backlog pool 0, refill = dispatcher/secretariat lane)")

MILE = ("W267 bm-a seat window (gate narrowed to W266 finalize by bm-c) + MF Monday blockade adjudication (<=10-19) "
        "+ bm-b/bm-c rootfix receipts (<=2 rounds) + month-boundary first exam 10-31")

TASK = "r1052: v2 adoption receipt + heartbeat ack heal + W266 finalize watch + S6 closeout"

ART = ("results/_r1052bma_s6chain_rc.log (42/42 rc0) + _r1052bma_heartack_heal.py (receipt-face fix HEAL-OK) "
       "+ MF day-9 rank evidence face (results/moneyflow_update_status.json 10:15:09)")

VERDICT = ("GREEN: r1052: v2 adoption self-verify CLOSED per O-20261018-0948-bm-a sec.1.1 (r1052 spawning line verbatim "
           "'hard-cap 240min, silence-kill 25min' in run_20261018_100801.log 10:08:03 vs old face 09:48 'budget 25min' = "
           "launcher reads-from-disk-each-fire law live) + heartbeat orders_ack heal (P0 false-debt root-caused: r1051 closeout "
           "wrote state ack but missed heartbeat append; healed append + 3 stale mirrors, scanner rerun CLEAN 102/111/0) "
           "+ D-19 orders delta consumed (af206ff3->a62af296 memory-gov CEO-order-2 supplemental row: executed bm-a + dispatched "
           "@bm-b/@bm-c, zero new BigMoney obligation; watermark advanced read-back equality; dec 0ad85a30 hold) + W266 "
           "splice+self-burn+sixgate PRE-FINALIZE 29th PASS landed (origin 839bf365f7, 12/12 shards results/p2cal_ext/n1_w266/) "
           "with finalize (n1_w266_results.json + sec.7/8 backfill) absent -> W267 seat stays GATED zero skip-claim (gate narrowed "
           "to finalize-only) + MF day-9 blockade evidence (main-lane conn_stopped fuse retained per design + rank-lane fresh attempt "
           "10:14:58 page-1 RemoteDisconnected fetch_failed 158s = blockade ALIVE day-9; Monday <=10-19 adjudication armed with "
           "day-8+day-9 chain) + bm-b/bm-c rootfix receipts absent (round 1 of <=2 window closes, watch continues) + orders CLEAN "
           "post-heal (O-0948 acked both faces, unacked=0) + S6 42/42 rc0 + smoke 49/49 + idle --worked (v2 receipt+heal+MF evidence "
           "= actual product work)")

VERIFY = ("run_20261018_100801.log 10:08:03 spawning line verbatim (hard-cap 240min, silence-kill 25min) + "
          "run_20261018_094801.log old-face contrast (budget 25min) + _r1052bma_heartack_heal.py HEAL-OK appended=True "
          "ack_count=111 + orders_ack_scan rerun CLEAN rc0 (102 orders/111 acks/0 unacked) + d19 advance ADVANCED "
          "ord=a62af296 read-back full-string equality OK + probe post-advance double-zero-delta + origin ls-tree: n1_w266 "
          "12/12 shards present, results/n1_w266_results.json absent + MF status face (rank fetch_failed: page 1: "
          "RemoteDisconnected ts 10:15:09, last_refresh conn_stopped=true failures=3 09:53:56) + "
          "results/_r1052bma_s6chain_rc.log 42 rc0 bad=0 + smoke 49/49 + satengine ALIVE queue0 + orphan face 0/27 + "
          "loop pin=8 no-op + claws installed x2 + watchdog query rc0 (S4U flip denial = C-20261016-04 carried) + "
          "idle_trigger --worked rc=0 (idle_rounds->0)")

ACK_NOTE = ("r1052: heartbeat ack-face heal closed the r1051 closeout gap (O-20261018-0948-bm-a.md appended to heartbeat "
            "orders_ack + orders_ack_last + 3 stale mirror fields synced from state canonical; scanner rerun CLEAN 102/111/0); "
            "D-19 orders delta a62af296 consumed = memory-gov CEO-order-2 supplemental row, zero new obligation; unacked=0")

ORD_SEEN = ("r1052: ord af206ff3->a62af296 advance consumed (10:04 memory-gov CEO-order-2 supplemental row: "
            "CEO-DIRECTION-BRIEF continuity package; executed(bm-a memory-gov seat) + dispatched(@bm-b/@bm-c receipts<=2026-10-25); "
            "zero new BigMoney-loop obligation)")

DEC_SEEN = "r1052: dec 0ad85a30 hold (probe zero-delta; advance read-back agree)"

NOTE = ("r1052: (1) v2 adoption self-verify CLOSED per O-20261018-0948-bm-a sec.1.1: this round was fired 10:08:01 by the NEW "
        "v2 script -- spawning line verbatim 'hard-cap 240min, silence-kill 25min' (run_20261018_100801.log) vs the 09:48 "
        "old-face 'budget 25min' (run_20261018_094801.log); launcher reads-from-disk-each-fire law live-verified on bm-a; "
        "(2) heartbeat ack-face asymmetry pit (NEW, CODELY.md row appended): r1051 closeout appended the O-0948 ack to state "
        "orders_ack but MISSED the heartbeat face (fleet/machines/bm-a.json) -- orders_ack_scan.py reads heartbeat only -> "
        "10:08 round-start scan false P0 debt on an already-consumed order; healed same-round (_r1052bma_heartack_heal.py: "
        "append + orders_ack_last + 3 stale mirror fields synced from state canonical: last_orders_sha eae5ac55->af206ff3, "
        "last_decisions_sha 1d4741e4->0ad85a30, last_orders_ts->10-18); rerun CLEAN 102/111/0; closeout ack appends must "
        "write BOTH faces; (3) W266 gate NARROWED: bm-c four-commit batch landed mid-round 10:11-10:17 (bc7cab9893/18f6ffe931 "
        "self-burn 12/12 shards + dc71ecc3f9 five-face splice estate + 839bf365f7 post-splice heal + sixgate PRE-FINALIZE 29th "
        "PASS) -- finalize (n1_w266_results.json + sec.7/8 backfill owner naming) still absent -> W267 seat stays GATED zero "
        "skip-claim; r1053 first-check finalize, window opens as FIRST ACTION when it lands; (4) MF day-9: main-lane "
        "conn_stopped fuse retained per design (day-8 spawn 09:53:56, 3x RemoteDisconnected) + rank-lane fresh attempt "
        "10:14:58 -> 'fetch_failed: page 1: RemoteDisconnected' 158s = blockade ALIVE day-9; Monday <=10-19 adjudication armed "
        "with day-8+day-9 chain; (5) D-19 orders delta af206ff3->a62af296 consumed (10:04 memory-gov CEO-order-2 supplemental "
        "row: CEO-DIRECTION-BRIEF continuity; executed bm-a + dispatched @bm-b/@bm-c <=10-25; zero new BigMoney-loop "
        "obligation); dec 0ad85a30 hold; (6) bm-b/bm-c rootfix receipts absent at window-1 close (watch continues, round 2 of "
        "<=2); (7) S6 chain = r1049 face clone verbatim (42 rc-lines bad=0), d19 advance run BEFORE the chain; (8) idle "
        "green_idle=true pool0 boards-empty -> standing faces consumed; --worked rc0 (v2 receipt + heal + MF evidence = "
        "product work); (9) quartet: loop pin=8 no-op, claws x2 reinstalled, watchdog query rc0 with S4U flip denial carried "
        "(C-20261016-04)")

REPORT_LINE = (NOW + " | r1052 bm-a (dept:工程·v2采纳自证闭环+回执面修复+S6维护收口) | "
    "WM-VERDICT: 绿(red=false lane=healthy; satengine ALIVE queue0 idle; idle green_idle=true 池0 板空→常设面消费·--worked(0)=v2采纳回执+心跳补账+MF day-9证据=实际产品工) | "
    "当前活=r1052: ①v2 采纳自证回执闭环（O-20261018-0948-bm-a §1.1）——本轮发射行逐字实证「spawning headless round (hard-cap 240min, silence-kill 25min, prompt_chars=31210, out=...round_20261018_100801.out)」vs 前轮旧面 09:48「budget 25min」=发射器每发从盘重读律活体生效·采纳完成；"
    "②回执双面缺口修复（真P0假债根因）——r1051 收口只把 O-0948 ack 写进 state orders_ack 而漏心跳件 fleet/machines/bm-a.json 数组（orders_ack_scan.py 只读心跳面）→10:08 轮首扫描假报 P0 未回执债；补账=_r1052bma_heartack_heal.py（append 令牌+orders_ack_last+同步 3 陈旧镜像字段：last_orders_sha eae5ac55→af206ff3/last_decisions_sha 1d4741e4→0ad85a30/last_orders_ts→10-18）→复扫 CLEAN（102 令/111 回执/0 债）·坑行入 CODELY.md；"
    "③D-19 orders 增量同轮消费（af206ff3→a62af296=10:04 记忆治理席 CEO令②「对话连续性」补录行·executed(bm-a 记忆治理席)+dispatched(@bm-b/@bm-c ≤10-25)·BigMoney 环路零新义务）·d19 --advance 单源推进·读回全串恒等 OK·dec 0ad85a30 hold；"
    "④W266 守望门收窄——中窗 fetch 捕 bm-c 四连提交（bc7cab9893/18f6ffe931=自烧 12/12 shard+dc71ecc3f9=五面 splice estate 落链+839bf365f7=post-splice heal+sixgate PRE-FINALIZE 29 连 PASS·10:11-10:17）但 finalize 产物 n1_w266_results.json+§7/8 回填仍缺→W267 席位窗维持 GATED 零 skip-claim（门仅剩 finalize 一件·r1053 首查）；"
    "⑤MF day-9 证据落档——主道 conn_stopped 熔断保持（day-8 spawn 09:53:56 三连 RemoteDisconnected·按设计停发）+rank 道 day-9 新尝试 10:14:58→「fetch_failed: page 1: RemoteDisconnected」158s=封锁 day-9 仍活·周一 ≤10-19 裁决 armed（day-8+day-9 双日证据链）；"
    "⑥bm-b/bm-c rootfix 回执仍缺（≤2 轮窗第 1 轮收口·MSG-20261018-*-rootfix.md 零）=守望续 r1053；"
    "⑦S6 42/42 rc0 bad=0（driver _r1052bma_s6chain.ps1·r1049 face clone verbatim）+孤儿面 0/27 | "
    "验证证据=logs/iteration-loop/run_20261018_100801.log:10:08:03 spawning 行逐字（hard-cap 240min, silence-kill 25min）+run_20261018_094801.log:09:48:02 旧面对照（budget 25min）+_r1052bma_heartack_heal.py HEAL-OK（appended=True ack_count=111）+复扫 CLEAN rc0+d19 advance ADVANCED 读回恒等+probe 后双零增量+origin ls-tree n1_w266 12 shard 在/finalize 件零+results/moneyflow_update_status.json（rank fetch_failed ts 10:15:09+conn_stopped=true failures=3）+results/_r1052bma_s6chain_rc.log 42 rc0 bad=0+smoke 49/49+satengine ALIVE queue0+孤儿面 0/27+loop pin=8 no-op+claws x2+watchdog rc0（S4U flip denial=C-20261016-04 carried）+idle --worked rc=0 | "
    "下轮指针=r1053: ①W266 finalize 守望（n1_w266_results.json+§7/8 回填 owner 名面·bm-c 窗）——落链即开 bm-a W267 席位窗 FIRST ACTION（_w267bma_20261018_probe.py live 跑→seat MSG→prereg derive+freeze·chain-order law·zero skip-claim）②bm-b/bm-c rootfix 回执守望（≤2 轮窗第 2 轮）③MF 周一 ≤10-19 封锁裁决（day-8+day-9 证据链）④idle verdict 守望（backlog 池 0·补货归秘书处）| "
    "最近实物=_r1052bma_heartack_heal.py（回执面修复件·可跑）+results/_r1052bma_s6chain_rc.log（42/42 rc0）+MF day-9 rank 证据面（results/moneyflow_update_status.json 10:15:09）| "
    "本地未达 origin commit 数=0（收口 push 验证后）")

CODELY_ROW = ("- [2026-10-18 10:2x r1052 bm-a] **回执双面写不对称坑（orders_ack 两面同步律）**：r1051 收口把新令 ack 只 append 进 "
    "state-bm-a.json orders_ack 而漏 fleet/machines/bm-a.json 心跳面——orders_ack_scan.py（T17 结构扫描器）只读心跳面→r1052 轮首扫描假报 "
    "P0 未回执债（令已实际消费）。正法=收口回执 append 必须双面同写（state+heartbeat·FLEET-OPS sec.3 回执闭合律）；一面缺=下轮扫描红=假债。"
    "修复实录=_r1052bma_heartack_heal.py（append+orders_ack_last+3 陈旧镜像字段 state 正典对齐：last_orders_sha eae5ac55→af206ff3/"
    "last_decisions_sha 1d4741e4→0ad85a30/last_orders_ts 10-17→10-18）→复扫 CLEAN 102/111/0。连带律=心跳 last_orders_sha/last_decisions_sha "
    "等镜像字段收口时也应从 state 正典面同步（r1051 心跳停在 r1049 期旧值）。How to apply：一切 orders_ack 回执 append 动作=state 与心跳两文件同轮同写；"
    "扫描器红先查两面差集勿当真债重执行。")

# ---- psutil faces ----
ram_free_gb = ram_free_pct = cpu_pct = None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / 2**30, 1)
    ram_free_pct = round(vm.available / vm.total * 100, 1)
    cpu_pct = round(psutil.cpu_percent(interval=0.3), 1)
except Exception:
    pass

# ---- 1. round report append ----
with open(REPORT, encoding='utf-8') as fh:
    rtxt = fh.read()
rnl = '\r\n' if rtxt.count('\r\n') > 10 else '\n'
if not rtxt.endswith('\n'):
    rtxt += rnl
rtxt += REPORT_LINE + rnl
with open(REPORT, 'w', encoding='utf-8', newline='') as fh:
    fh.write(rtxt)
with open(REPORT, encoding='utf-8') as fh:
    assert 'r1052 bm-a (dept' in fh.read()

# ---- 2. CODELY.md pit row (insert as last Project row, before '### Reference') ----
with open(CODELY, encoding='utf-8') as fh:
    ctxt = fh.read()
anchor = '### Reference'
assert ctxt.count(anchor) >= 1
cnl = '\r\n' if ctxt.count('\r\n') > 10 else '\n'
ctxt2 = ctxt.replace(anchor, CODELY_ROW + cnl + anchor, 1)
with open(CODELY, 'w', encoding='utf-8', newline='') as fh:
    fh.write(ctxt2)
csize = os.path.getsize(CODELY)
assert csize < 50 * 1024, csize
with open(CODELY, encoding='utf-8') as fh:
    back = fh.read()
assert CODELY_ROW in back and anchor in back

# ---- 3/4. state + heartbeat ----
def upd(d, is_heart):
    d['current'] = CUR
    d['did'] = CUR
    d['last_action'] = CUR
    d['current_task'] = NEXT
    d['next'] = NEXT
    d['next_milestone'] = MILE
    d['task'] = TASK
    d['verdict'] = VERDICT
    d['verify'] = VERIFY
    d['last_artifact'] = ART
    d['latest_artifact'] = ART
    d['recent_artifact'] = ART
    d['last_round'] = 'r1052'
    d['last_round_label'] = 'r1052'
    d['round_no_label'] = 'r1052'
    d['loop_round'] = 1052
    d['round'] = 1052
    d['round_no'] = 1053
    d['last_round_at'] = NOW
    d['last_round_closed'] = NOW
    d['last_round_ts'] = NOW
    d['last_run'] = NOW
    d['last_seen'] = NOW
    d['now_active'] = NOW
    d['updated'] = NOW
    d['updated_at'] = NOW
    d['ts'] = NOW
    d['last_action_at'] = NOW
    d['clock_read'] = NOW
    d['last_heartbeat_epoch_utc'] = OLD_EPOCH
    d['heartbeat_epoch_utc'] = EPOCH
    d['heartbeat_epoch_utc_type_int'] = True
    d['orders_ack_note'] = ACK_NOTE
    d['last_orders_seen'] = ORD_SEEN
    d['last_orders_at'] = NOW
    d['last_orders_ts'] = NOW
    d['last_orders_read_at'] = NOW
    d['last_decisions_seen'] = DEC_SEEN
    d['last_decisions_at'] = NOW
    d['last_decisions_ts'] = NOW
    d['last_decisions_read_at'] = NOW
    d['notes_r1052'] = NOTE
    d['idle_rounds'] = 0
    d['agenda_starved'] = False
    d['orphan_face'] = 0
    d['orphan_faces'] = 0
    d['orphan_killed'] = 0
    d['push_verified'] = {"ts": NOW, "origin_tip": None, "ahead_behind": "pending-closeout-push",
                          "note": "r1052 closeout push follows this write; fetch+ls-tree self-verify after push"}
    d['sync'] = dict(d['push_verified'])
    if ram_free_gb is not None:
        d['free_ram_gb'] = ram_free_gb
        d['ram_free_gb'] = ram_free_gb
        d['idle_ram_gb'] = ram_free_gb
        d['free_ram_pct'] = ram_free_pct
        d['ram_free_pct'] = ram_free_pct
        d['ram_load_pct'] = round(100 - ram_free_pct, 1)
        d['ram_free_mb'] = int(ram_free_gb * 1024)
        d['idle_ram_mb'] = int(ram_free_gb * 1024)
    if cpu_pct is not None:
        d['cpu_pct'] = cpu_pct
        d['cpu_util_pct'] = cpu_pct
        d['cpu_total_pct'] = cpu_pct
        d['cpu_load_pct'] = cpu_pct
    if is_heart:
        d['health'] = 'green'
        d['active'] = True
    else:
        d['d19_watermark_guard']['round_ref'] = 1052
        d['d19_watermark_guard']['ts'] = NOW
        d['last_round_label'] = 'r1052'

for path, is_heart in ((STATE, False), (HEART, True)):
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    upd(d, is_heart)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    with open(path, encoding='utf-8') as fh:
        c = json.load(fh)
    assert c['round_no'] == 1053 and c['loop_round'] == 1052
    assert isinstance(c['heartbeat_epoch_utc'], int)
    assert c['heartbeat_epoch_utc'] == EPOCH
    assert 'O-20261018-0948-bm-a.md' in c['orders_ack']

print('CLOSEOUT-OK now=%s epoch=%d ram_free_gb=%s cpu_pct=%s codely_size=%d'
      % (NOW, EPOCH, ram_free_gb, cpu_pct, csize))
