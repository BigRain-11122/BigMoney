# -*- coding: utf-8 -*-
"""r479 bm-c S4: one pit line append (CODELY union superseded-variant containment law)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

LINE = ("- [2026-10-04 14:58 r479 bm-c] CODELY/append-only union 被取代变体子串遏制律"
        "（r675 块级 union 律新面·r676 同令并发 race 实弹）：双侧同条目异形时（本例=我侧 "
        "r675 bm-b 条目 bullet-less 变体〔r417/r669 2B 缺陷族〕vs origin 侧同条目已 2B 归正"
        "带 bullet）——exact-line diff 会把缺陷变体误判为「我侧新增行」，裸 union=同条目双录"
        "（r453 dedup 违例）；且 union.count(ln) 计的是子串非行（缺陷行=origin 固定行的子串"
        "→count==2 断言当场拦）。正法=missing 行集先过字节遏制滤（ln in theirs_blob 即弃"
        "=origin 已携同条目归正式·追加双录禁），真新增行（非子串）才按序追加；配 origin 前缀"
        "恒等+真新增行恰一次断言。探针=results/_r479bmc_codely_debug.py（missing 清单先行"
        "再手术）；执法件=results/_r479bmc_merge_resolve.py resolve_codely。How to apply："
        "未来三机同窗 race 的 CODELY union 一律先跑 missing 清单探针，见「我侧行是 origin 行"
        "子串」即按本律弃录勿双录。")

cp = os.path.join("CODELY.md")
with open(cp, "rb") as f:
    raw = f.read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
needle = "r479 bm-c] CODELY/append-only union".encode("utf-8")
assert raw.count(needle) == 0, "pit line already present"
line = LINE.encode("utf-8") + eol
with open(cp, "ab") as f:
    f.write(line)
with open(cp, "rb") as f:
    raw2 = f.read()
assert raw2.count(needle) == 1 and raw2 == raw + line
print("PITLINE OK bytes=%d" % len(line))
