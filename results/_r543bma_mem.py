entry = ('- [2026-10-01 23:2x r543 bm-a] rebase 中途 --quit 丢余 pick 坑（r501 净路的序列边界补正·r543 双 commit rebase 实弹近误零损失）：r501 净路③「quit+update-ref」写就于单 pick 场景，多 pick 序列（r543=ride commit+r543 主 commit 两 pick）中手工 commit -C 落完首 pick 后即 quit=**余 pick 被静默丢弃**（本例 ride pick 的车道件内容被 daemon 后续 tick 新写超集覆盖=零损失侥幸，若余 pick 含非幂等产出=内容蒸发）；正确序=quit 前必核 rebase todo 余项（.git/rebase-merge/git-rebase-todo 在场性），有余项=逐个 cherry-pick 落完或证实内容被工作树超集覆盖后才 quit。How to apply：git 2.55 假拒绝走 commit -C 净路时，落完当前 pick 先 `git status` 看 rebase 是否仍在途（HEAD detached+todo 文件在场）——在途且有剩余 pick=继续处理勿径直 --quit；quit 后推送前必 diff 本地领先集 vs 原 pick 集断言无蒸发。')
with open('CODELY.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\r\n' + entry + '\r\n')
print('appended; size now:', len(open('CODELY.md','rb').read()))
