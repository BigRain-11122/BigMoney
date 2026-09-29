# -*- coding: utf-8 -*-
"""r449 fixup v2 (idempotent): restore User meta-law; age-migrate r440-b then r242-c
until under the 10,240B hard line; archive append only if entry not already archived
(prior failed run left one r440-b section in archive). Fail-closed, byte-accounted."""
import sys, io

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"
HARD = 10240

USER_PREFIX = "- [2026-09-24 16:07:32] CEO 最高判据宣言"

CANDIDATES = [
    ("- [2026-09-29 20:5x r440 bm-b] **初筛富集面≠注册级增量律**",
     "- 冷层指针：r440 bm-b 初筛富集面≠注册级增量律全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节（法面已由 TRIAL_LABOR_W10_PREREG §7/8+CEO-REPORT-WAVE10+attrition 承载）。",
     "- 冷层指针：r433 同门换用法"),
    ("- [2026-09-29 22:4x r242 bm-c] runner 外科手术四连坑族",
     "- 冷层指针：r242 bm-c runner 外科手术四连坑族全文 verbatim=archive 202609.md『热冷整编 2026-09-29 r449 bm-a 窗批』节（W11 runner 已建毕 selftest 47/47·坑律由 _r242bmc_w11_surgeon 系列工件承载）。",
     "- 冷层指针：r440 bm-b 初筛富集面"),
]
ARCH_HEADER = "## 热冷整编 2026-09-29 r449 bm-a 窗批（续：User 节元律恢复+r440/r242 让位水位）"


def main() -> int:
    src = open(CODELY, encoding="utf-8").read()
    arc = open(ARCHIVE, encoding="utf-8").read()
    arc_b0 = len(arc.encode("utf-8"))

    lines = src.splitlines()
    # 1) restore User meta-law if missing
    out, restored = [], False
    if any(ln.startswith(USER_PREFIX) for ln in lines):
        out = list(lines)
        print("User entry already hot")
    else:
        user_line = next(ln for ln in arc.splitlines() if ln.startswith(USER_PREFIX))
        for ln in lines:
            out.append(ln)
            if ln.strip() == "### User":
                out.append(user_line)
                restored = True
        assert restored, "### User header missing"
        print("User meta-law restored verbatim from archive")

    # 2) migrate candidates until under the line
    arc_appends = []
    for prefix, pointer, anchor in CANDIDATES:
        b = len(("\n".join(out) + "\n").encode("utf-8"))
        if b < HARD:
            break
        tgt = next((ln for ln in out if ln.startswith(prefix)), None)
        assert tgt, f"candidate not found hot: {prefix[:40]}"
        o2, pin = [], False
        for ln in out:
            if ln is tgt:
                continue
            o2.append(ln)
            if ln.startswith(anchor) and pointer not in out and not pin:
                o2.append(pointer)
                pin = True
        assert pin or pointer in out, f"pointer anchor missing for {prefix[:40]}"
        out = o2
        if tgt not in arc:
            arc_appends.append(tgt)
        print(f"migrated {prefix[12:40]}... ({len(tgt.encode('utf-8'))+1}B)")

    while out and out[-1].strip() == "":
        out.pop()
    src_new = "\n".join(out) + "\n"
    b1 = len(src_new.encode("utf-8"))
    assert b1 < HARD, f"still over hard line: {b1}"

    if arc_appends:
        arc_new = arc.rstrip("\n") + "\n\n" + ARCH_HEADER + "\n\n" + "\n".join(arc_appends) + "\n"
        for ln in arc_appends:
            assert ln in arc_new
        open(ARCHIVE, "w", encoding="utf-8", newline="").write(arc_new)
        arc = arc_new

    open(CODELY, "w", encoding="utf-8", newline="").write(src_new)

    chk, achk = open(CODELY, encoding="utf-8").read(), open(ARCHIVE, encoding="utf-8").read()
    user_line = next(ln for ln in achk.splitlines() if ln.startswith(USER_PREFIX))
    assert user_line in chk, "User meta-law must be hot"
    for prefix, pointer, _ in CANDIDATES:
        tgt = next((ln for ln in achk.splitlines() if ln.startswith(prefix)), None)
        if tgt is not None and tgt not in chk:
            assert tgt in achk, f"migrated entry not archived: {prefix[:30]}"
    assert len(chk.encode("utf-8")) == b1
    print(f"verify PASS: User meta-law hot; CODELY {len(src.encode('utf-8'))} -> {b1} B < {HARD}; "
          f"ARCHIVE {arc_b0} -> {len(achk.encode('utf-8'))} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
