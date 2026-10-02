# r586 bm-b W103 finalize closeout: prereg S7/S8 mechanical backfill (bytes-safe) +
# selftest re-run (r307 same-round law) + state/heartbeat/report update + commit + push
import subprocess, sys, os, json, time, datetime, psutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
CREATE = 0x08000000

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', creationflags=CREATE)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd[:4])))
        print((r.stdout or '')[-300:]); print((r.stderr or '')[-300:])
        sys.exit(1)
    return r

# 1. prereg S7/S8 backfill (bytes-level, r530 law)
P = 'research/PERPETUAL_N1_W103_PREREG.md'
raw = open(P, 'rb').read()
ph = ("## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010\u8dd1\u524d\u5fc5\u987b\u4e3a\u7a7a\u2014\u2014\u5360\u4f4d\u7eaa\u5f8b\uff1a\u5199\u6570\u5b57\u5373\u9020\u5047\u3011\n"
      "\n- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff1b\u4e24\u6001\u817f\u65ad\u8a00\u5728\u573a=r307 \u5f8b\uff09\n"
      "\n## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010\u5fc5\u586b\u00b7\u7ec8 7-T\u3011\n"
      "\n- \uff08finalize \u843d\u8d26\u540e\u673a\u68b0\u56de\u586b\uff09\n").encode('utf-8')
ph_crlf = ph.replace(b'\n', b'\r\n')
if ph in raw:
    eol = b'\n'; old = ph
elif ph_crlf in raw:
    eol = b'\r\n'; old = ph_crlf
else:
    print('PLACEHOLDER NOT FOUND'); sys.exit(1)

NB = ("\n" if eol == b'\n' else "\r\n")
S7 = ("## \u00a77 \u8dd1\u540e\u5b9e\u8bc1\u3002\u3010r584 \u51bb\u7ed3\u5360\u4f4d\u00b7r586 bm-b finalize \u6536\u53e3\u673a\u68b0\u56de\u586b\u3011")
L = [
 "- 12/12 \u5206\u7247 bm-b \u5f15\u64ce\u70e7\u6bd5\uff08r584 \u51bb\u7ed3 fbbde996f \u540e\u5f15\u64ce\u81ea\u71c3\u00b7r584/r585 \u5206\u6279\u4ea4\u4ed8 origin\u00b7finalize \u524d ls-tree 12/12 \u5b8c\u5907 r310 \u5f8b\uff09\uff1bfinalize one-pass\uff08r538 \u5f8b\u00b7\u9996\u8dd1\u7981\u91cd\u8dd1\u00b7r586 \u9996\u8dd1=\u552f\u4e00\u4e00\u8dd1\uff09\u3002",
 "- ledger\uff1aprev_total 588,948\uff08W102 bm-c r378 \u843d\u8d26\u89e3\u9501\u00b7\u94fe\u5e8f W100 584,548 bm-b\u2192W101 586,748 bm-a\u2192W102 588,948 bm-c\uff09+ batch_trials 2,200 = **591,148**\uff1bvoids_applied=LOWAMP-P1/P2\u3002",
 "- w103-only\uff1an=2,200\u00b7mu=\u22120.09905036363636398\u00b7sigma=0.2557854110170886\uff1bmerged\uff1aK=224,520\u00b7mu=\u22120.09289408382326719\u00b7sigma=0.24490354801693814\uff1bmu_delta_w103_vs_w102ext=\u22120.010323\u3002",
 "- skill_line_v2 @n_eff_held 588,948\uff1a1.169\u2192**1.1695**\uff08K-lift delta +0.0005\u2265\u22120.02 \u95e8\u5185\u00b7\u6b63\u8d1f\u4ea4\u66ff\u5982\u5b9e\u62a5\u3014W100 \u22120.0005\u2192W101 \u22120.0003\u2192W102 +0.0001\u2192W103 +0.0005\u3015\uff09\uff1bse_mu @K224,520=0.000517\uff08\u6536\u7a84\u94fe\u6301\u7eed\uff09\uff1bcanon_flip \u672a\u6267\u884c\uff08\u6cbb\u7406\u63d0\u6848\u9762\u00b7K2200 \u540c\u6cd5\uff09\u3002",
 "- \u00a75 \u9884\u6d4b\u56db\u95e8\u5168\u8fc7\uff08\u951a\u6eda\u52a8\u5f8b\u5408\u6cd5\u8de8\u952e\u00b7\u51bb\u7ed3\u951a=W98 merged \u22120.09294630058074185\uff09\uff1a|\u0394mu|=0.0061<0.02\uff08W103-only \u22120.09905036\u00b7\u5355\u6ce2\u504f\u79bb\u9762\u5982\u5b9e\u62a5\u00b7\u95e8\u5185\uff09\uff1b\u03c3 \u53d8\u5316 \u22120.01%<\u00b110%\uff08\u951a 0.24493002\u00b7\u672c\u6ce2 merged 0.24490355\uff09\uff1bA \u6863 p95 \u5dee 0.0211<0.05\uff08\u951a 0.3131\u00b7\u672c\u6ce2 0.3342\uff09\uff1bK-lift +0.0005\u2265\u22120.02\u3002\u4ea7\u7269 results/perpetual_faces/n1_w103_results.json\uff08\u9876\u5c42 evidence_cutoff=2026-09-22\u00b7audit.machine=bm-b\u00b7finalize_only=True\u00b7shards_consumed 12\uff09\u3002",
 "",
]
S8 = ("## \u00a78 \u6279\u540e\u590d\u76d8\u3002\u3010\u5fc5\u586b\u00b7\u7ec8 7-T\u3011")
L8 = [
 "- \u5168\u94fe\u4ea7\u54c1\u6d41\u5065\u5eb7\uff1aW103 \u70e7\u5f55\uff08bm-b \u5f15\u64ce 12/12\u00b7r584/r585 \u4ea4\u4ed8\uff09\u2192finalize\uff08r586 \u9996\u8dd1\u4e00\u8fc7\uff09\u2192\u94fe\u5934 591,148 \u843d\u8d26\u00b7K=224,520\uff1b\u4e0b\u6e38 W104 bm-a finalize \u968f\u5373\u89e3\u5c01\u3002",
 "- \u8bda\u5b9e\u6ce8\u8bb0\uff1a\u00a75 \u51bb\u7ed3\u951a=W98\uff08\u8d77\u8349\u7a97\u6700\u65b0\u5df2\u843d\u8d26 finalize\uff09\u00b7\u6536\u53e3\u7a97 W99..W102 \u56db\u6ce2\u5df2\u76f8\u7ee7\u843d\u8d26=\u951a\u6eda\u52a8\u5f8b\u5408\u6cd5\u8de8\u952e\uff08r576\uff09\uff1b\u56db\u95e8\u5728 W98 \u951a\u4e0a\u5168\u8fc7\u3002",
 "",
]
new = (S7 + NB + NB.join(L) + NB + S8 + NB + NB.join(L8)).encode('utf-8')
raw2 = raw.replace(old, new)
assert raw2 != raw and raw2.count(new) == 1
open(P, 'wb').write(raw2)
print('S7/S8 backfilled (eol=%r, %d bytes written)' % (eol, len(new)))

