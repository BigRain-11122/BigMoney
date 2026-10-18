#!/usr/bin/env python
# r1053 bm-a closeout: round report line + state-bm-a.json + heartbeat
# fleet/machines/bm-a.json (fresh-read-modify-write, single-writer faces,
# validate-then-atomic per r504 law).
import json
import os
import time
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, 'state-bm-a.json')
HEART = os.path.join(BASE, 'fleet', 'machines', 'bm-a.json')
REPORT = os.path.join(BASE, 'round_reports-bm-a.md')

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

CUR = (
    "r1053: \u56de\u6267\u53cc\u9762\u5751\u6839\u6cbb\u95f8\u843d\u5730\uff08Tools/orders_ack_append.py "
    "\u6b63\u5178\u53cc\u9762 ack \u8ffd\u52a0\u5668 selftest 8/8 + orders_ack_scan.py "
    "\u53cc\u9762\u5947\u5076\u6821\u9a8c\u95f8 exit4 selftest 17/17 + \u5b9e\u5f39\u590d\u626b CLEAN "
    "111/111 \u96f6\u5206\u6b67 + CODELY \u95f8\u5347\u7ea7\u884c\uff09"
    "+ bm-b fast-path \u89e3\u9501\u4e09\u4ef6\uff08r1046 \u914d\u65b9\u4e8c\u8fde\uff1abacklog \u884c14 "
    "O-0948 \u91c7\u7eb3\u6536\u53e3\u89e3\u9501\u5355\u5df2\u843d + \u6536\u53e3 push \u540e "
    "fleet-dispatch force-pull poke -Repos quant/bigmoney -Tasks Bigmoney-IterationLoop "
    "+ /status repo_heads \u9012\u8bb0\u9884\u671f\u672c push sha\uff09"
    "+ MF day-10 \u8bc1\u636e\uff08main lane 10:43:02 \u65b0\u9c9c\u5c1d\u8bd5 300706/07/08 "
    "RemoteDisconnected x3 conn_stopped=true = \u5c01\u9501\u4ecd\u6d3b day-10\uff1b\u5468\u4e00 "
    "<=10-19 \u88c1\u51b3 armed day-8/9/10 \u94fe\uff09"
    "+ W268 \u5b88\u95e8\uff08W266 finalize + W267 prereg \u5747\u672a\u843d origin=\u7ee7\u7eed "
    "GATED \u96f6\u62a2\u8dd1\uff09+ rootfix \u56de\u6267\u7a97\u672c\u673a\u8f6e2 \u6536\u53e3\u4ecd\u7f3a"
    "\uff08bm-c \u6d3b\u8dc3 10:28 \u672a ack=\u7a97\u6309\u5176\u81ea\u8eab\u8f6e\u8ba1\uff0c\u7591\u957f\u8f6e\u5728\u9014"
    "\uff1bbm-b \u5faa\u73af\u9762\u51bb\u7ed3 07:54 3h+=\u89e3\u9501\u5df2\u6267\u884c\uff09"
    "+ S6 42/42+live_paper rc0 + smoke 49/49 + idle --worked"
)
NEXT = (
    "r1054: (1) bm-b \u89e3\u9501\u9012\u9001\u9a8c\u8bc1\uff08/status repo_heads[quant/bigmoney]==\u672c\u8f6e "
    "push sha=\u884c14 \u5df2\u8fbe+\u4e0b\u8f6e\u8d77\u7834 fast-path\uff1b\u4ecd\u51bb\u7ed3=\u5347\u7ea7\u9762 "
    "bm-b \u5faa\u73af liveness \u62a5\u9762\uff09\uff1b(2) W268 \u5b88\u95e8\u7ee7\u7eed\uff08W267 prereg "
    "\u843d\u5730\u5373 FIRST ACTION live re-derive\uff09\uff1b(3) MF \u5468\u4e00\u88c1\u51b3 <=10-19"
    "\uff08day-8/9/10 \u94fe+\u5de5\u4f5c\u65e5\u91cd\u6d4b\uff09\uff1b(4) rootfix \u56de\u6267\u590d\u67e5"
    "\uff08bm-b \u89e3\u9501\u540e\u5176 2 \u8f6e\u7a97\u8d77\u8dd1\uff09"
)
VERDICT = (
    "GREEN: r1053: \u56de\u6267\u53cc\u9762\u5751\u95f8\u5347\u7ea7\u843d\u5730\uff08r1052 \u5f8b\u4ece\u6563\u6587\u2192"
    "\u811a\u672c\u65ad\u8a00\u7ea7\uff1a\u6b63\u5178\u8ffd\u52a0\u5668+\u626b\u63cf\u5668\u5947\u5076\u95f8\u53cc\u4ef6\u540c\u7a97"
    "\uff09+ bm-b fast-path \u89e3\u9501\u4e8c\u8fde\uff08r1046 \u914d\u65b9\u00b7\u884c14 \u5df2\u843d\u5f85 push "
    "\u540e poke\uff09+ MF day-10 \u5c01\u9501\u4ecd\u6d3b\u8bc1\u636e\uff08\u5468\u4e00\u88c1\u51b3 armed\uff09"
    "+ W268 GATED \u96f6\u62a2\u8dd1\u7ef4\u6301 + orders \u53cc\u626b CLEAN\uff08102/111/0+\u53cc\u9762 111/111 "
    "\u96f6\u5206\u6b67\uff09+ D-19 \u53cc\u96f6\u589e\u91cf + S6 42/42 rc0 + smoke 49/49 + idle --worked"
)
VERIFY = (
    "orders_ack_append selftest 8/8 + orders_ack_scan selftest 17/17\uff08L9-L13 \u65b0\u4e94\u817f\uff09"
    "+ \u5b9e\u5f39\u626b\u63cf CLEAN rc0\uff08face_divergence \u53cc\u7a7a\u96c6\uff09+ CODELY \u8ffd\u52a0 "
    "21,556B\u65ad\u8a00 + backlog \u884c14 6,470B\u65ad\u8a00 + results/_r1053bma_s6chain_rc.log "
    "42 rc0 bad=0 + MF status face\uff08main 10:43:02 RemoteDisconnected x3 + rank 10:15:09 "
    "fetch_failed 158s\uff09+ origin ls-tree\uff08n1_w266 12/12 shards\u3001finalize \u7f3a\uff1bw267 "
    "prereg \u7f3a\uff09+ smoke 49/49 + d19 probe dual-FALSE\uff08dec 0ad85a30/ord a62af296\uff09"
    "+ satengine ALIVE queue0 + orphan 0/23 + loop pin=8 no-op + claws x2\uff08watchdog S4U flip "
    "\u62d2=\u65e2\u6709 carried C-20261016-04\uff09+ attrition scan CLEAN\uff08S6 \u817f\uff09"
)
ART = (
    "Tools/orders_ack_append.py + Tools/orders_ack_scan.py \u53cc\u9762\u95f8 + fleet/backlog.md \u884c14 "
    "+ results/_r1053bma_s6chain_rc.log + MF day-10 status face"
)

