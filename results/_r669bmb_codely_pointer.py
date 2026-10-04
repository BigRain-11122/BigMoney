# r669 bm-b CODELY.md L6 pointer-line increment v2 (line-level identity invariant)
import hashlib

C = r"CODELY.md"
ADD = ("；r669 bm-b direct-write 1 条（ls-tree --name-only 带路径=path 前缀整名面——basename 过滤律·"
       "裸 startswith 集合恒空假 orphan 警报·r417 列位族姊妹变体）已入件（件内对账行为准）")

b = open(C, "rb").read()
pre_len, pre_lf = len(b), b.count(b"\n")
pre_cr, pre_crlf = b.count(b"\r"), b.count(b"\r\n")
assert pre_crlf == 0 and pre_cr == 0, "expected pure-LF CODELY.md"

text = b.decode("utf-8")
lines = text.split("\n")
idx = 5
assert lines[idx].startswith("- 域指针·D-20261002-06 首拆件"), "anchor line mismatch"
assert lines[idx].endswith("。"), "line must end with period"
assert ADD not in text, "already appended"
old_line = lines[idx]
new_line = old_line[:-1] + ADD + "。"
lines[idx] = new_line
out = "\n".join(lines).encode("utf-8")

# invariants: line count stable; all lines except idx byte-identical; edited line = old with insertion
out_lines = out.decode("utf-8").split("\n")
assert len(out_lines) == len(lines), "line count drift"
for i, (a, c) in enumerate(zip(lines, out_lines)):
    if i != idx:
        assert a == c, f"unrelated line {i} mutated"
assert out_lines[idx].startswith(old_line[:-1]) and out_lines[idx].endswith("。")
assert out.count(b"\n") == pre_lf and out.count(b"\r") == 0, "EOL drift"

open(C, "wb").write(out)
print("CODELY-EDIT-OK pre", pre_len, "post", len(out), "add", len(out) - pre_len,
      "LF", pre_lf, "md5pre", hashlib.md5(b).hexdigest()[:16])
