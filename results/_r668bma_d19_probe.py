"""r668 bm-a D-19 decisions/orders fresh-read probe (r660 raw-bytes law: python subprocess git show, no PS pipeline, no on-disk copy hashing)."""
import hashlib
import json
import subprocess
import sys

STATE = "state-bm-a.json"
GROUP_CANDIDATES = [
    r"C:\Users\sjs20\Desktop\Fluxgroup\FluxGroup",
    r"K:\Fluxgroup\FluxGroup",
]


def git_show_bytes(repo: str, path: str) -> bytes:
    # fetch first so origin/main is fresh; show raw blob bytes (content-addressed base law r660)
    subprocess.run(
        ["git", "-C", repo, "fetch", "origin"],
        capture_output=True,
        check=False,
    )
    r = subprocess.run(
        ["git", "-C", repo, "show", f"origin/main:{path}"],
        capture_output=True,
        check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git show failed rc={r.returncode}: {r.stderr[:200]!r}")
    return r.stdout


def main() -> int:
    repo = next((p for p in GROUP_CANDIDATES if __import__("os").path.isdir(p)), None)
    if repo is None:
        print(json.dumps({"verdict": "NO_GROUP_TREE", "candidates": GROUP_CANDIDATES}))
        return 2
    dec = git_show_bytes(repo, "docs/decisions.md")
    dec_sha = hashlib.sha256(dec).hexdigest()
    st = json.load(open(STATE, encoding="utf-8"))
    known = st.get("last_decisions_sha", "")
    match = dec_sha == known
    out = {
        "verdict": "MATCH" if match else "CHANGED",
        "decisions_sha256": dec_sha,
        "state_sha256": known,
        "repo": repo,
        "bytes": len(dec),
    }
    if not match:
        # surface only the tail lines that are new vs state timestamp for triage
        txt = dec.decode("utf-8", errors="replace")
        tail = txt.splitlines()[-40:]
        out["tail_preview"] = tail
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