# --- round report line ---
with open(REPORT, encoding='utf-8') as fh:
    rep = fh.read()
assert rep.endswith('\n')
line = (
    "%s | r1053 bm-a (dept:\u5de5\u7a0b\u00b7\u56de\u6267\u53cc\u9762\u95f8+bm-b\u89e3\u9501+S6\u7ef4\u62a4\u6536\u53e3) "
    "| WM-VERDICT: \u7eff (red=false lane=healthy; satengine ALIVE queue0 idle) "
    "| \u5f53\u524d\u6d3b=%s | \u9a8c\u8bc1\u8bc1\u636e=%s | \u4e0b\u8f6e\u6307\u9488=%s "
    "| \u5b9e\u7269=%s | \u672c\u5730\u672a\u8fbe origin commit \u6570=\u6536\u53e3 push \u540e\u9a8c "
    "| [r1053 bm-a ack-twoface-gate-bmb-unlock]\n" % (ts, CUR, VERIFY, NEXT, ART)
)
rep = rep + line
with open(REPORT, 'w', encoding='utf-8', newline='') as fh:
    fh.write(rep)

# --- state face ---
with open(STATE, encoding='utf-8') as fh:
    st = json.load(fh)
st['round_no'] = 1054
st['round'] = 1053
st['loop_round'] = 1053
st['last_round'] = 'r1053'
st['last_round_label'] = 'r1053'
st['last_round_at'] = ts
st['last_round_closed'] = ts
st['last_run'] = ts
st['last_seen'] = ts
st['now_active'] = ts
st['updated'] = ts
st['updated_at'] = ts
st['ts'] = ts
st['current'] = CUR
st['current_task'] = NEXT
st['did'] = CUR
st['last_action'] = CUR
st['task'] = "r1053: ack two-face gate + bm-b fastpath unlock + S6 closeout"
st['next'] = NEXT
st['next_milestone'] = (
    "W268 window watch (gated on W267 prereg, bm-c lane) + MF Monday blockade "
    "adjudication (<=10-19) + bm-b unlock delivery verify + rootfix receipts"
)
st['verdict'] = VERDICT
st['verify'] = VERIFY
st['last_artifact'] = ART
st['latest_artifact'] = ART
st['recent_artifact'] = ART
st['last_action_at'] = ts
st['heartbeat_epoch_utc'] = epoch
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['notes_r1053'] = (
    "r1053: (1) \u56de\u6267\u53cc\u9762\u5751\u95f8\u5347\u7ea7\uff08r1052 \u5f8b\u843d\u95f8\uff09\uff1a"
    "Tools/orders_ack_append.py=\u6b63\u5178\u53cc\u9762 ack \u8ffd\u52a0\u5668\uff08state+heartbeat "
    "\u540c\u5199\u00b7per-face \u5e42\u7b49\u00b7orders_ack_last \u53cc\u9762\u00b7--sync-mirrors "
    "\u516b\u955c\u50cf\u5b57\u6bb5\u00b7bm-b state.json \u7279\u4f8b\u00b7R170 epoch int \u5b88\u62a4\u00b7selftest "
    "8/8\uff09\uff1borders_ack_scan.py \u589e\u53cc\u9762\u5947\u5076\u6821\u9a8c\uff08exit 4=face_divergence"
    "\u00b7state \u9762\u7f3a/\u574f=exit4\u00b7unacked \u4f18\u5148 exit3\u4e0d\u53d8\u00b7selftest "
    "17/17\u00b7loop \u63a5\u7ebf best-effort \u96f6 rc \u6d88\u8d39=exit4 additive \u5b89\u5168\uff09\uff1b"
    "\u5b9e\u5f39\u771f\u9762 CLEAN 111/111 \u96f6\u5206\u6b67\uff1b\u6b64\u540e closeout \u56de\u6267 append "
    "\u4e00\u5f8b\u8d70\u6b63\u5178\u5de5\u5177\u7981\u624b\u6415\u5355\u9762\u5199\u3002"
    "(2) bm-b \u89e3\u9501\u4e8c\u8fde\uff1abm-b bigmoney \u5faa\u73af\u9762 origin \u51bb\u7ed3 07:54"
    "\uff083h+ \u96f6 push\uff09\u4e14\u96c6\u56e2 idle-watch \u672a\u53d1 BM \u9053 poke\uff08\u65e0 "
    "AUTO-REVIVE \u884c\u00b7\u90e8\u7f72\u9762\u53ea\u8bfb\u96c6\u56e2\u5fc3\u8df3\uff09=r1046 fast-path "
    "\u6b7b\u9501\u7b7e\u540d\u5168\u5339\u914d\uff1b\u6309 r1046 \u6b63\u6cd5\u4e09\u4ef6\u6267\u884c\uff1a"
    "\u884c14 \u89e3\u9501\u5355\u5df2\u843d\u672c\u8f6e commit\uff08\u7834 claimable_pool_lines "
    "0\u21921\uff09+ push \u540e fleet-dispatch force-pull poke\uff08-Repos quant/bigmoney -Tasks "
    "Bigmoney-IterationLoop\uff09+ /status repo_heads \u9a8c\u8bc1=r1054 \u9996\u52a1\u3002"
    "(3) rootfix \u56de\u6267\u7a97\uff1a\u672c\u673a\u8f6e 2 \u6536\u53e3\u4ecd\u7f3a\u2014\u2014\u7a97 "
    "\u6309\u53d7\u4ee4\u673a\u81ea\u8eab\u8f6e\u8ba1\uff08bm-c 10:28 \u540e\u7591\u957f\u8f6e\u5728\u9014"
    "\uff1bbm-b \u5faa\u73af\u51bb\u7ed3\u672a\u8d77\u8dd1\uff09\uff0cbm-b \u89e3\u9501\u540e\u5176 2 "
    "\u8f6e\u7a97\u6b63\u5f0f\u8d77\u8dd1\u3002(4) MF day-10\uff1amain lane \u65b0\u9c9c\u5c1d\u8bd5 "
    "10:43:02\uff08300706/07/08 RemoteDisconnected x3\u2192conn_stopped=true\uff09+ rank lane "
    "10:15:09 fetch_failed 158s\uff08r1052 \u7a97\u9762\u00b7\u4eca\u65e5 30min \u8282\u6d41\u5185 "
    "\u65e0\u65b0\u5c1d\u8bd5\uff09=\u5c01\u9501\u4ecd\u6d3b day-10\uff0c\u5468\u4e00 <=10-19 \u88c1\u51b3 "
    "armed\u3002(5) W268\uff1aW266 finalize\uff08n1_w266_results.json+\u00a77/8\uff09\u4e0e W267 "
    "prereg \u5747\u7f3a origin\uff08bm-c 10:28 \u540e\u96f6\u843d\u00b7\u7591\u957f\u8f6e\u5728\u9014"
    "\uff09\u2192GATED \u96f6\u62a2\u8dd1\u7ef4\u6301\u3002(6) S6 42/42+live_paper rc0 bad=0\uff08r1052 "
    "\u9762 verbatim \u514b\u9686 _r1053bma_s6chain.ps1\uff09"
)
st['orders_ack_note'] = (
    "r1053: \u53cc\u626b CLEAN 102/111/0 + \u53cc\u9762 111/111 \u96f6\u5206\u6b67\uff08\u65b0\u95f8 "
    "exit4 \u9762\u5b9e\u5f39\u8fc7\uff09\uff1b\u672c\u8f6e\u65e0\u65b0\u4ee4\uff08D-19 dual-FALSE "
    "dec 0ad85a30/ord a62af296\uff09\uff1bunacked=0\uff1b\u6b63\u5178\u8ffd\u52a0\u5668\u5f85\u4e0b\u4e00\u4ee4"
)
st['push_verified'] = {
    "ts": ts,
    "origin_tip": None,
    "ahead_behind": "pending-closeout-push",
    "note": "r1053 closeout push follows this write; fetch+ls-tree self-verify + fleet-dispatch poke after push",
}
st['sync'] = dict(st['push_verified'])

