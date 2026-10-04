"""r686 bm-b: deep parsed-compare current runnable_pool.json vs HEAD blob.
If deep-equal -> the sync_face write was pure formatting churn (r678 face):
revert worktree file to HEAD (origin/daemon format) to avoid daemon/library
format ping-pong. Evidence written to results/_r686bmb_pool_face_verdict.json."""
import json
import subprocess


def load_head(path):
    r = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))


cur = json.load(open("results/runnable_pool.json", encoding="utf-8"))
head = load_head("results/runnable_pool.json")
deep_equal = cur == head
verdict = {
    "deep_equal": deep_equal,
    "entries_cur": len(cur.get("entries", [])),
    "entries_head": len(head.get("entries", [])),
    "action": "revert-worktree-to-HEAD" if deep_equal
              else "KEEP (semantic delta present -- inspect before commit)",
}
if deep_equal:
    subprocess.run(["git", "checkout", "HEAD", "--",
                    "results/runnable_pool.json"], capture_output=True)
    after = json.load(open("results/runnable_pool.json", encoding="utf-8"))
    verdict["post_revert_parse_ok"] = after == head
    # lane face check too
    lane_cur = json.load(open("results/runnable_pool.bm-b.json", encoding="utf-8"))
    try:
        lane_head = load_head("results/runnable_pool.bm-b.json")
        verdict["lane_deep_equal"] = lane_cur == lane_head
    except Exception as e:
        verdict["lane_head_err"] = repr(e)
json.dump(verdict, open("results/_r686bmb_pool_face_verdict.json", "w",
                        encoding="utf-8"), ensure_ascii=True, indent=1)
print(json.dumps(verdict, ensure_ascii=True, indent=1))
