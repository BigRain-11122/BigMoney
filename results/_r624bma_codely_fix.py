import io
p = 'CODELY.md'
t = io.open(p, encoding='utf-8').read()
# locate the mangled block (starts at the r624 croc entry marker)
marker = '- [2026-10-03 13:3x r624 bm-a] croc 11.5.3'
i = t.find(marker)
assert i > 0, 'marker not found'
t = t[:i].rstrip('\n') + '\n'

clean = '''- [2026-10-03 13:3x r624 bm-a] croc 11.5.3 CLI 形态坑（T-156 接收端三连误点火实弹·r614 族新面）：①「receive」非子命令——码=位置参数（正=croc --relay <ip:port> --yes --out <dir> <code>），MSG 票面给的 --code/--output 形态对 11.5.3 全错→croc 静默转交互读码面、分离窗 stdin=EOF 即假死（Enter receive code→EOF）；②--out 非 --output；③Go 侧 ~/.config mkdir 拒面（AV/ACL 拦截未定谳）先炸 logger 后可致 flate decode 崩——预建 ~/.config/croc 目录即愈；④版本面怀疑：11.5.3 对旧版 sender 的 PAKE 面曾报 flate corrupt input——双端版本对齐待 bm-b 侧核。How to apply：croc 接收命令一律先跑 --help 核本机版本形态再点火；.config 拒面预建目录；分离接收端 stderr 走 UI 流（r614 律不变）。
- [2026-10-03 13:3x r624 bm-a] rebase --quit 后游离 HEAD 提交面坑（r305/r501 假拒绝净路的尾巴·当场自愈零损）：git rebase --quit（幽灵 unmerged 假拒绝走净路时）把会话留在游离 HEAD——后续所有 commit 落游离线上、本地 main 分支仍指旧基座→push 拒绝信息=「a pushed branch tip is behind its remote counterpart」（误导面：ls-remote 明明同步、rev-list 双 0），真态=分支指针没跟上游。修法=push 前必核 git symbolic-ref HEAD，非 refs/heads/* 即先 git branch -f main <游离HEAD>（先验 merge-base --is-ancestor origin/main <HEAD> 防 rewinding）；本窗实弹：5 commit 全落游离线、branch -f 一发治愈。How to apply：任何 --quit/--abort 序列后先 symbolic-ref 自检再提交；遇「behind its remote counterpart」但 ls-remote 同步=先查分离头勿疑网络。
'''
io.open(p, 'w', encoding='utf-8', newline='\n').write(t + clean)
v = io.open(p, encoding='utf-8').read()
print('size:', len(v))
print('escape-artifacts-remaining:', v.count(chr(92) + '`'))
print('entries:', v.count('r624 bm-a]'))
print('mojibake-?:', v[-2000:].count('?') > 20)
