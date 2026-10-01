# r524 bm-a: CODELY.md lesson append (S4 memory step).
# One matter: post-surgical-push reset --mixed leaves the working tree
# STALE vs origin until checkout -- dependency checks in that window must
# read origin refs (git show / ls-tree), not the local tree.
path = "CODELY.md"
raw = open(path, encoding="utf-8", newline="").read()
assert not raw.startswith("\ufeff"), "BOM drift"
entry = (
    "- [2026-10-01 16:5x r524 bm-a] 外科推送后 reset --mixed 工作树滞后窗坑"
    "（W12 finalize 前置检查实弹近误）：surgical temp-index 推送+reset --mixed "
    "重锚后，HEAD/索引=origin 而工作树仍=旧基——Test-Path 读本地树得 "
    "n1_w11_results.json=False（origin 实际在场，ls-tree 秒证）＝依赖检查差点误判"
    "「W11 finalize 未落账」；正解=reset 后未 checkout 前一切依赖/在场检查走 "
    "origin refs（git show origin/main:<path> / git ls-tree），checkout 同步完成"
    "后本地树才恢复真值面。连带小坑=append 型共享 jsonl 勿 sorted() 全集重排"
    "（本窗 pool_core_samples 43 行假 diff 当场抓回重做为最小 append 1 行）。"
    "How to apply：一切「surgical 推送→reset --mixed」序列后，先批量 checkout "
    "origin-owned 面再进依赖检查；append-union 写后 diff --stat 断言行数=新增行数。\n"
)
if not raw.endswith("\n"):
    raw += "\n"
open(path, "w", encoding="utf-8", newline="").write(raw + entry)
import os
print("appended; new size:", os.path.getsize(path), "bytes")
