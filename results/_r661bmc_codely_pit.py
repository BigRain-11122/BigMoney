# -*- coding: utf-8 -*-
# r661 bm-c: close-batch % pit main-file-first append (byte-exact,
# dominant-EOL preserving). New pits enter the main file first, then get
# swept to domain pit files by later increment batches (r651/r654 law).
import os

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "CODELY.md")
line = ("- [2026-10-07 07:3x r661 bm-c] **close 批字面 %×%-format 崩+RR/state 半程态（幂等门律）**："
        "did 叙事含字面 %（avg 0.5%）与 %dB 占位混用→ValueError unsupported format character；"
        "时序=RR 行已 append 而 state 未推进，裸重跑必轮账本双行。正法="
        "①% 格式化串内叙事字面 % 一律写 %%；"
        "②close 重跑带 RR 幂等门（tail 内本轮 marker 命中即跳 append）；"
        "③rebase 竞态窗 daemon 活 tick 折入 pick-1+-c core.editor=true rebase --continue 非交互正径（本窗实证免 r808 三步）。")
raw = open(P, "rb").read()
w = raw[-400:]
crlf = w.count(b"\r\n")
lf_only = w.count(b"\n") - crlf
eol = b"\r\n" if crlf > lf_only else b"\n"
pre = b"" if raw.endswith(b"\n") else eol
payload = pre + line.encode("utf-8") + eol
open(P, "ab").write(payload)
new_size = len(raw) + len(payload)
print("appended %dB (eol=%r pre=%r); CODELY.md worktree size=%dB" % (
    len(payload), eol, pre, new_size))
assert new_size <= 30720, "over 30KB gate: %d" % new_size
