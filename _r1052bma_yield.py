#!/usr/bin/env python
# r1052 bm-a W267 yield rewrite -- bm-c's seat MSG-1025 (origin 10:25) beat
# bm-a's local 10:28:55 claim (never pushed; commit soft-reset, MSG
# retracted). Per fleet README sec.4 commit-time order + r1043 W262
# precedent bm-a YIELDS. Strips the seat-claim append faces from
# verdict/verify/notes (exact markers), rewrites current/next with the
# yield adjudication, keeps the live probe receipt as honest evidence.
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S+08:00')

V_MARK = " + W267 SEAT CLAIMED same-round"
VF_MARK = " + probe stdout leg0-4 verbatim"
N11_MARK = " (11) W267 SEAT"
N12_MARK = " (12) first postscript run died"

CUR = ("r1052: 当前活=v2 采纳自证回执闭环（spawning 行逐字 hard-cap 240min/silence-kill 25min vs 09:48 旧面 budget 25min）"
       "+心跳回执面补账（HEAL-OK→复扫 CLEAN 102/111/0）+D-19 增量消费（a62af296 记忆治理令②·零新义务·读回恒等）"
       "+W266 全周期收官确认（splice+自烧+heal+PRE-FINALIZE 29 连+finalize 007ec5e713+fivekeys 6/6+§7/8 回填 5f6c14efd4"
       "=W266 CYCLE COMPLETE·10:11-10:24 中窗落链）+**W267 撞席让路**（本窗探针 post-W266 宇宙 live 跑 ADMIT〔A 602_701..604_700/"
       "B 604_701..604_900·与 r1050 预著投影零分歧·回执留档〕→bm-c 席位 MSG-1025 10:25 先发 origin=按 fleet README §4 "
       "commit 时间序后到让路〔r1043 W262 同案〕·双探针同带零事实分歧·本窗席位 MSG 未上链即撤〔soft-reset 零 origin 污染〕"
       "·W267=bm-c 第 86 自有波）+MF day-9 证据（rank 道 fetch_failed=封锁仍活·周一 ≤10-19 裁决 armed）"
       "+bm-b/bm-c rootfix 守望（窗 1/2）+S6 42/42 rc0+idle --worked；"
       "最近实物=results/_w267bma_20261018_probe_receipt.json（live ADMIT 让路证据）+_r1052bma_heartack_heal.py"
       "+results/_r1052bma_s6chain_rc.log；下个里程碑=W268 守望（W267=bm-c 波·bm-a 名面随 W267 prereg §7/8 回填定）"
       "+MF 周一 ≤10-19 裁决+rootfix 回执（≤2 轮窗）+月界首考 10-31；孤儿面=0/27；watermark=red=false healthy")

NEXT = ("r1053: (1) W268 watch -- W267 = bm-c own wave (bm-a YIELDED per fleet README sec.4 commit-time order: bm-c seat "
        "MSG-20261018-1025 pushed origin 10:25 vs bm-a local 10:28:55 never-pushed claim, soft-reset + MSG retracted "
        "pre-push; r1043 W262 precedent; both probes live-ADMIT identical bands A 602_701..604_700 / B 604_701..604_900 "
        "on the same post-W266 universe, zero fact divergence; bm-a receipt results/_w267bma_20261018_probe_receipt.json "
        "retained as honest yield evidence); bm-a W268 window naming rides the W267 prereg sec.7/8 backfill per "
        "chain-order law (yield if named otherwise; zero skip-claim); (2) bm-b/bm-c rootfix receipts watch (<=2-round "
        "window round 2, MSG-20261018-*-rootfix.md); (3) MF Monday <=10-19 blockade adjudication (day-8 + day-9 "
        "evidence chain, rank fetch_failed face); (4) idle verdict watch (backlog pool 0, refill = dispatcher/secretariat lane)")

MILE = ("W268 bm-a window watch (naming rides W267 prereg sec.7/8 backfill, bm-c freezer lane) + MF Monday blockade "
        "adjudication (<=10-19) + bm-b/bm-c rootfix receipts (<=2 rounds) + month-boundary first exam 10-31")

