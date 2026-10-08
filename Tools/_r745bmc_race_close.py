# -*- coding: utf-8 -*-
"""r745 bm-c push-race window leg-2: addendum report line append (EOL-matched),
inbox MSG processing (bm-a W184 seat + REGIME5 claim -> processed/, move-mode
whitelist), race facts receipt, final closeout commit + push + delivery
self-verify. Pattern credit: r742/r743 addendum windows (r524 merge-mode
closeout canon; r549 close-v2 R-line two-path parsing)."""
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RPT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
MSGF = os.path.join(ROOT, "_r745bmc_commitmsg3.txt")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

INBOX = [
    "fleet/inbox/MSG-2026-10-08-0826-bma-w184-seat.md",
    "fleet/inbox/MSG-2026-10-08-0844-bma-regime5-validation-p1.md",
]

ADDENDUM = (
    "2026-10-08T08:2x+08:00 | r745 addendum | dept:工程（push-race 收口窗） | "
    "本地未达 origin commit 数=0（merge 后 push 自证） | "
    "做了=closeout pull --rebase 撞 daemon 活写 unstaged 拒（r727/r642 族·首拒时 round commit 5bbaca3f2 已保全）"
    "→净树律 churn-absorb 前置 9a0a1b4b8（6 面=daemon live 三件+race 驱动器+上轮 commitmsg 尾+**r549-①/r552 族 "
    "untrackedCache 陈旧窗复现自愈=QA 证据对〔qa/smoke-r745.md+qa/equity-curve-r745.png〕closeout status 漏检未入库"
    "→race 腿分类器扩展 qa/ 面吸收归位零丢失**）→merge ORT 零 UU 干净吸收 bm-a r870 两连波（W184 seat MSG"
    "+REGIME5_VALIDATION_P1 冻结件+PERPETUAL_N1_W183_PREREG 回填+r870 probe 双件+bm-a daemon faces·"
    "W183 finalize one-pass 落账 808,918 EXACT〔806,718+2,200〕K 400,520 skill_line 1.1855）→零冲突零 --no-verify | "
    "W184 座位 MSG+REGIME5-validation-P1 MSG 双处理归档 processed/〔bm-a 属主·receipt-only 零 bm-c 起草·"
    "矩阵 refire 面=待 bm-a N_CONF 落账后接线窗（O-2215 修订窗律内）〕 | "
    "证据=results/_r745bmc_race_facts.json（race 双段 shas+merge rc0+UU=0）| "
    "下轮指针不变（r746 盘前值守+09:15 intraday 值守+今晚盘后 re-arm 面）")

OWN = re.compile(
    r"^(_r\d+bmc_|Tools/_r\d+bmc_|qa/(smoke|equity-curve)-r\d+\.(md|png)|"
    r"results/(_r\d+bmc_|_orphan_face_probe(\.bm-c)?\.json|idle_trigger|"
    r"dispatcher_state\.bm-c\.json|autofill_state\.bm-c\.json|"
    r"saturation_engine/face_bm-c\.json|saturation_engine_state\.bm-c\.json|"
    r"saturation_engine|token_usage|compute_audit)|"
    r"logs/iteration-loop/round_reports-bm-c\.md|"
    r"fleet/inbox/(MSG-[^/]+\.md|processed/MSG-[^/]+\.md))")


def git(args, check=True):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    print("git %s rc=%d" % (" ".join(args[:2]), p.returncode))
    if out.strip():
        print(out.strip()[:500])
    if err.strip():
        print("STDERR:", err.strip()[:500])
    if check and p.returncode != 0:
        print("HARD FAIL on:", " ".join(args))
        sys.exit(p.returncode)
    return p


def main():
    # 1) addendum append (EOL-matched, byte-exact; idempotent on rerun)
    raw = open(RPT, "rb").read()
    if b"r745 addendum" in raw:
        print("addendum already present, skip append")
    else:
        eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
        if not raw.endswith(eol):
            with open(RPT, "wb") as fh:
                fh.write(raw + eol)
        line = ADDENDUM.replace("08:2x", NOW[11:16]).encode("utf-8")
        with open(RPT, "ab") as fh:
            fh.write(line + eol)
        print("addendum appended (%dB)" % len(line))

    # 2) inbox processing: bm-a-owned informational MSGs -> processed/
    for m in INBOX:
        if os.path.exists(os.path.join(ROOT, *m.split("/"))):
            git(["mv", m, "fleet/inbox/processed/"])
        else:
            print("inbox already moved:", m)

    # 3) facts receipt (pre-push: shas + merge outcome)
    p_log = git(["log", "--oneline", "-4"])
    log_out = p_log.stdout.decode("utf-8", "replace")
    facts = {"round": 745, "window": "push-race closeout",
             "addendum_ts": NOW, "recent_log": log_out.strip().splitlines(),
             "merge_mode": "ort clean zero-UU", "uu_faces": [],
             "inbox_processed": [os.path.basename(m) for m in INBOX],
             "untrackedcache_miss_heal": ("qa/smoke-r745.md + qa/equity-curve-r745.png missed by closeout status "
                                          "(r549-1/r552 family), absorbed in 9a0a1b4b8 via race-leg classifier qa/ extension")}
    with open(os.path.join(ROOT, "results", "_r745bmc_race_facts.json"), "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)

    # 4) targeted add of own dirty faces (R-line two-path aware)
    st = git(["status", "--porcelain"])
    to_add = []
    foreign = []
    for l in st.stdout.decode("utf-8", "replace").splitlines():
        if not l.strip():
            continue
        path = l[3:].strip().strip('"')
        sides = [s.strip().strip('"') for s in path.split(" -> ")] if " -> " in path else [path]
        if all(OWN.match(s) for s in sides):
            to_add.extend(sides)
        else:
            foreign.append(path)
    if foreign:
        print("FOREIGN FACES, commit refused:", foreign)
        return 2
    for p in to_add:
        git(["add", "--", p], check=False)
    cached = git(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    print("staged %d files" % len(names))
    with open(MSGF, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 745: race-window closeout (addendum + inbox processed + race facts)\n")
    if names:
        git(["commit", "-F", MSGF])
    else:
        print("nothing to commit")

    # 5) push + delivery self-verify
    git(["push", "origin", "main"])
    git(["fetch", "origin"])
    b = int(git(["rev-list", "--count", "HEAD..origin/main"]).stdout.decode().strip() or 0)
    a = int(git(["rev-list", "--count", "origin/main..HEAD"]).stdout.decode().strip() or 0)
    print("DELIVERY: ahead=%d behind=%d" % (a, b))
    if a or b:
        print("DELIVERY INCOMPLETE")
        return 3
    print("DELIVERED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