# 2. selftest re-run post-backfill (r307 same-round law, default-wave per r522)
r = run(['python', 'scripts/perpetual_faces_n1.py', 'selftest'], check=False)
tail = (r.stdout or '').strip().splitlines()
print('n1 selftest rc=%s | %s' % (r.returncode, tail[-1][:120] if tail else ''))
if r.returncode != 0:
    sys.exit(1)
r = run(['python', 'scripts/perpetual_faces.py', 'selftest'], check=False)
tail = (r.stdout or '').strip().splitlines()
print('pf selftest rc=%s | %s' % (r.returncode, tail[-1][:80] if tail else ''))
if r.returncode != 0:
    sys.exit(1)

# 3. state/heartbeat/report addendum
now_iso = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
s = json.load(open('state.json', encoding='utf-8'))
s["note"] = ("r586: W103 FINALIZE one-pass landed (prev 588,948 W102 bm-c landed + 2,200 = 591,148 chain-linear, K=224,520, "
             "merged mu -0.09289408 sigma 0.24490355, skill_line 1.169->1.1695 K-lift +0.0005, S5 four gates ALL PASS on "
             "W98 freeze anchor, voids LOWAMP-P1/P2; downstream W104 bm-a finalize UNBLOCKED) + W106 burn products 12/12 "
             "delivered to origin (2,200 backtests, 96th wave) + S0 pure-FF surgical + W14 governance-park verified r483 "
             "zero action + S6 33 legs rc0 ZERO-DRIFT 30/3 + WM py_low_board_clear legal idle + S7 5/5")
