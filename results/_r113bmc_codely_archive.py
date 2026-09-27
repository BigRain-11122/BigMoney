"""R113 bm-c: CODELY.md batch-35 hot-cold archival (10,322B > 10,000B line).

O-20260927-0230 law: append-window over-line -> in-window archival.
Batch number 35 per r176 yield law (34 declared origin-first by bm-b r346).
Migrates 6 migration-history rows verbatim to archive, leaves one folding
pointer line + one new pit-law row (r239 claim-fetch atomic-window law).
Zero-loss assertion: every migrated row byte-present in archive post-append.
"""
import io

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

ROWS = [
    "- 二十七批外迁（r101 bm-c·2026-09-27·水位律当窗整编·指针行二次折叠·行级零丢失）：r91 S0 stash-pop 定侧源、r334 rolling-ledger dedup 面实时间键（二十三/二十六批双记）、r335 tick add/stash 不受 r201 护栏（二十五/二十六批双记）、r339 blob 尾态字节拼接、r340 round_no %5 义务撞窗漏做、r341 stale-takeover 双证并取——8 指针行原样外迁=archive 202609.md『坑律归档 2026-09-27 二十七批』节（所指 verbatim 皆在对应批节在位）。",
    "- 二十六批外迁（r341 bm-a·2026-09-27·二次撞头当窗整编·行级零丢失）：bm-b r336 与本机 r341 同窗双整编，r176 让号律=本机 25 批节自重编为 26 批；bm-b 侧保留行 22 条+本机律行变体 1 条外迁=archive 202609.md『坑律归档 2026-09-27 二十六批』节；保留=法行 2+23/24/25 批指针 5+新指针 3。",
    "- 二十九批外迁（r109 bm-c·2026-09-27·贴线当窗整编·行级零丢失）：r96（二十八批双记）/r345/r100/r350/r101/r340bmb/r351×2/r353/r355 共 10 条全文 verbatim=archive 202609.md『坑律归档 2026-09-27 二十九批』节；保留=User 元律+法行 2+冷层指针+23/24-28 批指针行族；CODELY.md 由 9,962B 降至水位线下。",
    "- 三十批外迁（r110 bm-c·2026-09-27·超线 14,690B 当窗整编·行级零丢失）：r342 bm-b 全文 verbatim=archive 202609.md『坑律归档 2026-09-27 三十批』节；r96/r345/r100/r350/r101/r340bmb/r351×2/r353/r355 十条=二十九批节（r96 二十八批双记）已录全文本行同窗 union 吸收回潮再折叠（archive 在位核验 10/10 全过）；保留=User 元律+法行 2+冷层指针+批指针行族+r109 律+r110 律。",
    "- 三十一批外迁（r359 bm-a·2026-09-27·同窗撞批号让号重编 r176 律·行级零丢失）：本机同窗独立整编批（原三十批号让 origin r110 bm-c 批）——r109bmc/r342bmb/r359bma 三行 verbatim 入三十一批节（r342 与三十批双记=双记先例）；十条 union 再 materialize 行与 r110 批同动作收敛（verbatim 二十九批节在位）。",
    "- 三十三批外迁（r112 bm-c·2026-09-27·超线 10,254B>10,000B 当窗整编·行级零丢失·同窗撞批号让号 r176 律：三十二批号让 origin d60676fb bm-a r360 批）：r344 bm-b 两行 verbatim=archive 202609.md『坑律归档 2026-09-27 三十三批』节；保留=User 元律+法行+批指针行族+r360 律。",
]

FOLD = ("- 二十六/二十七/二十九/三十/三十一/三十三批外迁史行族 6 行 verbatim="
        "archive 202609.md 对应批节+『坑律归档 2026-09-27 三十五批』节"
        "（批号让号 r176 律沿革族·三十五批再折叠·行级零丢失）。")

NEW_LAW = ("- [2026-09-27 23:3x r113 bm-c] 坑律：认领动作=fetch 紧贴认领原子窗"
           "（r239 律实弹第三犯：S0 22:50 pull『already up to date』后经 3 分钟"
           "勘察窗才认领，窗内 bm-b 22:49:09 认领提交已落 origin=本机按陈旧快照"
           "盲领 T-94→push 撞锁→§4 后到让路，整轮 s1 产物移侧支；正典=fetch+"
           "board 复核+claim+push 一气呵成零勘察间隙，调研一律认领后做；让路处置"
           "=产物保全侧支 machine/<id>-r<N>+MSG 移交回执禁裸弃）。"
           "指针=origin/machine/bm-c-r113+MSG-2261。")

SECTION_HEAD = ("\n## 坑律归档 2026-09-27 三十五批"
                "（r113 bm-c·CODELY.md 10,322B>10,000B 超线当窗整编·行级零丢失·"
                "批号让号 r176 律：三十四批号 origin bm-b r346 已占）\n")
SECTION_TAIL = ("\n三十五批记录：上 6 行=CODELY.md 批号沿革/外迁史行族 verbatim "
                "外迁（纯迁移叙事行，archive 本身即权威正本）；CODELY.md 侧留单行"
                "折叠指针+本批新坑律行（r239 认领 fetch 原子窗律·R113 bm-c）。\n")


def main():
    with io.open(CODELY, encoding="utf-8") as f:
        src = f.read()
    size_before = len(src.encode("utf-8"))
    lines = src.split("\n")
    out, removed = [], []
    for ln in lines:
        if any(ln.startswith(r[:24]) for r in ROWS):
            hit = next(r for r in ROWS if ln.startswith(r[:24]))
            assert ln == hit, "row drift: " + ln[:40]
            removed.append(ln)
            continue
        out.append(ln)
    assert len(removed) == 6, f"expected 6 rows, got {len(removed)}"
    body = "\n".join(out)
    # fold pointer + new law appended at the Reference section tail
    assert body.rstrip().endswith("指针=logs/iteration-loop/round_reports.md r346。")
    body = body.rstrip("\n") + "\n" + FOLD + "\n" + NEW_LAW + "\n"
    with io.open(ARCHIVE, "a", encoding="utf-8", newline="") as f:
        f.write(SECTION_HEAD)
        for r in removed:
            f.write(r + "\n")
        f.write(SECTION_TAIL)
    with io.open(CODELY, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    with io.open(ARCHIVE, encoding="utf-8") as f:
        arc = f.read()
    for r in removed:
        assert r in arc, "zero-loss FAIL: " + r[:40]
    size_after = len(body.encode("utf-8"))
    print(f"batch-35: CODELY {size_before}B -> {size_after}B "
          f"(limit 10,000B: {'PASS' if size_after <= 10_000 else 'FAIL'})")
    print(f"zero-loss verbatim assertions: {len(removed)}/6 PASS")
    assert size_after <= 10_000
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
