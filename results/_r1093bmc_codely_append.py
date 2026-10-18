# -*- coding: utf-8 -*-
# r1093 bm-c: append two pit entries to repo CODELY.md (fresh-read-edit-write per multi-writer law)
import io

PATH = "CODELY.md"
raw = io.open(PATH, encoding="utf-8", newline="").read()
eol = "\r\n" if raw.count("\r\n") >= raw.count("\n") - raw.count("\r\n") else "\n"

E1 = ("- [2026-10-18 16:0x r1093 bm-c] **fivekeys 锚精度坑（W269 实弹·fail-closed 首跑拦截）**："
      "克隆 fivekeys 脚本时把 cross-check 锚常数从 prereg §5 文字段抄（8 位小数舍入面，如 −0.09273778），"
      "与活读全精度实值（−0.09273778356481482）在 1e-9 容差断言下必炸。"
      "正法=锚常数一律从上一波 finalize 产物 JSON 机读全精度值（r587 live-read 律的克隆面），prereg 文字段只作叙述核对。")
E2 = ("- [2026-10-18 16:0x r1093 bm-c] **bm-c 仓 core.autocrlf=true smudge 面（W269 预检实弹）**："
      "本仓工作树文本件=origin blob 的 CRLF 再 smudge 形态（checkout 时 LF→CRLF）——盘面 raw 字节 sha/尺寸≠blob"
      "（如 W269 prereg 盘 23,270B vs blob 23,207B）但 norm-eq 恒真；git status 不显脏（check-in 归一后恒等）。"
      "冻结面/预检比对一律走 git-object 级（git show/rev-parse/hash-object 归一）或内容归一比对，"
      "禁 raw 盘面 vs blob 直比（假 DRIFT 判负）；编辑器 lineage 读 canon 用 newline='' 保真不变。")

assert raw.count(E1.split('**')[1]) == 0 and raw.count(E2.split('**')[1]) == 0, "dup guard"
marker = "### Reference"
i = raw.find(marker)
assert i > 0, "Reference marker missing"
ins = E1 + eol + E2 + eol + eol
t2 = raw[:i] + ins + raw[i:] if raw[i - len(eol) - len(eol):i] != eol + eol else raw[:i] + ins + raw[i:]
# simpler robust form: insert both lines + blank line right before the marker block
t2 = raw[:i].rstrip(eol) + eol + E1 + eol + E2 + eol + eol + raw[i:]
assert t2.count("r1093 bm-c]") == 2
io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
print("CODELY.md appended 2 entries; bytes", len(t2.encode("utf-8")))
