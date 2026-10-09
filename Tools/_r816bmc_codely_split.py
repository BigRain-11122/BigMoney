# -*- coding: utf-8 -*-
"""r816 bm-c CODELY mini-split (ritual r441/r731/r747, direct-write r666
paradigm for new laws): migrate the r811 S0-scratch-x-CRLF fake-dirty-loop
entry (original face, verbatim from main tail) + direct-write two new family
faces (r814 pull-fetch-second-window double-reject variant; r815
rebase-direct first-reject variant) -> research/pit-git-resolver-rebase.md
(LF tail); direct-write r815 H3 downloader DOA triple-bug -> research/
pit-data.md (CRLF tail). Main tail block replaced by a compact r816 pointer
line (CRLF). Byte accounting: per-block bytes + sha16, prefix-identity
assert on main, verbatim-bytes-in-target assert, 30,720B caps on all three
files, treasure_guard prescan rc recorded (rel paths per L46 abs-miss pit).
Receipt -> results/_r816bmc_codely_minisplit.json."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(ROOT, "CODELY.md")
REB = os.path.join(ROOT, "research", "pit-git-resolver-rebase.md")
DAT = os.path.join(ROOT, "research", "pit-data.md")
OUT = os.path.join(ROOT, "results", "_r816bmc_codely_minisplit.json")
CAP = 30720
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
A_KEY = "- [2026-10-09 17:1x r811 bm-c]".encode("utf-8")

B_TEXT = (
"- [2026-10-09 18:1x r814 bm-c] **r811 CRLF 假脏环二连拒变体（pull 的 fetch 秒窗活 daemon 再写面→再拒·r811 族第 2 面）**："
"checkout 归一后 pull --rebase 自带的 fetch 秒窗内活 daemon 再写该面（CRLF 漂移面+真重写面叠加）→再拒（r814 实弹）。"
"正法=已 fetch 一次后直接 git rebase origin/main（免 pull 自带 re-fetch 缩窗）+首拒后 drift-normalize checkout 归一+紧重试环 1 发即中"
"（r814/r815 两轮连验 0/0）。How to apply：S0 rebase 拒 unstaged changes 且面为 daemon 活写/CRLF 漂移面时勿走 pull，直接 rebase origin/main。"
)
C_TEXT = (
"- [2026-10-09 18:3x r815 bm-c] **rebase 直跑首发拒变体（fetch-rebase 间隙活 daemon 10 面再写→unstaged·r811 族第 3 面·r814 正法第 2 轮连验）**："
"即便免 pull 直接 rebase，fetch 与 rebase 之间 daemon 活写面（autofill/saturation/marks 族）仍可再写→rebase 首发拒 unstaged changes（r815 实弹 10 面）。"
"正法=rebase 首拒后 status --porcelain 取「 M」面集→git checkout -- <faces> drift-normalize（可再生状态件零信息损失）→rebase retry 1 发即中。"
"How to apply：S0 助手 rebase 拒收先按 r814 正法直跑，首拒即 drift-normalize+retry 一发，禁手工逐面排查（三步闭环已入 _r811bmc_s0.py 1-gen 血统）。"
)
D_TEXT = (
"- [2026-10-09 18:3x r815 bm-c] **H3 下载器 DOA 三连 bug（分离长活下载器零可见性假活面·r814 点火 22min 死面实弹）**："
"①urllib urlopen timeout=(30,90) 元组=非法形态（requests 惯用法误植入 urllib·每线程即抛 TypeError·单值 only）——urllib 族 timeout 只收单值；"
"②except 静默吞+5s 重试环=零可见性假活面（进程活·CPU 1.4s 停滞·零字节·runner.out 0B·错误零落盘）——长活诊断三判据=CPU 时间停滞+字节零增+日志零行；"
"③deploy 脚本 manifest 声明字节≠服务器真值（file2 目标 156,871,142,551=10× 错·服务器 Content-Range 真值 15,687,142,551·五 URL 探针全 206 交叉验证；"
"manifest 服务器真和 40,282,065,079B vs 脚本声明 40,282,346,779 差 281,700B）——目标字节一律服务器 Content-Range 实测为准禁脚本声明面直信。"
"How to apply：分离下载器点火后必验活面三判据（CPU/字节/日志）；silent except 禁入长活脚本（错误面必须 state json 可见化）；"
"多线程下载目标字节先探针 Content-Range 真值再落 target 字段。"
)
PTR_TEXT = (
"- 域指针·r816 bm-c mini-split（10-09 18:5x·主件 30,544B 余量 176B 红线·仪式 r731/r747 同款）："
"r811 S0 scratch×CRLF 假脏环条目（原面）+r814 二连拒变体（pull fetch 秒窗·正法=fetch 后直接 rebase）"
"+r815 rebase 直跑首发拒变体（drift-normalize+retry 一发）三面 verbatim/direct-write→pit-git-resolver-rebase.md"
"+r815 H3 下载器 DOA 三连 bug（urllib timeout 元组+静默吞重试环+10× 字节）direct-write→pit-data.md〔r666 直写先例〕"
"——逐块字节+sha16 对账=receipt results/_r816bmc_codely_minisplit.json（零丢失断言=逐块 bytes in target verbatim"
"+主件保留面恒等+主/域件 ≤30KB·prescan rc 留痕）；新坑律仍先入主件后回扫（直写例外 r666 范式）。"
)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    old_main = open(MAIN, "rb").read()
    old_reb = open(REB, "rb").read()
    old_dat = open(DAT, "rb").read()
    # prescan (rel paths per L46 abs-form silent-miss pit)
    pr = subprocess.run(
        [sys.executable, os.path.join("Tools", "treasure_guard.py"), "prescan",
         "CODELY.md", "research/pit-git-resolver-rebase.md",
         "research/pit-data.md"],
        cwd=ROOT, capture_output=True, creationflags=CNW, timeout=60)
    prescan_rc = pr.returncode
    prescan_out = (pr.stdout or b"").decode("utf-8", "replace")[:300]
    # block A: verbatim tail line of main (line + its CRLF)
    off = old_main.rfind(A_KEY)
    assert off > 0, "r811 block not found in main"
    blockA = old_main[off:]
    assert blockA.endswith(b"\r\n"), "blockA tail CRLF expected"
    prefix = old_main[:off]
    # new blocks: resolver-rebase target uses LF; pit-data uses CRLF
    blockB = B_TEXT.encode("utf-8") + b"\n"
    blockC = C_TEXT.encode("utf-8") + b"\n"
    blockD = D_TEXT.encode("utf-8") + b"\r\n"
    ptr = PTR_TEXT.encode("utf-8") + b"\r\n"
    new_reb = old_reb + blockA + blockB + blockC
    new_dat = old_dat + blockD
    new_main = prefix + ptr
    # zero-loss asserts
    blocks = {"A_r811": blockA, "B_r814": blockB, "C_r815": blockC,
              "D_h3doa": blockD}
    assert blockA in new_reb, "A not verbatim in resolver-rebase"
    assert blockB in new_reb and blockC in new_reb, "B/C not in target"
    assert blockD in new_dat, "D not verbatim in pit-data"
    assert new_main[:off] == prefix, "main prefix identity broken"
    assert len(new_main) <= CAP and len(new_reb) <= CAP and len(new_dat) <= CAP
    # write
    open(MAIN, "wb").write(new_main)
    open(REB, "wb").write(new_reb)
    open(DAT, "wb").write(new_dat)
    receipt = {
        "round": 816, "machine": "bm-c",
        "prescan_rc": prescan_rc, "prescan_out": prescan_out,
        "sizes_before": {"CODELY.md": len(old_main),
                         "pit-git-resolver-rebase.md": len(old_reb),
                         "pit-data.md": len(old_dat)},
        "sizes_after": {"CODELY.md": len(new_main),
                        "pit-git-resolver-rebase.md": len(new_reb),
                        "pit-data.md": len(new_dat)},
        "blocks": {k: {"bytes": len(v), "sha16": sha16(v),
                       "target": ("pit-git-resolver-rebase.md"
                                  if k != "D_h3doa" else "pit-data.md")}
                   for k, v in blocks.items()},
        "pointer_line": {"bytes": len(ptr), "sha16": sha16(ptr)},
        "asserts": {
            "blocks_verbatim_in_target": True,
            "main_prefix_identity": True,
            "main_le_cap": len(new_main) <= CAP,
            "reb_le_cap": len(new_reb) <= CAP,
            "dat_le_cap": len(new_dat) <= CAP,
            "main_delta": len(new_main) - len(old_main),
            "reb_delta": len(new_reb) - len(old_reb),
            "dat_delta": len(new_dat) - len(old_dat),
        },
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, indent=1, ensure_ascii=False)
    print("MINISPLIT-OK main=%d reb=%d dat=%d prescan_rc=%d"
          % (len(new_main), len(new_reb), len(new_dat), prescan_rc))
    for k, v in blocks.items():
        print("  %s %dB %s" % (k, len(v), sha16(v)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