tmp = STATE + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
os.replace(tmp, STATE)
with open(STATE, encoding='utf-8') as fh:
    chk = json.load(fh)
assert isinstance(chk['heartbeat_epoch_utc'], int)
assert chk['round_no'] == 1054

# --- heartbeat face ---
with open(HEART, encoding='utf-8') as fh:
    hb = json.load(fh)
hb['last_seen'] = ts
hb['ts'] = ts
hb['current'] = CUR
hb['current_task'] = NEXT
hb['did'] = CUR
hb['last_action'] = CUR
hb['task'] = st['task']
hb['verdict'] = VERDICT
hb['verify'] = VERIFY
hb['last_artifact'] = ART
hb['latest_artifact'] = ART
hb['recent_artifact'] = ART
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = epoch
hb['heartbeat_epoch_utc_type_int'] = True
hb['clock_read'] = ts
hb['last_round'] = 'r1053'
hb['next'] = NEXT
hb['next_milestone'] = st['next_milestone']
tmp = HEART + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
os.replace(tmp, HEART)
with open(HEART, encoding='utf-8') as fh:
    hchk = json.load(fh)
assert isinstance(hchk['heartbeat_epoch_utc'], int)
assert 'T' in hchk['clock_read']

print('CLOSEOUT-OK ts=%s epoch=%d state_round_no=%d' % (ts, epoch, chk['round_no']))
