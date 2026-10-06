# r767 bm-b: D-19 dual read. Lineage: verbatim copy of results/_r767bmb_d19_read.py (r767 bloodline
# verbatim + r537 algo-pick leg: watermark-key hex length decides SHA-1 40hex for orders.md /
# SHA-256 64hex for decisions.md); only the output path prefix changed _r766bmb_ -> _r771bmb_.
import subprocess, tempfile, shutil, os, sys, json, hashlib

URLS = ["git@github.com:BigRain-11122/FluxGroup.git",
        "https://github.com/BigRain-11122/FluxGroup.git"]
FILES = ["docs/decisions.md", "docs/orders.md"]
STATE_KEYS = {"docs/decisions.md": "last_decisions_sha",
              "docs/orders.md": "last_orders_sha"}

def sha256_upper(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()

def main() -> int:
    d = tempfile.mkdtemp(prefix="d19read_")
    try:
        ok = False
        for url in URLS:
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d, exist_ok=True)
            r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                                "--sparse", url, d],
                               capture_output=True, text=True, timeout=180)
            if r.returncode == 0:
                ok = True
                break
        if not ok:
            print(json.dumps({"status": "CLONE_FAIL"}))
            return 2
        subprocess.run(["git", "-C", d, "sparse-checkout", "set", "--skip-checks"] + FILES,
                       capture_output=True, timeout=120)
        with open(os.path.join("state.json"), "rb") as f:
            st = json.loads(f.read().decode("utf-8"))
        out = {"status": "OK", "files": {}}
        for name in FILES:
            p = os.path.join(d, name.replace("/", os.sep))
            try:
                with open(p, "rb") as f:
                    b = f.read()
            except OSError:
                b = b""
            w = os.path.join("results", "_r771bmb_" + os.path.basename(name))
            with open(w, "wb") as f:
                f.write(b)
            key = STATE_KEYS[name]
            prev = st.get(key, "")
            # r537 law: algo picked by watermark key form (40hex->SHA-1, 64hex->SHA-256), never default sha256
            if b and len(prev) == 40:
                sha = hashlib.sha1(b).hexdigest().upper()
            elif b:
                sha = sha256_upper(b)
            else:
                sha = "EMPTY_BLOB"
            out["files"][name] = {
                "bytes": len(b),
                "sha": sha,
                "algo": "sha1" if len(prev) == 40 else "sha256",
                "watermark_key": key,
                "prev": prev,
                "changed": bool(sha != prev),
            }
        print(json.dumps(out, ensure_ascii=False))
        rc = 0
        for name in FILES:
            if out["files"][name]["changed"]:
                rc = 1  # signal: new content to consume
        return rc
    finally:
        shutil.rmtree(d, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main())
