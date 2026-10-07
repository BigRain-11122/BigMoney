import datetime
import json
import os
import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec='minutes')


def run(args, env_extra=None):
    e = dict(os.environ)
    if env_extra:
        e.update(env_extra)
    p = subprocess.run(args, capture_output=True, env=e)
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


# --- 1) S7 attach row (push-race receipt, r725-S7附加 precedent; utf-8 append
#        per close.py canonical convention)
row = (
    f"{TS} | r727-S7附加 | S7 push-race 窗实录：push #1 pre-push 爪正确拦截"
    "（幻影删除族 r759·bm-a r860 波窗中前进 behind=5·爪拦=正确执法零绕过）"
    "→净树零 autostash 律尾吸收 f9e4a607e（r642/r789）→pull --rebase 单 UU="
    "results/token_usage.json（stage3=本侧整面=正典解：-bm-a 双侧恒等 1,481,071"
    "·-bm-c 我新 2,444,903·generated 04:09:07 我新·delta_vs_prev 链接 origin 前值"
    "·r782 rebase stage-inversion 律全程在册）+compute_audit.json 自动合并="
    "正典解直收（latest=我 04:08:25 新者+history ts-union 12 条零重·审计门过）"
    "→continue 拒进=r855 第四态（无关未暂存 daemon churn 面×2 触发 diff-files "
    "--quiet 假冲突报·ls-files -u 恒空二分定性）→churn 吸收+原子 continue 秒过"
    "（round commit 重放 2b46809ff）→pick2 尾 commit 撞 2 件 satengine 面 UU"
    "→内容 ts 择新整面解（stage2 04:14:37>stage3 04:13:31 live-wins）→"
    "Successfully rebased→标记扫描 r651 域律改扫本轮 43 变更面=零新污染"
    "（全树扫 400 假阳性=历史 resolver 收据件合法含标记文本·r651 家族第五连）"
    "→push #2 non-FF 再拒（origin 再前进 4=bm-a r861 波+autofill tick×3·"
    "双机 5 分钟环同窗竞态常态）→本附加行+churn/探针收据尾吸收 #2 后三连"
    "（add+rebase+push 原子窗·r696 节拍竞速法）收口 [via bm-c r727]"
)
rp = 'logs/iteration-loop/round_reports-bm-c.md'
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(row + '\n')
print('S7 attach row appended')

# --- 2) atomic window: add all (own churn + receipts + report row) -> tail
#        commit -> pull --rebase -> push
msg = ('round 727 bm-c: S7 push-race appendix row + churn/receipt tail absorb #2 '
       '(r696 race window) [via bm-c r727]')
open('_r727bmc_tailmsg2.txt', 'w', encoding='utf-8', newline='').write(msg)
rc, o, e = run(['git', 'add', '-A'])
rc, o, e = run(['git', 'commit', '-F', '_r727bmc_tailmsg2.txt'])
print('tail#2 commit rc', rc, o[:80])
rc, o, e = run(['git', 'pull', '--rebase'], env_extra={'GIT_EDITOR': 'true'})
print('pull-rebase rc', rc)
print((o + e)[:400])
p = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
uu = [l for l in p.stdout.splitlines()
      if l[:2] in ('UU', 'AA', 'DU', 'UD')]
if rc != 0 or uu:
    print('UU faces:', uu)
    sys.exit(2)
rc, o, e = run(['git', 'push'])
print('push rc', rc)
print((o + e)[:400])
run(['git', 'fetch'])
rc, o, e = run(['git', 'rev-list', '--count', 'origin/main..HEAD'])
ahead = o.strip()
rc, o, e = run(['git', 'rev-list', '--count', 'HEAD..origin/main'])
behind = o.strip()
rc, o, e = run(['git', 'rev-parse', 'HEAD'])
print('DELIVERY_PROOF tip=%s ahead=%s behind=%s' % (o.strip()[:12], ahead, behind))
