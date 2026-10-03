# -*- coding: utf-8 -*-
"""r447 bm-c D-06 final-sweep closure ops (after codely heal):

  OP1 flow-sinking (r444 paradigm): r635 bm-b + r644 bm-a O-2030 receipt
      entries -> research/memory-archive/202610.md verbatim; CODELY.md keeps
      one 冷层指针 line in the Reference section.
  OP2 pit-git.md assert-layer ruling line (r402/r419/r420 stay in pit-git).
  OP3 pit-encoding.md direct-write line (Windows-CP936 reverse-map heal law).
  OP4 CODELY.md campaign-closure line (T-144(c) D-06 full close).
  OP5 T-2026-10-02-144-P1 ticket flip claimed -> done.

Laws: r632 three-step byte surgery; r620/r420 needle-count==1 (needles carry
entry bodies, no bare furniture); r645 state-write programmatic + read-back
verify; ASCII-only stdout.
Exit 0 all-green, 2 assertion fail (no write), 1 unexpected.
Receipt: results/_r447bmc_d06_sink.json
"""
import hashlib, io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCH = os.path.join(ROOT, "research", "memory-archive", "202610.md")
PITGIT = os.path.join(ROOT, "research", "pit-git.md")
PITENC = os.path.join(ROOT, "research", "pit-encoding.md")
TICKET = os.path.join(ROOT, "fleet", "tasks", "T-2026-10-02-144-P1.json")
RECEIPT = os.path.join(ROOT, "results", "_r447bmc_d06_sink.json")

def fail(msg, extra=None):
    rec = {"status": "FAIL", "reason": msg}
    if extra:
        rec.update(extra)
    with io.open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("FAIL " + msg)
    sys.exit(2)

N_R635 = "- [2026-10-03 22:1x r635 bm-b] O-20261003-2030 CEO 宝藏保护令执行回执"
N_R644 = "- [2026-10-03 22:1x r644 bm-a] O-20261003-2030 宝藏保护令 bm-a 回执"
POINTER = "- 冷层指针（r447 bm-c 合并·指针合并归档 r444 范式）：r635 bm-b O-20261003-2030 宝藏保护令执行回执+r644 bm-a O-20261003-2030 宝藏保护令回执——两条全文 verbatim=archive 202610.md『热冷整编 2026-10-04 r447 bm-c 窗批』节；正典=令件 fleet/orders/O-20261003-2030*.md+守门引擎 Tools/treasure_guard.py。"
ARCH_HEAD = "## 热冷整编 2026-10-04 r447 bm-c 窗批"
ARCH_DESC = "（T-144(c) D-06 流水下沉腿·r444 范式·字节零丢失校验；r635 bm-b+r644 bm-a O-2030 宝藏保护令回执两条——CODELY.md 热层 verbatim 迁入；同窗=D-06 全线收口提前窗（原定 10-07）。）"
PITGIT_LINE = "> 收口行（r447 bm-c·T-144(c) D-06 final-sweep 断言层 increment 裁定）：r402/r419/r420 三条拆件断言层 direct-write 条目留驻本件（域归属定谳=git 面字节手术/对账断言族——与 r429 LF-blob 追加核、r439/r441 拆件批次断言层、r440 预对齐 blob 恒等断言同域·消费面=git 面字节手术与 staged 前对账必读）·不外迁；D-06 断言层悬项收口（提前窗 2026-10-04·原定 10-07）。"
PITENC_LINE = "- 直写行（r447 bm-c·Windows CP936 管线 mojibake 逆映射治愈律）：CODELY.md GBK mojibake 尾巴治愈实弹三律——①Python cp936 ≠ Windows CP936：逆映射须补 0x80→U+20AC 与 Microsoft PUA 三区（Z1 U+E000..E233=leads AA-AF×trails A1-FE·Z2 U+E234..E4C5=F8-FE×A1-FE·Z3 U+E4C6..E759=A1-A7×40-A0 除 7F）——纯 Python cp936 往返 20/20 全败，勿据此判不可恢复；②mojibake 内字面 '?'=.NET DecoderFallback 每 '?' 一丢字节——严格字节恢复恒不可得，零丢失证明降级=分段 containment（噪声位切分→净段≥12 字全文在场+段级 gram≥0.85+边缘修剪容错对齐残字）；③无在场可读孪生的条目（本例 r657 bm-a 两条被吞）自 git 史原 commit blob 原文复位（r407 事实重建律·出处留痕 receipt）。How to apply：会话壳/PS 管线产 mojibake 先跑 Windows-CP936 逆映射探针再定不可恢复；治愈手术=三步分离+组件和恒等+隔离区 manifest（范式=results/_r447bmc_d06_codely_heal.py）。"
CLOSURE = "- [2026-10-04 06:4x r447 bm-c] D-06 全线收口（T-144(c) final-sweep 提前窗·原定 10-07）：①pit-data CRLF 面=r420 已零动作收口（pit-data 收口行为准）②拆件断言层 r402/r419/r420 final-sweep 裁定=三条留驻 pit-git（收口行在件）③流水下沉=r635 bm-b+r644 bm-a O-2030 回执两条 verbatim→archive 202610.md『热冷整编 2026-10-04 r447 bm-c 窗批』节（冷层指针行在本件）④CODELY.md GBK mojibake 尾巴治愈（r660 bm-a 治愈候选·D-06 窗裁定执行：Windows CP936 逆映射+分段 containment 零丢失证明 17/17·r657 两条按 git 史 2c0c6dcf5 原文复位·r438 重复/r641 合并拆分·mojibake 块 42,873B 入隔离区 manifest·receipt=results/_r447bmc_d06_codely_heal.json）；T-144 全票面收口。"

