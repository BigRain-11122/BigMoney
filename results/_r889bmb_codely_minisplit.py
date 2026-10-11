"""r889 bm-b CODELY.md mini-split + direct-write ceremony (r731/r747/r888 pattern).

Trigger: main 30,686B, headroom 34B -- any new-pit append would cross the
30,720B cap. prescan rc3 = registry hit on memory/pit-law class files
(D-20260206 group split order authorizes migration-with-receipt; same face
as r888 receipt).

Ops:
  1. migrate r888 RW-4 restore-face entry verbatim main -> research/pit-data.md
     (restore/rebuild/external-data placement domain).
  2. new pit #1 (banned_direction_gate template-literal false hit) direct-write
     -> research/pit-tooling.md (r666 direct-write precedent, main full).
  3. new pit #2 (stash-pop pool-face owner_since backward + sync_face settle
     recipe) direct-write -> research/pit-git-resolver-rebase2.md.
  4. pointer row appended to main recording all three moves.

Zero-loss assertions + receipt json.
"""
import hashlib
import json

MAIN = "CODELY.md"
RCPT = "results/_r889bmb_codely_minisplit.json"
CAP = 30720

MIG_PREFIX = "- [2026-10-11 17:1x r888 bm-b] **恢复类数据面落位×RW-4 冻结锁冲突"
TGT_DATA = "research/pit-data.md"
TGT_TOOLING = "research/pit-tooling.md"
TGT_REBASE2 = "research/pit-git-resolver-rebase2.md"

PIT_TOOLING = (
    "- [2026-10-11 17:4x r889 bm-b] **banned_direction_gate 模板字面误触发坑（prereg 引用面=关键词扫描命中非本批方向）**："
    "起草 N2U3_ALPHAGEN_RL_P1 时 §4 判据节照抄 PREREG_TEMPLATE.md 原文「同族网格=g25_retro 先例」（PBO CSCV 同族参数网格先例引用），"
    "gate 扫描命中 BAN-04 Grid trading 拒收（rc1）——本批非网格交易=词组面假阳性。正解=改写措辞保语义零漂移（「同族网格」→「同族参数族」）"
    "过闸 ADMIT rc0；禁 --no-verify 逃生（掩真命中）。How to apply：prereg 引用模板判据原文时先跑 banned_direction_gate 预检；"
    "命中=BAN 编号对照本批方向定性——真命中走 §0.5 例外声明三件套（new_data/new_mechanism+原否证不可见面），词组假阳性=改写措辞；"
    "PREREG_TEMPLATE.md §4 PBO 行本身含该词组=上游修复候选（未改·下批 template 维护窗处理）。"
)

PIT_REBASE2 = (
    "- [2026-10-11 17:4x r889 bm-b] **stash→pull --rebase→pop 后池面 owner_since 回退坑（MSG-0612 环律 stash-pop 新变体·settle 兜底法实证）**："
    "S0 轮首脏（车道状态件）走 stash→pull→pop 环，pop 恢复的本地池面与 origin 新 tip 池面分叉（实弹=runnable_pool.json "
    "TRIAL-LABOR-W18-SCREEN-SHARD-0 owner_since 17:32:04→17:20:34 backward）→ commit 后 push 被 pre-push 爪拦（ring-replay family）。"
    "正解三步=python -c \"from merge_lane_views import sync_face; sync_face('runnable_pool')\" 两向 settle（origin blob unioned as "
    "leading base·r627 stale-settle law·wrote shared+lane）→ 新 commit → pull --rebase 重放 → push 过爪；禁反复重跑循环/禁手改 "
    "owner_since/禁 --no-verify 闯爪。How to apply：stash-pop 环后凡池面/共享协调面（runnable_pool/crash_fuse 族）必跑 sync_face "
    "settle 再 commit——S6 pool_dualrun 证据腿不覆盖此窗（它跑在 pop 之前）；push 爪拦 backward 时本配方三步=默认解。"
)

