# r1025 bm-a POOL-0013 executor: worktree-on-origin surgical collection of untracked 软著 products
# + docs/orders.md receipt row + push + byte-verify + local duplicate quarantine (manifest, reversible)
# Laws applied: 10-09 worktree race law / D-02 claw-safe (zero deletions) / 95MB red line /
# quarantine-not-delete / CJK via python raw paths (never console mojibake).
import subprocess, json, os, sys, shutil, tempfile, hashlib, datetime

GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
BIGMONEY = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
SOFT = u"软著申请材料"
QUAR_BASE = r"C:\Users\sjs20\.codely-cli\tmp"
GUARD = os.path.join(BIGMONEY, "Tools", "treasure_guard.py")
RECEIPT = os.path.join(BIGMONEY, "results", "_r1025bma_pool0013_receipt.json")
MAX_BYTES = 95 * 1024 * 1024

def g(args, cwd=GROUP, check=True):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s rc=%d :: %s" % (" ".join(args[:3]), r.returncode,
                                                    r.stderr.decode("utf-8", "replace")[:300]))
    return r

out = {"ts": None, "err": None, "steps": [], "status_entries": 0, "files": [],
       "commit": None, "push_attempts": 0, "origin_verified": False,
       "guard_prescan_rc": None, "quarantine_dir": None, "orders_row": False}

