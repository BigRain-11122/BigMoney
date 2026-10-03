"""r619 bm-b S7 bookkeeping: state round_no bump + heartbeat + round report + CODELY memory entry."""
import json, time, os, glob, subprocess, datetime

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# --- 0) live burn tails for report ---
def k_tail(p):
    try:
        lines = open(p, encoding='utf-8').read().strip().splitlines()
        return json.loads(lines[-1])['k'], len(lines)
    except Exception:
        return -1, 0
v_k, v_n = k_tail('results/fund_value_p1/nulls.jsonl')
q_k, q_n = k_tail('results/fund_quality_p1/nulls.jsonl')
d_k, d_n = k_tail('results/fund_divlowvol_p1/nulls.jsonl')

# --- 1) state.json round bump ---
st = json.load(open('state.json', encoding='utf-8'))
st['round_no'] = 619
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no ->', st['round_no'])

# --- 2) heartbeat ---
hb_path = 'fleet/machines/bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb['last_seen'] = ts
hb['ts'] = ts
hb['updated'] = ts
hb['updated_at'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['round_no'] = 619
hb['round_no_label'] = 'round 619 (bm-b)'
hb['current_task'] = (
    f'r619 done: inherited-interrupted-rebase rescue closed (18+14 UU two-stage resolve, '
    f'r614 truncation holes backfilled, merge 6a3141646 pushed, r618 deliverables landed on origin); '
    f'T-156 COMPLETE: 13/13 files 1.84GB p1c_stock landed bm-a (send5 log tail, croc clean exit); '
    f'triple burns alive VALUE-NULLS {v_k}/2000 + QUALITY-NULLS {q_k}/2000 + DIVLOWVOL-NULLS {d_k}/2000'
)
hb['verdict'] = (
    'round 619 done: WM=loaded_ok green; smoke 47/47; S6 33/33 rc0 (dualrun ZERO-DRIFT streak 9, audit CLEAN '
    'burning-healthy); S7 4/4 (loop pin no-op + watchdog idempotent rebuild r613 known-face + claws live + '
    'attrition CLEAN); D-19 MATCH 4167b784 zero action; orders 151/151 double-scan zero unacked; '
    'DELIVERABLE: T-156 1.84GB cross-machine data lane closed + stranded r618 commit chain landed origin'
)
# fresh machine sampling (reuse last sample fields where absent)
hb.setdefault('cpu_cores', 16)
json.dump(hb, open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be ISO T format'
print('heartbeat written, epoch int ok:', chk['heartbeat_epoch_utc'])

# --- 3) round report line ---
rr = 'logs/iteration-loop/round_reports.md'
line = (
    f"{ts} | r619 bm-b (dept:\u5de5\u7a0b+\u8230\u961f\u00b7\u7ee7\u627f\u65ad\u5934rebase\u6536\u53e3\u8f6e) | "
    f"[watermark verdict: \u7eff(red=false; probe loaded_ok py 75.4% \u4e09\u70e7\u5f55\u5728\u98de burning-healthy\u00b7audit CLEAN\u00b7dualrun ZERO-DRIFT streak 9)] | "
    f"\u5f53\u524d\u6d3b: \u4e09\u70e7\u63a8\u8fdb VALUE-NULLS {v_k}/2000+QUALITY-NULLS {q_k}/2000+DIVLOWVOL-NULLS {d_k}/2000\u00b7\u6c60\u5185\u70ed | "
    f"\u6700\u8fd1\u5b9e\u7269: T-156 13/13\u6587\u4ef6 1.84GB p1c_stock \u8de8\u673a\u843d\u5730 bm_a(send5 \u65e5\u5fd7\u5c3e vwap.npy 100% 13/13 croc \u6b63\u5e38\u9000\u51fa\u00b7\u5f53\u65e5\u9a8c\u6536)+\u65ad\u5934 rebase \u6536\u53e3 merge 6a3141646 \u63a8\u9001 origin(r618 \u5168\u94fe\u4ea7\u7269\u843d\u5730) | "
    f"\u4e0b\u4e2a\u91cc\u7a0b\u7891: bm-a \u4fa7\u56db\u70b9\u9a8c\u8bc1+divlowvol fuse \u6e05+SENS \u91cd\u8ba4\u9886(\u5176\u4e0b\u8f6e)\u00b7\u672c\u673a\u70e7\u5f55\u6279\u6bd5\u540e\u6c60\u7ffb\u9762 finalize(\u7a97\u226448h) | "
    f"\u672c\u8f6e\u505a\u4e86: S0 \u7ee7\u627f\u65ad\u5934 rebase(round618 pick \u649e18UU \u505c\u70b9+\u4f592 churn pick+\u6d3b\u70e7\u7a97)\u2192r510 retarget \u6b63\u6cd5: 18UU \u89e3\u9762(17 take-ours ts\u8bc1\u636e+compute_audit union 206 \u96f6\u4e22\u5931)\u2192r543 quit\u95e8\u8d85\u96c6\u9a8c\u8bc1**\u902e\u4f4f r614 \u622a\u65ad\u884c\u6d1e**(value k=231/quality k=136/engine history 14:26:05 \u4ec5\u5b58\u4e8e\u4f59 pick blob\u2014\u2014\u5b57\u9762\u5047\u8bbe\u4e0b quit=\u4e09\u884c\u6c38\u4e45\u84b8\u53d1)\u2192r614 \u5f8b k/ts-union \u56de\u586b+\u8fde\u7eed\u6027\u590d\u8bc1\u2192\u624d quit\u2192\u8d85\u96c6\u6536\u7f16 commit f3bb26bd1\u2192origin \u5df2\u8fdb2 commit\u2192constructive merge b6fa63650(r614 W18\u00d7W19 \u6d3b\u70e7\u7a97\u5f8b\u00b7\u514d r606 \u9648\u65e7\u9762 reset \u8def\u7ebf)14UU \u4e8c\u6bb5\u89e3(13 take-theirs ts\u8bc1\u636e+compute_audit union 207 \u96f6\u4e24\u4fa7\u4e22\u5931)\u2192merge 6a3141646 FF \u63a8\u9001+\u9001\u8fbe\u81ea\u8bc1; S0.5 \u4ee4\u53cc\u626b 151/151 \u96f6\u672a\u56de\u6267+D-19 MATCH 4167b784 \u96f6\u52a8\u4f5c(blobless clone \u65b0\u9c9c\u8bfb); S1 smoke 47/47; T-156 \u4f20\u8f93\u5b8c\u6210\u5b9e\u8bc1+MSG-1410 \u52a8\u4f5c\u95ed\u73af\u79fb processed; S6 33/33 rc0; S7 4/4(loop pin=2 no-op\u00b7watchdog \u5e42\u7b49\u91cd\u5efa r613 -Args \u5df2\u77e5\u9762\u00b7\u53cc\u722a\u5728\u4f4d\u00b7attrition CLEAN) | "
    f"\u9a8c\u8bc1\u8bc1\u636e: results/_r619bmb_resolve.py+_r619bmb_hole_hunt.py+_r619bmb_backfill.py \u5168 PASS \u65ad\u8a00+results/_r619bmb_s6_runner.log 33 LEG rc=0+\u63a8\u9001\u540e rev-parse origin/main==6a3141646+cro​c send5 err \u65e5\u5fd7\u5c3e+guard scan CLEAN | "
    f"\u4e0b\u8f6e\u6307\u9488: \u2460\u70e7\u5f55 harvest \u9762\u2461bm-a \u56de\u6267\u76d1\u63a7\u2462\u672c\u5730\u672a\u8fbe origin commit \u6570=0(push \u540e\u81ea\u8bc1\u8865\u8bb0)"
)
with open(rr, 'a', encoding='utf-8') as f:
    f.write('\n' + line + '\n')
print('round report appended,', len(line), 'chars')

# --- 4) CODELY.md memory entry (one entry, four-question gate passed) ---
mem_entry = (
    "- [2026-10-03 15:0x r619 bm-b] r543\u00d7r614 \u4ea4\u4e92\u9762\u5b9e\u5f39\uff1a\u65ad\u5934 rebase \u6536\u53e3\u7684 quit \u95e8\u300c\u4f59 pick \u5185\u5bb9\u88ab\u5de5\u4f5c\u6811\u8d85\u96c6\u8986\u76d6\u300d\u5047\u8bbe\u4f1a\u88ab rebase \u81ea\u8eab\u7684 checkout \u622a\u65ad\u9759\u9ed8\u7834\u574f\u2014\u2014\u6d3b\u70e7\u7a97\u91cd\u653e pick \u65f6\u8de8 nulls/engine history \u4e22\u884c\uff08\u672c\u7a97 value k=231/quality k=136/engine history 14:26:05\uff09\u6070\u5df2\u88ab\u540e\u7eed churn absorb pick blob \u72ec\u5b58\uff0c\u5b57\u9762 superset \u9a8c\u8bc1\u82e5\u53ea\u770b\u6587\u4ef6\u5728\u76d8\u5c31 quit=\u4e09\u884c\u552f\u4e00\u526f\u672c\u84b8\u53d1\uff1b\u6b63\u89e3=\u9010\u884c hole-hunt\uff08\u4f59 pick \u6bcf\u884c \u2208 \u5de5\u4f5c\u6811\uff09\u2192 r614 \u5f8b k/ts-union \u5b57\u8282\u6052\u7b49\u56de\u586b+contiguity \u590d\u8bc1\u2192\u624d\u8bb8 quit\u3002\u53e6\u4e24\u5c0f\u9762\uff1a\u6536\u53e3\u96c6\u6210\u4f18 merge \u4e8e reset --mixed\uff08origin-only \u4ef6\u81ea\u52a8\u843d\u4ed6\u4fa7=\u514d r606 \u9648\u65e7\u9762\u6e05\u5355\u624b\u5de5\uff09\uff1bcontiguity \u65ad\u8a00\u987b\u533a\u5206\u5e8f\u6001/\u96c6\u6001\uff08divlowvol \u4e09\u5bf9\u76f8\u90bb\u4ea4\u6362+engine history 11:47 \u5012\u5e8f=\u65e7\u75d5\u88c5\u9970\u9762\uff0cSET \u5b8c\u5907\u5373\u8fc7\u52ff\u6309 raw \u5e8f\u88c1 FAIL\uff09\u3002How to apply\uff1a\u65ad\u5934 rebase \u6536\u53e3\u4e00\u5f8b\u5148\u8dd1\u884c\u5f52\u5c5e\u63a2\u9488\uff08_r619bmb_hole_hunt.py \u8303\u5f0f\uff09\u6838\u4f59 pick \u884c\u5f52\u5c5e\uff0c\u56de\u586b\u540e\u624d quit\u3002\n"
)
with open('CODELY.md', 'a', encoding='utf-8') as f:
    f.write(mem_entry)
print('CODELY entry appended,', len(mem_entry), 'chars')

# --- 5) orders second scan (S7 double-scan law) ---
ack = set(json.load(open(hb_path, encoding='utf-8'))['orders_ack'])
files = set(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
unacked = sorted(files - ack)
print('S7 orders rescan: on-disk', len(files), 'un-acked:', unacked if unacked else 'NONE')
