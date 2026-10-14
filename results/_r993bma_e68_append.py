# -*- coding: utf-8 -*-
"""r993 bm-a: append E68 methodology card (twin-pair side-alignment law in shared-regen rebase resolve).
Multi-writer file: fresh-read-append in one process (replace-tool append ban law)."""
import io, sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"knowledge\METHODOLOGY_ASSETS.md"
t = io.open(P, encoding="utf-8").read()
CARD = """

- **E68 twin 对同侧配对律（共享再生面 rebase resolve 的 md/json 双胞胎分侧坑）**：proven，工程面。shared-regen 批 rebase resolve 中 REPORT/LIVE 等「md+json 孪生对」禁按文件独立裁侧——json 侧可 deep-ts 解析（ta/tb 比较出 16:51 vs 16:42 精确胜方），md 侧常不可解析（裸 markdown 头 ts 探针 miss）→回退 commit-side 法则两侧不对称=**md/json 孪生分侧错账**（json 取 replay 16:51、md 取 origin 16:42=CEO 面文件对自相矛盾·json↔md 内容漂移）。正法=**孪生对裁侧以可解析侧为准、md 强制同侧**（pair-alignment leg：json deep-ts 胜方侧→md checkout --theirs/--ours 同侧硬接线）；E52 归一律解决「同侧怎么比」，本卡解决「对内怎么同侧」——resolver 脚本须先枚举孪生对清单再逐对裁侧，禁逐文件散裁。live 实证：r993 bm-a（19-UU 批 resolve 首跑 md 三件错侧→同窗 checkout --theirs 配对改判·REPORT/LIVE 10-14 三对 md=json 同侧收口零漂移）。"""
assert "E68" not in t, "E68 already present"
io.open(P, "a", encoding="utf-8", newline="").write(CARD)
t2 = io.open(P, encoding="utf-8").read()
assert "E68 twin" in t2 and len(t2) > len(t)
print("E68-APPENDED", len(t), "->", len(t2))
