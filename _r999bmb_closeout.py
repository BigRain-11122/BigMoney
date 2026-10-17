import subprocess, json, os, sys, time, re
from datetime import datetime, timezone, timedelta

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)
os.environ['PYTHONIOENCODING'] = 'utf-8'

def sh(*args):
    r = subprocess.run(list(args), capture_output=True)
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

now = datetime.now(timezone(timedelta(hours=8)))
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
SHA = 'b15d5e6999ef4eeb844d49ff22a0edce8928a41f'

# ---------- 1) O-0348 receipt section ----------
p = r'fleet\orders\O-20261018-0348-bm-a.md'
txt = open(p, encoding='utf-8').read()
receipt = (
    "\n### 2026-10-18 05:5x · bm-b r999 回执（O-0348 §1 同轮执行·CEO 令即时律）\n\n"
    "- git status 盘点=48 行（r998 遗产 staged 面 40 件含 MSG-0216 正身 + 守护进程活跃面 13 件未提交）。\n"
    "- commit+push sha=**b15d5e6999ef4eeb844d49ff22a0edce8928a41f**（fetch+rev-parse 双验 DELIVERED·base=origin tip be7d2f90a5 非陈旧基座）。\n"
    "- 路径实录：前任 r999 会话（03:1x 被杀）已 staged 全套遗产面；本会话接手时 pre-commit 爪拦 results/post_review.jsonl:11896 diff3 基座段 ||||||| 标记行（rebase 解冲突残留）→ 手术只删标记行保 13 行唯一账行 → 爪过提交。push 首撞 pre-push 爪（陈旧基座会 revert bm-a r1046 新增 56 件）→ 正法重放：rebase sequencer 死循环（r1032 判例复发·--continue 拒收零 UU）→ quit+温索引树手术重放 commit 于新 tip → 爪过推送。\n"
    "- 三枚 stash（r999-daemon-faces/r999-midround-unstashed/r999-s0-autostash 死会话 03:19 遗产）全保留待下轮内容级回收：midround 含 CODELY.md 79 行重组+B.7 登记行+O-0137 ✅ 翻面 7 行未落地面；s0-autostash 含 post_review 50 行+state 面。零丢弃零丢失。\n"
    "- 附加完成：backlog 行13 解锁单 done（本行同 commit）+ orders_ack 收录本令。\n"
)
if 'bm-b r999 回执' not in txt:
    open(p, 'a', encoding='utf-8', newline='').write(receipt)
    print('receipt appended')

# ---------- 2) backlog row 13 done ----------
p = r'fleet\backlog.md'
lines = open(p, encoding='utf-8').read().splitlines()
hit = False
for i, l in enumerate(lines):
    if l.startswith('13. ') and 'r998 git 面收口解锁单' in l and 'done@' not in l:
        lines[i] = l.rstrip() + (' → claimed@bm-b@2026-10-18T05:34:00+08:00 → done@bm-b@2026-10-18T05:55:00+08:00+BigMoney b15d5e699（O-0348 §1 同轮收口：r998 遗产 40 件含 MSG-0216 正身上链 DELIVERED；post_review 标记行手术+树手术重放正法·三 stash 保全待下轮回收）')
        hit = True
open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('backlog13 done', hit)

