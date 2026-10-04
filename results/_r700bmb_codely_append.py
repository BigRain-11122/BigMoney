# r700 bm-b: append one new pit entry to CODELY.md main (EOL-true, idempotent)
import os
ENTRY = ("- [2026-10-04 23:3x r700 bm-b] schtasks /query /xml 的 python subprocess 解码面假空坑"
          "（D-02 自证窗实弹·r676① 编码面族 python 侧新形态）："
          "`subprocess.run([\"schtasks\",\"/query\",\"/tn\",t,\"/xml\"])` 的 stdout 按 `utf-16` 解码"
          "在无控制台宿主下拿到 GBK 输出→mojibake 串→`<LogonType>` 正则零命中="
          "**五任务全「LogonType 空」假读数**（幸 r661 双形交叉律在先：PS `schtasks /query /xml` "
          "直读实为 S4U×4+InteractiveToken×1——若按单形消费即产出「全线无 LogonType」错误自证）。"
          "正法=①schtasks XML 判读一律 PS 直读（无歧义判读面·r676① 律）"
          "②python 探针消费 schtasks 输出时先 decode(\"gbk\"/\"utf-16\") 双形试解"
          "+LogonType 元素存在性断言（缺失≠空）③单形读数禁直接消费（r661 律再犯面）。\n")
raw = open("CODELY.md", "rb").read()
marker = "r661 律再犯面）。"
if marker.encode("utf-8") in raw:
    print("already appended, skip")
    raise SystemExit(0)
eol = b"\r\n" if b"\r\n" in raw else b"\n"
body = raw[:-1] if raw.endswith(b"\n") else raw
entry_b = ENTRY.replace("\n", "\r\n").encode("utf-8") if eol == b"\r\n" else ENTRY.encode("utf-8")
open("CODELY.md", "wb").write(body + eol + eol + entry_b)
print("appended", len(entry_b), "bytes; new size", os.path.getsize("CODELY.md"))
