# r684 bm-b: inspect the two structurally-merged faces before resolving
# (r456 per-key union law for token_usage machines; compute_audit history union)
import io, json, subprocess

def side(path, rev):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    return json.loads(r.stdout.decode("utf-8", "replace"))

for rev, tag in (("HEAD", "OURS"), ("MERGE_HEAD", "THEIRS")):
    tu = side("results/token_usage.json", rev)
    print("token_usage", tag, "top keys:", list(tu.keys()))
    mach = tu.get("machines") or {}
    print("  machines keys:", list(mach.keys()))
    ca = side("results/compute_audit.json", rev)
    print("compute_audit", tag, "top keys:", list(ca.keys())[:12])
    hist = ca.get("history")
    if isinstance(hist, list):
        print("  history len:", len(hist), "| first key sample:",
              list(hist[0].keys())[:6] if hist else None)
    print("  ts:", ca.get("ts"), "| epoch:", ca.get("epoch"))
