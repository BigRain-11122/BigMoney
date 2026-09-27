# -*- coding: utf-8 -*-
"""r346 bm-b close: round report line + state round_no 346 + heartbeat + inbox moves."""
import json, os, time, shutil, datetime

REPORT = 'logs/iteration-loop/round_reports.md'
STATE = 'logs/iteration-loop/state.json'
HB = 'fleet/machines/bm-b.json'

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S') + ('+' if now.utcoffset() >= datetime.timedelta(0) else '-') + f"{abs(now.utcoffset()).seconds//3600:02d}:{abs(now.utcoffset()).seconds%3600//60:02d}"

line = (ts + ' | round 346 bm-b | dept:\u5de5\u7a0b+\u8230\u961f | '
 'WM=\u7eff(red=false@22:30:21 lane healthy; probe 22:36 py 28.6% verdict=py_low_with_work_cands=\u5408\u6cd5\u9762\u552f\u4e00 work cand=CENSUS-FUS-S2-W2A \u672c\u8eab\u5728\u70e7 4-worker BelowNormal \u8bbe\u8ba1\u8db3\u8ff9~25-28%\u00b7\u65e0\u8fdd\u4ee4\u53ef\u70b9\u540d\u00b7\u5408\u6cd5\u767d\u540d\u5355\u9762=\u6c60\u552f\u4e00\u5206\u7247\u5df2\u71c3+\u677f\u5168\u95ed\u73af+bandit \u7a7a+no-kill \u7eaa\u5f8b; compute_audit CLEAN \u96f6\u65d7\u96f6\u50f5\u5c38) '
 '| did: (1) S0 \u8f6e\u9996\u810f=p1d_gates tick \u70ed\u5199(22:30:20) \u5b9a\u5411\u63d0\u4ea4\u540e pull--rebase \u5e72\u51c0\u524d\u8fdb(bm-a r360 \u5165\u7a97); (2) S0.5 \u53cc\u626b\u524d\u534a orders 96/96 \u96c6\u5408\u5dee\u96c6\u96f6\u672a\u56de\u6267+\u96c6\u56e2 decisions.md \u4e09\u8def\u5f84\u7f3a\u4f4d\u8bda\u5b9e no-op+\u6536\u4ef6 MSG-2215(bma W2B \u6c60\u884c verbatim \u6062\u590d\u56de\u6267 ack \u96f6\u52a8\u4f5c+r340 \u65cf union \u6cd5\u5f8b\u5df2\u5438\u6536); (3) S1 smoke 25/25; (4) S2 \u53cc\u677f\u96f6 open(job_list \u7a7a+\u4efb\u52a1\u677f\u65e0 open); '
 '(5) W2-A burn \u6d3b\u4f53\u540c\u6e90\u5b9a\u8c2d: psutil \u540c\u6e90\u63a2\u9488(parent 13148+4 spawn workers 22:35 \u5feb\u7167 cpu_delta 5.05-6.00s/6s \u6ee1\u6838\u71c3\u70e7+RSS \u5408\u8ba110.9GB+wall~7.5h 15:12:51 \u8d77)\u2014\u2014Get-Process \u8868\u9762\u8bef\u8bfb\u96f6\u8fdb\u7a0b\u9669\u81ea\u8bc1\u6b7b\u4ea1\u8fd1\u5f39=\u65b0\u5751\u5f8b\u540c\u7a97\u5165\u518c; no-kill \u7ef4\u6301\u00b7w2_results.json \u672a\u843d=finalize \u672a\u5230\u7a97; '
 '(6) W2B D8 \u63a5\u6536\u56de\u6267\u95ed\u73af: npz sha256+bytes \u5b57\u8282\u6052\u7b49(9febb7b4../60,418,563)+git \u885b\u751f\u5168\u8fc7(\u672a\u8ddf\u8e2a/\u672a\u6682\u5b58/gitignore:124)\u2192\u8bc1\u636e results/_r346bmb_w2b_d8_receipt.json+MSG-20260927-2240 \u56de\u6267 bm-a;\u6c60\u96f6\u5199\u5165(W2B waiting=\u771f\u5b9e\u6001\u00b7\u907f tick \u7ade\u6001\u4e0e r340 \u65cf\u6574\u4ef6\u8986\u76d6);\u7ffb\u8f6c\u95e8=W2-A finalize+RAM>=12GB \u53cc\u6ee1; '
 '(7) S4 \u5751\u5f8b+CODELY 10KB \u786c\u7ebf\u540c\u7a97\u70ed\u51b7\u6574\u7f16=\u4e09\u5341\u4e09\u6279(r344x2/r360/r346 \u56db\u884c verbatim\u2192archive 202609.md\u00b7CODELY \u6307\u9488\u884c\u7559\u00b7\u96f6\u4e22\u5931\u6821\u9a8c 4/4\u00b710,140\u219210,024B \u4f4e\u4e8e r360 \u6536\u5b98\u6c34\u4f4d); '
 '(8) S6 30/30 rc=0 \u5468\u65e5 no-op \u5bb6\u65cf(update_daily 0 \u65b0\u884c cutoff 09-24 \u5468\u4e94\u4e2d\u79cb\u4f11\u5e02\u811a\u672c\u65e5\u5386\u81ea\u8bc1/\u65e0\u65b0bar \u95e8\u63a7\u94fe\u5408\u6cd5\u8df3\u8fc7/clock ORANGE_COOL sleeves=4/astock+rev_osc bm-b \u53cc\u8f66\u9053\u5e42\u7b49 no-op/8 \u8f66\u9053\u62a4\u680f\u8bda\u5b9e no-op/t24_promotion 0/22 \u8bda\u5b9e/aggr-alloc-grid \u7eb8\u76d8\u5e73\u7b49\u5e42\u7b49/t35_export \u518d\u751f 6 \u5458\u6301\u4ed3\u6743\u76ca 5,996,645/daily_report faces=4/build_status/token L2 1 \u817f) '
 '| \u8bc1\u636e: smoke 25/25+S6 30x rc=0+D8 sha \u5b57\u8282\u6052\u7b49+psutil \u53cc\u8bc1\u63a2\u9488+fold \u96f6\u4e22\u5931 4/4+\u4e09\u5341\u4e09\u6279\u5728\u4f4d '
 '| \u4e0b\u8f6e: r347 W2-A finalize \u6536\u5272\u7a97(w2a_results.json \u843d\u5730\u5373 pool W2A done-flip+T-86 bm-a \u56de\u6267+W2B probe ONCE+run+pool waiting\u2192ready \u540c\u8f6e\u00b7\u95e8=finalize+RAM>=12GB)\u00b7\u5468\u4e00 09-28: 09:15 T-91 s3 auto-fire+15:30 T-87 astock \u9996\u589e\u91cf+\u65b0bar \u5168\u94b7\u00b7r350 5x HANDOVER\u00b710-01 \u6708\u9996\u4e09\u4ef6\u5957+REGIME_GUARD v3 \u65e5\u671f\u95e8')