# ---------- OP1a: CODELY.md receipts removal + pointer insert ----------
raw = open(CODELY, "rb").read()
if not (raw.count(b"\r") == raw.count(b"\r\n") == raw.count(b"\n")):
    fail("CODELY EOL census not pure CRLF")
blines = raw.split(b"\r\n")
texts = [b.decode("utf-8", "replace") for b in blines]
i635 = [i for i, t in enumerate(texts) if t.startswith(N_R635)]
i644 = [i for i, t in enumerate(texts) if t.startswith(N_R644)]
if len(i635) != 1 or len(i644) != 1:
    fail("receipt needles not unique", {"i635": i635, "i644": i644})
i635, i644 = i635[0], i644[0]
if not (i644 == i635 + 2 and texts[i635 + 1] == ""):
    fail("receipt pair not adjacent-with-blank", {"i635": i635, "i644": i644})
cp_last = [i for i, t in enumerate(texts) if t.startswith("- 冷层指针")]
if not cp_last:
    fail("no cold-pointer lines found for insertion point")
insert_at = cp_last[-1] + 1

r635_bytes = blines[i635]
r644_bytes = blines[i644]

new_list = []
for i, b in enumerate(blines):
    if i in (i635, i635 + 1, i644):
        continue
    new_list.append(b)
    if i == insert_at - 1 and i not in (i635, i635 + 1, i644):
        pass
# insert pointer after the last cold-pointer line (recompute in new coords)
pos = insert_at - sum(1 for x in (i635, i635 + 1, i644) if x < insert_at)
new_list.insert(pos, POINTER.encode("utf-8"))
# closure line at end (file ends with trailing CRLF -> last piece empty)
if new_list and new_list[-1] != b"":
    fail("file does not end with trailing CRLF piece")
new_list.insert(len(new_list) - 1, CLOSURE.encode("utf-8"))
new_raw = b"\r\n".join(new_list)
# component identity
kept_sum = sum(len(b) for i, b in enumerate(blines) if i not in (i635, i635 + 1, i644))
expected = kept_sum + len(POINTER.encode("utf-8")) + len(CLOSURE.encode("utf-8")) \
    + 2 * (len(new_list) - 1)
if expected != len(new_raw):
    fail("CODELY component-sum mismatch", {"expected": expected, "actual": len(new_raw)})

# ---------- OP1b: archive append ----------
arch = open(ARCH, "rb").read()
if not arch.endswith(b"\r\n"):
    fail("archive does not end with CRLF")
arch_append = (ARCH_HEAD + "\r\n\r\n" + ARCH_DESC + "\r\n\r\n").encode("utf-8") \
    + r635_bytes + b"\r\n" + r644_bytes + b"\r\n"
new_arch = arch + arch_append

# ---------- OP2: pit-git ruling line ----------
pg = open(PITGIT, "rb").read()
if not pg.endswith(b"\r\n"):
    fail("pit-git does not end with CRLF")
new_pg = pg + (PITGIT_LINE + "\r\n").encode("utf-8")

# ---------- OP3: pit-encoding direct-write line ----------
pe = open(PITENC, "rb").read()
if not pe.endswith(b"\r\n"):
    fail("pit-encoding does not end with CRLF")
new_pe = pe + (PITENC_LINE + "\r\n").encode("utf-8")

