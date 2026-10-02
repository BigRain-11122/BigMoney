# r594 bm-b CODELY.md pit append (bytes-safe CRLF/utf-8, r530 family law).
ENTRY = (
    "- [2026-10-02 21:2x r594 bm-b] 集成探针 deletion 检查只扫 staged 前缀=worktree 删除面漏检假绿坑"
    "（pre-push 爪首拦实弹·D-20261002-04 正运行）：纯 FF reset --mixed 后探针按 startswith('D ') "
    "只查已暂存删除，而他机 commit 新增件（bm-a 死会话收养件 _r592bma_* 9 件）本地盘从未物化"
    "=porcelain 呈 ' D'（worktree 删除）漏检假绿→后续 git add -A 把「本地无此文件」暂存成删除集"
    "=爪按非本机属主件双拦（零损失收口）。正法=①集成探针 deletion 检查双前缀（'D ' OR ' D'）"
    "②恢复面=git checkout origin/main -- <paths> 先物化他机新增件再 add -A ③amend 收口守卫="
    "rev-list origin/main..HEAD==1+HEAD 属主核验。How to apply：一切 reset --mixed/纯 FF 集成序列后、"
    "add -A 前探针必双前缀扫（staged+worktree）；见他机新增件被自己 add -A 吞成删除=先 checkout "
    "origin 物化，禁 --no-verify 绕爪。"
)
with open("CODELY.md", "ab") as f:
    f.write(("\r\n\r\n" + ENTRY + "\r\n").encode("utf-8"))
print("CODELY.md pit entry appended")
