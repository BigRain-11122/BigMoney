# r947 bm-b disaster-recovery closeout: state.json + round report line.
# Deferred to r948 (faces mid-restore): heartbeat, CODELY.md line, smoke, S6, orders scan.
import json, datetime, subprocess

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
R = 'r947'

LINE = (NOW + ' | ' + R + ' bm-b | WM-VERDICT: disaster-recovery round (git-loss r834-family recurrence; '
    'watermark_red.json face lost with results/ intact but probe skipped-honest; satengine probe in shell) | '
    '当前活: P0 git-loss 灾修唯一使命 (S1-law analog) | 最近实物: .git 精简重建 (init+fetch --depth=1 --filter=blob:none '
    'origin tip ebf8a644 = r946 closeout + bm-a r997 全在 = 零 origin 损失) + 恢复 worker 分离续跑 '
    'results/_r947bmb_restore_worker.ps1 + forensics results/_r947bmb_gitloss_forensics.json + '
    'fleet/inbox/MSG-20261014-2015-bmb.md (对等机 bundle 后援请求) | 下个里程碑: r948 恢复验收 (faces+heartbeat+smoke 49/49+'
    'claws+orders 双扫+unshallow, 窗<=10min 轮距; bundle 后援=bm-a/bm-c 已被 MSG 请求) | did: S0-1 锚定 bm-b (state.json '
    'machine_id 实证, round 947); 19:32 首 r947 已被 25min 击杀 (灾修克隆遗留 0 字节停滞已击杀取证); 灾窗 19:26-20:03; '
    'treasure_guard restore rc1 (登记簿在灭失面, r834 正例放行 git 再生); git init -b main + lean fetch + reset --mixed '
    '+ faces checkout 惰性微包推进中 (38+ pack 实证小包通大包滞); 定向本产物 commit+push; smoke/S6/心跳/CODELY/订单扫描 '
    '诚实缓办 (面未齐勿跑); 根因未定谳=转录取证 r948 (被杀会话 .jsonl + USN journal; 集团仓镜像说已证伪 origin/main:quant '
    '无 bigmoney 条目) | evidence: forensics JSON + worker log + origin tip ebf8a644 + 38 lazy micro-packs | '
    'next: r948 恢复验收+补账 (heartbeat epoch-int+T 时钟, CODELY 记忆行, claws, S0.5 双扫含 SLI 回执, unshallow) | '
    '孤儿面=0 (探测在 shell, 杀清单红线未触) | 记账预算: 3/5 (state+report+forensics/MSG 落地; 灾修轮豁免面) | '
    '产品积分: 2 (可跑灾修实物: .git 重建+worker+forensics) | 本地未达 origin commit 数=见 push 自证行 | [r947 bm-b]')

sp = ROOT + r'\state.json'
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 948
st['round'] = 947
st['round_no_label'] = R
for k in ('last_round_at', 'last_round_ts', 'last_seen', 'updated', 'updated_at', 'ts', 'clock_read'):
    st[k] = NOW
st['last_action'] = R + ': git-loss disaster recovery (lean .git rebuild ebf8a644 + restore worker detached + forensics/MSG)'
st['last_action_at'] = NOW
st['current'] = st['current_task'] = st['now_active'] = (
    R + ': disaster-recovery round; faces restore in flight via detached worker (fleet/docs/firm/engine/knowledge/'
    'legacy/live + root trio); heartbeat+CODELY+smoke deferred r948')
st['did'] = (R + ': S0-1 anchor; killed stalled 0-byte clone (first r947 attempt estate); treasure_guard rc1; '
    'git init -b main + fetch --depth=1 --filter=blob:none (origin ebf8a644, zero origin loss) + reset --mixed + '
    'faces lazy-checkout in flight; this product commit+push; honest skips: smoke/S6/orders/heartbeat (faces incomplete)')
st['next'] = (R + ' next(r948): 1) verify worker log+faces complete 2) if stalled: bundle fallback per MSG-20261014-2015 '
    '(bm-a/bm-c git bundle --all + taildrop) 3) post-restore: heartbeat(epoch int/T clock)+CODELY line+smoke 49/49+claws '
    'x2+orders full ack diff (incl killed-round ORD delta b202b9510 + SLI dispatch leftover: fleet/inbox reply to bm-a)'
    '+unshallow attempt+S6 chain+state r948 bump 4) root-cause forensics: killed session .jsonl transcript + USN window + '
    'sentinel cross-check 5) standing: no rm on repo faces; group-tree zero-touch (already lawed)')
st['next_milestone'] = ('repo fully restored + smoke 49/49 + unshallow (self-heal window <=24h; bundle fallback armed via '
    'MSG to bm-a/bm-c)')
st['verdict'] = ('AMBER->GREEN trajectory: P0 git-loss discovered+contained; .git rebuilt lean (shallow+promisor, unshallow '
    'pending); faces restore in flight; zero origin-side loss (r946+r997 on ebf8a644); root cause unknown (r834-family), '
    'transcript forensics r948')
st['note'] = (R + ': git-loss recurrence window 19:26-20:03; destroyed=.git+8dirs+root trio (r834 signature minus data); '
    'old r836 clone dir = hollow (0 objects, not an asset); group-repo mirror theory disproven (origin/main:quant clean); '
    'treasure_guard rc1; heartbeat NOT written this round (fleet face mid-restore, checkout would clobber - deferred r948 '
    'BY DESIGN not omission)')
st['latest_artifact'] = st['last_artifact'] = ('results/_r947bmb_gitloss_forensics.json + results/_r947bmb_restore_worker.ps1'
    ' (+log) + fleet/inbox/MSG-20261014-2015-bmb.md')
st['orphan_face'] = 0
st['orphan_faces'] = 0
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state written r947')

with open(ROOT + r'\logs\iteration-loop\round_reports.md', 'a', encoding='utf-8') as f:
    f.write(LINE + '\n')
print('report line appended')

r = subprocess.run(['python', 'Tools/idle_trigger.py', '--worked'], capture_output=True, cwd=ROOT)
print('idle --worked rc=', r.returncode)
