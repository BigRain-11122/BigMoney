# -*- coding: utf-8 -*-
"""r346 bm-b final close: T-94 claim (CEO immediate-law) + orders_ack + heartbeat + report addendum."""
import json, time, datetime, subprocess

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
stamp = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'

# 1) T-94 claim (fetch already fresh from rebase#2; claim = status flip + commit lock)
P = 'fleet/tasks/T-2026-09-27-94-P1.json'
t = json.load(open(P, encoding='utf-8'))
assert t['status'] == 'open', f"unexpected status {t['status']} -- another machine may have claimed; re-check"
t['status'] = 'claimed'
t['claimed_by'] = 'bm-b (OS iteration loop, round 346 S7 double-scan catch; claim-and-start same round per O-20260924-1730 immediate-law; git fetch immediately before claim per r239 collision law)'
t['claimed_at'] = stamp
t['claim_note'] = ('bm-b slice = s1: wave-level prereg draft FROZEN FIRST (R99 law) per O-20260927-2245 sec.3 s1 -- generation grammar (registered-six templates + judged school templates + T-86 census surviving factor legs CONSUMED WHEN READY, W2A/W2B in-flight runs NOT duplicated per anti-dup hard law) x refine-bench axes x random draws (RANDOM_LARGE_SAMPLE_LAW sec-2 N>=500/family Sobol/uniform) + T-84 s3 dedup gate law (per-rebalance holdings sha256 + |corr|>=0.999 collapse, 1000=ceiling not quota). Precise continuation point: draft from research/PREREG_TEMPLATE.md + science_gates shared lib (no hand-copied judgment lines), land r347 first mission; s2 stage-1 screen pool batch follows prereg freeze only.')
with open(P, 'wb') as f:
    f.write(json.dumps(t, ensure_ascii=False, indent=1).encode('utf-8'))
print('T-94 claimed by bm-b @', stamp)

# 2) heartbeat: orders_ack += both CEO orders + refresh
HB = 'fleet/machines/bm-b.json'
hb = json.load(open(HB, encoding='utf-8'))
for o in ('O-2026-09-27-2245-bm-a.md', 'O-2026-09-27-2250-bm-a.md'):
    if o not in hb['orders_ack']:
        hb['orders_ack'].append(o)
