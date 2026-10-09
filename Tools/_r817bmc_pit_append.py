# -*- coding: utf-8 -*-
"""r817 bm-c pit direct-append (r666 direct-write precedent; pure append of
NEW entries, zero deletion -> no treasure_guard prescan trigger family).
Two new pit entries (live-fire this round) + one HQ-FEEDBACK receipt row
(O-1715 @bm-c audit receipt + mechanism suggestion). UTF-8 LF-safe append
(tail-newline guard); pit domain files size-gated <=30,720B after append.
Receipt: results/_r817bmc_pit_append.json (bytes+sha16 per block)."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

E_PIT_PS = (
    "- [2026-10-09 19:2x r817 bm-c] **PS 管道 Select-Object -First N 截杀 native 命令"
    "→$LASTEXITCODE 停留前值→分支误走坑（fleet-link v1.2 升级窗实弹·零持久伤害当场自愈）**："
    "`git fetch ... | Select-Object -First 2` 在 Select 收满 2 对象时提前终止管道→上游 git 被"
    "截杀（未及落自身 exit code）→$LASTEXITCODE 停留在上一条 native（checkout rc0）的 0→"
    "`if ($LASTEXITCODE -ne 0)` 误判 fetch 成功走 else 腿（对陈旧 origin/main merge 出假 "
    "up-to-date 面）。正法=①分支判定腿的 native 命令禁接 -First N/截断管道——输出先全量落"
    "变量/文件再消费；②$LASTEXITCODE 判定必须紧跟目标 native 命令（中间禁插管道截断件）；"
    "③截断消费改先 `($out = git ...)` 全量落变量再 Select。How to apply：一切 rc 分支腿="
    "裸跑 native→先判 $LASTEXITCODE→再消费输出。\n")

E_PIT_TOOLING = (
    "- [2026-10-09 19:1x r817 bm-c] **fleet-workspace-audit A-sync 判读=fetch 断链期陈旧 "
    "tracking ref 假 FAIL 坑（O-1715 @bm-c 首跑实弹）**：审计窗 GitHub SSH 连环 reset（7 次）"
    "→A 腿 fetch 全败→判据用本地陈旧 origin/main 引用比 HEAD→本机刚 push 的 tip（HEAD="
    "7b486b31=19:10 canon push 回执时点 live tip）被报 FAIL——实况=同步绿（HEAD⊇origin 全部"
    "+自身已推）。正法=①A FAIL 先 `git rev-list --left-right --count HEAD...origin/main` 分辨 "
    "ahead/behind：纯 ahead+push 回执在案=假警报；②fetch 失败期同步判读挂 channel-outage "
    "注记禁直判 FAIL；③live 复核走 ls-remote（通道允许时）+push 回执时间戳。How to apply："
    "通道断链窗审计/同步判读必过 ahead-behind 分辨门+push 回执核。\n")

E_HQ = (
    "- F-20261009-05 [bm-c r817 2026-10-09T19:2x+08:00·决策回执面·O-20261009-1715 @bm-c 机队"
    "工作区审计首跑+同律整改回执（≤24h 令·含机制建议）] **bm-c 审计首跑 VERDICT FAIL→同窗整改"
    "面：B 脏面治愈+A 面证伪；建议 A-sync 腿加 ahead/behind 分辨+通道断链挂起注记**——①首跑证据"
    "=results/_r817bmc_ws_audit.txt（A sync=FAIL·B dirty=1〔Tools/fleet-link.ps1 盘面陈旧 v1.2 "
    "覆写·HEAD 已含 bm-a ebef6de v1.3〕·C=0·E=0·D 面=quant/bigmoney 本轮收口推送自愈·"
    "gaming/MiniGame GIT_BIG 2172MB ahead5379=owner 司域件在委员会案册非 bm-c 整改面）；②A FAIL "
    "证伪=审计窗 SSH 连环 reset（7 次 Connection reset）→fetch 全败用陈旧 origin/main 引用"
    "（1bb9119a=HEAD 7b486b31 之父）判 HEAD≠origin——rev-list 分辨纯 ahead 1=自身 canon push"
    "（19:10 push 回执在案）+merge --ff-only \"Already up to date\" 铁证=假 FAIL；③同窗整改="
    "B 面 checkout 复原 v1.3+监听器 5min 保活自升级实证（/health version=1.3）+树净面；④建议="
    "A 腿判据升「ls-remote live tip+ahead/behind 分辨+fetch 失败挂 channel-outage 注记不判 "
    "FAIL」；live 更新复核因通道 reset 挂起下轮 heal 复核（挂起注记如实）。状态=open（集团周"
    "进化轮收取）\n")

TARGETS = [
    (os.path.join(ROOT, "research", "pit-ps.md"), E_PIT_PS, True),
    (os.path.join(ROOT, "research", "pit-tooling.md"), E_PIT_TOOLING, True),
    (os.path.join(ROOT, "HQ-FEEDBACK.md"), E_HQ, False),
]


def main():
    receipt = {"round": 817, "blocks": []}
    for path, entry, gate in TARGETS:
        with open(path, "rb") as f:
            raw = f.read()
        pre = len(raw)
        prefix = b"" if raw.endswith(b"\n") else b"\n"
        blob = prefix + entry.encode("utf-8")
        with open(path, "ab") as f:
            f.write(blob)
        with open(path, "rb") as f:
            post = len(f.read())
        assert post == pre + len(blob), "size mismatch " + path
        if gate:
            assert post <= 30720, "pit file over cap: %s %dB" % (path, post)
        receipt["blocks"].append({
            "file": os.path.relpath(path, ROOT),
            "pre_bytes": pre, "append_bytes": len(blob), "post_bytes": post,
            "sha16": hashlib.sha256(blob).hexdigest()[:16],
        })
    outp = os.path.join(ROOT, "results", "_r817bmc_pit_append.json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    for b in receipt["blocks"]:
        print("%s %dB->%dB +%dB sha16=%s" % (
            b["file"], b["pre_bytes"], b["post_bytes"], b["append_bytes"],
            b["sha16"]))
    print("receipt=%s" % outp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
