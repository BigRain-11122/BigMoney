# r582 bm-b wrap: state, heartbeat, round report, CODELY line
import json, time, datetime, subprocess, os

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

import psutil
ram_free = round(psutil.virtual_memory().available / 2**30, 1)
cpu_pct = psutil.cpu_percent(interval=2)

gpu_free = 2.2
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=20)
    if r.returncode == 0 and r.stdout.strip():
        gpu_free = round(int(float(r.stdout.strip().splitlines()[0])) / 1024, 1)
except Exception:
    pass

# 1. state.json (bm-b uses state.json per S5)
st = json.load(open('state.json', encoding='utf-8'))
st['round_no'] = 582
st['note'] = ("r582: W95 FINALIZE one-pass landed (prev 571,348 W94 bm-a r582 unblocked + 2,200 = 573,548, "
              "K=206,920, K-lift +0.0000, sec5 4/4 PASS (dmu 0.0050/dsigma -1.30%/A-p95 diff 0.0184/K-lift), "
              "sec7/8 backfilled, selftest PASS + parity PASS) -> unblocks W96 bm-a finalize; "
              "W97 12/12 shard products verified (2000A+200B, machine=bm-b) + ridden to origin (r310 precondition met, finalize pending W96); "
              "S0 surgical align e7ab861fa->5125dc25d (live-writer faces present, rebase banned r532, deletion-set empty); "
              "S6 33 legs green holiday no-op (dualrun streak 26/3, paper block skipped honest - National Day holiday no new bar); "
              "S7 catch: LoopWatchdog missing -> re-registered 16:13; orders 143/143 double-scan EMPTY; D-19 honest skip (bm-b no group tree); "
              "next: W97 finalize pending W96 bm-a landing")
st['last_round_at'] = epoch
st['last_round_ts'] = iso
st['ts'] = iso
st['updated'] = 'r582 bm-b: W95 finalize landed + W97 products delivered + S6 all-green'
st['updated_at'] = iso
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json -> round 582')

# 2. heartbeat
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['current_task'] = ("W95 finalize landed (chain 573,548); W97 12/12 products delivered to origin, "
                      "finalize pending W96 bm-a; engine idle queue 0")
hb['cpu_cores'] = psutil.cpu_count(logical=True)
hb['free_ram_gb'] = ram_free
hb['idle_ram_gb'] = ram_free
hb['ram_free_gb'] = ram_free
hb['gpu_free_vram_gb'] = gpu_free
hb['gpu_idle_vram_gb'] = gpu_free
hb['gpu_free_vram_mb'] = int(gpu_free * 1024)
hb['gpu_idle_vram_mb'] = int(gpu_free * 1024)
hb['cpu_util_pct'] = cpu_pct
hb['round_no'] = 582
hb['round_no_label'] = 'r582'
hb['verdict'] = ("healthy-idle-science-closed (W95 finalize one-pass chain-linear 573,548; W97 products at origin "
                 "12/12 finalize-pending W96; supply line relay W98 bm-a burning; holiday no new bar)")
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
d2 = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(d2['heartbeat_epoch_utc'], int)
print('heartbeat -> r582, epoch int verified, ram_free=%s gpu_free=%s cpu=%s' % (ram_free, gpu_free, cpu_pct))

