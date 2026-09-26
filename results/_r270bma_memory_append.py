# -*- coding: utf-8 -*-
"""R270 bm-a: CODELY.md S4 坑律 append（LF 面·trailing-nl 镜像）。"""
import io

P = "CODELY.md"
ENTRY = (
    "- [2026-09-26 22:0x] 坑律（bm-a R270·T-83 s3 件⑥·治理审计死链裁定面·E1 裁定期自捕）："
    "**路径引用检测器的「死链/挪位」宣告前必过三假面族实探——①子串前缀盲：`data/repo_daily.csv` 是 "
    "`Money0923/data/repo_daily.csv` 的子串照样命中=已带前缀的正确路径被报挪位候选（CASH_LEG 实证；"
    "幂等 fixer 的 skip(already) 腿自捕）②车道本地大文件面：.gitignore 的 `results/t22/*` 产机在位、"
    "他机检测视角不可见=双链假死（.gitignore:65 实证）③集团仓面：FluxGroup `docs/governance.md`、"
    "`cph4/*` 在集团仓在位、仓内 Test-Path 必假红**；正律=裁定前同 basename 实位核+产机在位核+"
    "集团仓 Test-Path 三核先行；检测器改进候选=集团仓/gitignore 白名单（下轮 s2 机改脸）。"
    "指针=research/AUDIT-20260926-S2-ADJUDICATION.md 裁定①②⑦+results/_r270bma_pointer_fixes.py skip 腿\n"
)
b = open(P, "rb").read()
assert b.endswith(b"\n") and b"\r\n" not in b[-200:], "byte face drifted (expect LF + trailing nl)"
assert b"R270" not in b, "duplicate append"
open(P, "wb").write(b + ENTRY.encode("utf-8"))
nb = open(P, "rb").read()
print("appended; new size:", len(nb), "bytes (<50KB watermark:", len(nb) < 51200, ")")
