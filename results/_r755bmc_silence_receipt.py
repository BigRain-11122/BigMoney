# -*- coding: utf-8 -*-
"""r755 bm-c silence-order receipt CAS (O-20261008-1240-bm-c): append bm-c
receipt sub-line under the P-2026-10-08-11 row in cph4/evolution-ledger.md,
CAS direct-commit to group origin/main (single-blob edit, r739 law family:
40-hex hard validation, push keyword scan, ls-remote tip verify, one retry)."""
import datetime
import json
import os
import re
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000
TARGET = "cph4/evolution-ledger.md"


def git(args, env=None):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace"), \
        p.stderr.decode("utf-8", "replace")


def build_ledger_text(now_hm):
    rc, text, err = git(["show", "origin/main:" + TARGET])
    if rc != 0:
        raise SystemExit("ABORT show: %s" % err[:200])
    eol = "\r\n" if "\r\n" in text[:2000] else "\n"
    lines = text.split(eol)
    idx = -1
    for i, ln in enumerate(lines):
        if ln.startswith("- **P-2026-10-08-11 |"):
            idx = i
            break
    assert idx >= 0, "P-11 row not found"
    receipt = ("  - 回执（bm-c r755·2026-10-08 " + now_hm + "·收令=轮首双扫#2 11:54·≤1h SLA 内）："
               "O-20261008-1240-bm-c 三步毕——①silence-enforce.ps1 首跑（origin verbatim 本地落位·hash 恒等）"
               "=闸读回 ToastEnabled=0 ✓（10-06 落 C 机后首次自复写）+NOC 门=absent（本机无 ximalaya 键）"
               "+任务审计违规计数=0（全任务链 wscript 隐藏合规）+Quark 面=3 旧任务已 Disabled+1.0.0.21 现役任务 "
               "Disable-ScheduledTask 拒绝访问（厂商 ACL 硬化·提权处置=物理件域如实披露）+HKCU Run Quark 键零残留 ✓；"
               "②HQ-SilenceGuard 常设自愈任务已注册（本机用户登录+每日 04:07·wscript //B //nologo 隐藏链跑本地 "
               "Tools\\silence-enforce.vbs→ps1·WorkingDirectory=组根·下跑 2026/10/9 04:07 实锚）；"
               "③合规 JSON 已落 .codely-cli/patrol/silence-audit.json（host=FLUXGROUP·toast_gate=0·violations=0）"
               "供 patrol 消费；附注=脚本 quark_updater_killed 字段在多任务机输出 System.Object[] 形态缺陷（@HQ 修法面）。"
               "[via bm-c r755]")
    lines.insert(idx + 1, receipt)
    return eol.join(lines), receipt


def cas_push(ledger_text, msg_text):
    tmp_ledger = os.path.join(REPO, "results", "_r755bmc_cas_ledger2.md")
    tmp_msg = os.path.join(REPO, "results", "_r755bmc_cas_msg2.txt")
    idx = os.path.join(REPO, "results", "_r755bmc_cas2.index")
    for path, content in ((tmp_ledger, ledger_text), (tmp_msg, msg_text)):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
    rc, base, err = git(["rev-parse", "origin/main"])
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", base.strip()):
        return None, "bad base"
    p = subprocess.run(["git", "-C", GROUP, "hash-object", "-w", tmp_ledger],
                       capture_output=True, creationflags=CF)
    blob = p.stdout.decode("utf-8", "replace").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", blob):
        return None, "bad blob"
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    if os.path.exists(idx):
        os.remove(idx)
    rc, _, err = git(["read-tree", base.strip()], env=env)
    if rc != 0:
        return None, "read-tree: %s" % err[:150]
    rc, _, err = git(["update-index", "--add", "--cacheinfo", "100644", blob,
                      TARGET], env=env)
    if rc != 0:
        return None, "update-index: %s" % err[:150]
    rc, tree, err = git(["write-tree"], env=env)
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", tree.strip()):
        return None, "bad tree"
    rc, newc, err = git(["commit-tree", tree.strip(), "-p", base.strip(),
                         "-F", tmp_msg])
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", newc.strip()):
        return None, "bad commit"
    rc, out, err = git(["push", "origin", newc.strip() + ":main"])
    combined = (out + " " + err).lower()
    if rc != 0 or any(k in combined for k in ("fatal", "rejected", "failed",
                                              "error")):
        return None, "push fail rc=%d %s %s" % (rc, out[:150], err[:150])
    rc, tip, _ = git(["ls-remote", "origin", "main"])
    tip_sha = tip.strip().split("\t")[0] if tip.strip() else ""
    if tip_sha != newc.strip():
        return None, "tip verify fail"
    if os.path.exists(idx):
        os.remove(idx)
    return {"commit": newc.strip(), "base": base.strip()[:12],
            "tip_verified": tip_sha[:12]}, None


def main():
    msg_text = ("机队静默根治令 bm-c 回执（O-20261008-1240-bm-c·P-2026-10-08-11 回执行："
                "闸读回 0+违规 0+HQ-SilenceGuard 注册+Quark 拒绝访问如实披露）[via bm-c r755]\n")
    now_hm = datetime.datetime.now().astimezone().strftime("%H:%M")
    for attempt in (1, 2):
        rc, _, err = git(["fetch", "origin"])
        if rc != 0:
            print("FETCH-WARN %s" % err[:120])
        ledger_text, receipt = build_ledger_text(now_hm)
        result, why = cas_push(ledger_text, msg_text)
        if result:
            out = {"receipt_line": receipt, "cas": result,
                   "ts": datetime.datetime.now().astimezone().isoformat(
                       timespec="seconds")}
            with open(os.path.join(REPO, "results",
                                   "_r755bmc_silence_receipt.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(out, fh, indent=1, ensure_ascii=False)
            print("CAS OK attempt=%d commit=%s base=%s receipt=%dB"
                  % (attempt, result["commit"][:12], result["base"],
                     len(receipt.encode("utf-8"))))
            return 0
        print("CAS attempt %d failed: %s" % (attempt, why))
    return 2


if __name__ == "__main__":
    sys.exit(main())
