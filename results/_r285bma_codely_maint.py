"""R285 bm-a: root CODELY.md hot-cold maintenance (D-20260925-01④).

1) Archive the single flow-type entry (执行记录, 2026-09-26 23:31:09) to
   research/memory-archive/202609.md per the 冷层指针 (line-level
   zero-loss: removed line must exist verbatim in archive).
2) Append one new trap-law entry (judged-batch harvest closure gap).
3) Verify sizes/faces and the <50KB watermark after the append.
"""
import io

ROOT = "CODELY.md"
ARCH = "research/memory-archive/202609.md"

raw = open(ROOT, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
text = raw.decode("utf-8-sig")
eol_crlf = "\r\n" in text
print("root: bom=%s crlf=%s len=%d" % (bom, eol_crlf, len(raw)))

lines = text.split("\n")
flow_marker = "- [2026-09-26 23:31:09] 执行 O-20260926-2330"
hits = [i for i, l in enumerate(lines) if l.startswith(flow_marker)]
assert len(hits) == 1, "flow line not uniquely found: %s" % hits
idx = hits[0]
flow_line = lines[idx]
print("flow line len(bytes)=%d" % len(flow_line.encode("utf-8")))

# ---- remove flow line (keep structure: drop the line + its newline) ----
del lines[idx]
new_text = "\n".join(lines)

# ---- append new trap-law entry at end (file currently ends with newline) ----
assert new_text.endswith("\n"), "root must keep trailing newline"
entry = (
    "- [2026-09-27 02:2x] 坑律（bm-a R285·judged 批收割闭环缺口面·复审器盲区维·E1 收割后自捕）："
    "**收割 commit 落地判定≠批闭环——r282 harvest（a0425122）落了判定+池 flip+attrition 三面"
    "却漏 prereg §7/§8 回填与 post_review 行注册=验收腿静默开（行未注册=复审器结构性盲区，"
    "缺口无 ✗ 红可见=比红更险的静默绿）**；正律=judged 批收割同轮三件套齐="
    "①判定+attrition 入账②prereg §7/§8 一次定稿③post_review 行注册（稳定产物锚·D-20260927-04 律）"
    "——「同轮收割」（r244）的语义=回填+注册含在内非仅池 flip；自检法=收割 commit 后必查"
    "该批 prereg §7 非占位+criteria 含该批行。指针=R285 slice-a/b 实录（REV-OSC 补回填+注册"
    " 32→33 YES·CN-SOE 三件套同轮齐 17 checks YES）\n"
)
new_text += entry

out = ("\ufeff" if bom else "") + new_text
data = out.encode("utf-8")
with open(ROOT, "wb") as fh:
    fh.write(data)
print("root written: %d bytes" % len(data))

# ---- archive append (verbatim flow line, tail newline exists) ----
araw = open(ARCH, "rb").read()
assert araw.endswith(b"\n"), "archive must keep trailing newline"
with open(ARCH, "ab") as fh:
    fh.write(flow_line.encode("utf-8") + b"\n")
print("archive: +%d bytes -> %d" % (len(flow_line.encode("utf-8")) + 1,
                                    len(araw) + len(flow_line.encode("utf-8")) + 1))

# ---- zero-loss verification ----
back_root = open(ROOT, "rb").read()
back_arch = open(ARCH, "rb").read()
assert flow_line.encode("utf-8") in back_arch, "archived line lost"
assert flow_line not in back_root.decode("utf-8-sig"), "flow line still hot"
root_size = len(back_root)
print("VERIFY ok: flow line archived verbatim; removed from hot; root=%d bytes "
      "(<50KB watermark: %s)" % (root_size, root_size < 51200))