PTR_ROW = (
    "- 域指针·r889 bm-b mini-split+直写（10-11 17:4x·主件 30,686B 余量 34B 双新坑 append 必越帽·r731/r747/r888 范式·"
    "prescan rc3=记忆/坑律类四命中·D-20260206 集团拆件令授权迁移面）：r888 RW-4 恢复面落位条 verbatim 迁 research/pit-data.md"
    "〔恢复/重建/外采数据面动作前改读〕+r889 两新坑直写域件（r666 直写先例·主件满员例外）：banned_direction_gate 模板字面误触发坑"
    "→research/pit-tooling.md〔prereg 起草/gate 预检动作前改读〕+stash-pop 池面 owner_since 回退 settle 兜底坑→"
    "research/pit-git-resolver-rebase2.md〔stash-pop 环/池面 settle 动作前改读〕——逐条字节+sha16 对账=receipt "
    "results/_r889bmb_codely_minisplit.json（零丢失断言=迁移条 bytes in target verbatim+直写条 in target verbatim+主件保留面恒等+"
    "主/域件 ≤30KB）；新坑律直写域件例外后回扫归位（r747 范式）。"
)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def append_line(path, line):
    b = open(path, "rb").read()
    t = b.decode("utf-8")
    if t and not t.endswith("\n"):
        t += "\n"
    t += line + "\n"
    nb = t.encode("utf-8")
    assert len(nb) <= CAP, f"{path} over cap: {len(nb)}"
    open(path, "wb").write(nb)
    return b, nb


def main():
    main_before = open(MAIN, "rb").read()
    data_before = open(TGT_DATA, "rb").read()

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
    text2 += PTR_ROW + "\n"
    main_new = text2.encode("utf-8")
    assert len(main_new) <= CAP, f"main over cap: {len(main_new)}"

    # 1. RW-4 entry -> pit-data.md verbatim
    data_b, data_new = append_line(TGT_DATA, mig_line)
    # 2/3. direct-write pits
    tool_b, tool_new = append_line(TGT_TOOLING, PIT_TOOLING)
    reb2_b, reb2_new = append_line(TGT_REBASE2, PIT_REBASE2)

    # zero-loss assertions
    assert mig_blob in data_new, "RW-4 blob not verbatim in pit-data"
    assert MIG_PREFIX not in main_new.decode("utf-8"), "RW-4 still in main"
    assert PIT_TOOLING.encode("utf-8") in tool_new, "tooling pit not verbatim"
    assert PIT_REBASE2.encode("utf-8") in reb2_new, "rebase2 pit not verbatim"

    open(MAIN, "wb").write(main_new)

    receipt = {
        "round": "r889 bm-b",
        "ceremony": "CODELY.md mini-split + direct-write (r731/r747/r888 pattern)",
        "trigger": "main 30,686B headroom 34B, two new pits would cross cap",
        "prescan_rc": 3,
        "prescan_note": "treasure_guard prescan rc3 registry hit on 4 memory/pit-law files; "
                        "D-20260206 group split order authorizes migration-with-receipt",
        "migrated_entry": {
            "id": "r888 RW-4 restore-face placement conflict",
            "bytes": len(mig_blob), "sha16": sha16(mig_blob),
            "from": MAIN, "to": TGT_DATA, "verbatim_in_target": True,
        },
        "direct_written_pits": [
            {"id": "r889 banned_direction_gate template-literal false hit",
             "bytes": len(PIT_TOOLING.encode("utf-8")),
             "sha16": sha16(PIT_TOOLING.encode("utf-8")), "to": TGT_TOOLING,
             "law": "r666 direct-write precedent (main full exception)"},
            {"id": "r889 stash-pop pool-face owner_since backward settle recipe",
             "bytes": len(PIT_REBASE2.encode("utf-8")),
             "sha16": sha16(PIT_REBASE2.encode("utf-8")), "to": TGT_REBASE2,
             "law": "r666 direct-write precedent (main full exception)"},
        ],
        "pointer_row_bytes": len(PTR_ROW.encode("utf-8")),
        "sizes": {
            "main_before": len(main_before), "main_after": len(main_new),
            "pit_data_before": len(data_b), "pit_data_after": len(data_new),
            "pit_tooling_before": len(tool_b), "pit_tooling_after": len(tool_new),
            "pit_rebase2_before": len(reb2_b), "pit_rebase2_after": len(reb2_new),
        },
        "assertions": {
            "migrated_blob_verbatim_in_target": True,
            "direct_pits_verbatim_in_targets": True,
            "entry_removed_from_main": True,
            "all_files_le_cap": True,
        },
        "zero_loss": True,
    }
    with open(RCPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({
        "main": f"{len(main_before)} -> {len(main_new)}",
        "pit-data": f"{len(data_b)} -> {len(data_new)}",
        "pit-tooling": f"{len(tool_b)} -> {len(tool_new)}",
        "pit-rebase2": f"{len(reb2_b)} -> {len(reb2_new)}",
        "receipt": RCPT,
    }))


if __name__ == "__main__":
    main()
