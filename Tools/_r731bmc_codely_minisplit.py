"""r731 bm-c CODELY mini-split: main at 30,606B (114B headroom) -> new
pit-law row must not push it over the 30,720B cap (D-20261002-06).
Surgery (r666 direct-write family + r703 mini-split precedent):
  1. new amend-on-pushed-commit pit row -> research/pit-git-staged.md
     (verbatim direct-write, commit-entry-gate family, r806/r689 same domain)
  2. r853 row (GitHub stale-fullname 404, 338B) -> research/pit-tooling.md
     verbatim migration out of main
  3. main: r853 row replaced by one compact pointer row
  4. byte-accounting receipt + assertions (main <= 30720 post-op,
     moved block sha16 recorded, verbatim-in-target verified)
Receipt -> results/_r731bmc_codely_minisplit.json"""
import hashlib
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(REPO, "CODELY.md")
STAGED = os.path.join(REPO, "research", "pit-git-staged.md")
TOOLING = os.path.join(REPO, "research", "pit-tooling.md")
RCPT = os.path.join(REPO, "results", "_r731bmc_codely_minisplit.json")

CAP = 30720

R853 = ("- [2026-10-08 01:2x r853 bm-a] **GitHub 手写库全名过期 404 坑（OSS 扫描 3/6 实弹）**："
        "手写 owner/repo 三条过期全 404（gplearn→trevorstephens、mbhushan→PyPortfolioOpt、"
        "dcajasun→dcajasn）；正法=外部库全名禁手写，一律 search-by-name 实证"
        "（search 自带 star/license/push 免 core 重取）。")

NEW_PIT = ("- [2026-10-08 05:1x r731 bm-c] **amend 改写已推提交坑（收口尾随登记窗实弹"
           "·同窗 -m 包装器引号吞重踏·零损失自愈）**：收口 tail 提交已 push 后用 "
           "`git commit --amend` 补登记新件=本地历史与 origin 分叉（origin tip b41e6240e "
           "已在册·amend 后本地 e6bcbf0b1）→push 必非快进被拒、禁 force=无合法出路；"
           "正法三件=①amend 前必 ls-remote 核 origin tip（已含目标提交=禁 amend 改走新提交"
           "快进）②已推后补登记一律新提交（amend/rebase 只许作用于零-push 本地面）"
           "③误 amend 后=reset --soft 回已推 tip（index 保全）+新提交+快进 push——"
           "实弹自愈：reset --soft b41e6240e→tail3 02c8ab3d4→push CLEAN"
           "（b41e6240e..02c8ab3d4·三证恒等·零 force 零改写零丢失）。"
           "How to apply：尾随登记批模板必带 ls-remote 前置门；-m 一律 -F 消息件替代"
           "（r849/r731 双踏）。")

POINTER = ("- 域指针·r731 bm-c（10-08）：amend 已推提交坑（push 必非快进·禁 force→"
           "正法=ls-remote 前置门+reset --soft 回已推 tip+新提交快进·实弹零损失）"
           "→pit-git-staged.md〔r806/r689 同域〕+r853 行（GitHub 手写库全名 404）"
           "verbatim 迁 pit-tooling.md；收据=results/_r731bmc_codely_minisplit.json。")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    main_bytes = open(MAIN, "rb").read()
    before_main = len(main_bytes)
    text = main_bytes.decode("utf-8")
    assert text.count(R853) == 1, "r853 row must appear exactly once in main"
    assert R853 + "\n" in text or text.endswith(R853), "r853 row at tail"
    new_text = text.replace(R853, POINTER)
    assert R853 not in new_text and POINTER in new_text
    # verify pure swap: only the swapped block differs
    assert len(new_text) == len(text) - len(R853) + len(POINTER)
    open(MAIN, "w", encoding="utf-8", newline="").write(new_text)

    # 1) new pit row -> pit-git-staged.md (verbatim direct-write)
    st_bytes = open(STAGED, "rb").read()
    st_text = st_bytes.decode("utf-8")
    if not st_text.endswith("\n"):
        st_text += "\n"
    st_text += NEW_PIT + "\n"
    open(STAGED, "w", encoding="utf-8", newline="").write(st_text)

    # 2) r853 row -> pit-tooling.md (verbatim migration)
    tl_bytes = open(TOOLING, "rb").read()
    tl_text = tl_bytes.decode("utf-8")
    if not tl_text.endswith("\n"):
        tl_text += "\n"
    tl_text += R853 + "\n"
    open(TOOLING, "w", encoding="utf-8", newline="").write(tl_text)

    # assertions + receipt
    after_main = len(open(MAIN, "rb").read())
    assert after_main <= CAP, "main must be <= 30720 post-op, got %d" % after_main
    assert R853.encode("utf-8") in open(TOOLING, "rb").read(), "verbatim in target"
    assert NEW_PIT.encode("utf-8") in open(STAGED, "rb").read(), "new pit verbatim in target"
    rcpt = {
        "round": 731,
        "op": "codely-minisplit-r731",
        "main_bytes_before": before_main,
        "main_bytes_after": after_main,
        "main_cap": CAP,
        "migrated": {
            "row": "r853 GitHub stale-fullname 404",
            "bytes": len(R853.encode("utf-8")),
            "sha16": sha16(R853.encode("utf-8")),
            "to": "research/pit-tooling.md",
        },
        "direct_write": {
            "row": "r731 amend-on-pushed-commit pit",
            "bytes": len(NEW_PIT.encode("utf-8")),
            "sha16": sha16(NEW_PIT.encode("utf-8")),
            "to": "research/pit-git-staged.md",
        },
        "pointer_row_bytes": len(POINTER.encode("utf-8")),
        "zero_loss_assert": True,
        "staged_bytes_after": len(open(STAGED, "rb").read()),
        "tooling_bytes_after": len(open(TOOLING, "rb").read()),
    }
    json.dump(rcpt, open(RCPT, "w", encoding="utf-8"), indent=1)
    print(json.dumps(rcpt, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
