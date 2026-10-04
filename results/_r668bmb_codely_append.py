# Append r668 bm-b pitlaw entry to CODELY.md (bytes-mode end-append, presence gate)
import io

ENTRY = """- [2026-10-04 12:0x r668 bm-b] finalize 完成≠池面翻面=autofill 重烧环实证（THEME-JUDGE-P1 实弹·r203 律代价面首证）：bm-a 10:26 finalize 判负落账全链（results JSON+attrition+ledger+prereg s7/s8）但 runnable_pool shard 停留 ready → bm-b autofill 11:36:28 tick 对同 shard 重复点火 447.8s 确定性重烧（r189 CTA-WAVE1 先例零害）直至 r668 轮 entry+shard 双翻面才止。律=判决批 finalize 收口轮必须同窗完成池面双翻（r244 landed-marker 律的漏翻代价面：未翻面=autofill 每 tick 重烧直到翻转）；收口自检=finalize 后立即探针本批 id 在池内 status==done，否则当窗补翻。附带=r655 双 Format-Table 空表错读本窗原样重犯自纠（inbox 假未读警报→显式分表复查=零未读）——该律执法面=复合清单命令一律 Write-Host 分表标题。
"""

with io.open("CODELY.md", "rb") as f:
    data = f.read()
assert data.count(b"[2026-10-04 12:0x r668 bm-b]") == 0, "entry already present"
sep = b"\n" if data.endswith(b"\n") else b""
with io.open("CODELY.md", "ab") as f:
    f.write(sep + ENTRY.encode("utf-8"))
with io.open("CODELY.md", "rb") as f:
    chk = f.read()
assert chk.count(b"[2026-10-04 12:0x r668 bm-b]") == 1, "append verify failed"
print("CODELY.md r668 entry appended, verify PASS | size:", len(chk))