TASK = "r1052: v2 adoption receipt + heartbeat ack heal + W267 race yield + S6 closeout"

ART = ("results/_w267bma_20261018_probe_receipt.json (live ADMIT, yield evidence) + _r1052bma_heartack_heal.py "
       "(receipt-face fix) + results/_r1052bma_s6chain_rc.log (42/42 rc0)")

YV = (" + W267 seat RACE YIELDED same-round per fleet README sec.4 commit-time order (bm-c seat MSG-20261018-1025 "
      "pushed origin 10:25 vs bm-a local 10:28:55 never-pushed -- claim commit soft-reset + seat MSG retracted "
      "pre-push, zero origin pollution; r1043 W262 precedent; both machines' probes live-ADMIT identical bands "
      "A 602_701..604_700 / B 604_701..604_900 on the same post-W266 universe, zero fact divergence -- pure "
      "commit-time race, not a facts dispute; bm-a probe receipt retained as honest evidence; W267 = bm-c 86th own wave)")

YVF = (" + yield evidence: origin fleet/inbox/MSG-20261018-1025-bmc-w267-seat.md (bm-c claim, bands identical to bm-a "
       "receipt) + bm-a claim commit 90b57728b8 soft-reset pre-push (never reached origin) + probe receipt "
       "results/_w267bma_20261018_probe_receipt.json retained")

N11 = (" (11) W267 seat race YIELDED: gate opened mid-round (W266 cycle complete 10:24) -> bm-a ran the pre-authored "
       "probe LIVE (ADMIT rc0, bands A 602_701..604_700 / B 604_701..604_900, zero divergence from r1050 projections, "
       "receipt _w267bma_20261018_probe_receipt.json) and authored seat MSG-1030, but bm-c's r1086-continuation window "
       "had already published seat MSG-1025 at 10:25 (on origin BEFORE bm-a's 10:28:55 local commit ever pushed) -> "
       "bm-a yields per fleet README sec.4 commit-time order (r1043 W262 precedent: plan expectation does not beat a "
       "landed claim); unpushed claim commit soft-reset + seat MSG retracted pre-push (zero origin pollution); both "
       "probes derived identical bands on the same post-W266 universe (zero fact divergence -- the race was pure "
       "commit-time); W267 = bm-c 86th own wave; bm-a W268 window naming rides the W267 prereg sec.7/8 backfill per "
       "chain-order law; lesson-let: on a freshly-opened gate with a hot upstream machine, PULL-FETCH immediately "
       "before authoring a seat MSG (my zero-vacancy check at 10:26 predated their 10:25 push reaching my fetch by "
       "minutes; the claim MSG authoring+commit window is where the race was lost)")

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
    v = d.get('verdict', '')
    if V_MARK in v:
        v = v.partition(V_MARK)[0]
    d['verdict'] = v + YV
    vf = d.get('verify', '')
    if VF_MARK in vf:
        vf = vf.partition(VF_MARK)[0]
    d['verify'] = vf + YVF
    n = d.get('notes_r1052', '')
    if N11_MARK in n:
        head = n.partition(N11_MARK)[0]
        tail12 = ''
        if N12_MARK in n:
            tail12 = N12_MARK + n.partition(N12_MARK)[2]
        n = head + N11 + tail12
    d['notes_r1052'] = n
    d['ts'] = NOW
    d['updated'] = NOW
    d['updated_at'] = NOW
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)
    with open(path, encoding='utf-8') as fh:
        c = json.load(fh)
    assert 'YIELDED' in c['verdict'] and 'MSG-20261018-1025' in c['verdict']
    assert 'W267 SEAT CLAIMED' not in c['verdict']
    assert 'W268 watch' in c['next']
    assert '(12) first postscript run died' in c['notes_r1052']
    assert 'race YIELDED' in c['notes_r1052']
    assert c['round_no'] == 1053

print('YIELD-REWRITE-OK %s' % NOW)