# 3. round report line (append bytes, UTF-8)
rr_line = (
"%s | r582 bm-b | dept:\u7814\u7a76/\u5de5\u7a0b | [watermark verdict: \u7eff\u2014\u2014py \u4f4e\u4f46\u5408\u6cd5 idle \u767d\u540d\u5355\u9762\uff08\u56fd\u5e86\u5047\u671f\u65e0\u65b0 bar+\u677f\u65e0 unclaimed \u7968+\u5f15\u64ce\u961f\u5217 0\uff08W97 \u70e7\u6bd5 12/12\uff09\uff09] | "
"\u5f53\u524d\u6d3b=W95/W97 \u5f15\u64ce\u6ce2\u6536\u53e3\u7ebf\uff1b\u6700\u8fd1\u5b9e\u7269=results/perpetual_faces/n1_w95_results.json\uff0816:0x finalize \u843d\u8d26\u00b7\u94fe 573,548\uff09+W97 12/12 \u5206\u7247\u4ea7\u54c1\u63a8 origin\uff1b\u4e0b\u4e2a\u91cc\u7a0b\u7891=W96 bm-a finalize \u843d\u8d26\u540e W97 finalize\uff08\u672c\u673a\u00b7\u94fe\u5e8f\u7a97 \u226448h\uff09 | "
"\u672c\u8f6e\u4e3b\u4ea7\u51fa\uff08\u5b9e\u7269\uff09\uff1a(1) **W95 FINALIZE one-pass \u843d\u8d26**\uff08prev=571,348=W94 bm-a r582 \u89e3\u9501\u00b7+2,200=**573,548**\u00b7K=206,920\u00b7w95-only mu=\u22120.0977067 \u03c3=0.2453123\u00b7merged mu=\u22120.0928112\u00b7K-lift **+0.0000**\u00b7se_mu \u94fe 0.000550\u2192\u2026\u21920.000538\u00b7\u00a75 \u56db\u95e8\u5168\u8fc7\uff08\u0394mu 0.0050<0.02/\u03c3 \u22121.30%<\u00b110%/A p95 \u5dee 0.0184<0.05/K-lift \u95e8\u5185\uff09\u00b7\u00a77/\u00a78 \u673a\u68b0\u56de\u586b\uff0810+/4\u2212 \u5916\u79d1\uff09+selftest PASS+parity PASS\uff09\u2192**\u89e3\u9501 W96 bm-a finalize**\uff0812/12 \u4ea7\u54c1\u5df2\u5728 origin\uff09"
"(2) **W97 12/12 \u5206\u7247\u4ea7\u54c1\u9a8c\u6bd5\u63a8 origin**\uff082000 A+200 B=2,200\u00b7audit.machine=bm-b\u00b7r310 \u5b8c\u5907\u6027\u95e8=W97 finalize \u524d\u7f6e\u5c31\u7eea\uff09"
"(3) S0 \u5916\u79d1\u5bf9\u9f50\uff08e7ab861fa\u21925125dc25d \u4e09 commit \u8ffd\u5e73\u00b7\u6d3b\u5199\u9762\u5728\u573a\u7981 rebase r532 \u5f8b\u00b7reset+split-face checkout\u00b7\u5220\u96c6\u7a7f\u65ad\u8a00\uff09"
"(4) S7 \u5b9e\u6548\u6355\u83b7\uff1aBigmoney-LoopWatchdog \u67e5\u65e0\u2192\u8fdb\u7a0b\u5185\u91cd\u5efa\uff0816:13 \u9996\u8df3\uff09 | "
"smoke 47/47\uff1bS6 33 \u817f\u5168\u7eff\u5047\u671f no-op\uff08dualrun streak 26/3 \u96f6\u6f02\u79fb\u00b7paper \u5757\u8bda\u5b9e\u8df3\u8fc7=\u5047\u671f\u65e0\u65b0 bar\uff09\uff1bD-19 bm-b \u65e0\u96c6\u56e2\u6811\u8bda\u5b9e\u8df3\u8fc7\uff08r481 \u7279\u4f8b\uff09\uff1borders 143/143 \u53cc\u626b EMPTY\uff1battrition CLEAN\uff1b\u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08\u63a8\u9001\u540e fetch \u81ea\u8bc1\uff09 | "
"\u4e0b\u8f6e\uff1a\u5019 W96 bm-a finalize\u2192**W97 finalize\uff08\u672c\u673a\u6ce2\u00b7\u4ea7\u54c1\u5df2 12/12 \u5728 origin\uff09**\uff1bW98 bm-a \u70e7\u5f55\u8fdb\u5ea6\u76ef\u67e5\n"
)
with open('logs/iteration-loop/round_reports.md', 'ab') as f:
    f.write(rr_line.encode('utf-8'))
print('round report appended')

# 4. CODELY one-liner (append at end, LF)
cl_line = (
"- [2026-10-02 16:1x r582 bm-b] \u901a\u7528 D-19 \u5de5\u5177\u673a\u9762\u5047\u8bbe\u5751\uff08Tools/d19_check.py \u9996\u72af\u5b9e\u5f39\uff09\uff1ageneric \u5de5\u5177\u6309 state-<id>.json \u6a21\u5f0f\u786c\u7f16\u7801\u8bfb state-bm-b.json\u2014\u2014bm-b \u662f state.json \u7279\u4f8b\uff08S5 \u5f8b\uff09\u2192FileNotFoundError \u5d29\uff1bbm-b \u4f1a\u8bdd\u4e00\u5f8b\u7528 Tools/_r579bmb_d19.py \u53d8\u4f53\uff08\u7ec4\u4ed3\u63a2\u6d4b fallback+\u8bda\u5b9e skip\uff09\u3002How to apply\uff1abm-b \u8f6e D-19 \u6b65\u7981\u7528 generic d19_check.py\uff0c\u76f4\u63a5 _r579bmb_d19.py\u3002\n"
)
b = open('CODELY.md', 'rb').read()
assert b.count(b'\r\n') == 0
if b and not b.endswith(b'\n'):
    b += b'\n'
b += cl_line.encode('utf-8')
open('CODELY.md', 'wb').write(b)
print('CODELY appended, new size', len(b))
