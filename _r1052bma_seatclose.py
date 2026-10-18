#!/usr/bin/env python
# r1052 bm-a W267 seat-claim closeout -- updates state + heartbeat with the
# seat-claim faces AND completes the heartbeat postscript that the first
# postscript run missed (it died on a self-inflicted assert typo AFTER the
# state write but BEFORE the heartbeat write).
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S+08:00')

PS10 = (" (10) POSTSCRIPT 10:2x: W266 finalize landed mid-closeout-push (bm-c 007ec5e713 10:21:39, n1_w266_results.json + "
        "ledger EXACT) -- the r1052 committed verdict 'finalize absent -> W267 GATED' was true at the 10:22:05 state write "
        "but stale by the 10:22:52 push (the pre-push claw's own fetch is what surfaced bm-c's batch; rebase landed cleanly "
        "on top of it, zero UU, bm-c files intact on origin tip). Gate condition (splice+finalize) now MET; W266 prereg "
        "sec.7/8 backfill landed 5f6c14efd4 10:24:08 declaring the W267 vacancy 'next free number, seat-first, re-derive on "
        "post-W266 universe'")

CUR = ("r1052: 当前活=v2 采纳自证回执闭环（spawning 行逐字 hard-cap 240min/silence-kill 25min vs 09:48 旧面 budget 25min）"
       "+心跳回执面补账（HEAL-OK→复扫 CLEAN 102/111/0）+D-19 增量消费（a62af296 记忆治理令②·零新义务·读回恒等）"
       "+W266 全周期收官确认（splice+自烧+heal+PRE-FINALIZE 29 连+finalize 007ec5e713+fivekeys 6/6+§7/8 回填 5f6c14efd4"
       "=W266 CYCLE COMPLETE·10:11-10:24 中窗落链）+W267 席位认领闭环（门条件 MET·名面=next free number seat-first"
       "→零占位终验→探针 post-W266 宇宙 live 跑 ADMIT〔A 602_701..604_700 第十六连 A-hop/B 604_701..604_900 第十七连 "
       "above-own-A·与 r1050 预著投影零分歧〕→席位 MSG-20261018-1030 推 origin=认领成立·bm-a 第 131 自有波）"
       "+MF day-9 证据（rank 道 fetch_failed=封锁仍活·周一 ≤10-19 裁决 armed）+bm-b/bm-c rootfix 守望（窗 1/2）"
       "+S6 42/42 rc0+idle --worked；最近实物=fleet/inbox/MSG-20261018-1030-bma-w267-seat.md+"
       "results/_w267bma_20261018_probe_receipt.json+_r1052bma_heartack_heal.py；"
       "下个里程碑=r1053 首动作=W267 prereg derive+freeze（W266/W262 节奏=冻结后 splice 执行窗）"
       "+MF 周一 ≤10-19 裁决+rootfix 回执（≤2 轮窗）+月界首考 10-31；孤儿面=0/27；watermark=red=false healthy")

NEXT = ("r1053: (0) FIRST ACTION = W267 prereg derive+freeze on the post-W266 universe per the W267 seat MSG "
        "(bm-a own seat, engine_owner==bm-a rows 130 + candidate = 131st own wave; bands A 602_701..604_700 / "
        "B 604_701..604_900 CANDIDATE-RESERVED -- re-derive governs, divergence disclosed honestly; draft from "
        "research/PREREG_TEMPLATE.md, N=2,200 (A 2,000 / B 200), ledger +2,200 projection 1,009,535+2,200=1,011,735 / "
        "K 583,120+2,200=585,320; banned_direction_gate --prereg pre-freeze; freeze commit = the wave claim; five-face "
        "splice = next execution window per W266 cadence r1085-freeze -> r1086-splice); (1) bm-b/bm-c rootfix receipts "
        "watch (<=2-round window round 2, MSG-20261018-*-rootfix.md); (2) MF Monday <=10-19 blockade adjudication "
        "(day-8 + day-9 evidence chain, rank fetch_failed face); (3) idle verdict watch (backlog pool 0, refill = "
        "dispatcher/secretariat lane)")

MILE = ("W267 prereg derive+freeze (r1053 FIRST ACTION) + splice/self-burn/finalize chain + MF Monday blockade "
        "adjudication (<=10-19) + bm-b/bm-c rootfix receipts (<=2 rounds) + month-boundary first exam 10-31")