hb['n_orders_ack'] = len(hb['orders_ack'])
import psutil
hb['last_seen'] = iso
hb['clock_read'] = iso
hb['heartbeat_epoch_utc'] = int(time.time())
hb['current_task'] = 'r346 closed: W2B D8 receipt + W2-A burn no-kill carry + storm resolve 18-UU + T-94 CLAIMED s1 prereg next + TRIAL_LABOR_LAW standing line r347+'
hb['round_no'] = 346
hb['round'] = 346
hb['loop_round'] = 346
hb['verdict'] = 'healthy'
hb['free_ram_gb'] = round(psutil.virtual_memory().available / 1e9, 1)
with open(HB, 'wb') as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1).encode('utf-8'))
chk = json.load(open(HB, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int) and 'T' in chk['clock_read']
print('HB acks =', chk['n_orders_ack'], 'epoch int =', chk['heartbeat_epoch_utc'])

# 3) round report addendum (r343 precedent)
line = (iso + ' | round 346 addendum bm-b | dept:\u5de5\u7a0b+\u8230\u961f | '
 'S7 \u53cc\u626b\u6355\u83b7\u8f6e\u4e2d\u65b0\u4ee4\u4e24\u9053: O-20260927-2245(\u5343\u4eba\u8bd5\u7528\u671f\u4ee4\u00b7T-94 \u5019\u9009\u5927\u8003\u6279 1000 \u9996\u6ce2/5000 \u6269\u5bb9\u5f8b\u00b7prereg \u51bb\u7ed3\u5148\u884c)+O-20260927-2250(TRIAL_LABOR_LAW v1.0 \u5e38\u8bbe\u7acb\u6cd5+S3 \u94fe\u710a\u63a5 bm-a \u5df2\u843d\u5730\u5b9e\u8bc1\u5f8b\u6587\u4ef6+prompt \u710a\u63a5\u5747\u5728\u4f4d) -- \u53cc\u4ee4 orders_ack \u5df2\u56de\u6267(98/98) | T-94 \u8ba4\u9886\u5373\u5f00\u8dd1\u672c\u8f6e\u5b8c\u6210: claimed_by=bm-b\u00b7s1 \u5207\u7247=\u6ce2\u7ea7 prereg \u8349\u6848(R99 \u51bb\u7ed3\u5148\u884c\u00b7PREREG_TEMPLATE+\u5171\u4eab\u5224\u636e\u5e93\u00b7T-86 \u5b58\u6d3b\u817f\u4f9b\u7ed9\u9762\u5f85\u5c31\u7eea\u4e0d\u91cd\u590d W2A/W2B \u5728\u98de\u6279)\u00b7\u7cbe\u786e\u7eed\u4f5c\u70b9\u5df2\u5165\u7968 claim_note\u00b7r347 \u9996\u4efb\u52a1=\u8349\u6848\u843d\u5730 | \u98ce\u66b4\u89e3\u56de\u6267: 18-UU \u5206\u7c7b\u5668\u8def\u7531\u5168\u89e3(10 snapshot deep-ts \u53d6\u65b0+compute_audit history union 201+201\u2192203 \u96f6\u4e22\u5931+autofill launches cap47+daily_report/js \u53cc\u80de\u80d6\u540c\u4fa7+\u53cc\u6298\u53e0\u649e\u6279 r176 \u8ba9\u53f7=\u672c\u673a\u4e09\u5341\u4e09\u2192\u4e09\u5341\u56db\u6279\u91cd\u7f16)+\u4e8c\u8f6e rebase \u5e72\u51c0\u843d\u5730 aca13514 | CODELY \u5b9e\u51b5=6,158B \u6c34\u4f4d\u7ebf\u4e0b(bm-c r112 \u6298\u53e0\u7248\u4e3a\u57fa+\u672c\u673a r346 \u6307\u9488\u884c\u5408\u5e76\u00b7archive \u56db\u6279\u8282\u96f6\u4e22\u5931\u5b9e\u8bc1) | W2-A burn \u6301\u7eed\u71c3\u70e7\u4e2d no-kill | \u4e0b\u8f6e: r347 T-94 s1 prereg \u8349\u6848\u9996\u4efb\u52a1+TRIAL_LABOR \u5e38\u8bbe\u7ebf\u9996\u6267\u884c+W2-A finalize \u6536\u5272\u7a97')
with open('logs/iteration-loop/round_reports.md', 'ab') as f:
    f.write((line + '\n').encode('utf-8'))
print('addendum appended')

# 4) state next-pointer refresh
S = 'logs/iteration-loop/state.json'
st = json.load(open(S, encoding='utf-8'))
st['next'] = ('r347: T-94 s1 wave-level prereg draft FIRST MISSION (R99 frozen-first: PREREG_TEMPLATE + science_gates shared lib + T-84 s3 dedup + census-survivor supply face) + TRIAL_LABOR_LAW S3 standing line first execution + W2-A finalize harvest window (w2a_results.json -> pool done-flip + T-86 bm-a receipt + W2B probe ONCE + run, gate=finalize+RAM>=12GB) + Mon 09-28: 09:15 T-91 s3 auto-fire + 15:30 T-87 astock first increment + r350 5x HANDOVER + 10-01 monthly trio')
st['current_task'] = 'r346 closed: T-94 claimed (s1 prereg next) + W2B D8 receipt + storm resolve + burn no-kill carry'
st['last_seen'] = iso
st['ts'] = iso
with open(S, 'wb') as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1).encode('utf-8'))
print('state next updated')
