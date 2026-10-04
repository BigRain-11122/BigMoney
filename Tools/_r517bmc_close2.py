# -*- coding: utf-8 -*-
"""r517 bm-c close2: S7-close ledger row + receipt commit + final push_verify."""
import datetime
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def git(*a):
    env = dict(os.environ)
    env["GIT_EDITOR"] = "true"
    p = subprocess.run(["git"] + list(a), capture_output=True, cwd=ROOT,
                       env=env, creationflags=CREATE, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stdout or "", p.stderr or ""


def main():
    rr = os.path.join(ROOT, "round_reports-bm-c.md")
    raw = open(rr, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    row = (f"{TS} | r517 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED："
           f"round commit 1960e27ec 57 面+churn-absorb×2〔cfd6daad8+e3d9607af·r620 律〕→"
           f"pull --rebase 31 UU 单窗正典解〔r506 v2 血统：twins×3 对+dashboard js/json twin-lock"
           f"+paper 6 新基+compute_audit history-union+token_usage per-key union+x2_watch in-block "
           f"union+regen 面 ts-newer·零 UNHANDLED·零 marker 残留·零 --no-verify〕→rebase --continue "
           f"单过→push_verify tip 28324f61d0da==remote·ahead=0/behind=0·零强推） | 零清扫/归档/删除/"
           f"恢复类动作轮：登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面） | 记分:2"
           f"（qa/ 证据包 r517 刷新=能跑/能看实物〔smoke-r517.md 5/5+equity png+driver 复跑〕"
           f"+S6 38 面 CEO 再生） | 记账预算:3 面内（state+心跳+轮报=法定簿记） | 方法论捕获="
           f"任务族命名面坑律入册 CODELY（r517 条）·宝藏捕获=无（无五类收口面：判决 finalize 未落·"
           f"名单进出零）{eol.decode()}")
    with open(rr, "ab") as fh:
        fh.write(row.encode("utf-8"))
    print("S7-CLOSE-ROW appended", TS)

    for f in ("round_reports-bm-c.md", "results/_r517bmc_rebase_resolve.json"):
        rc, out, err = git("add", "--", f)
        if rc != 0:
            print("ADD-FAIL", f, err[:120])
            return 1
    rc, out, err = git("commit", "-m",
                       "round r517 supplement: push-race close record "
                       "(31 UU single-window canon resolved, DELIVERED "
                       "28324f61d0da) + resolver receipt")
    print("COMMIT rc=%d %s" % (rc, (out or err).strip()[:160]))
    if rc != 0:
        return 1
    p = subprocess.run([sys.executable, "Tools/push_verify.py"],
                       capture_output=True, creationflags=CREATE, cwd=ROOT)
    print("PUSH_VERIFY rc=%d" % p.returncode)
    print((p.stdout or b"").decode("utf-8", "replace").strip()[-400:])
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
