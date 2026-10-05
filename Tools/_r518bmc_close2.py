# -*- coding: utf-8 -*-
"""r518 bm-c close2: S7-close ledger row + receipt commit + final push_verify.
Defensive ladder: on push rejection -> churn-absorb (results/* own-lane faces)
-> pull --rebase -> push_verify once. Pattern credit: Tools/_r517bmc_close2.py."""
import datetime
import io
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


def push_verify():
    p = subprocess.run([sys.executable, "Tools/push_verify.py"],
                        capture_output=True, creationflags=CREATE, cwd=ROOT)
    print("PUSH_VERIFY rc=%d" % p.returncode)
    print((p.stdout or b"").decode("utf-8", "replace").strip()[-400:])
    return p.returncode


def main():
    rr = os.path.join(ROOT, "round_reports-bm-c.md")
    raw = open(rr, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    row = (f"{TS} | r518 bm-c S7-close | dept:工程 | 本地未达 origin commit 数=0（DELIVERED："
           f"round commit e7a48b33d 42 面〔簿记三写+S6 再生面族+qa 三件+轮工具族〕→"
           f"push#1 被拒（origin 轮中再进 3）→协议阶梯 machine/bm-c-r518 分支兜底推"
           f"〔pre-rebase 面·已被 main 正典 supersede〕→正典收口=churn-absorb a31651aca"
           f"（r620 律·5 daemon 面）→pull --rebase 4-UU 单窗正典解〔r506 v2/r517 血统·"
           f"r518 面组扩展：compute_audit history-union 212+201→213 零丢失·token_usage "
           f"per-key union·attrition/regime_state regen take-newer ours top-clock·"
           f"零 UNHANDLED·零 marker 残留·零 --no-verify·回执 _r518bmc_rebase_resolve.json〕"
           f"→rebase --continue 单过（round commit 重放 a06be27a1）→push_verify DELIVERED "
           f"tip 7e1bc479ec==remote·ahead=0/behind=0·零强推） | 零清扫/归档/删除/恢复类动作轮："
           f"登记册零命中断言 N/A-无此类动作（O-2030 §二.3 自证面） | 记分:2"
           f"（qa/ 证据包 r518 刷新=能跑/能看实物〔smoke-r518.md 5/5+equity png+driver 复跑〕"
           f"+S6 38 面 CEO 再生） | 记账预算:3 面内（state+心跳+轮报=法定簿记） | 方法论捕获="
           f"无新方法（全链复用正典范式·resolver 面组扩展=血统复制非新法）·宝藏捕获=无"
           f"（无五类收口面：判决 finalize 未落·名单进出零）{eol.decode()}")
    with open(rr, "ab") as fh:
        fh.write(row.encode("utf-8"))
    print("S7-CLOSE-ROW appended", TS)

    for f in ("round_reports-bm-c.md", "results/_r518bmc_rebase_resolve.json",
              "Tools/_r518bmc_rebase_resolve.py"):
        rc, out, err = git("add", "--", f)
        if rc != 0:
            print("ADD-FAIL", f, err[:120])
            return 1
    rc, out, err = git("commit", "-m",
                       "round r518 supplement: push-race close record "
                       "(4-UU single-window canon resolved, DELIVERED "
                       "7e1bc479ec) + resolver receipt")
    print("COMMIT rc=%d %s" % (rc, (out or err).strip()[:160]))
    if rc != 0:
        return 1
    rc = push_verify()
    if rc == 0:
        return 0
    # defensive ladder: absorb own-lane churn -> rebase -> retry once
    print("REJECTED -> absorb+rebase retry")
    rc, st, _ = git("status", "--porcelain")
    faces = [l[3:].strip().strip('"') for l in st.splitlines()
             if l.strip() and l[3:].strip().startswith("results/")]
    if faces:
        for f in faces:
            git("add", "--", f)
        rc, out, err = git("commit", "-m",
                           "churn-absorb r518 close2: own-lane daemon faces "
                           "(r620 law)")
        print("ABSORB-COMMIT rc=%d" % rc)
    rc, out, err = git("pull", "--rebase", "origin", "main")
    print("PULL-REBASE rc=%d %s" % (rc, (out or err).strip()[:160]))
    if rc != 0:
        rc2, uu, _ = git("ls-files", "-u")
        if uu.strip():
            print("UU=%d remains -> stop, manual window next round"
                  % len(uu.splitlines()))
            git("rebase", "--abort")
            return 2
        git("rebase", "--abort")
        return 2
    rc = push_verify()
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
