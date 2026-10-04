"""D-19 watermark probe r683 bm-a: group decisions.md/orders.md raw-bytes sha256 via Desktop real-path fetch+git-show (r631/r660/r682 laws: python subprocess raw bytes, zero PS pipe, zero disk-file hashing)."""
import json
import hashlib
import subprocess
import sys

GROUP = r"C:\Users\sjs20\Desktop\FluxGroup"
OUT = r"results\_r685bma_d19_probe.json"


def run_git(args: list) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", GROUP] + args, capture_output=True)


def git_show_bytes(path: str) -> bytes:
    r = run_git(["show", f"origin/main:{path}"])
    if r.returncode != 0:
        raise RuntimeError(f"git show {path} rc={r.returncode} stderr={r.stderr[:300]!r}")
    return r.stdout


def main() -> int:
    fr = run_git(["fetch", "origin"])
    probe = {"round": 685, "machine": "bm-a", "method": "Desktop real-path fetch+git-show raw bytes sha256", "fetch_rc": fr.returncode}
    if fr.returncode != 0:
        probe["fetch_stderr"] = fr.stderr.decode("utf-8", errors="replace")[:300]
        json.dump(probe, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 2
    state = json.load(open("state-bm-a.json", encoding="utf-8"))
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
    print(json.dumps({k: (v.get("verdict") if isinstance(v, dict) else v) for k, v in probe.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

