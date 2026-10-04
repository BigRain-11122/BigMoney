# r669 bm-b pit-git.md direct-write append v2 (md5pre caliber per r658 precedent + N convergence loop)
import hashlib

PIT = r"research\pit-git.md"
LINE = (
    "> 直写行（r669 bm-b·post-split convention direct-write）：+1 条（ls-tree --name-only 带路径=path 前缀整名面·r417 列位族姊妹变体："
    "S0.5 orders 差集探针实弹——git ls-tree --name-only HEAD fleet/orders/ 返回 fleet/orders/O-*.md 全路径前缀而非裸文件名，"
    "对原始行 startswith(\"O-\") 过滤=盘面集合恒空→153/153 全员假 orphan 警报（双计数 153==153 双绿也掩不住集合面假警）；"
    "正法=os.path.basename(line) 后再过滤+集合差集探针写完必自检非空侧（disk==0 而 ack>0=探针坏非仓库空，先修探针再定谳——"
    "r646 同口径集合比对律的执法面：计数比对是必要非充分判据，集合非空侧自检才是差集探针的完整性门））"
    "·追加核 {N} B·LF blob 净·md5pre={M}·件尾整行追加·件内对账行为准。"
)

b = open(PIT, "rb").read()
pre_len, pre_lf = len(b), b.count(b"\n")
pre_cr, pre_crlf = b.count(b"\r"), b.count(b"\r\n")
md5pre = hashlib.md5(b).hexdigest()
assert pre_crlf == 0 and pre_cr == 0 and b.endswith(b"\n")

# N convergence loop (digit-count fixed point)
n_guess = len((LINE.format(N=99999, M=md5pre) + "\n").encode("utf-8"))
for _ in range(6):
    cand = (LINE.format(N=n_guess, M=md5pre) + "\n").encode("utf-8")
    if len(cand) == n_guess:
        break
    n_guess = len(cand)
else:
    raise SystemExit("N convergence failed")

final = b + cand
post_lf, post_cr, post_crlf = final.count(b"\n"), final.count(b"\r"), final.count(b"\r\n")
assert post_lf == pre_lf + 1, f"LF increment mismatch {pre_lf}->{post_lf}"
assert post_cr == 0 and post_crlf == 0, "CR contamination"
assert final[:pre_len] == b, "prefix mutation"
assert hashlib.md5(final[:pre_len]).hexdigest() == md5pre, "pre-blob identity"

open(PIT, "wb").write(final)
print("APPEND-OK pre_len", pre_len, "append", len(cand), "post_len", len(final),
      "LF", pre_lf, "->", post_lf, "md5pre", md5pre, "md5post", hashlib.md5(final).hexdigest())
