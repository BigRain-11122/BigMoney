# r782 bm-b: D-19 orders.md delta extraction. Lineage: r631 sparse-clone recipe (r783bmb_d19_read
# bloodline) extended with depth-10 history walk to anchor the old watermark blob (631E5DF2...)
# and emit the added rows vs current origin (6F3AC292...). Zero tree-touch on any resident repo.
import subprocess, tempfile, shutil, os, sys, json, hashlib

URLS = ["git@github.com:BigRain-11122/FluxGroup.git",
        "https://github.com/BigRain-11122/FluxGroup.git"]
OLD_SHA = "631E5DF26951337D4B8E10A72D7292126D8FA2727089119BE1F2792AA53C0497"  # state last_orders_sha
CUR_SHA = "6F3AC292C93EACC795413B507772A338B761458D45AC31D9D9D2FF1FB017DA42"

def sh(cwd, *args, timeout=180):
    r = subprocess.run(["git", "-C", cwd] + list(args), capture_output=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

def main() -> int:
    d = tempfile.mkdtemp(prefix="d19delta_")
    try:
        ok = False
        for url in URLS:
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d, exist_ok=True)
            r = subprocess.run(["git", "clone", "--depth", "10", "--filter=blob:none",
                                "--sparse", url, d], capture_output=True, timeout=180)
            if r.returncode == 0:
                ok = True
                break
        if not ok:
            print(json.dumps({"status": "CLONE_FAIL"}))
            return 2
        rc, _, _ = sh(d, "sparse-checkout", "set", "--skip-checks", "docs/orders.md", "docs/decisions.md", timeout=120)
        rc, out, _ = sh(d, "log", "--format=%H", "--", "docs/orders.md")
        commits = out.decode("utf-8", "replace").split()
        old_blob = None
        anchor_commit = None
        for c in commits:
            rc, b, _ = sh(d, "show", c + ":docs/orders.md")
            if rc != 0:
                continue
            s = hashlib.sha256(b).hexdigest().upper()
            if s == OLD_SHA:
                old_blob = b.decode("utf-8", "replace")
                anchor_commit = c
                break
        if old_blob is None:
            print(json.dumps({"status": "OLD_WATERMARK_NOT_IN_DEPTH10",
                              "commits_scanned": len(commits)}))
            return 3
        rc, cur_b, _ = sh(d, "show", "HEAD:docs/orders.md")
        cur_blob = cur_b.decode("utf-8", "replace")
        old_lines = old_blob.splitlines()
        cur_lines = cur_blob.splitlines()
        old_set = set(old_lines)
        added = [ln for ln in cur_lines if ln not in old_set]
        removed = [ln for ln in old_lines if ln not in set(cur_lines)]
        payload = {"status": "OK", "anchor_commit": anchor_commit[:9],
                   "added_count": len(added), "removed_count": len(removed),
                   "added": added, "removed": removed}
        with open("results/_r782bmb_d19_orders_delta.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        print(json.dumps(payload, ensure_ascii=False)[:3000])
        return 0
    finally:
        shutil.rmtree(d, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
