r"""r691 bm-a S0 decisions watermark check (D-20261004-02(c)(3) sparse-clone path).

Group tree K:\Fluxgroup\FluxGroup absent in this session -> temp sparse clone,
git show origin/main:docs/decisions.md original bytes (r660 subprocess law),
sha256 vs state-bm-a.json last_decisions_sha. ssh URL first (r677), mkdtemp
unique dir, cleanup best-effort.
"""
import subprocess, hashlib, json, tempfile, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPOS = [
    "git@github.com:BigRain-11122/FluxGroup.git",
    "https://github.com/BigRain-11122/FluxGroup.git",
]

def run(cmd, cwd=None):
    return subprocess.run(cmd, capture_output=True, cwd=cwd)

def main():
    out = {"decisions": None, "orders": None}
    tmp = tempfile.mkdtemp(prefix="d19_r691_")
    clone_rc = None
    try:
        for url in REPOS:
            r = run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                     url, tmp])
            clone_rc = r.returncode
            if r.returncode == 0:
                out["clone_url"] = url
                break
        if clone_rc != 0:
            out["error"] = "clone_failed"
            print(json.dumps(out))
            return 2
        r = run(["git", "sparse-checkout", "set", "--skip-checks",
                 "docs/decisions.md", "docs/orders.md"], cwd=tmp)
        if r.returncode != 0:
            out["error"] = "sparse_set_failed: " + r.stderr.decode("utf-8", "replace")[:200]
            print(json.dumps(out))
            return 2
        for path, key in (("docs/decisions.md", "decisions"), ("docs/orders.md", "orders")):
            r = run(["git", "show", "origin/main:" + path], cwd=tmp)
            if r.returncode != 0:
                out[key] = {"rc": r.returncode, "len": 0, "sha256": None,
                            "err": r.stderr.decode("utf-8", "replace")[:120]}
                continue
            b = r.stdout
            out[key] = {"rc": 0, "len": len(b),
                        "sha256": hashlib.sha256(b).hexdigest().upper()}
        st = json.load(open("state-bm-a.json", encoding="utf-8"))
        prev_d = st.get("last_decisions_sha", "")
        cur_d = (out["decisions"] or {}).get("sha256") or ""
        out["prev_decisions_sha"] = prev_d
        out["decisions_changed"] = (prev_d.upper() != cur_d) if cur_d else None
        # orders watermark key (SHA-1 per r458/r672 value-length self-evidence)
        prev_o = st.get("last_orders_sha", "")
        if prev_o:
            r = run(["git", "show", "origin/main:docs/orders.md"], cwd=tmp)
            if r.returncode == 0:
                # r672 value-length self-evidence: 64-hex watermark -> sha256, 40-hex -> sha1
                algo = hashlib.sha256 if len(prev_o.strip()) == 64 else hashlib.sha1
                cur_o1 = algo(r.stdout).hexdigest()
                out["prev_orders_sha"] = prev_o
                out["orders_algo"] = algo().name
                out["orders_changed"] = (cur_o1.lower() != prev_o.lower())
        print(json.dumps(out))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