s["last_round_at"] = epoch
s["last_round_ts"] = now_iso
s["ts"] = now_iso
s["updated"] = "r586 bm-b: W103 FINALIZE landed (591,148) + W106 products delivered + S6/S7 green"
s["updated_at"] = now_iso
json.dump(s, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
vm = psutil.virtual_memory()
h["last_seen"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["current_task"] = "idle: W103 finalized (591,148) + W106 delivered; next bm-b finalize = W106 (after W104 bm-a + W105 bm-c)"
h["free_ram_gb"] = round(vm.available / 1e9, 1)
h["cpu_util_pct"] = psutil.cpu_percent(interval=0.5)
h["round_no"] = 586
h["verdict"] = "W103 FINALIZE one-pass landed 591,148 K=224,520 (S5 4/4 on W98 anchor); W106 12/12 delivered; W104 bm-a unblocked"
assert isinstance(h.get("orders_ack"), list) and len(h["orders_ack"]) == 143
json.dump(h, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
loaded = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(loaded["heartbeat_epoch_utc"], int)
print('state/heartbeat updated (epoch=%d)' % loaded["heartbeat_epoch_utc"])

rp = 'logs/iteration-loop/round_reports.md'
raw3 = open(rp, 'rb').read()
eolr = b'\r\n' if raw3.endswith(b'\r\n') else b'\n'
line = ("{ts} | r586 finalize addendum | WM=py_low_board_clear | 当前活=W103 FINALIZE one-pass 落账（本机第 35 自有波收口）| "
        "最近实物=results/perpetual_faces/n1_w103_results.json（591,148 落账 18:1x）+ n1_w106/ 12 分片交付 | "
        "下个里程碑=W104 bm-a finalize 落地后 W105 bm-c→W106 bm-b 链序推进（~24h 窗）| 做了什么=W101 bm-a+W102 bm-c 双上游落账解封核验"
        "（origin 时序面 r518 律）→finalize 前置 ls-tree 12/12 完备断言（r310 律）→finalize one-pass（r538 首跑唯一一跑·prev 588,948+2,200=591,148 "
        "链性验）→§5 四门全过（|Δmu| 0.0061<0.02·σ −0.01%<±10%·A p95 差 0.0211<0.05·K-lift +0.0005）→§7/§8 机械回填（bytes 面）→n1 缺省波 selftest "
        "复跑 PASS+r2 pf 9/9（r307 同轮律） | 验证=finalize stdout 机出数+results JSON 顶层键+n1/pf selftest 双绿 | 本地未达 origin commit 数=0（推送后复核）| "
        "下轮指针=W104 bm-a finalize 落地监测+W106 finalize 待 W104/W105 链序·W107 bm-a 在飞·W109 bm-b 轮转波位").format(ts=now_iso)
with open(rp, 'ab') as f:
    f.write(line.encode('utf-8') + eolr)
print('report addendum appended')

# 4. commit + push
PAYLOAD = [
    'research/PERPETUAL_N1_W103_PREREG.md', 'results/perpetual_faces/n1_w103_results.json',
    'state.json', 'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md',
    'results/p1d_gates.json', 'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/history_bm-b.jsonl', 'results/saturation_engine/ledger_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
    'results/_r586bmb_push.py', 'results/_r586bmb_surgical_push.py', 'results/_r586bmb_w103_finalize_close.py',
]
run(['git', 'add', '--'] + PAYLOAD)
MSG = ("round 586 bm-b: W103 FINALIZE landed one-pass (chain head 588,948 W102 bm-c landed + 2,200 = 591,148, "
       "K=224,520; w103-only mu=-0.09905036 sigma=0.25578541; merged mu=-0.09289408 sigma=0.24490355; "
       "skill_line_v2 @n_eff 588,948: 1.169 -> 1.1695, K-lift delta +0.0005; voids_applied LOWAMP-P1/P2; "
       "S5 four gates ALL PASS on the W98 freeze anchor; prereg S7/S8 mechanical backfill r307 same-round law; "
       "n1 default-wave selftest PASS + pf 9/9; downstream W104 bm-a finalize UNBLOCKED) "
       "[via bm-b r586]")
mp = r'..\.codely-cli\scratch\r586bmb_msg2.txt'
os.makedirs(os.path.dirname(mp), exist_ok=True)
open(mp, 'w', encoding='utf-8', newline='\n').write(MSG)
r = run(['git', 'commit', '-F', mp], check=False)
print('commit rc=', r.returncode, (r.stdout or r.stderr)[:200])
if r.returncode:
    sys.exit(1)
r = run(['git', 'push'], check=False)
print('push rc=', r.returncode)
print(((r.stdout or '') + (r.stderr or ''))[:300])
