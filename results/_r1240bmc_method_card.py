# -*- coding: utf-8 -*-
"""r1240 bm-c: methodology card E97 append (adjudicator raw-path defect)."""
import io

P = 'knowledge/METHODOLOGY_ASSETS.md'
card = """
## E97 工具把**原始参数**直接拼进 git 对象路径（r1240 bm-c 实弹·W329 冻结面裁决）
- 缺陷：`Tools/n1_freeze_face_adjudicate.py` 用 `--editor/--receipt/--prereg` 的**原样字符串**去执行 `git show <splice>:<path>`；Windows 反斜杠路径（`results\\_w329bmc_freeze_edits.py`）在 git 眼里是另一个路径 → `fatal: path ... exists on disk, but not in '<sha>'`，工具以 rc1 退出、没有任何内容漂移。判读上极易被误读成「冻结件没进 splice 提交」。
- 正法：调用一律传**正斜杠**路径（`results/_w329bmc_freeze_edits.py`）；工具侧若要根治=入参先 `p.replace(os.sep,'/')` 再拼对象名。
- 证据：`results/_n1_face_adjudication_w329.json` verdict PASS（pre/post 双面命中、replay_lf_eq_landed=true、0 heal / 0 unexplained），同命令换成反斜杠即 rc1。
- 2026-10-25 11:0x 由 bm-c r1240 于 W329 收口窗立。
"""
t = io.open(P, encoding='utf-8').read()
if '## E97' not in t:
    if not t.endswith('\n'):
        t += '\n'
    io.open(P, 'w', encoding='utf-8', newline='\n').write(t + card)
print('appended', '## E97' in io.open(P, encoding='utf-8').read())