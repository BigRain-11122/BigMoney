# -*- coding: utf-8 -*-
"""r1062 trim pass: tighten merged pointer + compressed faces to land CODELY.md under BOTH
10KB readings (<=10,000B). Fresh single-file read-modify-write (multi-writer law)."""
import hashlib
import json

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
CODELY = ROOT + r"\CODELY.md"
RECEIPT = ROOT + r"\results\_r1062bma_codely_hotcold_receipt.json"

PAIRS = [
    # merged sec4 pointer: selftest legs carry the assertion semantics (canon in code)
    ("selftest 第 9 腿（9/9 PASS 正反断言）+n1 selftest D-20261002-05 pin leg"
     "（W68 判例锚·越 hit 读法==W68 注册带恒等/窗步链读法≠注册带拒绝）。",
     "selftest 第 9 腿（9/9）+n1 selftest D-20261002-05 pin leg（正反断言·W68 锚）。"),
    ("（算术窗内非边缘端点命中·越 hit 起窗 vs 窗步链跳位两读法可分叉时）",
     "（算术窗内非边缘端点命中·两读法可分叉时）"),
    # reference row compressed faces
    ("rebase --continue 三连坑=哑终端 git -c core.editor=true 修+commit 面不走 pre-commit 爪"
     " continue 后必 marker 扫残+活写者重写 UU=MM 重 add newer-wins（r1048）",
     "rebase --continue 三连坑=dumb 终端 git -c core.editor=true 修+commit 面不走 pre-commit 爪"
     "必 marker 扫残+活写者 MM 重 add（r1048）"),
    ("push 挂死 5min 零输出=零残留进程→ls-remote 探送达→fetch 重核→重放重推禁盲重试（r1005）",
     "push 挂死=零残留进程→ls-remote 探送达→fetch 重核→重放重推禁盲重试（r1005）"),
]

with open(CODELY, "r", encoding="utf-8", newline="") as f:
    src = f.read()
for old, new in PAIRS:
    n = src.count(old)
    assert n == 1, "trim anchor count=%d for %r" % (n, old[:36])
    src = src.replace(old, new)
post = len(src.encode("utf-8"))
assert post <= 10000, "still over decimal-10KB line: %d" % post
with open(CODELY, "w", encoding="utf-8", newline="") as f:
    f.write(src)
with open(CODELY, "r", encoding="utf-8", newline="") as f:
    chk = f.read()
assert chk == src
for _, new in PAIRS:
    assert new in chk

with open(RECEIPT, "r", encoding="utf-8") as f:
    receipt = json.load(f)
receipt["trim_pass"] = {"pairs": len(PAIRS),
                        "codely_post_bytes_trimmed": post,
                        "note": "second pass to land under both 10KB readings (<=10,000B)"}
receipt["codely_post_bytes"] = post
receipt["md5_codely_post"] = hashlib.md5(src.encode("utf-8")).hexdigest()
with open(RECEIPT, "w", encoding="utf-8", newline="") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps({"codely_final_bytes": post, "under_line": "PASS(<=10000B)"}, ensure_ascii=False))
