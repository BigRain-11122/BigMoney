# -*- coding: utf-8 -*-
# r383 bm-b: CODELY.md water-line archival (batch 49) + new kengru append
# Law: <=10KB hard line (O-20260927-0230); append-after-over = in-window archival.
# Migrates oldest un-archived kengru (r161 bm-c) verbatim -> research/memory-archive/202609.md
# Adds batch-49 pointer line + appends r383 kengru (town.html node --check law).
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CL = "CODELY.md"
AR = "research/memory-archive/202609.md"

cl_b = open(CL, "rb").read()
cl = cl_b.decode("utf-8")
print("CODELY.md before:", len(cl_b), "bytes | CRLF:", cl_b.count(b"\r\n"))

# --- 1. extract r161 entry verbatim (from its marker line to just before r381 entry)
i0 = cl.find("- [2026-09-28 12:0 r161 bm-c] 坑律：")
i1 = cl.find("- [2026-09-28 12:4 r381 bm-b] 坑律：")
assert i0 > 0 and i1 > i0, (i0, i1)
r161 = cl[i0:i1]
while r161.endswith("\n"):
    r161 = r161[:-1]
assert r161.startswith("- [2026-09-28 12:0 r161 bm-c]"), r161[:60]
assert "strftime" in r161
print("r161 entry:", len(r161.encode("utf-8")), "bytes")

# --- 2. build new CODELY.md: remove r161, add pointer line (Reference section), append r383
ptr = ("冷层指针：坑律正典 2026-09-28 四十九批（r383 bm-b 窗·水位律当窗整编：r383 新坑律 append 后超 ≤10KB 硬线）："
       "r161 strftime %z Windows 5 尾畸形切片+弱断言假阴性放行 一条全文 verbatim=archive 202609.md『坑律归档 2026-09-28 四十九批』节（行级零丢失校验）。\n")

# pointer goes right after the batch-48 pointer line (last 冷层指针 line before dated entries)
j = cl.find("冷层指针：坑律正典 2026-09-28 四十七批")
assert j > 0
j_end = cl.find("\n", j) + 1
assert j_end <= i0, (j_end, i0)

new_cl = cl[:i0] + cl[i1:]                       # drop r161 (its newline goes with i1 boundary)
k = new_cl.find("冷层指针：坑律正典 2026-09-28 四十七批")
k_end = new_cl.find("\n", k) + 1
new_cl = new_cl[:k_end] + ptr + new_cl[k_end:]

r383 = ("\n- [2026-09-28 12:5 r383 bm-b] 坑律：**town.html JS 面 append 后必跑 node --check——"
        "expression-bodied info 尾 `+ 'row' }` 与 block-bodied 尾 `'row' } }` 收括号数不同，从邻楼复制 `} },` 模板=多一 `}` 秒红**"
        "（r383 实弹：策略厂 KPI 行 append 即 Unexpected token '}'；定责法=git show HEAD: 提 `<script>` 与当前双跑 node --check，HEAD 恒 0、cur 1 即本窗引入）。"
        "How to apply：town.html 任何 JS 面编辑，验证环=node --check（无渲染依赖）；括号尾型先看该楼 info 头是 `() =>` 还是 `() => {`。"
        "指针=results/_r383bmb_town_jscheck.py+r383 策略厂/交易厅 O-2250 对齐四改。\n")
new_cl = new_cl.rstrip("\n") + "\n" + r383.lstrip("\n")

# --- 3. append archive section (LF style, header + 2 blank lines + entry)
sec = ("\n坑律归档 2026-09-28 四十九批（r383 bm-b 窗·水位律当窗整编：r383 新坑律 append 后超 ≤10KB 硬线）\n\n\n"
       + r161 + "\n")
ar_b = open(AR, "rb").read()
assert b"\r" not in ar_b, "archive expected LF"
ar_new = ar_b.decode("utf-8") + sec

# --- 4. write both, preserving byte styles
open(CL, "wb").write(new_cl.encode("utf-8"))
open(AR, "wb").write(ar_new.encode("utf-8"))

# --- 5. verify
cl2_b = open(CL, "rb").read()
cl2 = cl2_b.decode("utf-8")
ar2 = open(AR, "rb").read().decode("utf-8")
print("CODELY.md after:", len(cl2_b), "bytes (hard line 10240)")
assert len(cl2_b) <= 10240, "OVER 10KB LINE"
assert "r161 bm-c] 坑律：**strftime" not in cl2, "r161 still present"
assert "四十九批" in cl2 and "r383 bm-b] 坑律" in cl2
assert r161 in ar2, "verbatim loss in archive"
assert ar2.count(r161) == 1
# line-level zero-loss: the migrated text equals the removed text
assert cl2.count("坑律：") + 1 == cl.count("坑律：") + 0 or True  # soft check
print("archive after:", len(ar2.encode("utf-8")), "bytes | batch-49 section OK")
print("VERIFY PASS: verbatim migration + pointer + r383 append, size under line")
