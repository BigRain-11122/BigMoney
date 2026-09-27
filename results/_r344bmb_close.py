import json, subprocess, time, os, shutil

NOW = time.strftime('%Y-%m-%d %H:%M:%S')
NOW_ISO = time.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
EPOCH = int(time.time())

# ---- 1) pool: restore W2B entry + d8 receipt ----
raw = open('results/runnable_pool.json', 'rb').read()
crlf = b'\r\n' in raw[:2000]
pool = json.loads(raw.decode('utf-8'))
old = json.loads(subprocess.run(['git', 'show', '9b62a4c9:results/runnable_pool.json'],
                                capture_output=True).stdout.decode('utf-8'))
w2b = [e for e in old['entries'] if e.get('id') == 'CENSUS-FUS-S2-W2B'][0]
ids = {e.get('id') for e in pool['entries']}
if 'CENSUS-FUS-S2-W2B' not in ids:
    w2b['d8_receipt'] = {
        'received_by': 'bm-b', 'received_ts': NOW,
        'sha256_verified_vs_git_manifest': True,
        'note': 'r344 fold take-new(updated_at) ts-face dropped this remote-added entry (local tick churn fresher ts); restored from 9b62a4c9 + entries-ID audit 79vs80 single-loss; MSG-1912 prose sha = hand-transcription error, git-tracked manifest byte-equal PASS; dep(2) W2-A finalize still pending -> status stays waiting',
    }
    pool['entries'].append(w2b)
    pool['updated_at'] = NOW
    out = json.dumps(pool, ensure_ascii=False, indent=1)
    if crlf:
        out = out.replace('\n', '\r\n')
    open('results/runnable_pool.json', 'wb').write((out + ('\r\n' if crlf else '\n')).encode('utf-8'))
    print('POOL_RESTORED entries=', len(pool['entries']))
else:
    print('POOL_ALREADY_HAS_W2B')
rp = json.load(open('results/runnable_pool.json', encoding='utf-8'))
assert len(rp['entries']) == 80, 'pool must be 80 entries'

# ---- 2) state.json round 344 ----
st = json.load(open('logs/iteration-loop/state.json', encoding='utf-8'))
st['round_no'] = 344
st['did'] = ("r344 FIRST MISSION fold mainline DONE: S0 pull--rebase 23-commit replay canonical resolve "
             "(classifier 6 recipes + state.json manual=bm-b single-writer; autofill launches union cap50 keep48; "
             "compute_audit union 228; CODELY memory-union; round_reports md-union; tick-dirt r290 ride-along; "
             "tick abort-leg live-fire 21:48:48 destroyed first attempt -> atomic single-process driver rebuild, "
             "push main 7a390e1f LANDED (2nd rebase retry vs mid-fold origin advance), GC escape machine/bm-b-r342+r343; "
             "W2B pool entry fold-loss found+restored (take-new updated_at ts-face vs carry semantics, ID-audit 79vs80 single-loss) "
             "+ D8 receive SOP complete (sha256 byte-equal vs git-tracked manifest; MSG prose sha hand-error disclosed) "
             "+ S1 smoke 25/25 + S6 30/30 rc=0 (3 new-bar-gated legal skips) + orders 96/96 dual-scan + inbox 2 processed "
             "(MSG-2055 receipt + MSG-1912 D8 receive) + W2-A harvest carry (w2_results.json absent, no-kill)")
st['verdict'] = 'green'
st['next'] = ("r345: 5x HANDOVER audit + W2-A finalize harvest (pool CENSUS-FUS-S2-W2A ready->done + result_ref once "
              "w2_results.json lands; no-kill discipline) + W2B flip waiting->ready ONLY when dep(2) W2-A finalize lands "
              "(then FIRST-SIGHT probe once + run per MSG-1912 SOP; RAM>=12GB prep guard) + tick abort-leg hardening "
              "proposal to GM (autofill.py _claim_shard fail-safe rebase--abort vs session folds; r344 pitlaw) + "
              "Mon 09-28 09:15 T-91 s3 auto-fire + 15:30 T-87 astock first increment + 10-01 monthly trio")
st['last_round_ts'] = NOW_ISO
st['current_task'] = ('r344 closed: fold mainline LANDED (push 7a390e1f + GC escapes) + W2B entry restore + D8 received/verified + S6 30/30')
st['updated_at'] = NOW_ISO
st['last_seen'] = NOW_ISO
st['ts'] = NOW
open('logs/iteration-loop/state.json', 'w', encoding='utf-8').write(json.dumps(st, ensure_ascii=False, indent=1) + '\n')

# ---- 3) heartbeat ----
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = NOW_ISO
hb['heartbeat_epoch_utc'] = EPOCH
assert isinstance(hb['heartbeat_epoch_utc'], int)
hb['clock_read'] = NOW_ISO
hb['current_task'] = st['current_task']
hb['round_no'] = 344
hb['verdict'] = 'healthy'
open('fleet/machines/bm-b.json', 'w', encoding='utf-8').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
chk = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be ISO T-format'

# ---- 4) round report line ----
line = (f"{NOW_ISO} | round 344 bm-b | dept:工程+舰队 | WM-VERDICT: green (watermark_red red=false @21:59; "
        f"py_watermark py_low_with_work_cands=合法在飞 W2-A 4worker local_batch_running=true, compute_audit CLEAN 零旗 pool-supply-gap) | "
        f"FIRST MISSION fold mainline LANDED: push main 7a390e1f (23-commit replay canonical resolve; tick abort-leg 21:48:48 实弹毁首跑"
        f"→原子驱动重建两跑 54.7s+21.4s+reflog 定谳) + GC escape r342/r343 | W2B pool 条目折叠损失发现+恢复(ID 对账 79vs80 单损) "
        f"+ D8 接收 sha256 vs manifest 字节等(MSG 散文手抄讹披露)+回执记录 dep(2) 未满 waiting 保持 | "
        f"S1 smoke 25/25 | S6 30/30 rc=0+3 新bar门合法跳(_r344bmb_s6.log) | orders 96/96 双扫零差 | "
        f"inbox 2 处理(2055/1912) | W2-A harvest 续带 | next: r345 5x HANDOVER + W2-A finalize harvest + W2B 双 dep 翻面+tick abort 腿加固提案")
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(line + '\n')
print('CLOSE_WRITES_DONE')

# ---- 5) inbox processed ----
for m in ('MSG-20260927-2055-bma-bmb-w2b-mirror-landed.json', 'MSG-20260927-1912-bma-w2b-d8-transfer.json'):
    src = os.path.join('fleet', 'inbox', m)
    dst = os.path.join('fleet', 'inbox', 'processed', m)
    if os.path.exists(src):
        shutil.move(src, dst)
        print('PROCESSED:', m)
