"""r668 bm-a D-19 decisions fresh-read probe v2 (sparse-clone fallback per D-20261004-02③ / r631 bm-b recipe)."""
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
    known = st.get("last_decisions_sha", "")
    tmp = os.path.join(tempfile.gettempdir(), f"fg-d19-{uuid.uuid4().hex[:8]}")
    r = subprocess.run(
        ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", URL, tmp],
        capture_output=True,
    )
    if r.returncode != 0:
        print(json.dumps({"verdict": "CLONE_FAIL", "stderr": r.stderr[-300:].decode("utf-8", "replace")}))
        return 2
    try:
        # read raw blob bytes via git show from the sparse clone (content-addressed, no working-copy hashing)
        g = subprocess.run(
            ["git", "-C", tmp, "show", "origin/main:docs/decisions.md"],
            capture_output=True,
        )
        if g.returncode != 0:
            print(json.dumps({"verdict": "SHOW_FAIL", "stderr": g.stderr[-300:].decode("utf-8", "replace")}))
            return 2
        dec = g.stdout
        dec_sha = hashlib.sha256(dec).hexdigest()
        match = dec_sha == known
        out = {
            "verdict": "MATCH" if match else "CHANGED",
            "decisions_sha256": dec_sha,
            "state_sha256": known,
            "bytes": len(dec),
            "method": "sparse-clone git show origin/main raw bytes",
        }
        if not match:
            txt = dec.decode("utf-8", errors="replace")
            out["tail_preview"] = txt.splitlines()[-40:]
        print(json.dumps(out, ensure_ascii=False))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