# ---------- OP5: ticket flip ----------
with io.open(TICKET, encoding="utf-8-sig") as f:
    tk = json.load(f)
if tk.get("status") != "claimed":
    fail("ticket not in claimed state: " + str(tk.get("status")))
tk["status"] = "done"
tk["progress_r447_bmc"] = ("r447 bm-c: D-06 final-sweep EARLY CLOSE (scheduled 10-07, executed 10-04) -- "
    "(1) CODELY.md GBK mojibake tail L69-L87 healed one-window: 17 duplicate lines deleted (win-cp936 "
    "reverse-map recovery + segment-containment zero-loss proof 17/17 + entry-key twins), 2 r657 bm-a "
    "pit entries re-instated verbatim from git history 2c0c6dcf5 (crash-window swallowed bm-a's "
    "readables; bm-b r646 'genuinely new' note + bm-a r660 heal-candidate adjudicated at this D-06 "
    "window), r438-dup/r641 merged line split; 42,873B removed to quarantine manifest; file "
    "86,416B -> 42,401B; receipt results/_r447bmc_d06_codely_heal.json ALL_GREEN. "
    "(2) assert-layer final-sweep ruling: r402/r419/r420 stay in pit-git.md (ruling line in-file). "
    "(3) flow-sinking r444-paradigm: r635 bm-b + r644 bm-a O-2030 receipts verbatim -> archive "
    "202610.md + cold-pointer line. (4) pit-data CRLF face already closed r420 (zero-action, "
    "in-file receipt line). (5) pit-encoding direct-write: win-cp936 reverse-map heal law.")
tk["result_ref"] = ("results/_r447bmc_d06_codely_heal.json (ALL_GREEN) + results/_r447bmc_d06_sink.json "
    "+ pit-git/pit-encoding closure lines + archive 202610.md r447 batch")
with io.open(TICKET, "w", encoding="utf-8", newline="\n") as f:
    json.dump(tk, f, ensure_ascii=False, indent=1)
with io.open(TICKET, encoding="utf-8-sig") as f:
    if json.load(f).get("status") != "done":
        fail("ticket read-back verify failed")

# ---------- writes (r632: single independent wb per file) ----------
with open(CODELY, "wb") as f:
    f.write(new_raw)
with open(ARCH, "wb") as f:
    f.write(new_arch)
with open(PITGIT, "wb") as f:
    f.write(new_pg)
with open(PITENC, "wb") as f:
    f.write(new_pe)

# ---------- read-back verification ----------
raw2 = open(CODELY, "rb").read()
t2 = [b.decode("utf-8", "replace") for b in raw2.split(b"\r\n")]
ok_removal = sum(1 for t in t2 if t.startswith(N_R635) or t.startswith(N_R644)) == 0
ok_pointer = sum(1 for t in t2 if t.startswith("- 冷层指针（r447 bm-c 合并")) == 1
ok_closure = sum(1 for t in t2 if t.startswith("- [2026-10-04 06:4x r447 bm-c] D-06 全线收口")) == 1
ok_eol = raw2.count(b"\r") == raw2.count(b"\r\n") == raw2.count(b"\n")
arch2 = open(ARCH, "rb").read()
ok_arch = (ARCH_HEAD.encode("utf-8") in arch2 and r635_bytes in arch2 and r644_bytes in arch2)
pg2 = open(PITGIT, "rb").read()
ok_pg = PITGIT_LINE.encode("utf-8") in pg2
pe2 = open(PITENC, "rb").read()
ok_pe = PITENC_LINE.encode("utf-8") in pe2
ok = ok_removal and ok_pointer and ok_closure and ok_eol and ok_arch and ok_pg and ok_pe

receipt = {"status": "OK" if ok else "VERIFY-FAIL",
           "codely": {"bytes": len(raw), "->": len(raw2), "receipts_removed": 2,
                      "pointer_line": ok_pointer, "closure_line": ok_closure, "eol_pure_crlf": ok_eol},
           "archive_202610": {"bytes": len(arch), "->": len(arch2), "receipts_verbatim": ok_arch},
           "pit_git_ruling": ok_pg, "pit_encoding_direct_write": ok_pe,
           "ticket_T-144": "done (read-back verified)",
           "all_green": bool(ok)}
with io.open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(("SINK-OK " if ok else "VERIFY-FAIL ") + "codely %d->%d arch %d->%d" % (
    len(raw), len(raw2), len(arch), len(arch2)))
sys.exit(0 if ok else 2)
