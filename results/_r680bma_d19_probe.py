"""D-19 watermark probe r680 bm-a: group decisions.md/orders.md raw-bytes sha256 via sparse-clone git show (r631/r660 laws: python subprocess raw bytes, zero PS pipe, zero disk-file hashing)."""
import json
import hashlib
import subprocess
import sys

CLONE = r"C:\Users\sjs20\AppData\Local\Temp\fg_decisions_d19_r680"
OUT = r"results\_r680bma_d19_probe.json"


def git_show_bytes(path: str) -> bytes:
    r = subprocess.run(
        ["git", "-C", CLONE, "show", f"origin/main:{path}"],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git show {path} rc={r.returncode} stderr={r.stderr[:300]!r}")
    return r.stdout


def main() -> int:
    state = json.load(open("state-bm-a.json", encoding="utf-8"))
    probe = {"round": 680, "machine": "bm-a", "method": "sparse-clone git-show raw bytes sha256"}
    for path, key in (("docs/decisions.md", "last_decisions_sha"), ("docs/orders.md", "last_orders_sha")):
        b = git_show_bytes(path)
        sha = hashlib.sha256(b).hexdigest()
        prev = state.get(key)
        probe[path] = {
            "sha256": sha,
            "prev_watermark": prev,
            "verdict": "MATCH" if sha == prev else "CHANGED",
        }
        if sha != prev:
            probe[path]["bytes"] = len(b)
            probe[path]["new_content_tail"] = b.decode("utf-8", errors="replace")[-4000:]
    json.dump(probe, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if isinstance(v, str) else v.get("verdict")) for k, v in probe.items() if k != "round" and k != "machine" and k != "method"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
