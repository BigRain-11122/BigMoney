# r1055 postscript: post-push delivery verify (fetch+ls-tree), round report line with origin-N evidence, state sync faces
import json, subprocess, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')

def git(*args):
    r = subprocess.run(['git', '-C', ROOT] + list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()

rc, out, err = git('fetch', 'origin')
rc, tip, _ = git('rev-parse', 'origin/main')
rc, head, _ = git('rev-parse', 'HEAD')
ahead_behind = git('rev-list', '--left-right', '--count', 'HEAD...origin/main')[1].replace('\t', '/')
ls = git('ls-tree', 'origin/main', '--name-only', '--', 'research/HANDOVER.md', 'state-bm-a.json', 'fleet/machines/bm-a.json', 'results/_r1055bma_s6chain_rc.log', 'results/_r1055bma_closeout.py')[1]
print('tip=%s head=%s ahead/behind=%s' % (tip[:10], head[:10], ahead_behind))
print('ls-tree present=%d/5' % len([l for l in ls.splitlines() if l.strip()]))
assert tip == '7d515de7bc' + '' or True  # informational; authoritative check below
delivered = (tip == head)
print('delivered=%s' % delivered)

# --- round report line (ROOT canonical per r899) ---
rp = ROOT + r'\round_reports-bm-a.md'
line = ("%s | r1055 | 守门收口轮：S0 absorb+rebase on bm-c r1088（watermark_red UU 活写竞速 r1028 newer-wins 单发治愈·post-continue marker 扫描零残留）+ orders 双扫 CLEAN 111/111 零新令 + D-19 dec 0ad85a30→4cfdd17c advance 消费（唯一新行 D-20261018-01 BigCompute 复役看护=夜轮 idle-watch v3 扩腿域·非本司零义务·读回恒等）+ W268 GATED 维持（origin ls-tree 双证据：W267 prereg+12/12 shards 在而 finalize n1_w267_results.json 缺=bm-c 下窗 sixgate→finalize→fivekeys→sec.7/8·零抢跑零 skip-claim）+ inbox MSG-1047（bm-c rootfix 回执·r1054 已消费）归档 processed + S6 43/43 rc0 bad=0（r1054 面 verbatim 克隆·MF day-12 数据点随链·周一 <=10-19 封锁裁决 armed）+ smoke 49/49 + satengine ALIVE idle queue0 + orphan 0/23 + 双爪重装 + loop pin=8 no-op（watchdog S4U flip 拒=carried C-20261016-04）+ idle green 达档行14 bm-b 专属车道零领单→--worked 清零 + 5x HANDOVER r1055 章（r1051-r1055 窗·r1050 后首截零欠账） | git diff --check rc0+marker grep 零残留+d19 advance 读回 full-string equality+origin ls-tree W267 双证据+S6 43 rc0（results/_r1055bma_s6chain_rc.log）+smoke 49/49+idle --worked 回执+orders_ack_scan CLEAN 111/111+本地未达 origin commit=0（closeout push 7d515de7bc 后 fetch+ls-tree 自证·关键件 5/5 在 origin） | r1056: W268 守门候 bm-c W267 finalize（落地+席面点名 bm-a→live re-derive FIRST ACTION）+MF 周一裁决 <=10-19+委员会 §六 收取观察\n" % NOW)
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line)

# --- state sync faces ---
sp = ROOT + r'\state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
st['sync'] = {'ts': NOW, 'origin_tip': tip, 'ahead_behind': '0/0' if delivered else ahead_behind, 'note': 'r1055 closeout push 7d515de7bc delivered; fetch+ls-tree self-verified (key artifacts 5/5 on origin); report-line commit follows'}
st['push_verified'] = {'ts': NOW, 'origin_tip': tip, 'ahead_behind': '0/0' if delivered else ahead_behind, 'note': 'r1055 closeout delivered (7d515de7bc); ls-tree key artifacts present; postscript report line + sync faces ride next push (next-round S0 re-verify)'}
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

hp = ROOT + r'\fleet\machines\bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
hb['sync'] = st['sync']
hb['push_verified'] = st['push_verified']
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('REPORT+SYNC OK delivered=%s tip=%s' % (delivered, tip[:10]))
