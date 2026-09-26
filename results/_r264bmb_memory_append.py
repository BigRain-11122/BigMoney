# r264 bm-b: S4 memory append (one entry) + HQ-FEEDBACK fleet suggestion row.
# Byte faces mirrored from probes: CODELY.md LF/no-BOM/single tail-NL;
# HQ-FEEDBACK.md CRLF/no-BOM/tail-NL.
import os

# --- CODELY.md (root memory, LF) ---
P1 = "CODELY.md"
raw = open(P1, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf") and b"\r\n" not in raw and raw.endswith(b"\n")
entry = (
    "- [2026-09-26 17:5x] 坑律（bm-b r264·post_review R256 二犯·热票 git 检查 depth 缓解非根治·E1 轮首自捕）："
    "**depth=30 窗在 ~11 轮双机 progress 追加下照 rot（R256 的 depth 修复=延时非根治）**；"
    "正律=git_log_file 检查一律锚「唯一 commit 触及的稳定产物件」（一次性 harvest/探针脚本类=窗口结构性永不可 rot），"
    "热票面任何 depth 禁作检查锚；rot 行修复律照 R256=事实 git 实证预验+同冻结事实耐久再编码+_reconciled 留痕，禁删检查翻绿。"
    "指针=results/_r264bmb_postreview_reanchor.py+results/post_review_criteria.json _reconciled r264 行\n"
)
assert entry.encode("utf-8") and len(entry.encode("utf-8")) < 1536
open(P1, "wb").write(raw + entry.encode("utf-8"))
print("CODELY.md appended, new size:", len(raw) + len(entry.encode("utf-8")))

# --- HQ-FEEDBACK.md (CRLF, fleet suggestion) ---
P2 = "HQ-FEEDBACK.md"
raw2 = open(P2, "rb").read()
assert not raw2.startswith(b"\xef\xbb\xbf") and b"\r\n" in raw2 and raw2.endswith(b"\r\n")
frow = (
    "- F-20260926-06 [bm-b r264 2026-09-26 17:5x·O-2115 复审门·机队级注册律建议] "
    "**post_review git_log_file 检查锚热票面禁令（R256 二犯实证）**——depth=30（R256 正典修复参数）"
    "在双机每轮追加 progress 的 CEO 票上 ~11 轮即挤出窗，复审假红 ✗ 二连（bm-a R256 depth-5 一犯、bm-b r264 depth-30 二犯）；"
    "证据=results/post_review.jsonl 2026-09-26 16:21/17:19 两 NO 行均 git_log_file:no git hit+results/_r264bmb_postreview_reanchor.py；"
    "建议方向=集团法例化「复审检查禁锚热票面任何 depth，必须锚唯一 commit 稳定产物件或 json_field 面」（与既有 R256 律互补：R256 给了 depth 参数，本建议收回热票面使用权）；"
    "状态=本司已按此执行自纠，待集团收取\n"
).replace("\n", "\r\n")
open(P2, "wb").write(raw2 + frow.encode("utf-8"))
print("HQ-FEEDBACK appended")
