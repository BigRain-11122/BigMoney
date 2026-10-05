# r745 bm-b: D-19 new-content read with hash leg fixed (r701 sha=None bug closure, next-item (e))
# Reads origin blobs for docs/decisions.md + docs/orders.md via sparse clone (r631 recipe),
# computes SHA-256 hex UPPER of raw bytes, compares vs state.json watermark keys.
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
            w = os.path.join("results", "_r745bmb_" + os.path.basename(name))
            with open(w, "wb") as f:
                f.write(b)
            sha = sha256_upper(b) if b else "EMPTY_BLOB"
            key = STATE_KEYS[name]
            prev = st.get(key, "")
            out["files"][name] = {
                "bytes": len(b),
                "sha": sha,
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
