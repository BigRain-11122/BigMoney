# r1013 bm-b postscript: detached-HEAD incident pit row (CODELY.md) + round-report
# postscript line. Byte-safe python append; size assert vs 10,240 hard line.
import io, os, json, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = os.path.join(ROOT, "CODELY.md")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

pit_row = ("- [2026-10-19 02:1x r1013 bm-b] **裸 git status 分支附着态盲区坑（detached HEAD 全程隐身实弹）**："
           "`git status --porcelain` 不显示分支附着行——本轮全程以 --porcelain 盘点树态，HEAD 实自 r1012 手术期即游离"
           "（detached from 57eb794255）全程零察，收口 commit 落游离指针、main 分支滞留 r1012 位（9cdbb0afa1）"
           "→`git push origin main` 实推陈旧分支=非快进拒（ancestor 逆推伪装成「落后远端」假象）。"
           "正法：①轮首核附着态一律 `git symbolic-ref -q HEAD`（空输出=detached 先 re-attach）或裸 `git status` 头两行；"
           "②修法=merge-base --is-ancestor 零孤儿实核后 `git update-ref refs/heads/main <sha>`（全名律 r1012）+`git checkout main`；"
           "③push 拒绝先 `git rev-parse main origin/main` 对位判方向（ancestor 逆推≠远端领先）。"
           "How to apply：一切轮首树态盘点必带附着态检查；detached 态下禁直接 push 分支名。")

c_bytes = open(CODELY, "rb").read()
bom = c_bytes.startswith(b"\xef\xbb\xbf")
text = c_bytes.decode("utf-8-sig")
if not text.endswith("\n"):
    text += "\n"
text += pit_row + "\n"
new_bytes = (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")
assert len(new_bytes) <= 10240, "over 10KB hard line: %d" % len(new_bytes)
open(CODELY, "wb").write(new_bytes)

ps_line = ("{ts} | r1013 bm-b postscript | push window incident disclosed + healed: session ran on DETACHED HEAD "
           "(inherited from r1012 surgery era; root cause = git status --porcelain hides the branch line, all-round blind spot) "
           "-> closeout commit 2d94895c7f landed on the detached pointer while branch main stayed stale at 9cdbb0afa1 "
           "-> push origin main pushed the stale branch = non-FF rejected (ancestor-reverse masquerading as behind-remote) "
           "-> healed: is-ancestor zero-orphan verified + update-ref refs/heads/main 2d94895c7f (full-name law) + checkout attach "
           "+ CODELY pit row (symbolic-ref -q HEAD round-start check law) + re-push receipt; zero worktree touch, zero data loss"
           ).format(ts=now_iso)
with io.open(REPORT, "a", encoding="utf-8") as f:
    f.write(ps_line + "\n")

print(json.dumps({"codely_size": len(new_bytes), "report_ps_len": len(ps_line)}, ensure_ascii=False))
