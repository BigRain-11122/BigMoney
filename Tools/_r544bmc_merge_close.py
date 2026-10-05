# -*- coding: utf-8 -*-
"""r544 bm-c merge close phase-2 (r511-③ law: git output consumption via
python subprocess stdout-only; wrapper stderr-merge poisoned the PS UU check
with CRLF warning lines -> false UU, fail-fast exit 1 with 20 faces staged,
merge state intact -- this driver redoes: UU assert (stdout-only) ->
merge commit -F -> push -> fetch -> rev-list count -> ls-tree probes ->
honest S7-close line append (tail-defer on any failure)."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CREATE = 0x08000000


def git(args):
    r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return r.returncode, r.stdout.decode("utf-8", "replace").strip(), \
        r.stderr.decode("utf-8", "replace").strip()


def main():
    out = {}
    # 1. ZERO-UU assertion (stdout-only truth source, r713+r511-③ laws)
    rc, uu, _ = git(["diff", "--name-only", "--diff-filter=U"])
    uu_paths = [x for x in uu.splitlines() if x.strip()]
    if rc != 0:
        print("FAIL: diff rc=%d" % rc)
        return 2
    if uu_paths:
        print("FAIL: UU REMAINS %d: %s" % (len(uu_paths), uu_paths))
        return 1
    print("ZERO-UU ok (stdout-only)")
    # 2. staged face count (name-only stdout-only)
    rc, names, _ = git(["diff", "--cached", "--name-only"])
    face_list = [x for x in names.splitlines() if x.strip()]
    print("staged_faces=%d" % len(face_list))
    out["staged_faces"] = len(face_list)
    # 3. merge commit -F
    rc, so, se = git(["commit", "-F",
                      r"K:\Fluxgroup\FluxGroup\quant\.codely-cli\scratch\_r544bmc_mergemsg.txt"])
    print("commit rc=%d %s" % (rc, so.splitlines()[0] if so else se[:120]))
    if rc != 0:
        print("FAIL: commit rc=%d stderr=%s" % (rc, se[:300]))
        return 1
    rc, sha, _ = git(["log", "-1", "--format=%h"])
    print("HEAD=%s" % sha)
    out["merge_commit"] = sha
    # 4. push
    prc, so, se = git(["push", "origin", "main"])
    print("push rc=%d %s" % (prc, (se or so)[:160]))
    # 5. fetch + count
    git(["fetch", "origin"])
    rc, cnt, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    print("post-push count=%r" % cnt)
    parts = cnt.split()
    ahead = int(parts[0]) if parts and parts[0].isdigit() else -1
    behind = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else -1
    # 6. ls-tree probes (stdout-only, 40hex assert)
    probe = ["qa/equity-curve-r544.png", "qa/smoke-r544.md",
             "results/_r544bmc_s6_log.txt",
             "results/_r544bmc_merge_resolve.json",
             "round_reports-bm-c.md", "state-bm-c.json"]
    hitp = 0
    for p in probe:
        rc, blob, _ = git(["rev-parse", "HEAD:" + p])
        if re.match(r"^[0-9a-f]{40}$", blob):
            hitp += 1
        else:
            print("PROBE_MISS: %s" % p)
    print("ls-tree probe %d/%d" % (hitp, len(probe)))
    out["probe"] = "%d/%d" % (hitp, len(probe))
    out["push_rc"] = prc
    out["ahead"], out["behind"] = ahead, behind
    # 7. tail-defer honest close line
    if prc == 0 and ahead == 0 and behind == 0:
        now = datetime.now().astimezone().isoformat(timespec="seconds")
        line = (
            "%s | r544 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0"
            "（DELIVERED 两跳收口 per r524 律：首 push 拒〔落后 origin 信号·他机 bm-a r726 收口波 "
            "2 commit 同窗竞态·tail-defer 门当拦零假行〕→fetch 实核 count=2/2→merge origin/main 停 "
            "18-UU〔全 S6 再生面双写竞态·r726 镜像窗〕→resolver 18/18 全 ours-newer〔定向归一 ts 探针 "
            "r711·孪生同侧 r708·history/per-key union r515·readback 断言 r704·残留屏 18/18 r505·回执 "
            "results/_r544bmc_merge_resolve.json〕→UU 复核走 python stdout-only〔r511-③ 律·PS 面首试被"
            "包装器 stderr 合流 CRLF warning 假 UU 拦·fail-fast 零半提交零伤害〕→merge commit %s→push "
            "rc=%d 复推首过过双爪零 --no-verify→push_verify 复证 count=%d/%d·ls-tree 送达探针 %d/%d blob "
            "40hex 在册）| 零清扫/归档/删除/恢复类动作轮：登记册零命中断言 N/A-无此类动作"
            % (now, sha, prc, ahead, behind, hitp, len(probe)))
        rp = os.path.join(ROOT, "round_reports-bm-c.md")
        raw = open(rp, "rb").read()
        eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
        with open(rp, "ab") as f:
            f.write(eol + line.encode("utf-8"))
        print("S7-close line appended (two-hop honest, host-eol=%s)"
              % ("CRLF" if eol == b"\r\n" else "LF"))
    else:
        print("TAIL_DEFERRED: push rc=%d count=%d/%d -- line NOT written"
              % (prc, ahead, behind))
        return 1
    with open(os.path.join(ROOT, "results", "_r544bmc_close_receipt.json"),
              "wb") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
