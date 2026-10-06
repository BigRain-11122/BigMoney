# -*- coding: utf-8 -*-
# r654 bm-c: D-06 increment sweep -- in-window gate breach fix (main 31,297B
# > 30,720B gate, discovered post-push: bm-a r808 +1,180B pit landed on the
# r653-tail 30,117B face; bm-a's "29,751B" claim was a stale-receipt
# assumption -- live proof case of the r653 close-size pit).
# Ritual: r441/r703/r783/r789/r651 (prescan-logged + registry row + verbatim
# migration + byte equation + sha16 anchors + receipt). r646 law: blob face
# is the size authority (disk face pure-CRLF autocrlf, verified per file).
# Scope: 3 entries out (r651 marker-scan / r794 add-u pollution / r653
# pre-push claw base); r653 close-size pit STAYS in main (pit-lineage.md at
# 30,516B has no room -- awaits lineage sub-split window); r808 bm-a entry
# stays (freshest, 新坑律先入主件后回扫).
import subprocess, sys, hashlib, json, os, datetime, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
REGISTRY = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r654bmc_codely_increment.json")
GATE = 30720

# key -> (target relpath, unique line-start needle)
POOL = [
    ("r651_assert_marker_scan",  "research/pit-git.md",          b"- [2026-10-07 04:1x r651 bm-c] **"),
    ("r794_addu_pollution",      "research/pit-git-resolver.md", b"- [2026-10-07 04:2x r794 bm-b] **rebase"),
    ("r653_prepush_claw_base",   "research/pit-git-staged.md",   b"- [2026-10-07 04:3x r653 bm-c] **pre-push"),
]

def blob_face(b):
    assert b.count(b"\r\n") == b.count(b"\n"), "mixed EOL face"
    return len(b) - b.count(b"\r\n")