TASK = "r1052: v2 adoption receipt + heartbeat ack heal + W267 SEAT CLAIM + S6 closeout"

ART = ("fleet/inbox/MSG-20261018-1030-bma-w267-seat.md (W267 seat claim) + results/_w267bma_20261018_probe_receipt.json "
       "(live ADMIT) + _r1052bma_heartack_heal.py (receipt-face fix)")

VERDICT_APPEND = (" + W267 SEAT CLAIMED same-round on the freshly-opened gate (W266 cycle complete 10:24 -> gate MET -> "
                  "naming face 'next free number seat-first' -> zero-vacancy re-verify -> probe LIVE ADMIT "
                  "(A 602_701..604_700 / B 604_701..604_900, zero divergence from r1050 pre-authored projections) -> "
                  "seat MSG pushed origin = bm-a 131st own wave; prereg derive+freeze armed as r1053 FIRST ACTION)")

VERIFY_APPEND = (" + probe stdout leg0-4 verbatim + receipt results/_w267bma_20261018_probe_receipt.json (bma_rows=130 "
                 "ordinal 257, bands A(602701,604700)/B(604701,604900), relation_asserts all true, verdict ADMIT) + "
                 "seat MSG fleet/inbox/MSG-20261018-1030-bma-w267-seat.md + zero W267 seat artifacts on origin "
                 "pre-claim (twice-verified ls-tree)")

NOTE_APPEND = (" (11) W267 SEAT CLAIM tail-of-round: bm-c landed W266 CYCLE COMPLETE mid-r1052 (finalize 007ec5e713 "
               "10:21:39 + fivekeys/sec.7/8 backfill 5f6c14efd4 10:24:08 -- W267 vacancy declared 'next free number, "
               "seat-first, re-derive on post-W266 universe'); gate condition (splice+finalize) MET + naming face open "
               "+ zero W267 seat artifacts on origin (twice-verified) + O-20260924-1730 same-round claim law -> probe "
               "run LIVE in-window (ADMIT rc0, receipt _w267bma_20261018_probe_receipt.json, bands EXACTLY the r1050 "
               "pre-authored expectations: A 602_701..604_700 16th consecutive A-hop / B 604_701..604_900 17th "
               "consecutive above-own-A, zero divergence disclosed) -> seat MSG authored + pushed (claim by "
               "commit-time order per r1043 W262 precedent); prereg derive+freeze = r1053 FIRST ACTION (W266/W262 "
               "cadence: seat window then freezer window); (12) first postscript run died on a self-inflicted assert "
               "typo (checked 'POSTSCRIPT' uppercase vs the lowercase 'postscript' inside the NEXT string) AFTER the "
               "state write but BEFORE the heartbeat write -- state carried the postscript, heartbeat did not; THIS "
               "write completes the heartbeat face (no data loss; both faces now carry the seat-claim + sharpened "
               "next-task)")

for path in (os.path.join(BASE, 'state-bm-a.json'),
             os.path.join(BASE, 'fleet', 'machines', 'bm-a.json')):
    with open(path, encoding='utf-8') as fh:
        d = json.load(fh)
    d['current'] = CUR
    d['did'] = CUR
    d['last_action'] = CUR
    d['next'] = NEXT
    d['current_task'] = NEXT
    d['next_milestone'] = MILE
    d['task'] = TASK
    d['last_artifact'] = ART
    d['latest_artifact'] = ART
    d['recent_artifact'] = ART
    d['verdict'] = d.get('verdict', '') + VERDICT_APPEND
    d['verify'] = d.get('verify', '') + VERIFY_APPEND
    n = d.get('notes_r1052', '')
    if 'POSTSCRIPT' not in n:
        n = n + PS10
    d['notes_r1052'] = n + NOTE_APPEND
    d['ts'] = NOW
    d['updated'] = NOW
    d['updated_at'] = NOW
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    with open(path, encoding='utf-8') as fh:
        c = json.load(fh)
    assert 'W267 SEAT CLAIM' in c['next'] or 'W267 prereg derive+freeze' in c['next']
    assert '007ec5e713' in c['current']
    assert '(12) first postscript run died' in c['notes_r1052']
    assert c['round_no'] == 1053

print('SEAT-CLOSEOUT-OK %s' % NOW)
