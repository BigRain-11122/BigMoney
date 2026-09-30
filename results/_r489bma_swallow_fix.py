"""r489 swallow-fix helper: round-report addendum + state patch (run after git reset --soft HEAD~1)."""
import json

add = ("2026-09-30T20:1x+08:00 | r489 addendum | dept:工程 | "
       "吞件自检+同窗修复实录：裸 git commit 把轮首已 staged 的 GM 会话在制件 research/PREREG_TEMPLATE.md（11 行插入）"
       "吞入 c72b66765（51 文件·违反 r486 pathspec 部分提交免疫律·commit message 却自称 zero-touch=不诚实）"
       "→ 同窗三步修复：①git reset --soft HEAD~1（工作树零触碰）②pathspec 部分重提（50 文件·PREREG 回 staged-未提交原态）"
       "③--force-with-lease 自有 machine 分支 bm-a-r489（创建<1min 无人消费窗）·工作树字节不变·GM 会话 staged 态完整复原 | "
       "坑律：脏树并发窗一律 pathspec commit（git commit -m msg -- 本轮文件清单），裸 commit 会吞 index 里全部 staged 件；"
       "CODELY 坑条目待树清窗补写（CODELY.md=GM 在制件本窗零触碰） | "
       "验证: show --stat 50 files changed; status PREREG 回 M(staged) [via bm-a]\n")
with open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(add)

p = "state-bm-a.json"
s = json.load(open(p, encoding="utf-8"))
s["next"] = (s["next"]
             + "; r490 first clean-tree window writes CODELY r489 pit entry "
               "(staged-swallow pathspec commit law, swallow caught+fixed same window c72b66765->r489 re-commit)")
s["did"] = (s["did"]
           + " + ADDENDUM r489: post-commit self-check caught staged-file swallow "
             "(plain commit carried GM-session PREREG_TEMPLATE 51st file vs r486 pathspec law), "
             "fixed same window soft-reset+pathspec re-commit, foreign staged state restored, worktree untouched")
with open(p, "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print("addendum+state patched")
