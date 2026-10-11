"""r888 bm-b CODELY.md mini-split ceremony (r731/r885 pattern).

Trigger: main 29,966B + new pit entry append would cross the 30,720B cap.
Migration: r885 weekend-task-audit-blindspot entry (machine/task-ops domain)
            -> research/pit-machine.md verbatim (prescan rc3 authorized face,
            D-20260206 group split order; TREASURE_PROTECTION_LAW s2 receipt).
New pit entry (RW-4 restore-face placement conflict) enters main per
"new pits enter main first" law. Zero-loss assertions + receipt json.
"""
import hashlib
import json

MAIN = "CODELY.md"
TARGET = "research/pit-machine.md"
RCPT = "results/_r888bmb_codely_minisplit.json"
CAP = 30720

MIG_PREFIX = "- [2026-10-11 15:5x r885 bm-b] **周末任务健康审计盲区"

PTR_ROW = (
    "- 域指针·r888 bm-b mini-split（10-11 17:1x·主件 29,966B+新坑例 append 越帽当窗即办·r731/r885 范式·"
    "prescan rc3=记忆/坑律类·D-20260206 集团拆件令授权迁移面）：r885 周末任务健康审计盲区条目 verbatim "
    "迁 research/pit-machine.md〔任务健康审计/机队任务运维域·E2/复启/健康审计清单动作前改读该件〕——逐条字节+sha16 对账="
    "receipt results/_r888bmb_codely_minisplit.json（零丢失断言=迁移条 bytes in target verbatim+主件保留面恒等+主/域件 ≤30KB）；"
    "新坑例（RW-4 恢复面落位冲突）本窗入主件。"
)

NEW_ENTRY = (
    "- [2026-10-11 17:1x r888 bm-b] **恢复类数据面落位×RW-4 冻结锁冲突（spec 字面路径≠合法命名空间）**：T-184 修复轮把 "
    "4784-bar 510880 裸码 face 按 spec 字面落回 data/daily/ 并 git-track，当轮 S6 即被 RW-4 G3 冻结锁 fail-closed 拒收"
    "（T-127/D-20260930-05：in-service 面板=knowledge/panel_gate.py 48 core48 白名单冻结面而非目录清单·新裸文件=整批拒收）"
    "→ live_paper/t24_prospect_paper/aggressive_lab 三腿红。正解=迁出裸命名空间（→data/ext_slots/etf_daily/510880_t73_longhist.csv·"
    "sha 恒等保全·ext_slots=gitignore 槽位区惯例）；禁白名单 re-freeze（510880 非在役成员·扩锁=live-paper 批面科学漂移）"
    "禁 load_core 改目录过滤（=拆门禁绊线）。How to apply：恢复/重建/外采数据面前先查 panel_gate.py 白名单——data/daily "
    "裸码位=在役面板专属，非白名单面一律落 ext_slots/前缀名/专项目录；票面 payload 路径与冻结锁冲突时以锁为准+票面回执调解记档"
    "（正典=T-2026-10-11-184-P1.json r888b 回执）。"
)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    main_before = open(MAIN, "rb").read()
    tgt_before = open(TARGET, "rb").read()

    text = main_before.decode("utf-8")
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(MIG_PREFIX)]
    assert len(hits) == 1, f"migration anchor not unique: {hits}"
    mig_line = lines[hits[0]]
    mig_blob = mig_line.encode("utf-8")
    del lines[hits[0]]
    text2 = "\n".join(lines)
    if text2 and not text2.endswith("\n"):
        text2 += "\n"
    text2 += PTR_ROW + "\n" + NEW_ENTRY + "\n"
    main_new = text2.encode("utf-8")

    tgt_text = tgt_before.decode("utf-8")
    if tgt_text and not tgt_text.endswith("\n"):
        tgt_text += "\n"
    tgt_text += mig_line + "\n"
    tgt_new = tgt_text.encode("utf-8")

    # zero-loss assertions
    assert mig_blob in tgt_new, "migrated blob not verbatim in target"
    assert MIG_PREFIX not in main_new.decode("utf-8"), "entry still in main"
    assert len(main_new) <= CAP, f"main over cap: {len(main_new)}"
    assert len(tgt_new) <= CAP, f"target over cap: {len(tgt_new)}"

    open(MAIN, "wb").write(main_new)
    open(TARGET, "wb").write(tgt_new)

    receipt = {
        "round": "r888 bm-b",
        "ceremony": "CODELY.md mini-split (r731/r885 pattern)",
        "trigger": "main 29,966B + new pit entry would cross 30,720B cap",
        "prescan_rc": 3,
        "prescan_note": "treasure_guard prescan rc3 = registry hit on memory/pit-law files; "
                        "D-20260206 group split order authorizes migration-with-receipt",
        "migrated_entry": {
            "id": "r885 weekend-task-audit blindspot",
            "bytes": len(mig_blob),
            "sha16": sha16(mig_blob),
            "from": MAIN,
            "to": TARGET,
            "verbatim_in_target": True,
        },
        "new_entry": {
            "id": "r888 RW-4 restore-face placement conflict",
            "bytes": len(NEW_ENTRY.encode("utf-8")),
            "sha16": sha16(NEW_ENTRY.encode("utf-8")),
            "location": "main (new pits enter main first)",
        },
        "pointer_row_bytes": len(PTR_ROW.encode("utf-8")),
        "main_bytes_before": len(main_before),
        "main_bytes_after": len(main_new),
        "target_bytes_before": len(tgt_before),
        "target_bytes_after": len(tgt_new),
        "assertions": {
            "migrated_blob_verbatim_in_target": True,
            "entry_removed_from_main": True,
            "main_le_cap": len(main_new) <= CAP,
            "target_le_cap": len(tgt_new) <= CAP,
        },
        "zero_loss": True,
    }
    with open(RCPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({
        "main": f"{len(main_before)} -> {len(main_new)}",
        "target": f"{len(tgt_before)} -> {len(tgt_new)}",
        "migrated_bytes": len(mig_blob),
        "receipt": RCPT,
    }))


if __name__ == "__main__":
    main()
