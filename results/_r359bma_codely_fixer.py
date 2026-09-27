# -*- coding: utf-8 -*-
"""r359 bm-a fixer pass for the 30th-batch restructure: (a) CODELY.md pointer
rows written by _r359bma_codely_restructure.py carried over-long conclusions
(file 12,547B > 10,240B hard line) -- rewrite all 13 pointer rows with
one-sentence conclusions; (b) archive 30th-batch section got the r359 verbatim
line appended BEFORE the section header (conditional-fold branch ran before
the header block) -- rebuild that section cleanly. Verbatim-in-archive and
final-size assertions fail-closed."""
import io
import sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

SHORT = {
    "18:35 r96 bm-c]": ("二十九", "收尾时间戳一律 fresh read、epoch/clock_read 同次取时派生、对外留痕以 git %ci 为锚"),
    "19:17 r345 bm-a]": ("二十九", "resolver 取新探针键表漏生产者拼写→假 tie 误取旧侧；逐件显式写时键探+同键异值 side-diff 复验"),
    "20:1x r100 bm-c]": ("二十九", "探针键下划线变体漏配+非 ts 值毒化 max；正典=目录硬化（键 strip 全剥再前配+值 ^20\\d{2}- 形门）"),
    "20:0x r350 bm-a]": ("二十九", "探针排除表本身=新 miss 载体；键歧义靠值形门裁决、idempotent 探针读 stage blob"),
    "20:3x r101 bm-c]": ("二十九", "树重建后 lane owner 必盘点 gitignored 原始采集面 vs 派生面分核"),
    "20:1x r340 bm-b]": ("二十九", "池批 checkpoint 保尾=中途 kill 全批重烧；正典=on_result 增量落盘+flushed-set 防双写"),
    "20:5x r351 bm-a] 坑律（二十九批外迁·指针）：rebase 重放窗": ("二十九", "rebase 重放窗侧位=「:2:=HEAD 对岸面 / :3:=本链面」与 merge 直觉相反；先落侧位断言再动手"),
    "20:5x r351 bm-a] 坑律（二十九批外迁·指针）：rebase UU 停点窗": ("二十九", "UU 停点窗 tick blind-add 毁共享件 stage；读 stage 失败先定件态；:X0:01 tick 前后 1min 禁 resolver 批"),
    "20:4x r353 bm-a]": ("二十九", "strip 只剥两端不剥中间（as_of 族漏探假 tie）；键名 re.sub 全剥再前配；js 包装件禁 json.loads 直吞"),
    "21:1x r355 bm-a]": ("二十九", "同轮二撞头已解件常被 auto-merge；resolver 逐 handler 带 UU-membership guard+side-assert :3: 固定指纹"),
    "21:3x r109 bm-c]": ("三十", "轮首脏树=tick 单行热写；先定向提交该件再 pull --rebase；同窗撞行 take-new max ts 手工 resolve 禁起 resolver"),
    "21:15 r342 bm-b]": ("三十", "PS Start-Job 不继承 CWD；job 块首显式 Set-Location 仓根+Wait-Job -Timeout 有界收口；死窗探测一律有界化"),
    "22:1x r359 bm-a]": ("三十", "网络死窗整件提交静默吞池行（W2B 实弹）；watch-face 每轮对实文件复验；共享件死窗提交必对账 union；恢复=权威版本 verbatim 复位+零丢失复验"),
}


def detect_newline(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return "\r\n" if b"\r\n" in raw else "\n"


def main():
    nl = detect_newline(CODELY)
    anl = detect_newline(ARCHIVE)
    with io.open(CODELY, encoding="utf-8") as fh:
        lines = [ln.rstrip("\r\n") for ln in fh]

    # (a) rewrite the 13 pointer rows with short conclusions
    n_rewritten = 0
    for i, ln in enumerate(lines):
        for key, (batch, short) in SHORT.items():
            if key in ln and "批外迁·指针）：" in ln:
                tag = ln.split(" 坑律（")[0]
                lines[i] = (f"{tag} 坑律（{batch}批外迁·指针）：{short}"
                            f"——全文 verbatim=research/memory-archive/202609.md"
                            f"『坑律归档 2026-09-27 {batch}批』节。")
                n_rewritten += 1
                break
    assert n_rewritten == 13, f"pointer rows rewritten={n_rewritten} != 13"

    with io.open(CODELY, "w", encoding="utf-8", newline=nl) as fh:
        fh.write(nl.join(lines) + nl)

    # (b) rebuild archive tail: the stray r359 line must move INSIDE the 30th-batch section
    with io.open(ARCHIVE, encoding="utf-8") as fh:
        arch_lines = [ln.rstrip("\r\n") for ln in fh]
    hdr_i = [i for i, ln in enumerate(arch_lines)
             if ln.startswith("## 坑律归档 2026-09-27 三十批")]
    assert len(hdr_i) == 1, f"30th-batch headers={len(hdr_i)}"
    h = hdr_i[0]
    assert "r359 bm-a" in arch_lines[h - 1], "expected stray r359 line right before header"
    stray = arch_lines.pop(h - 1)                       # remove stray line
    # section now = header + r109 + r342; append r359 verbatim at section end
    insert_at = h  # after pop, header index = h-1; first line after section content:
    # find end of section (next blank line after header) -> just append after r342 row
    j = h  # header is at h-1 now; rows follow
    while j < len(arch_lines) and arch_lines[j].startswith("- [2026-09-27"):
        j += 1
    arch_lines.insert(j, stray)
    with io.open(ARCHIVE, "w", encoding="utf-8", newline=anl) as fh:
        fh.write(anl.join(arch_lines) + anl)

    # ---- verify pass ----
    with io.open(ARCHIVE, encoding="utf-8") as fh:
        arch_text = fh.read()
    hh = arch_text.index("## 坑律归档 2026-09-27 三十批")
    section = arch_text[hh:]
    for key in ("21:3x r109 bm-c]", "21:15 r342 bm-b]", "22:1x r359 bm-a]"):
        assert key in section, f"30th-batch section missing {key}"
    size = len(open(CODELY, "rb").read())
    assert size <= 10240, f"CODELY.md still over hard line: {size}B"
    print(f"fixer OK: 13 pointer rows shortened, archive 30th-batch section "
          f"clean (header -> r109 -> r342 -> r359 verbatim order), "
          f"CODELY.md -> {size}B <= 10,240B hard line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
