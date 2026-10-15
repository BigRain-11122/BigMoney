"""r1034 bm-c CAS direct-commit of O-20261015-1800/1834 spawn-gate receipt row
to group tree origin/main docs/orders.md (C-20261015-03 sec.4 receipt carrier).
Zero working-tree touch (group tree currently holds a stale staged-deletion
face from a dead window -- CAS path avoids it entirely): temp-index +
commit-tree + push <sha>:main (r739 recipe clone). Laws: r849 (UTF-8 msg
file, explicit origin param), r731 (no amend, ls-remote precheck), CAS hard
validation (40-hex blob/tree/commit + push keyword scan + duplicate-delivery
gate + tip verify). Race retry x2 (fresh fetch + recompose each attempt)."""
import datetime
import os
import re
import subprocess
import sys

GROUP = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TARGET = "docs/orders.md"
IDX = os.path.join(REPO, "results", "_r1034bmc_receipt.index")
MSG = os.path.join(REPO, "results", "_r1034bmc_receipt_msg.txt")
ROWTMP = os.path.join(REPO, "results", "_r1034bmc_receipt_row.md")
MARKER = "spawn 闸 preflight 落位+机级错峰核查 PASS（@bm-c"

MSG_TEXT = ("docs/orders: bm-c receipt O-20261015-1800/1834 spawn-gate "
            "preflight landed (bigmoney Tools/spawn_gate.ps1 + iteration_loop "
            "wiring, selftest 3/3) + machine stagger audit PASS (single codely "
            "igniter pin :X5) + heartbeat codely_live_count field; delivered "
            "by bm-c r1034 before 24:00 deadline law\n")


def g(args, env=None):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True, env=env)
    return p.returncode, p.stdout, p.stderr


def compose_row():
    now = datetime.datetime.now()
    hh = now.strftime("%H")
    mm10 = now.minute // 10
    return ("| 10-15 %s%d%s | **bm-c 回执：O-20261015-1800/1834 spawn 闸 preflight "
            "落位+机级错峰核查 PASS（@bm-c 24h 窗·C-20261015-03 §四/§七·24:00 死线前收口）** "
            "| ①spawn 闸=quant/bigmoney 仓 Tools/spawn_gate.ps1（§三 spec 正身：codely.exe 活体"
            "计数·cap=2·fail-open 探测炸=照常点火·DEFER=一行台账 results/cloud_cap_ledger.jsonl"
            "+下网格槽自 retry）+Tools/iteration_loop.ps1 点火前接线（rc=3=本轮让路跳过·与 "
            "round.lock 单实例律叠加）；selftest 3/3 实证（PROBE live=1/GO rc0/DEFER rc3+台账行"
            "落盘）；②机级错峰核查 PASS：bm-c 全机 codely 点火面单一=Bigmoney-IterationLoop PT10M "
            "pin :X5（三机错峰钉位 D-20260928-03① 在役）·MiniGameComfyDraftTick/KeepAlive 实查="
            "ComfyUI python 守护非 codely 会话（action 'codely' 匹配=.codely-cli 路径段假阳性）"
            "·零同分钟齐射面=零改动零备份需求；③观察哨=heartbeat codely_live_count 字段同窗写入 "
            "fleet/machines/bm-c.json（三机同字段律·本窗实测 live=1）；④本地路由硬执法="
            "LOCAL_FIRST（O-2325）+token_meter 既有法零新动作；⑤附带披露=本机 group 工作树存在"
            "陈旧 staged 删除面（Tools/card-lint.py/patrol-fleet-*/protected-hash-* 等约 7 件·"
            "疑死窗遗物·codely_live=1 证无活会话在飞）——本回执全程 CAS 零树触碰·该面登记待集团"
            "管家裁定（card-lint.py=POOL 转单卡律引用件·删除面请优先核） | executed（bm-c r1034） |\n"
            ) % (hh, mm10, "x" if now.minute % 10 < 10 else "")


def attempt():
    rc, _, _ = g(["fetch", "origin"])
    if rc != 0:
        print("ABORT: fetch", rc)
        return 3
    rc, base, err = g(["rev-parse", "origin/main"])
    base = base.decode().strip()
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", base):
        print("ABORT: bad base", rc, err[:200])
        return 3
    rc, blob_out, err = g(["show", "origin/main:" + TARGET])
    if rc != 0:
        print("ABORT: show", err[:200])
        return 3
    content = blob_out
    if MARKER.encode("utf-8") in content:
        print("ABORT: receipt row already on origin/main (duplicate delivery)")
        return 3
    row = compose_row().encode("utf-8")
    with open(ROWTMP, "wb") as fh:
        fh.write(content + row)
    p = subprocess.run(["git", "-C", GROUP, "hash-object", "-w", ROWTMP],
                       capture_output=True)
    blob = p.stdout.decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", blob):
        print("ABORT: bad blob", blob, p.stderr.decode()[:200])
        return 3
    env = dict(os.environ, GIT_INDEX_FILE=IDX)
    if os.path.exists(IDX):
        os.remove(IDX)
    rc, _, err = g(["read-tree", base], env=env)
    if rc != 0:
        print("ABORT: read-tree", err[:200])
        return 3
    rc, _, err = g(["update-index", "--add", "--cacheinfo",
                    "100644", blob, TARGET], env=env)
    if rc != 0:
        print("ABORT: update-index", err[:200])
        return 3
    rc, tree, err = g(["write-tree"], env=env)
    tree = tree.decode().strip()
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", tree):
        print("ABORT: bad tree", err[:200])
        return 3
    with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(MSG_TEXT)
    rc, newc, err = g(["commit-tree", tree, "-p", base, "-F", MSG])
    newc = newc.decode().strip()
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", newc):
        print("ABORT: bad commit", err[:200])
        return 3
    print("base", base[:12], "blob", blob[:12], "tree", tree[:12],
          "commit", newc[:12])
    rc, out, err = g(["push", "origin", newc + ":main"])
    combined = (out + b" " + err).decode("utf-8", "replace").lower()
    bad = any(k in combined for k in ("fatal", "rejected", "failed", "error"))
    if rc != 0 or bad:
        print("PUSH-FAIL rc", rc, combined[:300])
        return 2
    rc, tip, err = g(["ls-remote", "origin", "main"])
    tip_sha = (tip.decode().strip().split("\t")[0] if tip.strip() else "")
    if tip_sha != newc:
        print("VERIFY-FAIL: remote tip", tip_sha[:12], "!= commit", newc[:12])
        return 2
    print("TIP VERIFIED", tip_sha[:12])
    return 0


def main():
    for i in (1, 2, 3):
        rc = attempt()
        if rc == 0:
            for f in (IDX, MSG, ROWTMP):
                if os.path.exists(f):
                    os.remove(f)
            print("RECEIPT LANDED attempt", i)
            return 0
        if rc == 3:
            return rc
        print("retry after race, attempt", i)
    return 2


if __name__ == "__main__":
    sys.exit(main())