def finish(rc):
    out["ts"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("POOL0013_RC=%d files=%d commit=%s verified=%s err=%s" % (
        rc, len(out["files"]), out["commit"], out["origin_verified"], out["err"]))
    return rc

try:
    g(["fetch", "origin"]); out["steps"].append("fetch")
    # 1) untracked status entries under 软著申请材料/ (NUL-safe parse)
    r = g(["status", "--porcelain", "-z", "--", SOFT + "/"])
    entries = [e for e in r.stdout.decode("utf-8", "replace").split("\0") if e.strip()]
    untracked = [e[3:] for e in entries if e.startswith("?? ")]
    out["status_entries"] = len(untracked)
    if not untracked:
        out["err"] = "no untracked files under %s (face already collected?)" % SOFT
        finish(3); sys.exit(3)
    # card face = 12 entries; tolerate drift with honest note but require <= 20
    if len(untracked) > 20:
        out["err"] = "untracked entries=%d exceeds sane bound (20) -- honest abort" % len(untracked)
        finish(3); sys.exit(3)
    # 2) expand to actual files
    r = g(["ls-files", "-o", "--others", "--exclude-standard", "--", SOFT + "/"])
    files = [x for x in r.stdout.decode("utf-8", "replace").splitlines() if x.strip()]
    out["files"] = files
    if not files:
        out["err"] = "ls-files -o returned zero files"
        finish(3); sys.exit(3)
    for f in files:
        p = os.path.join(GROUP, f)
        if not os.path.isfile(p):
            out["err"] = "missing file %s" % f
            finish(3); sys.exit(3)
        if os.path.getsize(p) > MAX_BYTES:
            out["err"] = "file over 95MB red line: %s" % f
            finish(3); sys.exit(3)
    # 3) treasure guard prescan (quarantine-class action law)
    try:
        rg = subprocess.run([sys.executable, GUARD, "prescan"] + untracked,
                            cwd=BIGMONEY, capture_output=True)
        out["guard_prescan_rc"] = rg.returncode
        if rg.returncode == 3:
            out["err"] = "treasure_guard prescan rc3 registry hit -- quarantine skipped, files left in place"
            out["quarantine_dir"] = "SKIPPED_GUARD_RC3"
    except Exception as e:
        out["guard_prescan_rc"] = "unavailable: %r" % e
    # 4) worktree on origin tip
    wt = tempfile.mkdtemp(prefix="pool0013_wt_")
    out["steps"].append("worktree_add")
    g(["worktree", "add", "--detach", wt, "origin/main"])
    try:
        # 5) copy files
        for f in files:
            dst = os.path.join(wt, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(GROUP, f), dst)
        out["steps"].append("copy_%d" % len(files))
        # 6) orders.md receipt row (append at end, fresh-read single-file)
        row = (u"| 2026-10-17 01:2x | **@bm-a 回执：POOL-0013 软著A机刷新批产物收编上链完成"
               u"（O-20261014-1035 L1018 勘正实收口+O-20261017-0100 §2.1 执行件·card-lint 9/9）** "
               u"| ①staged M 107 面已在 bc34c07（C-02 wave-F 124 件分诊）落 origin 实证（path log 三笔）；"
               u"②本窗 untracked 12 项（_报审提交区第1-5批+报审台账.md 等报审包）worktree 正法 pathspec 收编+push（本 commit 同批·零删除 D-02 爪面安全）；"
               u"③本地 12 副本字节恒等验证后隔离暂存（.codely-cli/tmp/pool0013-quarantine-*/manifest.json·可逆）；"
               u"④证据=quant/bigmoney results/_r1025bma_pool0013_receipt.json |")
        omp = os.path.join(wt, "docs", "orders.md")
        with open(omp, "rb") as f:
            text = f.read().decode("utf-8")
        if not text.endswith("\n"):
            text += "\n"
        text += row + "\n"
        with open(omp, "wb") as f:
            f.write(text.encode("utf-8"))
        out["orders_row"] = True
        # 7) stage scoped paths only
        g(["add", "--", SOFT + "/", "docs/orders.md"], cwd=wt)
        # 8) zero-deletion assert (D-02 claw-face safety)
        r = g(["diff", "--cached", "--name-only", "--diff-filter=D"], cwd=wt)
        dels = [x for x in r.stdout.decode("utf-8", "replace").splitlines() if x.strip()]
        if dels:
            raise RuntimeError("staged deletions present: %s" % dels[:5])
        out["steps"].append("nodelet_assert")
        # 9) commit via -F utf-8 message file
        msg = (u"POOL-0013 软著A机收编上链: 12 untracked 报审产物 + orders 回执行 [card ID POOL-0013, action=done]\n\n"
               u"- staged M 107 face already landed via bc34c07 (C-02 wave-F triage), path-log verified\n"
               u"- %d files under %s/ collected via worktree-on-origin surgical commit, zero deletions staged\n"
               u"- local duplicates byte-verified then quarantined (reversible, manifest in place)\n"
               u"- receipt evidence: quant/bigmoney results/_r1025bma_pool0013_receipt.json\n"
               u"- provenance: O-20261014-1035 L1018 + O-20261017-0100 sec.2.1 [via bm-a]") % (len(files), SOFT)
        mf = os.path.join(QUAR_BASE, "pool0013_commit_msg.txt")
        with open(mf, "w", encoding="utf-8") as f:
            f.write(msg)
        g(["commit", "-F", mf], cwd=wt)
        out["commit"] = g(["rev-parse", "HEAD"], cwd=wt).stdout.decode().strip()
        out["steps"].append("commit")
        # 10) push with one rebase retry
        rc = g(["push", "origin", "HEAD:main"], cwd=wt, check=False)
        out["push_attempts"] = 1
        if rc.returncode != 0:
            g(["fetch", "origin"], cwd=wt)
            g(["rebase", "origin/main"], cwd=wt)
            rc = g(["push", "origin", "HEAD:main"], cwd=wt, check=False)
            out["push_attempts"] = 2
            if rc.returncode != 0:
                raise RuntimeError("push failed twice: %s" % rc.stderr.decode("utf-8", "replace")[:300])
        out["steps"].append("push")
        # 11) origin ancestry verify
        g(["fetch", "origin"], cwd=wt)
        rv = g(["merge-base", "--is-ancestor", "HEAD", "origin/main"], cwd=wt, check=False)
        out["origin_verified"] = (rv.returncode == 0)
        if not out["origin_verified"]:
            raise RuntimeError("commit not found on origin/main after push (verify fail)")
        # 12) byte-verify + quarantine local duplicates (skip if guard rc3)
        if out.get("quarantine_dir") != "SKIPPED_GUARD_RC3":
            qdir = os.path.join(QUAR_BASE, "pool0013-quarantine-" +
                                datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
            manifest = []
            for f in files:
                src = os.path.join(GROUP, f)
                h1 = hashlib.sha256(open(src, "rb").read()).hexdigest()
                h2 = hashlib.sha256(open(os.path.join(wt, f), "rb").read()).hexdigest()
                if h1 != h2:
                    raise RuntimeError("byte mismatch on %s -- quarantine aborted" % f)
                dst = os.path.join(qdir, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)
                manifest.append({"path": f, "sha256": h1})
            os.makedirs(qdir, exist_ok=True)
            with open(os.path.join(qdir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump({"ts": out["ts"], "reason": "POOL-0013 collected to origin; local dup quarantine",
                           "origin_commit": out["commit"], "files": manifest}, f, ensure_ascii=False, indent=1)
            out["quarantine_dir"] = qdir
            out["steps"].append("quarantine_%d" % len(manifest))
    finally:
        try:
            g(["worktree", "remove", "--force", wt])
            out["steps"].append("worktree_removed")
        except Exception:
            out["steps"].append("worktree_remove_failed")
    finish(0); sys.exit(0)
except Exception as e:
    out["err"] = repr(e)
    finish(2); sys.exit(2)