# ---------- 3) state.json ----------
p = 'state.json'
st = json.load(open(p, encoding='utf-8'))
st['round_no'] = 999
st['round'] = 999
st['round_no_label'] = 'r999'
st['clock_read'] = ts
st['last_round_at'] = ts
st['last_round_ts'] = ts
st['last_seen'] = ts
st['ts'] = ts
st['updated'] = ts
st['updated_at'] = ts
st['now_active'] = 'r999 closing'
st['current'] = 'r999: O-0348 r998-estate git-face closeout (P0) + orphan rebase absorb + 3-stash preserve'
st['current_task'] = 'r999: closeout (state/heartbeat/round-report/push)'
st['task'] = st['current_task']
st['did'] = (
    "r999: (a) P0 O-20261018-0348-bm-a §1 executed same-round: dead-r999-session staged estate (40 files incl MSG-0216 receipt body + r999 voicegen audition products MSG-0319/3 audition mp3s) landed on origin via b15d5e699 (DELIVERED fetch-verified); post_review.jsonl:11896 diff3 base-section marker line surgically removed keeping 13 unique ledger rows (claw had blocked); push first attempt blocked by pre-push claw (stale-base would revert bm-a r1046 56 files) = claw correct; rebase sequencer deadloop (r1032 recurrence, --continue refused with zero UU) -> r1032 law bypass: rebase --quit + temp-index tree surgery replay on fresh tip be7d2f90a5 -> claw passed -> ff push; local main healed same tree zero-worktree-change. (b) orphan rebase-merge (external 05:32-tick pull died mid-S0, gits self-dead 20min/13min hang) absorbed per dead-predecessor estate law. (c) 3 stashes ALL preserved (daemon faces live-wins skip + midround CODELY.md 79-line reorg/B.7/O-0137 7-line pending + dead-session s0-autostash 50 ledger rows) - zero drop zero loss, next-round content-level recovery. (d) backlog row13 unlock ticket done@b15d5e699. (e) smoke/S6 deferred honestly (bm-a r1046 ran S6 43/43 rc0 + smoke 49/49 at 05:2x group-face; bm-b no new data faces Sunday; next bm-b full round runs chain). (f) D-19 deferred citing bm-a r1046 fresh probe (dual-FALSE zero-delta 05:2x)."
)
st['last_action'] = 'r999: O-0348 estate landed b15d5e699 + orphan rebase absorbed + 3 stashes preserved'
st['last_action_at'] = ts
st['next'] = (
    "r1000: 1) 3-stash content-level recovery (CODELY.md 79-line reorg union vs bm-a r1046 CODELY edits + O-0137 7-line flip patch + s0-autostash 50 ledger rows union audit) 2) S6 chain full run + smoke 3) D-19 own probe 4) voicegen audition follow-through (MSG-0319 with bm-a: taildrop 4 files to CEO channel - verify taildrop rc + bm-a pickup) 5) BigHouse T-3 carry-over 6) S7 register loop/watchdog idempotent checks (claws proven live this round: pre-commit fired on marker, pre-push fired on stale-base)"
)
st['next_milestone'] = 'stash recovery + audition reel delivery to CEO channel (<=10-18 12:00 per O-1751 window) + BigHouse T-3 (<=10-19)'
st['latest_artifact'] = 'origin b15d5e699 (r998 estate incl MSG-0216) + media/drama-tts-out/r998_ep001_003/ + fleet/inbox/MSG-20261018-0319 (audition reel request)'
st['orphan_face'] = 7
st['orphan_faces'] = 7
st['orphan_face_note'] = 'r999 round-start probe (05:34): 7 py faces / 0 orphans'
st['sync']['r999_main_push'] = {
    'status': 'PUSHED_VERIFIED',
    'pushed_sha': SHA,
    'consumed_at': 'pending r1000',
    'behind_origin_main': 0,
    'note': 'r999 payload = r998-estate absorb commit (40 files incl MSG-0216 + r999 audition estate + post_review marker surgery) replayed on fresh tip via temp-index tree surgery after rebase sequencer deadloop; local main healed zero-worktree-change; delivery fetch+rev-parse verified',
}
st['verdict'] = 'GREEN: P0 O-0348 executed same-round (r998 estate DELIVERED b15d5e699 incl MSG-0216 receipt body) + orphan rebase estate absorbed + zero-loss 3-stash preserve + backlog row13 closed; smoke/S6 deferred honestly (no new data faces; bm-a r1046 chain-fresh at 05:2x); watermark red=false healthy'
json.dump(st, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print('state r999 written')

# ---------- 4) heartbeat ----------
p = r'fleet\machines\bm-b.json'
hb = json.load(open(p, encoding='utf-8'))
hb['last_seen'] = ts
hb['ts'] = ts
hb['clock_read'] = ts
hb['heartbeat_epoch_utc'] = int(time.time())
hb['round_no'] = 999
hb['round'] = 999
hb['task'] = st['current_task']
hb['did'] = ('r999: 当前活=O-0348 P0 已执行（r998 遗产面上链 b15d5e699·fetch 双验）+孤儿 rebase 遗产吸收+三 stash 零丢失保全；'
             '最近实物=origin b15d5e699（MSG-0216 回执正身+51 声审遗产 05:4x）+backlog 行13 done；'
             '下个里程碑=stash 内容级回收+声审卷投递 CEO 看片通道（≤10-18 12:00·O-1751 窗）·BigHouse T-3（≤10-19）；孤儿面=7/0')
hb['current_task'] = 'r1000: stash recovery + S6 chain + audition delivery watch'
hb['next'] = st['next']
hb['last_action'] = st['last_action']
hb['last_action_at'] = ts
hb['latest_artifact'] = st['latest_artifact']
hb['verdict'] = st['verdict']
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
if 'O-20261018-0348-bm-a.md' not in hb.get('orders_ack', []):
    hb['orders_ack'].append('O-20261018-0348-bm-a.md')
json.dump(hb, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
v = json.load(open(p, encoding='utf-8'))
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat r999 written, ack count', len(v['orders_ack']))

# ---------- 5) round report row ----------
p = r'logs\iteration-loop\round_reports.md'
row = (f"\n| {ts} | r999 | dept:工程 | O-0348 P0 同轮执行：死 r999 会话 staged 遗产 40 件（MSG-0216 正身+声审产物）经 post_review:11896 标记行手术+温索引树手术重放（rebase sequencer 死循环 r1032 复发→quit+plumbing 正法）上链 b15d5e699 DELIVERED；孤儿 rebase（05:32 tick 外部 pull 挂死遗产）吸收；三 stash 全保零丢失 | 验证=fetch+rev-parse origin/main==b15d5e699+爪双证活（pre-commit 拦标记/pre-push 拦陈旧基座）+孤儿探针 7/0 | 下轮=stash 内容级回收+烟测/S6 补跑+声审投递盯守 | watermark red=false | 本地未达 origin commit 数=0 | 记账预算=4/5 |"
       )
open(p, 'a', encoding='utf-8', newline='').write(row)
print('round report row appended')

# ---------- 6) cleanup scratch txt ----------
for f in ('_r999_mine.txt', '_r999_origin.txt'):
    if os.path.exists(f):
        os.remove(f)
        print('removed', f)

print('EDITS_DONE')
