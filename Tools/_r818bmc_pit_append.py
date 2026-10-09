# -*- coding: utf-8 -*-
"""r818 bm-c pit direct-append (r666 direct-write precedent; pure append of
NEW entries, zero deletion -> no treasure_guard prescan trigger family).
One new pit entry (live-fire this round): drift-normalize checkout restores
a live long-runner's milestone-written state json to the git HEAD face --
diagnosis from it misleads; truth-teller = the runner's write-targets
(part files + mtimes) + process query. r811 family face 4 (diagnosis face,
not the refusal-loop face of r811/r814/r815).
Receipt: results/_r818bmc_pit_append.json (bytes+sha16 per block)."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

E_PIT_REBASE = (
    "- [2026-10-09 19:2x r818 bm-c] **drift-normalize checkout 还原活长跑器 state 件=陈旧假面"
    "坑（r811 族第 4 面·诊断面·r815 H3 下载器实弹）**：S0 checkout -- 归一的「可再生状态件」"
    "若属活长跑器（下载/烧批 daemon）的 state json，checkout 会还原成 git HEAD 版（=早期初始"
    "化面），而 daemon 只在里程碑/错误时回写盘——r815 H3 下载器实测：内存态已推进到 file-2 且 "
    "file-1 已完成落盘验讫，盘面 state json 仍显 file-1 init 面（曾一度误诊「驱动卡死 file-1/"
    "并发双驱动」险些错误干预）；r811/r814/r815 治的是 rebase 拒收环，本条治的是诊断面。正法="
    "活长跑器诊断一律看其写目标实体（part 分段文件+mtime 进度、产物文件、进程 CPU 时间+命令行"
    "实测），禁以 git 还原后的 state json 作在飞态证据；state 件面只作静态里程碑史。How to "
    "apply：S0 checkout 后读任何 in-flight 面先问「这是 daemon 亲写盘还是 git 还原脸」——"
    "daemon 亲写面（mtime 晚于 checkout 时点）才可作证据。\n")

TARGETS = [
    (os.path.join(ROOT, "research", "pit-git-resolver-rebase.md"),
     E_PIT_REBASE, True),
]


def main():
    receipt = {"round": 818, "blocks": []}
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
    outp = os.path.join(ROOT, "results", "_r818bmc_pit_append.json")
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
