# -*- coding: utf-8 -*-
"""r894 bm-b: G 系 owner 腿源程序收口（O-20261011-1917-bm-c §1 / 集团 O-20261010-1810 ③）

本机(bm-b)十款软著源程序材料全量重出，落集团权威位 FluxGroup:软著申请材料/。
方法（partial clone blob:none 环境正法）：
  - 零树触碰：不 checkout、不 worktree；只 cat-file 所需小文本 blob（指南 md×10+README+生成器）
  - 暂存区跑 canonical generate_copyright.py（src_abs 指本机 Unity 源 C:\\Fluxgroup\\MiniGame\\<En>\\Assets\\_Game）
  - plumbing 提交：temp index(read-tree origin/main) + hash-object -w + update-index --cacheinfo
    + write-tree + commit-tree + push origin <sha>:refs/heads/main（外科推送·快进）
判据（O-20261010-1810 回执口径）：逐款文件名+页数清单；源程序量实测回写指南；README 台账行刷新。
"""
import os, sys, io, json, re, subprocess, shutil, time

REPO = r"C:\Fluxgroup\FluxGroup"
SCRATCH = os.path.join(os.environ.get("TEMP", r"C:\Users\Administrator\AppData\Local\Temp"), "r894soft")
SC = os.path.join(SCRATCH, "\u8f6f\u8457\u7533\u8bf7\u6750\u6599")  # 软著申请材料
SRC_BASE = r"C:\Fluxgroup\MiniGame"
IDX = os.path.join(SCRATCH, "r894.index")
LOG_PATH = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r894bmb_gsoft_run.log"
RECEIPT_PATH = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r894bmb_gsoft_receipt.json"

# key -> (english project dir at SRC_BASE, out_dir on origin)
GAMES = {
    "G04": ("ScrewOut", "G04_ScrewOut"),
    "G05": ("ReelRiot", "G05_ReelRiot"),
    "G07": ("MobTide", "G07_MobTide"),
    "G08": ("CrazyCampus", "G08_CrazyCampus"),
    "G13": ("CrazyFarm", "G13_\u6211\u60f3\u6709\u4e2a\u519c\u573a"),          # 我想有个农场
    "G14": ("CrazyRestaurant", "G14_\u5927\u4e0d\u4e86\u5f00\u996d\u9986"),    # 大不了开饭馆
    "G20": ("MonsterInn", "G20_MonsterInn"),
    "G23": ("CardRogue", "G23_CardRogue"),
    "G26": ("ExileFarm", "G26_ExileFarm"),
    "G28": ("ArrowOut", "G28_ArrowOut"),
}
SC_NAME = "\u8f6f\u8457\u7533\u8bf7\u6750\u6599"  # 软著申请材料
CN_SHORT = {  # 权威简称（README 台账行展示用）
    "G04": "\u87ba\u4e1d\u4ed9\u4eba", "G05": "\u7206\u62a4", "G07": "\u4eba\u4ece\u4f17",
    "G08": "\u5f00\u5b66\u5566", "G13": "\u6211\u60f3\u6709\u4e2a\u519c\u573a",
    "G14": "\u5927\u4e0d\u4e86\u5f00\u996d\u9986", "G20": "\u591c\u804a\u658b",
    "G23": "\u8fd9\u5f20\u724c\u6709\u8bc8", "G26": "\u5f52\u56ed\u7530\u5c45", "G28": "\u8fd9\u4e00\u7bad\u7a33\u4e86",
}


