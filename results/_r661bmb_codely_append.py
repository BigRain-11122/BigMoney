# Append r661 bm-b pitlaw entry to CODELY.md Project section (bytes-mode, needle-count==1 gate)
import io

ENTRY = """- [2026-10-04 09:4x r661 bm-b] 探针单形假死读数×决策前双形交叉律（r659 姊妹面·QUALITY 收养核验实弹）：liveness 探针首读 pid 57116 "NOT FOUND"（CIM -Filter 单 pid 形）而全量扫 Where-Object 形证活——r641 复现律先跑再立法：四形对照复现证伪「CIM -Filter 假死坑」假说，真根=探针自身格式串 bug（`-Filter 'ProcessId=%d'` 占位符未 `% pid` 格式化=字面 %d 当 WQL→恒空结果→假死读数）；正法=①探针命令串内一切 % 占位符落盘后必实格式化（探针文件 review 首查项）②活性读数若驱动 claim-release/kill/respawn 类池面决策，必以独立第二形（全量扫+匹配）交叉证活才许动手——单形读数禁直接消费（本窗若无全量扫交叉，将误走 MSG-0915 item 2 的 release→re-light 路=烧毁在飞 QUALITY 判决批）。How to apply：写 pid 探针先自查占位符；「进程死了」读数与池面动作间必隔双形证据。
"""

with io.open("CODELY.md", "rb") as f:
    data = f.read()

needle = b"[2026-10-04 09:3x r660 bm-b]"
assert data.count(needle) == 1, "anchor needle count != 1"
assert data.count(b"[2026-10-04 09:4x r661 bm-b]") == 0, "entry already present"

# append at end of file (after last entry, keeping trailing structure)
sep = b"\n" if data.endswith(b"\n") else b""
with io.open("CODELY.md", "ab") as f:
    f.write(sep + ENTRY.encode("utf-8"))

with io.open("CODELY.md", "rb") as f:
    chk = f.read()
assert chk.count(b"[2026-10-04 09:4x r661 bm-b]") == 1, "append verify failed"
print("CODELY.md r661 entry appended, verify PASS | size:", len(chk))
