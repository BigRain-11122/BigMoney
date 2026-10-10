"""r827 bm-b: direct-write pit entry into pit-git-racewin.md (r666 exception,
CODELY main at 30,384B near cap). UTF-8 append."""
import io
import os

entry = (
    "- [2026-10-10 09:5x r827 bm-b] 共享队列 md 行编辑 insert-未-replace 双行缺陷+跨机 union 治愈律"
    "（E6 撞窗实弹·bm-a r949 推面 explore.md 同项双行：stale open 行与 r949 done 行并存=行编辑插新未删旧）："
    "队列行 done 翻面必须 replace 旧行、禁插新增行（同项双行=消费面与 T-18 探针 head 定位双读·状态面自相矛盾）；"
    "跨机 union 解时按「一行一项」治愈=保 done 弃 stale+回执留痕（他机内容零丢失）；"
    "resolver 断言面=每项行数恰一级别（count('| E6 |')==1）。"
    "How to apply：编辑共享队列/名册 md 行先查同项行数恰一；union 后逐项断言恰一行；"
    "发现他机双行缺陷=治愈+轮报告注明（勿盲保双行勿盲保「他机原文」表象）。\n"
)
path = os.path.join("research", "pit-git-racewin.md")
with io.open(path, "a", encoding="utf-8", newline="\n") as f:
    f.write(entry)
print("appended, new size:", os.path.getsize(path))
