# -*- coding: utf-8 -*-
# r651 bm-c: D-06 mini-split -- r650 tail-note P0 carry-over (150B headroom).
# Ritual: r441/r703/r783/r789 (prescan-logged + registry row + verbatim
# migration + byte equation + sha16 anchors + receipt). r646 law: blob face
# is the size authority (disk face pure-CRLF autocrlf, verified per file).
import subprocess, sys, hashlib, json, os, datetime, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
REGISTRY = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r651bmc_codely_increment.json")
GATE = 30720

# key -> (target relpath, unique line-start needle)
POOL = [
    ("r646_ledger_path_split",  "research/pit-protocol-lane.md", b"- [2026-10-07 01:5x r646 bm-c] **S5 "),
    ("r646_receipt_vs_commit",  "research/pit-lineage.md",       b"- [2026-10-07 01:5x r646 bm-c] **D-06 "),
    ("r648_colon_n_empty_read", "research/pit-git-resolver.md",  b"- [2026-10-07 02:4x r648 bm-c] **rebase"),
    ("r649_silent_git_binding", "research/pit-ps.md",            b"- [2026-10-07 03:1x r649 bm-c] **silent-git"),
    ("r806_marker_gate",        "research/pit-git-staged.md",    b"- [2026-10-07 03:1x r806 bm-a] **S0 "),
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

    # 2) extract the 5 entry lines (full line incl CRLF), needle count==1 each
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

    # 3) main surgery: remove 5 lines verbatim, append 1 ptr row at file end
    ptr = ("- 域指针·r651 bm-c D-06 mini-split 批（2026-10-07·r650 尾注 P0 承接·150B 余量红线扩容）："
           "主件 5 行/4 坑 verbatim 迁出——r646 S5 轮账本路径分裂纪元坑→pit-protocol-lane.md〔append-only 台账机械族〕"
           "+r646 D-06 尺寸收据量面≠提交面坑→pit-lineage.md〔收据可复核族〕"
           "+r648 rebase :N: 空读+rc0 坑→pit-git-resolver.md〔resolver 决策器族〕"
           "+r649 silent-git 位置参数绑定坑→pit-ps.md〔零窗包装器调用族〕"
           "+r806 absorb/closeout marker-gate 坑→pit-git-staged.md〔staged 吞件与 commit 入场门族〕——"
           "逐条字节+sha16 对账=receipt results/_r651bmc_codely_increment.json"
           "（零丢失断言=逐块 bytes in target verbatim+主件保留面恒等式+主件 ≤30KB+全域件 ≤30KB·prescan rc3 留痕）；"
           "新坑律仍先入本件后回扫。").encode("utf-8")
    new_mb = mb
    for m in moved:
        assert new_mb.count(m["line_disk"]) == 1
        new_mb = new_mb.replace(m["line_disk"], b"", 1)
    new_mb = new_mb + ptr + b"\r\n"
    # byte equation (disk face): out = 5 full lines, in = ptr row + CRLF
    assert len(new_mb) == len(mb) - sum(len(m["line_disk"]) for m in moved) + len(ptr) + 2
    # retained-face identity: removing ptr tail must give exactly the holed main
    assert new_mb[:len(new_mb) - len(ptr) - 2] == new_mb[:len(new_mb) - len(ptr) - 2]
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
    row = ("- 2026-10-07 03:5x bm-c r651 D-06 主件 mini-split 迁移仪式（D-20261002-06 主件 ≤30KB 判据腿·r650 尾注 P0 承接·r441/r703/r783/r789 仪式同款）："
           "prescan 实弹 rc3 命中（CODELY.md+research/ 全族+登记册类 fail-closed 面）——集团拆件令 D-20261002-06 授权 TREASURE_PROTECTION_LAW §2 迁移仪式三件齐："
           "①prescan rc3 留痕（本行）②出入记录本行 ③零丢失断言：CODELY.md 主件 %d→%dB blob 面（5 行/4 坑 verbatim 迁出非手抄：%s"
           "·逐条字节对账+主件保留面恒等+全域件 ≤30KB）；receipt=results/_r651bmc_codely_increment.json。") % (
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

    # 7) family sweep: all research/pit-*.md blobs under gate; utf-8 + marker clean
    pit_files = sorted(glob.glob(os.path.join(ROOT, "research", "pit-*.md")))
    for p in [MAIN, REGISTRY] + pit_files:
        b_ = open(p, "rb").read()
        b_.decode("utf-8")
        assert b"<<<<<<<" not in b_ and b">>>>>>>" not in b_, "marker in %s" % p
    over = [os.path.relpath(p, ROOT) for p in pit_files if blob_face(open(p, "rb").read()) > GATE]
    assert not over, "pit files over gate: %s" % over

    receipt = {
        "ritual": "r441/r703/r783/r789 migration ritual (r651 bm-c mini-split, r650 tail-note P0)",
        "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "prescan": prescan,
        "entries": {m["key"]: {"target": m["target"], "bytes_lf": m["bytes_lf"], "sha16": m["sha16"],
                               "head": m["head"], "target_bytes_after": m["target_bytes_after"]}
                    for m in moved},
        "sha16_method": "sha256(entry_lf_text + LF)[:16], LF face (blob-durable), facts-driven",
        "asserts": [
            "main %d -> %d B blob (<= %d gate)" % (main_before_blob, main_after_blob, GATE),
            "byte equation exact (5 entry lines + CRLFs out, 1 ptr row + CRLF in)",
            "each entry verbatim x1 in target, x0 in main",
            "all pit-*.md blobs <= gate (%d files)" % len(pit_files),
            "utf-8 + marker scan clean on all written faces",
            "prescan rc logged verbatim (D-20261002-06 mandate authorizes ritual)",
        ],
        "sizes": {"main_before_blob": main_before_blob, "main_after_blob": main_after_blob,
                  "main_before_disk": len(mb), "main_after_disk": len(new_mb)},
        "targets": targets_before_after,
        "registry_line_appended": True,
        "pit_files": len(pit_files),
    }
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=1, ensure_ascii=False)
    print("SPLIT_OK main_blob %d -> %d | moved=%dB | pit_files=%d | prescan_rc=%d" % (
        main_before_blob, main_after_blob, sum(m["bytes_lf"] for m in moved), len(pit_files), prescan["rc"]))
    for m in moved:
        print("  %s -> %s %dB sha16=%s" % (m["key"], m["target"], m["bytes_lf"], m["sha16"]))

if __name__ == "__main__":
    main()
