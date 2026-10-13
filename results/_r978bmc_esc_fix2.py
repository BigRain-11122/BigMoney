# -*- coding: utf-8 -*-
# r978 surgical fix 2 (source-level): r35gen stores needles as \uXXXX escapes in ITS source;
# remove the phantom \u00b7 (middle dot) from the two A-hops needles so they match R34 ground truth.
p = r"results\_r977bmc_r35gen.py"
src = open(p, encoding="utf-8").read()
BAD_OLD = '"=\\u00b7**A-hops-prior-B \\u9636\\u68af\\u51e0\\u4f55\\u7b2c\\u4e5d\\u5341\\u56db\\u4f8b\\uff08E36 \\u5361\\uff09**"'
GOOD_OLD = '"=**A-hops-prior-B \\u9636\\u68af\\u51e0\\u4f55\\u7b2c\\u4e5d\\u5341\\u56db\\u4f8b\\uff08E36 \\u5361\\uff09**"'
BAD_NEW = '"=\\u00b7**A-hops-prior-B \\u9636\\u68af\\u51e0\\u4f55\\u7b2c\\u4e5d\\u5341\\u4e94\\u4f8b\\uff08E36 \\u5361\\uff09**"'
GOOD_NEW = '"=**A-hops-prior-B \\u9636\\u68af\\u51e0\\u4f55\\u7b2c\\u4e5d\\u5341\\u4e94\\u4f8b\\uff08E36 \\u5361\\uff09**"'
assert src.count(BAD_OLD) == 1, "BAD_OLD %d" % src.count(BAD_OLD)
assert src.count(BAD_NEW) == 1, "BAD_NEW %d" % src.count(BAD_NEW)
src = src.replace(BAD_OLD, GOOD_OLD).replace(BAD_NEW, GOOD_NEW)
open(p, "w", encoding="utf-8", newline="").write(src)
import ast
ast.parse(src)
r34 = open(r"results\_w234bmc_r34_data.py", encoding="utf-8").read()
assert r34.count("=**A-hops-prior-B \u9636\u68af\u51e0\u4f55\u7b2c\u4e5d\u5341\u56db\u4f8b\uff08E36 \u5361\uff09**") == 1
print("FIX2 OK: escaped needles aligned to R34 ground truth")
