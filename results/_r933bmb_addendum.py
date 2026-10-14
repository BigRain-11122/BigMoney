# -*- coding: utf-8 -*-
import io, os, shutil, time
ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')

# 1) inbox: MSG-20261014-1255-bma-w238-finalize -> processed
src = os.path.join(ROOT, 'fleet', 'inbox', 'MSG-20261014-1255-bma-w238-finalize.md')
dst = os.path.join(ROOT, 'fleet', 'inbox', 'processed', 'MSG-20261014-1255-bma-w238-finalize.md')
if os.path.exists(src):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    print('inbox msg moved to processed')

# 2) round report addendum + ack line
rr = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
line = ('| ' + NOW + ' | r933 bm-b addendum | push landed after origin-midround race surgery: origin moved +2 during round (bm-a r986 w240-seat + bm-c r996 W239-frozen); first push correctly BLOCKED by pre-push claw (stale-base push would have dropped bm-a results/_w240bma_20261014_probe_receipt.json -- claw precise-diagnosis win); rebase replay of r933 hit shared-face conflict on results/_attrition_guard_scan.json (bm-b scan 13:36 vs bm-a r986 scan -- resolved ts-newer-wins mine) then rebase --continue refused with ZERO unmerged stages (ls-files -u empty) -> remedy: git add -A index drift-normalize + GIT_EDITOR=true continue one-shot pass (r863 zero-UU continue-refuse pit live second instance, remedy confirmed); stash@{0} = 3 satengine regen faces only, dropped per r930 ts-newer-wins; delivery self-proof behind=0 ahead=0 at c1c5f911e | PS pit hits this round: && separator invalid PS5.1 (use semicolons) + stash@{0} unquoted = hashtable mangle (r932 same-family repeat, single-quote it) | inbox processed: MSG-20261014-1255-bma-w238-finalize (bm-a to ALL, primary bm-c W239 freezer; bm-b informational: our TRIAL_LAB_W19_SCREEN 546 shared-chain interleave transparently disclosed in bm-a finalize deviation note -- no action for bm-b) | 本地未达 origin commit 数=0 (fetch+rev-list self-proof post-push) | \n')
with io.open(rr, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report addendum appended')

# 3) CODELY.md pit line (one thing: rebase-continue zero-UU remedy confirm)
cl = os.path.join(ROOT, 'CODELY.md')
cline = ('- [2026-10-14 14:1x] r933 bm-b git 域判例二连：①**rebase --continue 零 UU 仍拒坑第二实例+remedy 实证**（git ls-files -u 空且 continue 仍报「You must edit all merge conflicts」→ 正解=git add -A 索引漂移归一 + $env:GIT_EDITOR=\'true\' 再 continue 一发即过·r863 坑族·shared-face 冲突解决后常见残留态）；②PS `stash@{0}` 不加引号=hashtable mangle（「Too many revisions specified \'stash@\' \'MAA=\'」报形·r932 同坑当日二犯·引用一律单引号包）。\n')
with io.open(cl, 'a', encoding='utf-8', newline='') as f:
    f.write(cline)
print('CODELY.md pit line appended')
print('ADDENDUM DONE')
