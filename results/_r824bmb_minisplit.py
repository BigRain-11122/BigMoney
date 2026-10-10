# r824 bm-b CODELY.md mini-split (D-20261002-06 main <=30KB discipline, r731/r735/r747/r896 ritual)
# Trigger: main file 31,767B > 30,720B cap (bm-a r947 restructure debt) + new r824 lesson append this window.
# Migrations (verbatim, byte-identical):
#   [2026-10-10 03:5x r813 bm-b] dying-session rebase rescue  -> pit-git-resolver-rebase.md (2 rows)
#   [2026-10-10 04:1x r814 bm-b] watermark comparison domain  -> pit-protocol-d19.md (1 row)
# New lesson appended to main file post-split (standard first-entry flow).
import hashlib, io, json

CAP = 30720

def rows(blob):
    out = []
    for ln in blob.split(b"\n"):
        out.append(ln)
    return out

main_p = "CODELY.md"
tgt_a = "research/pit-git-resolver-rebase.md"
tgt_b = "research/pit-protocol-d19.md"

main_b = io.open(main_p, "rb").read()
pre_main = len(main_b)
lines = main_b.split(b"\n")

mig_a_prefixes = [b"- [2026-10-10 03:5x r813 bm-b]"]
mig_b_prefixes = [b"- [2026-10-10 04:1x r814 bm-b]"]

mig_a = [l for l in lines if any(l.startswith(p) for p in mig_a_prefixes)]
mig_b = [l for l in lines if any(l.startswith(p) for p in mig_b_prefixes)]
assert len(mig_a) == 2, "expect 2 r813 rows, got %d" % len(mig_a)
assert len(mig_b) == 1, "expect 1 r814 row, got %d" % len(mig_b)

keep = [l for l in lines if l not in mig_a + mig_b]

new_row = ("- [2026-10-10 08:4x r824 bm-b] **多环 push 爪竞速判例（r813 抢救后续环）**：对端分钟级 tick"
 "（bm-c autofill keepalive 单调前移 pool owner_since）下，任何耗时超过 tick 间隔的 fetch→rebase→resolve"
 " 窗口内远端必再进——pre-push 爪读的是 push 协商时真实远端 tip（非本地 origin/main ref），故两连拦"
 "「owner_since BACKWARD+删除集非己件」均为正确拦截非误报；正解三步单命令竞速=①活 daemon 面 add -A"
 " 吸收成 commit（rebase 拒脏树）②fetch→rebase（零冲突条件=我方提交不触碰对端 tick 面）③push 同命令"
 "连发（r814 同秒律的 push 面延释）——第三环竞速成功 fa222465a..0d0028cdc。禁 --no-verify 逃生门"
 "（会真回退对端 tick）；竞速确不可胜时正典 fallback=machine/<id>-r<N> 分支+轮报告留痕。").encode("utf-8")

keep_with_new = []
inserted = False
for l in keep:
    keep_with_new.append(l)
    if l == b"" and not inserted and keep.index(l) > 40:
        pass
# append new row at the end of the last non-empty row block (before trailing empties)
tail_empty = 0
while keep and keep[-1] == b"":
    keep.pop(); tail_empty += 1
keep.append(new_row)
for _ in range(tail_empty):
    keep.append(b"")

new_main = b"\n".join(keep_with_new if not keep else keep)
io.open(main_p, "wb").write(new_main)

ta = io.open(tgt_a, "rb").read()
ta_new = ta + b"\n" + b"\n".join(mig_a) + b"\n" if not ta.endswith(b"\n") else ta + b"\n".join(mig_a) + b"\n"
io.open(tgt_a, "wb").write(ta_new)

tb = io.open(tgt_b, "rb").read()
tb_new = tb + b"\n" + b"\n".join(mig_b) + b"\n" if not tb.endswith(b"\n") else tb + b"\n".join(mig_b) + b"\n"
io.open(tgt_b, "wb").write(tb_new)

checks = {
    "main_pre": pre_main,
    "main_post": len(new_main),
    "resolver_rebase_pre": len(ta), "resolver_rebase_post": len(ta_new),
    "d19_pre": len(tb), "d19_post": len(tb_new),
    "migrated_bytes_a": sum(len(x) for x in mig_a), "migrated_bytes_b": sum(len(x) for x in mig_b),
    "new_row_bytes": len(new_row),
    "migrated_a_verbatim_in_target": all(x in ta_new for x in mig_a),
    "migrated_b_verbatim_in_target": all(x in tb_new for x in mig_b),
    "migrated_rows_gone_from_main": all(x not in new_main for x in mig_a + mig_b),
    "new_row_in_main": new_row in new_main,
}
checks["main_under_cap"] = checks["main_post"] <= CAP
checks["tgt_a_under_cap"] = checks["resolver_rebase_post"] <= CAP
checks["tgt_b_under_cap"] = checks["d19_post"] <= CAP
io.open("results/_r824bmb_codely_minisplit.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps({"round": "r824", "law": "D-20261002-06 mini <=30KB, r731/r735/r747/r896 ritual",
                "sha16_main_post": hashlib.sha256(new_main).hexdigest()[:16], **checks},
               ensure_ascii=False, indent=1))
print(json.dumps(checks, ensure_ascii=False))
assert checks["main_under_cap"] and checks["tgt_a_under_cap"] and checks["tgt_b_under_cap"]
assert checks["migrated_a_verbatim_in_target"] and checks["migrated_b_verbatim_in_target"]
assert checks["migrated_rows_gone_from_main"] and checks["new_row_in_main"]
print("MINI-SPLIT ALL GREEN")