def run(cmd, cwd=None, env=None, timeout=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError("cmd failed rc=%d: %s\n%s" % (r.returncode, cmd[:6], r.stderr.decode("utf-8", "replace")[:2000]))
    return r


def blob(path, out_path=None):
    """Read origin/main blob bytes (small lazy fetch acceptable)."""
    r = run(["git", "-C", REPO, "show", "origin/main:" + path], check=False)
    if r.returncode != 0:
        return None
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        open(out_path, "wb").write(r.stdout)
    return r.stdout


def main():
    t0 = time.time()
    log = io.StringIO()
    def P(msg):
        log.write(msg + "\n")
        print(msg, flush=True)

    # ---------- Stage 1: materialize small text blobs ----------
    if os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(SC, exist_ok=True)

    b = blob(SC_NAME + "/generate_copyright.py", os.path.join(SC, "generate_copyright.py"))
    P("gen script bytes: %s" % (len(b) if b else "MISSING"))
    if not b:
        sys.exit(2)
    readme_bytes = blob(SC_NAME + "/README.md", os.path.join(SC, "README.md"))
    P("README bytes: %s" % (len(readme_bytes) if readme_bytes else "MISSING"))

    guides = {}
    for key, (en, out_dir) in GAMES.items():
        gpath = "%s/%s/\u7533\u8bf7\u8868\u586b\u5199\u6307\u5357.md" % (SC_NAME, out_dir)  # 申请表填写指南.md
        g = blob(gpath, os.path.join(SC, out_dir, "\u7533\u8bf7\u8868\u586b\u5199\u6307\u5357.md"))
        guides[key] = bool(g)
        P("guide %s: %s bytes" % (key, len(g) if g else "MISSING"))

    # ---------- Stage 2: run canonical generator with src_abs overrides ----------
    sys.path.insert(0, SC)
    import generate_copyright as gc
    P("generator imported, BASE=%s" % gc.BASE)

    cap = io.StringIO()
    receipt = {"games": {}, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
    for key, (en, out_dir) in GAMES.items():
        src_abs = os.path.join(SRC_BASE, en, "Assets", "_Game")
        entry = {"key": key, "out_dir": out_dir, "src_abs": src_abs, "src_ok": os.path.isdir(src_abs)}
        receipt["games"][key] = entry
        if not entry["src_ok"]:
            P("!! %s src missing: %s" % (key, src_abs))
            continue
        gc.PROJECTS[key]["src_abs"] = src_abs
        with_data = io.StringIO()
        old = sys.stdout
        sys.stdout = with_data
        try:
            gc.process_project(key)
        finally:
            sys.stdout = old
        cap.write(with_data.getvalue())
        # parse measurement from updated guide md
        gmd = os.path.join(SC, out_dir, "\u7533\u8bf7\u8868\u586b\u5199\u6307\u5357.md")
        m_lines = m_files = None
        if os.path.exists(gmd):
            c = open(gmd, "r", encoding="utf-8-sig").read()
            m = re.search(r"\| \u6e90\u7a0b\u5e8f\u91cf \| (\d+)\u884c\uff08(\d+)\u4e2a\.cs\u6587\u4ef6\uff09 \|", c)  # | 源程序量 | N行（M个.cs文件） |
            if m:
                m_lines, m_files = int(m.group(1)), int(m.group(2))
        name_en = gc.PROJECTS[key]["name_en"]
        ver = gc.PROJECTS[key]["version"]
        txt_name = "%s_%s_\u6e90\u7a0b\u5e8f.txt" % (name_en, ver)   # 源程序.txt
        pdf_name = "%s_%s_\u6e90\u7a0b\u5e8f.pdf" % (name_en, ver)   # 源程序.pdf
        txt_path = os.path.join(SC, out_dir, txt_name)
        pdf_path = os.path.join(SC, out_dir, pdf_name)
        pages = None
        if os.path.exists(txt_path):
            head = open(txt_path, "r", encoding="utf-8-sig").readline()
            m = re.search(r"\u5171 (\d+) \u9875", head)  # 共 N 页
            if m:
                pages = int(m.group(1))
        entry.update({
            "lines": m_lines, "cs_files": m_files, "pages": pages,
            "txt": txt_name, "pdf": pdf_name,
            "pdf_bytes": os.path.getsize(pdf_path) if os.path.exists(pdf_path) else None,
            "txt_bytes": os.path.getsize(txt_path) if os.path.exists(txt_path) else None,
            "guide_updated": guides[key] and m_lines is not None,
        })
        P("%s(%s): %s cs files, %s lines, %s pages -> %s (%s B)" % (
            key, CN_SHORT[key], m_files, m_lines, pages, pdf_name, entry["pdf_bytes"]))

    open(LOG_PATH, "w", encoding="utf-8").write(log.getvalue() + "\n===== generator output =====\n" + cap.getvalue())

    # ---------- Stage 3: README surgical update ----------
    readme_changed = False
    if readme_bytes:
        rd = open(os.path.join(SC, "README.md"), "r", encoding="utf-8-sig").read()
        agg_row = "| G02/G04/G05/G07/G08/G09 \u533b\u9662/G10/G12/G13/G14/G20/G26 | \u2014 | \u5f85 owner \u673a\u590d\u8dd1\u5b9e\u6d4b\u56de\u5199 | \u2014 | \u8bf4\u660e\u4e66+\u6307\u5357\u5df2\u6309\u7ec8\u540d\u6e32\u67d3 |"
        if agg_row in rd:
            new_rows = []
            for key, (en, out_dir) in GAMES.items():
                e = receipt["games"][key]
                if e.get("pages") is None:
                    continue
                new_rows.append("| G%s %s | %s | %s | %s | 10-11 bm-b r894 \u5237\u65b0 |" % (
                    key[1:], CN_SHORT[key], e["cs_files"], e["lines"], e["pages"]))
            residual = "| G02/G09 \u533b\u9662/G10/G12/G03/G06/G17/G18 | \u2014 | \u5f85 owner \u673a\u590d\u8dd1\u5b9e\u6d4b\u56de\u5199 | \u2014 | C\u673a\u6b3e\u57df\uff08bm-c \u91cd\u51fa\u5728\u98de\uff09 |"
            rd = rd.replace(agg_row, "\n".join(new_rows) + "\n" + residual)
            readme_changed = True
            P("README ledger rows updated: %d new rows" % len(new_rows))
        # §三 staleness repair for B机 games (two lines)
        l1_old = "\u2014\u2014\u8bf4\u660e\u4e66+\u6307\u5357\u6309\u7ec8\u540d\u6e32\u67d3\uff1b\u6e90\u7a0b\u5e8f+CCPC PDF \u7531 owner \u673a\u590d\u8dd1\u5f52\u62e2\u3002"
        l1_new = "\u2014\u2014\u8bf4\u660e\u4e66+\u6307\u5357\u6309\u7ec8\u540d\u6e32\u67d3\uff1b\u6e90\u7a0b\u5e8f B\u673a\u516d\u6b3e\u5df2\u590d\u8dd1\uff0810-11 bm-b r894\uff09\u00b7C\u673a\u4e24\u6b3e\u5f85 owner \u673a\uff1bCCPC PDF \u5f52\u62e2\u5f85\u7eed\u3002"
        if l1_old in rd:
            rd = rd.replace(l1_old, l1_new); readme_changed = True
        l2_old = "\u2014\u2014\u8bf4\u660e\u4e66+\u6307\u5357\u6309\u5b9a\u540d\u6e32\u67d3\uff082026-10-10\uff09\uff1b\u6e90\u7a0b\u5e8f\u5f85 owner \u673a\u590d\u8dd1\uff08\u516d\u6b3e\u6e90\u7801\u5728 B/C \u673a\uff09\u3002"
        l2_new = "\u2014\u2014\u8bf4\u660e\u4e66+\u6307\u5357\u6309\u5b9a\u540d\u6e32\u67d3\uff082026-10-10\uff09\uff1b\u6e90\u7a0b\u5e8f B\u673a\u4e24\u6b3e\uff08G20/G26\uff09\u5df2\u590d\u8dd1\uff0810-11 bm-b r894\uff09\u00b7C\u673a\u516b\u6b3e\u5f85 owner \u673a\u3002"
        if l2_old in rd:
            rd = rd.replace(l2_old, l2_new); readme_changed = True
        open(os.path.join(SC, "README.md"), "w", encoding="utf-8").write(rd)
        P("README updated: %s" % readme_changed)
    receipt["readme_updated"] = readme_changed

    # ---------- Stage 4: plumbing commit ----------
    # collect changed/new files
    include = []
    for root, dirs, files in os.walk(SC):
        for fn in files:
            fp = os.path.join(root, fn)
            rel = SC_NAME + "/" + os.path.relpath(fp, SC).replace("\\", "/")
            if fn == "generate_copyright.py" and os.path.dirname(fp) == SC:
                continue  # unchanged canonical script (committed copy identical)
            sha = run(["git", "-C", REPO, "hash-object", "-w", "--", fp]).stdout.decode().strip()
            # compare with origin blob
            r = run(["git", "-C", REPO, "rev-parse", "origin/main:" + rel], check=False)
            if r.returncode == 0 and r.stdout.decode().strip() == sha:
                continue  # identical, skip
            include.append((rel, sha))
    P("files to commit: %d" % len(include))

    env = dict(os.environ); env["GIT_INDEX_FILE"] = IDX
    base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()

    msg = ("B\u673ar894: G\u7cfb owner\u817f\u6e90\u7a0b\u5e8f\u6536\u53e3\u5341\u6b3e\uff08O-20261010-1810\u2462/O-20261011-1917\u00a71\uff09"
           "\u2014\u2014bm-b \u672c\u673a\u6b3e\u6e90\u7a0b\u5e8f PDF+txt \u5168\u91cf\u91cd\u51fa\u843d\u6743\u5a01\u4f4d\uff08G04 \u87ba\u4e1d\u4ed9\u4eba/G05 \u7206\u62a4/G07 \u4eba\u4ece\u4f17/G08 \u5f00\u5b66\u5566/G13 \u6211\u60f3\u6709\u4e2a\u519c\u573a/G14 \u5927\u4e0d\u4e86\u5f00\u996d\u9986/G20 \u591c\u804a\u658b/G23 \u8fd9\u5f20\u724c\u6709\u8bc8/G26 \u5f52\u56ed\u7530\u5c45/G28 \u8fd9\u4e00\u7bad\u7a33\u4e86\uff09"
           "\u00b7\u6e90\u7a0b\u5e8f\u91cf\u5b9e\u6d4b\u56de\u5199\u6307\u5357+README \u53f0\u8d26 10 \u884c\u5237\u65b0")
    P("commit msg: %s" % msg)

    pushed = False
    for attempt in (1, 2, 3):
        run(["git", "-C", REPO, "read-tree", "origin/main"], env=env)
        for rel, sha in include:
            run(["git", "-C", REPO, "update-index", "--add", "--cacheinfo", "100644,%s,%s" % (sha, rel)], env=env)
        tree = run(["git", "-C", REPO, "write-tree"], env=env).stdout.decode().strip()
        commit = run(["git", "-C", REPO, "commit-tree", tree, "-p", base, "-m", msg]).stdout.decode().strip()
        P("attempt %d: tree=%s commit=%s (base=%s)" % (attempt, tree[:12], commit[:12], base[:12]))
        r = run(["git", "-C", REPO, "push", "origin", commit + ":refs/heads/main"], check=False, timeout=900)
        if r.returncode == 0:
            pushed = True
            receipt["push"] = {"commit": commit, "base": base, "pushed": True, "files": len(include)}
            P("PUSH OK: %s" % commit[:12])
            run(["git", "-C", REPO, "update-ref", "refs/remotes/origin/main", commit])
            break
        P("push rejected: %s" % r.stderr.decode("utf-8", "replace")[:500])
        run(["git", "-C", REPO, "fetch", "origin"], timeout=300)
        base = run(["git", "-C", REPO, "rev-parse", "origin/main"]).stdout.decode().strip()
    if not pushed:
        receipt["push"] = {"pushed": False}
        P("!! PUSH FAILED after 3 attempts")

    receipt["elapsed_sec"] = round(time.time() - t0, 1)
    json.dump(receipt, open(RECEIPT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------- Summary (O-1810 receipt: per-game file+pages list) ----------
    P("\n===== r894 bm-b G softcopyright receipt =====")
    for key in GAMES:
        e = receipt["games"][key]
        P("%s %s %s | %s pages | %s lines / %s cs files | %s B" % (
            key, CN_SHORT[key], e.get("pdf", "?"), e.get("pages"), e.get("lines"), e.get("cs_files"), e.get("pdf_bytes")))
    P("push: %s" % receipt.get("push", {}).get("pushed"))
    return 0 if pushed else 3


if __name__ == "__main__":
    sys.exit(main())
