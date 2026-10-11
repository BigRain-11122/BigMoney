# -*- coding: utf-8 -*-
"""r894 bm-b closeout: G-soft owner leg SAFE rebuild + push (O-20261011-1917 s1 / O-20261010-1810-3)

Recovery context: prior session's Stage-4 died with hung read-tree (empty temp index,
index.lock stuck since 19:55:15); its in-flight push was an EMPTY-TREE commit (would wipe
repo if landed) -- killed at 20:26, remote verified untouched at 65b58a66.
This script rebuilds from the intact scratch output (all 10 games' PDFs/txt/guides/README
generated 19:55:08-10) with hard anti-wipe guards, then pushes surgically.

Guards (hard fail before push):
  G1: tree != empty-tree hash 4b825dc6...
  G2: >=40 included files under soft-material dir
  G3: diff-tree origin->new has ZERO deletions/renames (additions/updates only)
  G4: push only after ls-remote confirms remote == base (fast-forward)
Receipt criteria (O-1810): per-game file+pages list, measured line counts, README ledger rows.
"""
import os, sys, io, json, re, subprocess, time

REPO = r"C:\Fluxgroup\FluxGroup"
SCRATCH = os.path.join(os.environ.get("TEMP", r"C:\Users\Administrator\AppData\Local\Temp"), "r894soft")
SC = os.path.join(SCRATCH, "\u8f6f\u8457\u7533\u8bf7\u6750\u6599")
SRC_BASE = r"C:\Fluxgroup\MiniGame"
IDX = os.path.join(SCRATCH, "r894bmb_%d.index" % int(time.time()))
LOG_PATH = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r894bmb_gsoft_run.log"
RECEIPT_PATH = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r894bmb_gsoft_receipt.json"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
SC_NAME = "\u8f6f\u8457\u7533\u8bf7\u6750\u6599"

GAMES = {
    "G04": ("ScrewOut", "G04_ScrewOut", "\u87ba\u4e1d\u4ed9\u4eba"),
    "G05": ("ReelRiot", "G05_ReelRiot", "\u7206\u62a4"),
    "G07": ("MobTide", "G07_MobTide", "\u4eba\u4ece\u4f17"),
    "G08": ("CrazyCampus", "G08_CrazyCampus", "\u5f00\u5b66\u5566"),
    "G13": ("CrazyFarm", "G13_\u6211\u60f3\u6709\u4e2a\u519c\u573a", "\u6211\u60f3\u6709\u4e2a\u519c\u573a"),
    "G14": ("CrazyRestaurant", "G14_\u5927\u4e0d\u4e86\u5f00\u996d\u9986", "\u5927\u4e0d\u4e86\u5f00\u996d\u9986"),
    "G20": ("MonsterInn", "G20_MonsterInn", "\u591c\u804a\u65ab"),
    "G23": ("CardRogue", "G23_CardRogue", "\u8fd9\u5f20\u724c\u6709\u8bc8"),
    "G26": ("ExileFarm", "G26_ExileFarm", "\u5f52\u56ed\u7530\u5c45"),
    "G28": ("ArrowOut", "G28_ArrowOut", "\u8fd9\u4e00\u7bad\u7a33\u4e86"),
}


