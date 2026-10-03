"""_r435bmc_rebase_resolve.py -- per-face newer-wins adjudication for r435 S0 surgery.

Context: r434 (ca9c3a009+b4ab54ba0) never reached origin/main (false push-verified
claim in r434 state -- r502-family). Origin meanwhile advanced to bm-a r646
(e74c79c95, committed 23:06:32) which regenerated the same 15 shared S6/CEO
faces my r434 had regenerated at 22:53-22:57. Cherry-pick replay onto
origin/main conflicts on those faces; resolution law = MSG-0612 newer-wins
(same procedure as r433/r434 receipts, direction now flipped because bm-a's
regens are newer).

Usage (via Invoke-SilentExe, zero-window law):
  python results/_r435bmc_rebase_resolve.py <mine_sha> <origin_sha> <file> [<file>...]
Writes results/_r435bmc_rebase_resolve.json receipt; prints one line per face:
  <file>|<side>|<why>
side: origin (take pick-base/ours) | mine (take commit/theirs)
"""
import json
import re
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
TS_KEYS = [
    "generated_at", "generated", "updated_at", "updated", "ts", "last_run",
    "last_ts", "clock_read", "asof", "evidence_cutoff", "scan_time", "scanned_at",
]
TS_RE = re.compile(r'"([^"]*(?:at|ts|time|asof|cutoff|read)[^"]*)"\s*:\s*"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})')


def git_show(sha: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{sha}:{path}"],
        stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW,
    )


def first_ts(blob: bytes):
    m = TS_RE.search(blob.decode("utf-8", "replace"))
    if m:
        return m.group(1), m.group(2)
    return None, None


def main() -> int:
    mine_sha, origin_sha, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    faces = []
    for path in files:
        try:
            mine_blob = git_show(mine_sha, path)
        except subprocess.CalledProcessError:
            faces.append({"path": path, "side": "origin", "why": "not in mine commit"})
            continue
        origin_blob = git_show(origin_sha, path)
        mk, mv = first_ts(mine_blob)
        ok, ov = first_ts(origin_blob)
        if mk and ok and mv and ov:
            if ov > mv:
                side, why = "origin", f"origin {ok} {ov} > mine {mk} {mv}"
            elif mv > ov:
                side, why = "mine", f"mine {mk} {mv} > origin {ok} {ov}"
            else:
                side, why = "origin", f"ts tie {mv}, default origin (bm-a r646 committed 23:06:32 after my r434 22:5x)"
        else:
            side = "origin"
            why = f"ts extract incomplete (mine={bool(mv)} origin={bool(ov)}), default origin per r646-newer window"
        faces.append({
            "path": path, "side": side, "why": why,
            "bytes_mine": len(mine_blob), "bytes_origin": len(origin_blob),
        })
        print(f"{path}|{side}|{why}")
    receipt = {
        "round": "r435 bm-c", "mine_base": mine_sha, "origin_base": origin_sha,
        "procedure": "isolated-worktree cherry-pick per r630; per-face newer-wins per MSG-0612 (r433/r434 receipt family)",
        "faces": faces,
        "ok": True,
    }
    with open("results/_r435bmc_rebase_resolve.json", "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
