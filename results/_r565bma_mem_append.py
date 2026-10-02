# -*- coding: utf-8 -*-
"""r565 bm-a S4 memory append: one active-law entry to root CODELY.md (EOL-preserving byte append)."""
import io, os

fp = r'CODELY.md'
raw = open(fp, 'rb').read()
crlf = raw.count(b'\r\n')
lf = raw.count(b'\n') - crlf
eol = '\r\n' if crlf > lf else '\n'
entry = (
    '- [2026-10-02 08:3x r565 bm-a] 同窗撞面零成本让路+席位公示同窗再占位模式（W61 让路实弹·r530 族第 7 例）：'
    'never-dry 确定性设计下三机同窗同带撞面=结构性（W12/W39/W51/W58/W59/W60/W61 序列）——MSG-0640 FIX-A'
    '（编辑前 origin-blob 等值断言）在本地任何编辑前 abort=撞面预防级拦截首例实弹（对照 r563 W60 让路时 12 '
    '分片已烧的浪费面：本窗零烧零推纯草稿弃置）；让路正法=弃 unpushed 草稿→树取 origin→让路回执 MSG 内同窗发布 '
    'next own target 席位公示（published=reserved r518-①·W48/W49/W55 先例）→同窗冻结下一自由号（W62 同窗落地）。'
    'How to apply：freeze edits 工具 FIX-A abort=撞面信号（先 fetch 查 origin 表尾定正主·后到让路勿硬改）；'
    '让路后禁干等禁连撞——回执 MSG 内同窗公示席位再占位；确定性撞面下席位公示=现役唯一可靠错峰机制。'
)
if 'r565 bm-a' in raw.decode('utf-8'):
    print('entry already present (idempotent skip)')
else:
    with open(fp, 'ab') as f:
        if not raw.endswith(eol.encode('utf-8')):
            f.write(eol.encode('utf-8'))
        f.write(entry.encode('utf-8'))
        f.write(eol.encode('utf-8'))
    print('entry appended, new size =', os.path.getsize(fp))