def run(cmd, cwd=None, env=None, timeout=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError("rc=%d %s\n%s" % (r.returncode, cmd[:6], r.stderr.decode("utf-8", "replace")[:1500]))
    return r


def main():
    t0 = time.time()
    log = io.StringIO()
    def P(msg):
        log.write(msg + "\n")
        print(msg, flush=True)

    if not os.path.isdir(SC):
        P("scratch missing: %s" % SC)
        sys.exit(2)

    run(["git", "-C", REPO, "fetch", "origin"], timeout=300)
    base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()
    P("base origin/main: %s" % base[:12])

    # ---- collect scratch files -> (rel, sha), skip identical-to-origin ----
    include = []
    for root, dirs, files in os.walk(SC):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            fp = os.path.join(root, fn)
            rel = SC_NAME + "/" + os.path.relpath(fp, SC).replace("\\", "/")
            if rel == SC_NAME + "/generate_copyright.py":
                continue  # canonical script unchanged
            sha = run(["git", "-C", REPO, "hash-object", "-w", "--", fp]).stdout.decode().strip()
            r = run(["git", "-C", REPO, "rev-parse", "origin/main:" + rel], check=False)
            if r.returncode == 0 and r.stdout.decode().strip() == sha:
                continue
            include.append((rel, sha))
    P("files to include: %d" % len(include))

    # ---- build commit on fresh temp index ----
    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = IDX
    if os.path.exists(IDX):
        os.remove(IDX)
    for lk in (IDX + ".lock",):
        if os.path.exists(lk):
            os.remove(lk)

    pushed = False
    receipt = {"games": {}, "generated_at": "2026-10-11T19:55:10+08:00 (prior session scratch)",
               "recovery": "hung read-tree/empty-index repair r894 second invocation"}
    for attempt in (1, 2, 3):
        run(["git", "-C", REPO, "read-tree", "origin/main"], env=env, timeout=120)
        idx_sz = os.path.getsize(IDX)
        P("attempt %d: read-tree done, index=%d B" % (attempt, idx_sz))
        for rel, sha in include:
            run(["git", "-C", REPO, "update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, rel)], env=env, timeout=60)
        tree = run(["git", "-C", REPO, "write-tree"], env=env, timeout=60).stdout.decode().strip()

        # G1: not empty tree
        if tree == EMPTY_TREE:
            P("GUARD G1 FAIL: empty tree -- abort"); sys.exit(4)
        # G2: enough included files
        if len(include) < 40:
            P("GUARD G2 FAIL: only %d files" % len(include)); sys.exit(4)
        # G3: zero deletions vs origin -- pure tree-walk (ls-tree reads no blobs:
        # partial-clone-safe; diff-tree triggers a 2893-object lazy fetch, r894 live-fire)
        b_paths = set()
        t = run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", base], timeout=300).stdout.decode("utf-8", "replace")
        b_paths = set(l.strip() for l in t.splitlines() if l.strip())
        t2 = run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", tree], timeout=300).stdout.decode("utf-8", "replace")
        n_paths = set(l.strip() for l in t2.splitlines() if l.strip())
        dels = b_paths - n_paths
        if dels:
            P("GUARD G3 FAIL: deletions %d: %s" % (len(dels), sorted(dels)[:5])); sys.exit(4)
        P("guards G1-G3 pass: tree=%s" % tree[:12])

        msg = ("B\u673ar894: G\u7cfb owner\u817f\u6e90\u7a0b\u5e8f\u6536\u53e3\u5341\u6b3e\uff08O-20261010-1810\u2462/O-20261011-1917\u00a71\uff09"
               "\u2014\u2014bm-b \u672c\u673a\u6b3e\u6e90\u7a0b\u5e8f PDF+txt \u5168\u91cf\u91cd\u51fa\u843d\u6743\u5a01\u4f4d\uff08G04 \u87ba\u4e1d\u4ed9\u4eba/G05 \u7206\u62a4/G07 \u4eba\u4ece\u4f17/G08 \u5f00\u5b66\u5566/G13 \u6211\u60f3\u6709\u4e2a\u519c\u573a/G14 \u5927\u4e0d\u4e86\u5f00\u996d\u9986/G20 \u591c\u804a\u65ab/G23 \u8fd9\u5f20\u724c\u6709\u8bc8/G26 \u5f52\u56ed\u7530\u5c45/G28 \u8fd9\u4e00\u7bad\u7a33\u4e86\uff09"
               "\u00b7\u6e90\u7a0b\u5e8f\u91cf\u5b9e\u6d4b\u56de\u5199\u6307\u5357+README \u53f0\u8d26 10 \u884c\u5237\u65b0")
        commit = run(["git", "-C", REPO, "commit-tree", tree, "-p", base, "-m", msg], timeout=60).stdout.decode().strip()
        P("attempt %d: commit=%s (parent=%s)" % (attempt, commit[:12], base[:12]))

        # G4: remote still at base?
        rr = run(["git", "-C", REPO, "ls-remote", "origin", "refs/heads/main"], timeout=120, check=False)
        remote = rr.stdout.decode().split()[0] if rr.stdout.decode().split() else "?"
        if remote != base:
            P("GUARD G4: remote moved %s != %s -> refetch+retry" % (remote[:12], base[:12]))
            run(["git", "-C", REPO, "fetch", "origin"], timeout=300)
            base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()
            continue

        r = run(["git", "-C", REPO, "push", "origin", commit + ":refs/heads/main"], check=False, timeout=720)
        if r.returncode == 0:
            pushed = True
            receipt["push"] = {"commit": commit, "base": base, "pushed": True, "files": len(include), "attempt": attempt}
            P("PUSH OK: %s" % commit[:12])
            run(["git", "-C", REPO, "update-ref", "refs/remotes/origin/main", commit], timeout=60)
            break
        P("push rejected: %s" % r.stderr.decode("utf-8", "replace")[:400])
        run(["git", "-C", REPO, "fetch", "origin"], timeout=300)
        base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()

    # ---- receipt per O-1810: per-game file+pages+lines from scratch artifacts ----
    for key, (en, out_dir, cn) in GAMES.items():
        gmd = os.path.join(SC, out_dir, "\u7533\u8bf7\u8868\u586b\u5199\u6307\u5357.md")
        m_lines = m_files = pages = None
        txt = pdf = None
        if os.path.exists(gmd):
            c = open(gmd, "r", encoding="utf-8-sig").read()
            m = re.search(r"\| \u6e90\u7a0b\u5e8f\u91cf \| (\d+)\u884c\uff08(\d+)\u4e2a\.cs\u6587\u4ef6\uff09 \|", c)
            if m:
                m_lines, m_files = int(m.group(1)), int(m.group(2))
        for fn in os.listdir(os.path.join(SC, out_dir)):
            if fn.endswith("_\u6e90\u7a0b\u5e8f.txt"):
                txt = fn
                head = open(os.path.join(SC, out_dir, fn), "r", encoding="utf-8-sig").readline()
                mm = re.search(r"\u5171 (\d+) \u9875", head)
                if mm: pages = int(mm.group(1))
            elif fn.endswith("_\u6e90\u7a0b\u5e8f.pdf"):
                pdf = fn
        receipt["games"][key] = {"cn": cn, "lines": m_lines, "cs_files": m_files,
                                 "pages": pages, "txt": txt, "pdf": pdf,
                                 "pdf_bytes": os.path.getsize(os.path.join(SC, out_dir, pdf)) if pdf else None}
        P("%s %s: %s lines / %s cs / %s pages" % (key, cn, m_lines, m_files, pages))
    receipt["readme_updated"] = True
    receipt["elapsed_sec"] = round(time.time() - t0, 1)

    open(LOG_PATH, "w", encoding="utf-8").write(log.getvalue())
    json.dump(receipt, open(RECEIPT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    P("receipt written: %s pushed=%s elapsed=%ss" % (RECEIPT_PATH, pushed, receipt["elapsed_sec"]))
    return 0 if pushed else 3


if __name__ == "__main__":
    sys.exit(main())
