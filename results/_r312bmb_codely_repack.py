# -*- coding: utf-8 -*-
"""r312 bm-b CODELY hot/cold repack: <=10KB hard line (D-20260925-01(d) +
O-20260927-0230 law; r310 5th-batch precedent). Migrate two aged kenglu
lines verbatim (zero line loss) to research/memory-archive/202609.md 6th
batch, append three new r312 kenglu lines, verify size + zero-loss."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202609.md")

MIGRATE_PREFIXES = (
    "- [2026-09-27 05:4x r301 bm-b] 坑律：**轮中钟面回拨",
    "- [2026-09-27 06:5x r299 bm-a] 坑律：**冻结血统 runner 的 cache 门戳",
)
NEW_ENTRIES = [
    "- [2026-09-27 09:1x r312 bm-b] 坑律：**prereg 冻结窗写 seed 基必须先 rg 零命中后写值**——"
    "DECISION_CHAIN_E2E_P1 v1.1 冻结 20260929 时未察 t11_negday_ic 已于 09-24 22:4x 注册同基"
    "（v1.0 起草 08:08 vs 注册早 9h=起草窗漏扫；date-like 段 20260923/24/25/26/27/28/29/30 全占）；"
    "prereg 自载顺序律「跑前 rg+登记」救场=r312 s9.2 零跑修正取下一净位 20261001（20260930=cn_rev_tilt_p1 "
    "亦占）。正典=起草预注册时 seed 基候选即执行 rg 全仓探针，勿把顺序律推迟到 runner 建批日。"
    "指针=research/DECISION_CHAIN_E2E_P1.md §9.2+scripts/science_gates.py SEED_REGISTRY['decision_chain_e2e']。",
    "- [2026-09-27 09:1x r312 bm-b] 坑律：**regime_state.json 与 v3_state_series 跨源等值断言=虚假前提**——"
    "results/regime_state.json=market_regime probe 的 **v1 在役矩阵**（rule=firm/risk/REGIME_GUARD.md "
    "v1.0·O-20260923-2315；#10 below_ma200 已采集→ORANGE，raw_level_v3 文档明文「Live probe() keeps the "
    "v1 matrix until law amendment (PASS+GM approval+veto window)」），live.paper v3_state_series=**v3 校准层重放**"
    "（#10 已去采集 per v2 ruling→YELLOW）；两代机按律并存永不可断言相等，T-90 prereg G-V3 leg-2 原文即踩"
    "（r312 实弹红面定谳）→s9.3 零跑修正=新鲜度（asof=重放末日）+字母表+双读数分歧披露。当值分歧 "
    "ORANGE vs YELLOW（2026-09-24）=防线 v1→v3 升级案实证输入已呈 GM。"
    "指针=scripts/market_regime.py raw_level_v3 docstring+prereg §9.3+results/_r312 探针。",
    "- [2026-09-27 09:1x r312 bm-b] 坑律：**心跳 orders_ack 字符碎裂古疾+验证空洞**——fleet/machines/bm-b.json "
    "orders_ack 实为逐字符列表（2257 项≈94 令名×24 字符恰合；每轮以展平字符串追加所致，r309 起即碎），"
    "「集合差=94 unacked」假警报面实证；而历代轮报告「94/94 双扫零新增」却照过=验证走的是别的通道"
    "（未做 set-diff 自证）=验证空洞。正典=写心跳时 orders_ack=全文件名（含 .md）列表整体重写+写前自证"
    "（set(orders) ⊆ set(ack) 且交集数==orders 数），禁 str 展平进列表。指针=本行+r312 wrap 件修复实证。",
]


def main():
    codely = open(CODELY, encoding="utf-8").read()
    archive = open(ARCHIVE, encoding="utf-8").read()
    lines = codely.splitlines()
    migrated = []
    for pref in MIGRATE_PREFIXES:
        hits = [l for l in lines if l.startswith(pref)]
        assert len(hits) == 1, f"prefix not unique/found: {pref[:40]}"
        migrated.append(hits[0])
    kept = [l for l in lines if not any(l == m for m in migrated)]
    assert len(kept) == len(lines) - len(migrated)
    # insert new entries before the '### Reference' header
    out = []
    for l in kept:
        if l.strip() == "### Reference" and not any(
                x.startswith("### Reference") for x in out):
            out.extend(NEW_ENTRIES)
            out.append("")
        out.append(l)
    new_codely = "\n".join(out) + "\n"
    # zero-loss verify: migrated lines verbatim into archive 6th batch
    batch_header = ("## 坑律归档 2026-09-27 · 归档六批（r312 bm-b 热冷整编·行级 verbatim 零丢失）")
    archive_new = (archive.rstrip("\n") + "\n\n" + batch_header + "\n\n"
                   + "\n".join(migrated) + "\n")
    for m in migrated:
        assert m in archive_new, "zero-loss check failed"
        assert m not in new_codely, "migration left a copy in CODELY"
    assert len(new_codely.encode("utf-8")) <= 10240, (
        f"CODELY {len(new_codely.encode('utf-8'))}B > 10KB hard line")
    json.dumps({})  # noop sanity
    tmp = CODELY + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_codely)
    os.replace(tmp, CODELY)
    tmp = ARCHIVE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(archive_new)
    os.replace(tmp, ARCHIVE)
    print(f"migrated {len(migrated)} lines; new entries {len(NEW_ENTRIES)}; "
          f"CODELY={len(new_codely.encode('utf-8'))}B <= 10KB OK; "
          f"archive +{len(migrated)} lines")


if __name__ == "__main__":
    main()
