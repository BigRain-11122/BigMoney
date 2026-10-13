# r978 S0 stash-evidence recovery (byte-exact law, utf-8 throughout)
# Recovers 4 evidence files from autostash 45fadcc62 after atomic pop failure:
#  - post_review.jsonl: chronological union (append-only claims log)
#  - compute_audit.bm-c.json: stash wholesale (my face, newer, no foreign writes)
#  - pool_dualrun.bm-c.jsonl: stash wholesale (my rotating-window face, newer)
#  - compute_audit.json: history union by (ts,machine) key (shared face)
import json, subprocess, sys, io

GIT = r"C:\Program Files\Git\cmd\git.exe"
STASH = "45fadcc62be856f332dc07f81883dfbc344c1d36"

def stash_bytes(path):
    r = subprocess.run([GIT, "show", f"{STASH}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show failed for {path}: {r.stderr[:200]}")
    return r.stdout

def read_wt(path):
    with open(path, "rb") as f:
        return f.read()

def write_wt(path, data):
    with open(path, "wb") as f:
        f.write(data)

report = []

# 1) post_review.jsonl chronological union
pr_wt = read_wt("results/post_review.jsonl").split(b"\n")
pr_st = stash_bytes("results/post_review.jsonl").split(b"\n")
def line_ts(b):
    try:
        s = b.decode("utf-8", "replace").strip()
        if not s:
            return b""
        j = json.loads(s)
        return str(j.get("ts", "")).encode()
    except Exception:
        return b""
seen = set()
merged = []
i_wt, i_st = 0, 0
# merge two chronologically-sorted streams; exact-line dedupe
def next_key(lst, i):
    while i < len(lst):
        if lst[i].strip():
            return i
        i += 1
    return None
while True:
    iw = next_key(pr_wt, i_wt); isx = next_key(pr_st, i_st)
    if iw is None and isx is None:
        break
    if iw is None:
        cand, src, which = pr_st[isx], isx, "st"; i_st = isx + 1
    elif isx is None:
        cand, src, which = pr_wt[iw], iw, "wt"; i_wt = iw + 1
    else:
        tw, ts_ = line_ts(pr_wt[iw]), line_ts(pr_st[isx])
        if ts_ <= tw:  # stash line earlier or equal ts -> take stash first
            cand, src, which = pr_st[isx], isx, "st"; i_st = isx + 1
        else:
            cand, src, which = pr_wt[iw], iw, "wt"; i_wt = iw + 1
    h = cand.strip()
    if h and h not in seen:
        seen.add(h)
        merged.append(cand.rstrip(b"\r"))
out_pr = (b"\n".join(x for x in merged if x.strip()) + b"\n")
wt_lines = sum(1 for x in pr_wt if x.strip()); st_lines = sum(1 for x in pr_st if x.strip())
write_wt("results/post_review.jsonl", out_pr)
report.append(f"post_review.jsonl: wt={wt_lines} stash={st_lines} merged_unique={len([x for x in merged if x.strip()])}")

# 2+3) wholesale stash faces
for f in ("results/compute_audit.bm-c.json", "results/pool_dualrun.bm-c.jsonl"):
    sb = stash_bytes(f)
    write_wt(f, sb)
    report.append(f"{f}: stash wholesale {len(sb)}B (wt was {len(read_wt(f)) if False else ''}replaced)")

# 4) compute_audit.json shared history union
ca_wt = json.loads(read_wt("results/compute_audit.json").decode("utf-8"))
ca_st = json.loads(stash_bytes("results/compute_audit.json").decode("utf-8"))
hist_wt = ca_wt.get("history", [])
hist_st = ca_st.get("history", [])
def hkey(e):
    return (str(e.get("ts", "")), str(e.get("machine", e.get("host", ""))), str(e.get("cores", "")))
union = {}
order = []
for e in hist_wt + hist_st:  # wt first; stash entries same-key overwrite only if... keep wt priority for identical key
    k = hkey(e)
    if k not in union:
        union[k] = e
        order.append(k)
    else:
        # same ts+machine: prefer the entry with more keys (denser sample)
        if len(e) > len(union[k]):
            union[k] = e
ca_wt["history"] = [union[k] for k in order]
# top-level ts: newest wins
if str(ca_st.get("ts", "")) > str(ca_wt.get("ts", "")):
    for k in ("ts",):
        ca_wt[k] = ca_st[k]
write_wt("results/compute_audit.json", json.dumps(ca_wt, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
report.append(f"compute_audit.json: wt_hist={len(hist_wt)} stash_hist={len(hist_st)} union={len(order)} top_ts={ca_wt.get('ts')}")

print(json.dumps(report, ensure_ascii=False, indent=1))
print("RECOVERY-OK")
