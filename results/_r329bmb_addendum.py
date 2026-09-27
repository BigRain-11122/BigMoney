# r329 bm-b addendum writer (push-collision receipt + rebase-continue pitlaw entry)
import io, os, datetime

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'
now = datetime.datetime.now()
t = now.strftime('%H:%M')
ts_disp = now.strftime('%Y-%m-%dT%H:%M') + '+08:00'

addendum = ("2026-09-27T%s+08:00 | r329 addendum bm-b | S7 push-collision receipt: first push rejected vs bm-c r84/r85 (c5d480ac 30-UU re-land mega commit) in same window -> pull --rebase 2-UU canon-resolved per bigmoney-conflict-resolve (classifier GREEN 2/0 UNKNOWN): CODELY.md memory-union ADJUDICATED-archival (upstream=bm-c r85 in-place hot-cold archival 9036->7338B: 4 pit-law entries verified verbatim in worktree archive + index line refreshed by upstream + their r84 entry; mine=base+938B pure-append verified -> new=upstream+my suffix=8276B<10KB) + compute_audit rolling-ledger history union 208|201->209 (200 collisions content-identical diverged=0) + latest deep-ts take-new mine 14:24:13>14:06:16 | resolver=results/_r329bmb_resolve.py | rebase-continue quirk: git rebase --continue persistently refused ('You must edit all merge conflicts') on CLEAN index (ls-files -u empty, diff-filter=U empty, rebase-merge state intact, todo empty) -> zero-abort manual finalize: git commit -F .git/rebase-merge/message (dfeeca5e full 59-file face landed) + git rebase --quit + git update-ref refs/heads/main dfeeca5e + checkout (r220 no-abort law honored, zero loss; --skip NOT used -- would drop the pick) | push landed c5d480ac..dfeeca5e | post-push probes: W2-A burn pid7796 alive prep advancing (WS 5326->7064MB, CPU 213->573s); sina panel n_symbols 5228/5228 complete=False refresh lock alive = gate on knife edge, next round re-probe and draft sina-construct prereg if complete flips | evidence: resolver receipt asserts + git log dfeeca5e == origin/main tip | next: r329 main line\n" % t)

entry = ("- [2026-09-27 14:%s r329 bm-b] 坑律：**git rebase --continue 在 index 干净（ls-files -u 空·diff-filter=U 空·todo 空·rebase-merge 态完好）时仍恒拒行「You must edit all merge conflicts」=环境面假死——禁误判未解冲突、禁 abort 重来（r220 红线）、禁 --skip（弃当前 pick）**——r329 实弹：2-UU 解毕 continue 三连拒，正典三步零丢失收口=①手动补拍 `git commit -F .git/rebase-merge/message`（全量面落拍）②`git rebase --quit`（非 abort·工作全保）③`git update-ref refs/heads/main <sha>`+checkout 重挂。指针=results/_r329bmb_resolve.py+round_reports r329 addendum。\n" % now.strftime('%M'))

rr = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
with io.open(rr, 'rb') as f:
    assert f.read()[-1:] == b'\n'
with io.open(rr, 'ab') as f:
    f.write(addendum.encode('utf-8'))

cl = os.path.join(ROOT, 'CODELY.md')
with io.open(cl, 'ab') as f:
    f.write(entry.encode('utf-8'))
size = os.path.getsize(cl)
assert size <= 10240, 'CODELY over 10KB: %d' % size
print('ADDENDUM_OK codely=%dB' % size)