with open(REPORT, 'ab') as f:
    f.write((line + '\n').encode('utf-8'))

st = json.load(open(STATE, encoding='utf-8'))
st['round_no'] = 346
st['did'] = ('r346: W2B D8 \u63a5\u6536\u56de\u6267\u95ed\u73af(sha+bytes \u6052\u7b49+git \u885b\u5e72\u51c0\u00b7MSG-2240\u00b7\u6c60\u96f6\u5199\u907f tick \u7ade\u6001) + W2-A burn \u6d3b\u4f53 psutil \u540c\u6e90\u53cc\u8bc1\u5b9a\u8c2d(13148+4 workers \u6ee1\u6838\u71c3\u70e7~7.5h\u00b7no-kill \u7ef4\u6301) + S4 \u5751\u5f8b psutil \u5f8b\u5165\u518c+\u4e09\u5341\u4e09\u6279\u70ed\u51b7\u6574\u7f16(10,024B \u96f6\u4e22\u5931 4/4) + S6 30/30 rc=0 \u5468\u65e5 no-op + smoke 25/25 + orders 96/96 \u53cc\u626b\u96f6\u5dee')
st['verdict'] = 'green'
st['next'] = ('r347: W2-A finalize \u6536\u5272\u7a97(w2a_results.json \u843d\u5730\u2192 pool W2A done-flip+T-86 bm-a receipt+W2B probe ONCE+run+pool waiting\u2192ready \u540c\u8f6e; \u95e8=W2-A finalize+RAM>=12GB \u53cc\u6ee1) + \u5468\u4e00 09-28: 09:15 T-91 s3 auto-fire+15:30 T-87 astock \u9996\u589e\u91cf+\u65b0bar \u5168\u94fe(preflight 8/8) + r350 5x HANDOVER + 10-01 \u6708\u9996\u4e09\u4ef6\u5957+REGIME_GUARD v3 \u65e5\u671f\u95e8')
st['last_round_ts'] = ts
st['last_result'] = 'ok'
st['current_task'] = 'r346 closed: W2B D8 receipt + W2-A burn watch (no-kill) + S6 30/30 + 33rd-batch fold'
st['updated_at'] = ts
st['last_seen'] = ts
st['ts'] = ts
with open(STATE, 'wb') as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1).encode('utf-8'))

hb = json.load(open(HB, encoding='utf-8'))
import psutil
epoch = int(time.time())
clock_read = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
hb['last_seen'] = clock_read
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock_read
hb['current_task'] = 'r346 closed: W2B D8 receipt (sha verified) + W2-A burn alive watch no-kill carry + S6 30/30 + 33rd-batch CODELY fold'
hb['cpu_cores'] = psutil.cpu_count(logical=True)
hb['free_ram_gb'] = round(psutil.virtual_memory().available / 1e9, 1)
hb['total_ram_gb'] = round(psutil.virtual_memory().total / 1e9, 1)
hb['cpu_util_pct'] = psutil.cpu_percent(interval=1)
try:
    import subprocess
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=10)
    hb['gpu_free_vram_gb'] = round(int(out.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass
hb['round_no'] = 346
hb['round'] = 346
hb['loop_round'] = 346
hb['verdict'] = 'healthy'
with open(HB, 'wb') as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1).encode('utf-8'))

chk = json.load(open(HB, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read must be ISO8601 T-separated'
print('HB OK: epoch int =', chk['heartbeat_epoch_utc'], 'clock =', chk['clock_read'], 'ram_free =', chk['free_ram_gb'], 'GB py_cpu =', chk['cpu_util_pct'])

for msg in ('fleet/inbox/MSG-20260927-2215-bma-bmb-w2b-pool-restore.json',
            'fleet/inbox/MSG-20260927-2222-bmb-all-tick-abort-ownership.json'):
    if os.path.exists(msg):
        shutil.move(msg, msg.replace('inbox/', 'inbox/processed/'))
        print('moved:', os.path.basename(msg))
print('inbox root now:', sorted(os.listdir('fleet/inbox')))
