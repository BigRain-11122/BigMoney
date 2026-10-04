"""r668 bm-a D-19 group orders.md fresh-read (same sparse-clone raw-bytes law)."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

STATE = "state-bm-a.json"
URL = "https://github.com/BigRain-11122/FluxGroup.git"


def main() -> int:
    st = json.load(open(STATE, encoding="utf-8"))
    known = st.get("last_orders_sha", "")
    tmp = os.path.join(tempfile.gettempdir(), f"fg-ord-{uuid.uuid4().hex[:8]}")
    r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", URL, tmp], capture_output=True)
    if r.returncode != 0:
        print(json.dumps({"verdict": "CLONE_FAIL", "stderr": r.stderr[-300:].decode("utf-8", "replace")}))
        return 2
    try:
        g = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/orders.md"], capture_output=True)
        if g.returncode != 0:
            print(json.dumps({"verdict": "SHOW_FAIL", "stderr": g.stderr[-300:].decode("utf-8", "replace")}))
            return 2
        raw = g.stdout
        sha = hashlib.sha256(raw).hexdigest()
        match = sha == known
        out = {"verdict": "MATCH" if match else "CHANGED", "orders_sha256": sha, "state_sha256": known, "bytes": len(raw)}
        if not match:
            txt = raw.decode("utf-8", errors="replace")
            out["tail_preview"] = txt.splitlines()[-50:]
        print(json.dumps(out, ensure_ascii=False))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
