# r231 S7 addendum: push-rejection second rebase + poison self-catch disclosure
# + CODELY lesson line (python UTF-8 direct write, EOL preserved).
import io

NOW_STRAMP = "2026-09-26 08:1x"

addendum = (
    "[2026-09-26 08:1x | r231 addendum | bm-b] S7 push 撞车收尾披露：首推被拒"
    "（bm-a R233 同窗 08:00 落）→ pull --rebase 重放 3 提交撞 2 处 UU（0ea4b820 "
    "r230-tail 重放×autofill_state + 935cd194 本轮大件×11 文件批）；**E1 自捕零外泄**"
    "：首版重放时 in-repo 解器（_r231b 系列提交于本轮大件内=重放序后位）在早期"
    "重放步不存在树中，python 失败后 PS `;` 序继续 git add=把带冲突标记的 "
    "autofill_state 吞进两个重放中间提交（0121dc17/cf223bb9 字节级自检 2 标记+"
    "PARSE-FAIL 逮住，push 前自捕）→ 正解=abort 重来（毒化解非已解冲突，r220 禁"
    "abort 律不护毒化面）+解器外置 %TEMP% 跑三步全净（终验 HEAD~2..HEAD 四面 "
    "0 标记+pid17616 全保全+union 50+50→51/203 零丢失）；终推 9afbba2d..236f4cb0 "
    "fast-forward 成功；坑律新维：**重放依赖的 resolver 禁放待重放提交内（自引用"
    "死锁），一律外置 TEMP；PS 语句串 `;` 非失败封闭，解器步失败必 && 封锁 add**。"
    "另记：08:00:02 autofill tick 读到 pool_empty（翻面 07:59 先于 tick=r224 窗"
    "律达成实证，零空转 claim）。"
)

REP = "logs/iteration-loop/round_reports.md"
raw = open(REP, "rb").read()
crlf = b"\r\n" in raw[-2000:]
ends_nl = raw.endswith(b"\n")
sep = "\r\n" if crlf else "\n"
with io.open(REP, "a", encoding="utf-8", newline="") as fh:
    if not ends_nl:
        fh.write(sep)
    fh.write(addendum + sep)
print("addendum appended")

CODELY = "CODELY.md"
raw2 = open(CODELY, "rb").read()
crlf2 = b"\r\n" in raw2[-2000:]
ends_nl2 = raw2.endswith(b"\n")
sep2 = "\r\n" if crlf2 else "\n"
lesson = (
    "- [2026-09-26 08:1x] 坑律（bm-b r231 addendum·S7 push 撞车重放×解器可用性"
    "新维·E1 自捕零外泄）：**push 被拒后 pull --rebase 重放多提交时，重放各步依赖"
    "的 resolver 禁放「待重放提交序列后位」——in-repo _r<N> 解器提交在本轮大件内="
    "早期重放步树中不存在，解不动只能手解**；连带 **PS 语句串 `;` 非失败封闭——"
    "python 解器步失败后序列继续跑 git add=把冲突标记面吞进重放中间提交（毒化提交"
    "字节级自检三面：markers 计数+json.loads+pid17616 保全；本例 2 中间提交 2 标记"
    "PARSE-FAIL 自捕于 push 前）**；正解=①abort 重来（r220 禁 abort 律不护毒化解，"
    "毒化=白干正确化）②解器外置 %TEMP%（写路径 join(REPO)）③解器步与 add 步用 "
    "&&/分步封锁 ④重放完成必对 HEAD~n 逐提交字节自检 0 标记再推。指针=TEMP "
    "r231_replay_resolver.py 范式+round_reports r231 addendum 行。"
)
with io.open(CODELY, "a", encoding="utf-8", newline="") as fh:
    if not ends_nl2:
        fh.write(sep2)
    fh.write(lesson + sep2)
print("CODELY lesson appended; size_kb=", (len(raw2) + len(lesson.encode('utf-8'))) // 1024)
