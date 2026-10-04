"""r705 bm-a: append ONE S4 memory entry to repo CODELY.md (byte-safe,
host-EOL detected per r485 law)."""
import datetime

ENTRY = (
    "- [2026-10-05 01:2x r705 bm-a] 无 workers_plan 池条目（prep/one-shot 类）的"
    "会话认领正法＝复用 Tools/autofill._claim_shard 正典（r199 launch-claim 全套"
    "内置：origin 三态预读 r694-i+lane 权威写+settle+self-commit r290+rebase-retry "
    "r282；import 安全=纯路径常量）+ r324 分离 spawn（-u 无缓冲+自写日志+close_fds "
    "r317+BelowNormal CEO 余量律）——S8 法（O-2130）下 autofill 永不认领无 "
    "workers_plan 条目，此类只能会话接（r423/r484 judge-prep 先例面正式化）；"
    "keepalive 面自动覆盖（r288 扫活 runner 进程，与认领来源无关）。实弹：N2-W15 "
    "JUDGE-PREP 认领 True→188s PASS→r489 双层翻面+r497 范式 12 分片入池。"
    "How to apply：未来 judge 波（W16+）prep 步照此路走，禁重写 claim 协议、"
    "禁无认领裸烧。\n"
)

path = "CODELY.md"
raw = open(path, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-500:] else b"\n"
if not raw.endswith(eol):
    raw += eol
raw += ENTRY.encode("utf-8")
open(path, "wb").write(raw)
print("appended", len(ENTRY.encode("utf-8")), "bytes; new size:",
      len(open(path, 'rb').read()))
