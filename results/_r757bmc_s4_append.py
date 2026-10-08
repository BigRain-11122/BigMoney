# -*- coding: utf-8 -*-
"""r757 bm-c S4 memory direct-write: append group-tree git-log default-ref
stale-history pit to research/pit-git.md (mother file of git domain, 2.3KB
headroom; main CODELY.md at cap -> r666/r747 direct-write convention).
Mechanized byte+md5 reconciliation line per r742 pattern. Host EOL preserved
(r503/r485 law)."""
import hashlib
import os

PATH = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\pit-git.md"
ENTRY = ("- [2026-10-08 12:2x r757 bm-c] **集团树 git log 缺省 ref=静默陈史坑"
          "（ORD delta 探针 v1 实弹·v2 同轮自纠零错账）**：fresh-read 律只钉 blob 面"
          "（git show origin/main:path）——git log -- <path> 缺省走本地 HEAD，集团树"
          "常态落后 origin 时=静默返回陈史（v1 误判最新=10-07 尾·实情 origin/main 已有 "
          "10-08 七连提交）；git show 缺 ref 响亮报错、git log 缺 ref 静默给旧答案=同律"
          "新面（静默成功比响亮失败更毒）。正法=集团树一切历史/diff 查询显式带 "
          "origin/main（git log origin/main -- path / git diff <prev> origin/main -- "
          "path），消费前首行时间戳新鲜度自检。How to apply：ORD/DEC delta 消费探针复制"
          "血统先核命令全串带显式 ref；见「log 零新行但 blob sha 变」先疑缺省 ref 勿疑"
          "哈希机制。")

raw = open(PATH, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
assert raw.endswith(eol), "file must end with a clean line terminator"
core_lf = ENTRY.encode("utf-8") + b"\n"
core_bytes = len(core_lf)
md5 = hashlib.md5(core_lf).hexdigest()

ann = ("> 直写行（r757 bm-c·post-split convention direct-write）：+1 条（集团树 git log "
       "缺省 ref 静默陈史坑——正法显式 origin/main ref+首行新鲜度自检）·追加核 %d B"
       "（LF blob 面·md5=%s）·件尾整行追加·件内对账行为准。" % (core_bytes, md5))

with open(PATH, "ab") as fh:
    fh.write(core_lf.replace(b"\n", eol))
    fh.write(ann.encode("utf-8").replace(b"\n", eol))

size_after = os.path.getsize(PATH)
print("APPEND OK core=%dB md5=%s eol=%s file=%dB cap=30720 headroom=%d"
      % (core_bytes, md5, "CRLF" if eol == b"\r\n" else "LF", size_after,
         30720 - size_after))
