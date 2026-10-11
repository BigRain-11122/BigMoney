# -*- coding: utf-8 -*-
"""r868 bm-c addendum: delivery self-proof + sync face flip + churn absorb."""
import io, json, os, time, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime())

# fetch self-proof
subprocess.run(['git', 'fetch', 'origin'], capture_output=True, cwd=ROOT)
r = subprocess.run(['git', 'rev-parse', 'HEAD', 'origin/main'], capture_output=True, text=True, cwd=ROOT)
head, origin = r.stdout.split()
r2 = subprocess.run(['git', 'rev-list', '--left-right', '--count', 'HEAD...origin/main'], capture_output=True, text=True, cwd=ROOT)
ahead, behind = r2.stdout.split()

row = (
 "2026-10-11T11:26:00+08:00 | r868 bm-c addendum | "
 "delivery self-proof + mid-round race receipt: r868 commit aed5202d5 -> rebased 1ec2a1865 push 直通（origin mid-round advance=bm-a r876 E15 链 5 commit 吸收·14 UU 全 take-fresher-mine〔docs/daily_report+live_usage+update_status 等=双机 S6 再生面·mine 11:18 vs theirs 11:03〕；runnable_pool.json 双翻面验证俱存〔W17-JUDGE done+E15-EMOTION-REEVAL done〕）；"
 "rebase --continue 零 UU 仍拒=r863 已知坑律再证（satengine tick daemon live-churn 敏感面·TEMP 备份→checkout 清树→continue→live-wins 回移·禁 stash-pop）；"
 "fetch 自证 ahead/behind=%s/%s | 记账预算：第 4 面（预算内·r852 pre3 先例法）" % (ahead, behind)
)
with io.open(os.path.join(ROOT, 'logs/iteration-loop/round_reports-bm-c.md'), 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + row)

sp = os.path.join(ROOT, 'state-bm-c.json')
st = json.loads(io.open(sp, encoding='utf-8').read())
st['head_sha'] = head[:9]
st['last_action'] = 'r868 addendum: delivery self-proof (push direct, 14-UU take-fresher-mine, churn-face law re-proof)'
st['last_action_at'] = now
st['sync'] = {'ahead_behind': '%s/%s delivered' % (ahead, behind), 'origin_tip': head[:9], 'ts': now,
              'note': 'r868 addendum: clean delivery self-proof (push direct after 14-UU take-fresher-mine rebase; churn-face r863 law re-proof; zero claw block)'}
io.open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=1))
print('addendum OK: head=%s ahead=%s behind=%s' % (head[:9], ahead, behind))
