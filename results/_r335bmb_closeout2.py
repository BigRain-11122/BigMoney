# -*- coding: utf-8 -*-
"""r335 bm-b closeout-2: two more archival moves to bring CODELY under the 10KB hard line."""
import io

def eol_of(path):
    b = open(path, "rb").read()
    crlf = b.count(b"\r\n")
    return "\r\n" if crlf >= (b.count(b"\n") - crlf) and crlf > 0 else "\n"

P1 = "- 坑律正典全量归档（2026-09-27 集团令 O-20260927-0230-bm-a·CODELY ≤10KB 整编）"
P1_PTR = ("- 坑律正典全量归档（O-20260927-0230-bm-a·集团令）：**≤10KB 硬线——append 后超线=当窗即办热冷整编勿等月**"
          "（水位律自 >50KB 重锚·新坑律仍先入本件）；十五/十六批索引与迁移史全文 verbatim=archive 202609.md"
          "『坑律归档 2026-09-27 二十三批』节。")
P2 = "- [2026-09-27 16:2x r335 bm-a] 坑律（二十批外迁·指针）：PowerShell ConvertFrom-Json 会对合法 JSON 件假报 parse 失败"

eol = eol_of("CODELY.md")
lines = io.open("CODELY.md", encoding="utf-8").read().splitlines()
moved, out = [], []
for l in lines:
    if l.startswith(P1):
        moved.append(l)
        out.append(P1_PTR)
    elif l.startswith(P2):
        # twin-coverage dedupe: the 二十一批 twin pointer (identical law) stays live; full archived verbatim
        moved.append(l)
    else:
        out.append(l)
assert len(moved) == 2, f"expected 2 hits, got {len(moved)}"
with io.open("CODELY.md", "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(out) + eol)
sz = len(open("CODELY.md", "rb").read())
print(f"CODELY: -2 lines moved verbatim, size={sz}B ({'UNDER' if sz <= 10240 else 'STILL OVER!'} 10240B)")

eol_a = eol_of("research/memory-archive/202609.md")
with io.open("research/memory-archive/202609.md", "a", encoding="utf-8", newline="") as f:
    for l in moved:
        f.write(l + eol_a)
chk = io.open("research/memory-archive/202609.md", encoding="utf-8").read()
for l in moved:
    assert l in chk, "verbatim zero-loss assert FAIL"
print(f"202609.md: +2 verbatim (zero-loss assert PASS)")
assert sz <= 10240, f"CODELY {sz}B still over 10KB hard line"
print("CLOSEOUT-2 OK")
