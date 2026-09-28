# r415 bm-a: D-20260929-02(2) domain-immediate action -- codify the slice/pool
# submit fetch double-gate into fleet/README.md sec.4 + sec.9 revision note.
# Byte-level edit: fleet/README.md is pure CRLF; long CJK replace-tool strings
# are avoided per pit-law r198 (bm-c) -- do the insertion in Python instead.
import io, sys

P = "fleet/README.md"
b = open(P, "rb").read()

LAW = (
    "- **切片/池批 fetch 双闸律（D-20260929-02②·2026-09-29）**：MSG 声明式切片**开工前**"
    "+算力池条目 **submit 前**，强制 `git fetch` 重读 `fleet/inbox/` 最新 MSG 面——"
    "**见同面 rival 声明即冻结让路**（r239 池认领 fetch 前置律升格切片面·r394 实弹：声明 08:39:38"
    "→实件 08:47 盲窗内他机独立完成同移植=纯重复开发双烧，幸零格）。撞车已发生=按 commit 时间序"
    "后到让路+重复实件 take-origin 全量撤回（r244 落地标记律）。\r\n"
)
REV = (
    "- v1.1（2026-09-29）——§4 增「切片/池批 fetch 双闸律」（D-20260929-02② 司域即行：r394 "
    "撞车实弹→r239 fetch 前置律升格切片面；①双信号认领窗=HQ fleet-protocol 候选登记随 10-04 周轮，"
    "本司不另立新法防法熵）。\r\n"
)

LAW_B = LAW.encode("utf-8")
REV_B = REV.strip("\r\n").encode("utf-8")

ANCHOR_SEC4 = "- **超时释放**".encode("utf-8")
ANCHOR_SEC9 = "修订走 CODELY.md 记录变更理由与日期。".encode("utf-8")
LAW_KEY = "切片/池批 fetch 双闸律".encode("utf-8")
REV_KEY = "- v1.1（2026-09-29）".encode("utf-8")

assert LAW_KEY not in b, "law already present (idempotency guard)"
assert REV_KEY not in b, "rev note already present"
assert b.count(ANCHOR_SEC4) == 1, "sec4 anchor not unique"
assert b.count(ANCHOR_SEC9) == 1, "sec9 anchor not unique"

out = b.replace(ANCHOR_SEC4, LAW_B + ANCHOR_SEC4, 1)
out = out.replace(ANCHOR_SEC9, ANCHOR_SEC9 + b"\r\n" + REV_B, 1)
open(P, "wb").write(out)

# verify
v = open(P, "rb").read()
assert LAW_KEY in v and REV_KEY in v
assert v.count(b"\r\n") - v.count(b"\n") == 0  # still pure CRLF
assert v.startswith(b"# Bigmoney") 
print("OK bytes", len(b), "->", len(v))
print("law at", v.find(LAW_KEY), "rev at", v.find(REV_KEY))
