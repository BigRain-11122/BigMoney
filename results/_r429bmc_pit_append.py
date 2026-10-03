# -*- coding: utf-8 -*-
"""_r429bmc_pit_append.py -- r429 bm-c pit-ps.md append receipt (byte-level, CRLF face).

New pit: literal-replace no-match silent fallthrough x pattern-hit self-check
false positive (composite). Family: r420 needle-hit-furniture (assertion layer
false positives) + r428 Select-String self-check face, PS-host new instance.
"""
import hashlib

ENTRY = """- [2026-10-03 21:0x r429 bm-c] 字面替换未命中静默穿透×模式命中自证假阳性复合坑（S6 driver 跨轮适配实弹·r420 needle-furniture 族 PS 宿主新面·证据名覆写当场抓回零实伤）：.Replace('results/_r428bmc_s6_log.txt',…) 只命中文档串 docstring 同形文本，真目标 LOG 行是 os.path.join 分段字面量（"results", "_r428bmc_s6_log.txt"）零命中→替换静默穿透；自证 Select-String "_r429bmc_s6_log" -Quiet 命中的恰是已被换掉的 docstring=假阳性——r429 跑链日志写进 r428 证据文件名（M results/_r428bmc_s6_log.txt 现场=证据名覆写）。修法=①适配自证必须目标行级断言（regex ^LOG = 行含新名或 git diff 复核），禁文件级 pattern 命中当成功；②目标字面量替换前先数出现次数（b.count(needle)==1 型断言）再动手；③被覆写证据件从 HEAD blob python subprocess 原字节恢复（D-19 律）+修复后 driver 重跑幂等链重立证据名（_r429bmc_s6_log.txt 37/37 rc0 与首轮互证）。How to apply：一切「字面替换改代码/配置行」的跨轮适配（driver/模板/脚本复用）=数次数→替换→目标行断言三连；文件级 grep 命中≠目标行命中（r420 needle 避 furniture 律同源）。"""

eb = ENTRY.encode("utf-8")
b = open("research/pit-ps.md", "rb").read()
assert b.endswith(b"\r\n"), "file must end CRLF"
assert eb not in b, "entry already present"
open("research/pit-ps.md", "ab").write(eb + b"\r\n")
b2 = open("research/pit-ps.md", "rb").read()
assert eb + b"\r\n" in b2 and b2.startswith(b) and len(b2) == len(b) + len(eb) + 2
lf_face = hashlib.md5(eb + b"\n").hexdigest()
print("appended %dB (CRLF face) -> pit-ps.md size %dB" % (len(eb) + 2, len(b2)))
print("LF-blob face md5=%s (%dB)" % (lf_face, len(eb) + 1))
print("APPEND_OK")
