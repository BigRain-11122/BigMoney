# r1032: append sequencer-stall pitfall row to CODELY.md (shared-file python append law)
import io

row = ('[2026-10-17 14:xx r1032 bm-a] rebase --continue "conflicts fixed" 态反复拒收卡死判例'
       '（git 2.55.0.windows.2 实弹·r1032 全链绕过）：git status 明示 (all conflicts fixed: run git rebase --continue) '
       '且 git ls-files -u 空，但 rebase --continue 反复报 You must edit all merge conflicts...（rc1 零进展·'
       '触发条件未定谳·疑与共享探针面活写竞态相关）；绕过正法四步='
       '①读 .git/rebase-merge/{author-script,message} 手动 git commit -F message（带原 GIT_AUTHOR_* env）完成当前 stopped pick '
       '②git rebase --quit（保 HEAD 丢 sequencer 状态）'
       '③剩余 picks 改走 git cherry-pick（共享面 UU 按行 ts newer-wins / 当日幂等再生面整侧 take-HEAD 较新 generated 侧零损失——'
       '双窗同日 S6 产物 33 UU 全取 HEAD 三分钟解毕）'
       '④git update-ref refs/heads/main HEAD 后 checkout+push（热推期两连拒时 fetch 新 tip 再 cherry-pick 重放）。'
       'How to apply：sequencer 死循环勿 abort（丢 estate 应用态）勿反复 add 重试；quit+cherry-pick=estate 保真重放通道。')

t = io.open('CODELY.md', encoding='utf-8').read()
assert row[:25] not in t, 'dup row already present'
with io.open('CODELY.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + row + '\n')
print('CODELY appended bytes=', len(row.encode('utf-8')))
