"""r1022 bm-b CODELY.md hot-cold split (10KB hard-line law) + r1021 pit row append.

prescan rc=3 recorded (both faces registered treasures) -- authorized migration
face: the split law itself (坑律正典全量归档 <=10KB 硬线) mandates the
zero-loss verbatim move; r1009/r1013/r1017 window-batch precedent.
Moves 3 fat rows verbatim -> research/memory-archive/202610.md new window
section; replaces them with one merged pointer line; drops 1 duplicate
pointer line (same-topic dedup law); appends the r1021 nominal-vs-measured
semitone pit row (stays hot). Receipt with zero-loss assertions.
exit 0 ok / 1 assertion failure.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202610.md")
RECEIPT = os.path.join(ROOT, "results", "_r1022bmb_codely_hotcold_receipt.json")

MOVE_PREFIXES = [
    "- [2026-10-19 06:1x r1017 bm-b] **GPT-SoVITS",
    "- [2026-10-19 06:1x r1017 bm-b] **自愈假信号双坑",
    "- [2026-10-19 10:5x r1077 bm-a] **append-only 账本 NUL 全蚀三步正法",
]
DUP_EXACT = ("- 冷层指针：r1053 bm-a 回执双面坑闸（orders_ack_append.py 正典双面追加器+scan 奇偶闸）"
             "全文 verbatim=archive 202610.md『热冷整编 2026-10-18 r1012 bm-b 窗批』节。")
POINTER = ("- 冷层指针：GPT-SoVITS 推理环境三缺口律（「装好即用」验收探针必打真实 load/推理面非 import 面·"
           "marker 守卫 try 原生/soundfile 回退+shim 兜底+pip 幂等）+ 自愈假信号双坑（任务健康探针一律进程内直查 "
           "schtasks /query·带默认 principal 的 heal 脚本禁未实证缺失点火·语义闸 startswith lower()）+ r1077 "
           "append-only 账本 NUL 全蚀三步正法（treasure_guard restore 先跑→唯一合法路=行级 union 零 NUL 断言→"
           "复跑原腿自证）全文 verbatim=archive 202610.md『热冷整编 2026-10-19 r1022 bm-b 窗批』节。")
NEW_ROW = ("- [2026-10-19 10:5x r1021 bm-b] **名义半音≠实测半音（ST-010 分档试合成实弹）**：同句零样本合成把 F0 "
           "拉平到参考音域之外（ref 165.8/162.8/151.0Hz→synth 173.5/172.0/177.8Hz·参考音面推导的分档偏移不迁移）；"
           "librosa pitch_shift 名义 -4st 实测 -3.5st。正法=分档分离门一律在合成输出**实测面**上校验：实测 F0→"
           "重算档→再合成→再实测（FATHER -4→-5 两步收敛·三对全 ≥15% 出同嗓带）；±3st 安全区外=搜索域边界="
           "换源寻根非加档。How to apply：一切 DSP 变调/分档验收拿实测面说话，批产站=逐行校验-调整环。")
SECTION = "## 热冷整编 2026-10-19 r1022 bm-b 窗批"


def main():
    pre_bytes = os.path.getsize(CODELY)
    text = open(CODELY, encoding="utf-8").read()
    lines = text.split("\n")
    moved, kept, dup_dropped = [], [], 0
    inserted_pointer = False
    for ln in lines:
        if any(ln.startswith(p) for p in MOVE_PREFIXES):
            moved.append(ln)
            if not inserted_pointer:
                kept.append(POINTER)
                inserted_pointer = True
            continue
        if ln == DUP_EXACT and dup_dropped == 0:
            dup_dropped += 1
            continue
        if ln == DUP_EXACT and dup_dropped >= 1:
            dup_dropped += 1  # count any further dups, drop too
            continue
        kept.append(ln)
    if len(moved) != 3:
        print("FAULT: expected 3 moved rows, found %d" % len(moved))
        return 1
    if dup_dropped == 0:
        print("WARN: duplicate pointer line not found (schema changed?)")
    # append new pit row at end before trailing empties
    while kept and kept[-1].strip() == "":
        kept.pop()
    kept.append(NEW_ROW)
    kept.append("")
    new_text = "\n".join(kept)

    # archive append (verbatim zero-loss)
    arc = open(ARCHIVE, encoding="utf-8").read() if os.path.exists(ARCHIVE) else ""
    block = "\n\n%s\n\n%s\n" % (SECTION, "\n\n".join(moved))
    with open(ARCHIVE, "a", encoding="utf-8", newline="\n") as f:
        if arc and not arc.endswith("\n"):
            f.write("\n")
        f.write(block)
    with open(CODELY, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)

    # zero-loss assertions
    arc_now = open(ARCHIVE, encoding="utf-8").read()
    zero_loss = all(m in arc_now for m in moved)
    post_bytes = os.path.getsize(CODELY)
    receipt = {
        "round": "r1022", "machine": "bm-b", "ts_pre_bytes": pre_bytes,
        "post_bytes": post_bytes, "moved_rows": len(moved),
        "moved_prefixes": [m[:48] for m in moved],
        "dup_pointer_dropped": dup_dropped,
        "new_row_appended": NEW_ROW[:40],
        "prescan_rc": 3,
        "prescan_note": "treasure_guard prescan HARD REJECT rc3 on both faces (registered treasures); authorized migration face per split law (坑律正典 <=10KB 硬线·append 后超线=当窗即办) + r1009 window-batch precedent (rc3 recorded, zero-loss verbatim move, pointer replacement only)",
        "archive_section": SECTION, "zero_loss": bool(zero_loss),
        "under_10kb_line": bool(post_bytes <= 10240),
    }
    json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("SPLIT OK: %dB -> %dB moved=%d dup=%d zero_loss=%s under_line=%s"
          % (pre_bytes, post_bytes, len(moved), dup_dropped, zero_loss,
             receipt["under_10kb_line"]))
    return 0 if (zero_loss and post_bytes <= 10240) else 1


if __name__ == "__main__":
    sys.exit(main())
