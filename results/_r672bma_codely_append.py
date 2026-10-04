# r672 bm-a CODELY.md one-line append (UTF-8, blank-line separated bullet)
import io

CP = r"CODELY.md"
line = (
    "- [2026-10-04 11:0x r672 bm-a] 轮号取号必读轮报告表尾坑（多会话窗实弹）：state.last_round/next 字段在"
    "先行会话收口后可陈旧（本窗 state.last_round=r668 而轮报告已进 r670/r671——先行会话更新了报表与心跳 "
    "epoch 但 last_round 字段停在旧值），按 state.next 取号=跳号重做已完工序（本例 finalize redo 幸有 r259 "
    "prev-echo 幂等守卫零双记·attrition 单条实证）。How to apply：开轮取号一律以 round_reports-<id>.md 表尾"
    "最大轮号+1 为准，state.next 仅作任务指针非轮号源；发现「next 所指工序已被更晚轮报告回执」即按已完处理"
    "转补缺面。附带（r458 姊妹面自证法）：水位键口径在 state 无 *_sha_method 键时以值长度自证"
    "（64-hex=SHA-256·40-hex=SHA-1），bm-a 双水位键均 SHA-256 勿套 r458 bm-c SHA-1 结论。\n"
)

t = io.open(CP, encoding="utf-8").read()
assert "r672 bm-a] 轮号取号" not in t, "already appended"
with io.open(CP, "a", encoding="utf-8", newline="\n") as f:
    if not t.endswith("\n"):
        f.write("\n")
    f.write("\n" + line)
re = io.open(CP, encoding="utf-8", errors="replace").read()
assert "r672 bm-a] 轮号取号" in re
print("CODELY OK len:", len(re))