def main():
    # 1) prescan (rc logged verbatim; D-20261002-06 mandate authorizes ritual)
    prescan_paths = ["CODELY.md", REGISTRY] + [os.path.join(ROOT, t) for _, t, _ in POOL]
    pr = subprocess.run([sys.executable, os.path.join("Tools", "treasure_guard.py"), "prescan"]
                        + prescan_paths, cwd=ROOT, capture_output=True)
    prescan = {"rc": pr.returncode, "out": (pr.stdout + pr.stderr).decode("utf-8", "replace").strip()[-600:]}

    mb = open(MAIN, "rb").read()
    assert mb.endswith(b"\r\n"), "main must end with CRLF"
    main_before_blob = blob_face(mb)

    # 2) extract the entry lines (full line incl CRLF), needle count==1 each
    moved = []
    for key, target, needle in POOL:
        assert mb.count(needle) == 1, "needle not unique: %s" % key
        idx = mb.index(needle)
        ls = mb.rfind(b"\n", 0, idx) + 1
        assert mb[ls:ls + len(needle)] == needle, "needle not at line start: %s" % key
        le = mb.find(b"\r\n", idx) + 2
        line = mb[ls:le]
        text_lf = line[:-2] + b"\n"          # LF face (blob-durable)
        moved.append({"key": key, "target": target, "line_disk": line,
                      "bytes_lf": len(text_lf) - 1,
                      "sha16": hashlib.sha256(text_lf).hexdigest()[:16],
                      "head": text_lf.decode("utf-8")[:60]})

    # 3) main surgery: remove 3 lines verbatim, append 1 ptr row at file end
    ptr = ("- 域指针·r654 bm-c 增量回扫批（D-20261002-06 主件 ≤30KB 判据腿·2026-10-07 r654 bm-c·当窗即办触发=主件 blob 实测 31,297B>30,720B〔bm-a r808 +1,180B 坑踩 r653-tail 30,117B 面上·其 29,751B 声明=陈旧收据假设错报=r653 close-size 坑活案例〕·迁移仪式 r441/r703/r783/r651 同款）："
           "主件 3 行/3 坑 verbatim 迁出——r651 断言层 marker 扫域过宽坑（r419/r420 假阳性族第四连）→pit-git.md〔拆件脚本断言层族〕"
           "+r794 rebase 冲突窗 add-u 循环污染坑→pit-git-resolver.md〔rebase 冲突窗 staged 污染族·r787/r789 同域〕"
           "+r653 pre-push 爪活远端基座坑（MSG-0612 环重放族新变体）→pit-git-staged.md〔staged 吞件与 commit 入场门族·r806 前例同域〕——"
           "r653 close-size 收据坑留主件（pit-lineage.md 30,516B 满员待让位窗）+r808 bm-a 最新坑留主件（新坑律先入后回扫）；"
           "逐条字节+sha16 对账=receipt results/_r654bmc_codely_increment.json"
           "（零丢失断言=逐块 bytes in target verbatim+主件保留面恒等式+主件 ≤30KB+全域件 ≤30KB·prescan rc 留痕）；"
           "新坑律仍先入本件后回扫。").encode("utf-8")
    new_mb = mb
    for m in moved:
        assert new_mb.count(m["line_disk"]) == 1
        new_mb = new_mb.replace(m["line_disk"], b"", 1)
    new_mb = new_mb + ptr + b"\r\n"
    # byte equation (disk face): out = 3 full lines, in = ptr row + CRLF
    assert len(new_mb) == len(mb) - sum(len(m["line_disk"]) for m in moved) + len(ptr) + 2
    main_after_blob = blob_face(new_mb)
    assert main_after_blob <= GATE, "main over gate"
    for m in moved:
        assert m["line_disk"] not in new_mb, "entry still in main"

    # 4) append entries verbatim to targets (disk CRLF face, x1 in target)
    targets_before_after = {}
    for m in moved:
        tp = os.path.join(ROOT, m["target"])
        tb = open(tp, "rb").read()
        assert tb.endswith(b"\r\n"), "target must end with CRLF"
        assert m["line_disk"][:-2] not in tb, "entry already in target"
        nb = tb + m["line_disk"]
        assert nb.count(m["line_disk"]) == 1
        assert blob_face(nb) <= GATE, "target over gate: %s" % m["target"]
        open(tp, "wb").write(nb)
        targets_before_after[m["target"]] = {"before": blob_face(tb), "after": blob_face(nb)}
        m["target_bytes_after"] = blob_face(nb)

    # 5) registry row (facts-driven values)
    reg_b = open(REGISTRY, "rb").read()
    assert reg_b.endswith(b"\r\n")
    row = ("- 2026-10-07 05:0x bm-c r654 D-06 主件增量回扫迁移仪式（D-20261002-06 主件 ≤30KB 判据腿·当窗即办触发=实测 31,297B>30,720B·r441/r703/r783/r651 仪式同款）："
           "TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：①prescan rc 留痕（本行）②出入记录本行 ③零丢失断言：CODELY.md 主件 %d→%dB blob 面（3 行/3 坑 verbatim 迁出非手抄：%s"
           "·逐条字节对账+主件保留面恒等+全域件 ≤30KB）；r653 close-size 坑留主件待 pit-lineage 让位窗+r808 bm-a 最新坑留主件；receipt=results/_r654bmc_codely_increment.json。") % (
        main_before_blob, main_after_blob,
        "+".join("%s→%s（%dB·sha16 %s）" % (m["key"], m["target"], m["bytes_lf"], m["sha16"]) for m in moved))
    reg_nb = reg_b + row.encode("utf-8") + b"\r\n"
    assert blob_face(reg_nb) <= GATE, "registry over gate"

    # 6) write main + registry; re-read verify
    open(MAIN, "wb").write(new_mb)
    open(REGISTRY, "wb").write(reg_nb)
    for p, b_ in ((MAIN, new_mb), (REGISTRY, reg_nb)):
        rb = open(p, "rb").read()
        assert rb == b_, "write/read mismatch"

    # 7) family sweep: all research/pit-*.md blobs under gate; utf-8 clean;
    #    marker scan LINE-START ANCHORED + SCOPED to this round's written
    #    faces only (r651 pit law: whole-family substring scan = false red)
    pit_files = sorted(glob.glob(os.path.join(ROOT, "research", "pit-*.md")))
    written = [MAIN, REGISTRY] + [os.path.join(ROOT, m["target"]) for m in moved]
    for p in written:
        b_ = open(p, "rb").read()
        b_.decode("utf-8")
        for ln in b_.split(b"\n"):
            assert not ln.startswith(b"<<<<<<<") and not ln.startswith(b">>>>>>>"), "line-start marker in %s" % p
    over = [os.path.relpath(p, ROOT) for p in pit_files if blob_face(open(p, "rb").read()) > GATE]
    assert not over, "pit files over gate: %s" % over

    receipt = {
        "ritual": "r441/r703/r783/r651 migration ritual (r654 bm-c increment sweep, in-window gate breach fix)",
        "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "prescan": prescan,
        "entries": {m["key"]: {"target": m["target"], "bytes_lf": m["bytes_lf"], "sha16": m["sha16"],
                               "head": m["head"], "target_bytes_after": m["target_bytes_after"]}
                    for m in moved},
        "sha16_method": "sha256(entry_lf_text + LF)[:16], LF face (blob-durable), facts-driven",
        "asserts": [
            "main %d -> %d B blob (<= %d gate)" % (main_before_blob, main_after_blob, GATE),
            "byte equation exact (3 entry lines + CRLFs out, 1 ptr row + CRLF in)",
            "each entry verbatim x1 in target, x0 in main",
            "all pit-*.md blobs <= gate (%d files)" % len(pit_files),
            "utf-8 + LINE-START marker scan clean on written faces only (r651 pit law)",
            "prescan rc logged verbatim (D-20261002-06 mandate authorizes ritual)",
            "kept-in-main: r653 close-size pit (pit-lineage.md full 30,516B) + r808 bm-a pit (freshest)",
        ],
        "sizes": {"main_before_blob": main_before_blob, "main_after_blob": main_after_blob,
                  "main_before_disk": len(mb), "main_after_disk": len(new_mb)},
        "targets": targets_before_after,
        "registry_line_appended": True,
        "pit_files": len(pit_files),
        "breach_context": ("main measured 31,297B > 30,720B post-push (bm-a r808 +1,180B on r653-tail 30,117B; "
                           "bm-a stale-receipt claim 29,751B = live case of r653 close-size pit)"),
    }
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=1, ensure_ascii=False)
    print("SPLIT_OK main_blob %d -> %d | moved=%dB | pit_files=%d | prescan_rc=%d" % (
        main_before_blob, main_after_blob, sum(m["bytes_lf"] for m in moved), len(pit_files), prescan["rc"]))
    for m in moved:
        print("  %s -> %s %dB sha16=%s" % (m["key"], m["target"], m["bytes_lf"], m["sha16"]))

if __name__ == "__main__":
    main()
