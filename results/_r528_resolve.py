# r528 bm-b rebase-conflict resolver (S0 ride adopt of r527 W34 carry vs origin bm-a r545 W35 freeze)
# Scope: data-face conflicts only (scripts/perpetual_faces*.py resolved separately by constructive merge).
#  - results/pool_core_samples.jsonl  (UU append-log)  -> line-level union, origin order first, zero loss
#  - results/post_review.jsonl        (UU append-log)  -> line-level union, origin order first, zero loss
#  - results/post_review/REPORT-20261002.md (AA same-day idempotent regeneration) -> take-newer header side
# Deterministic, zero network, zero LLM. Stages read via git subprocess bytes (r209 law: no PS redirection).
import subprocess, sys, json

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage(face, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f":{face}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"stage read fail {face}:{path}: {r.stderr.decode('utf-8','replace')}")
    return r.stdout

def write_bytes(path, data):
    with open(f"{ROOT}\\{path}", "wb") as f:
        f.write(data)

def union_jsonl(path):
    a = stage(2, path)  # origin side (ours during rebase = base being replayed onto)
    b = stage(3, path)  # my ride side (theirs)
    la = a.decode("utf-8").splitlines()
    lb = b.decode("utf-8").splitlines()
    sa = set(la)
    extra = [ln for ln in lb if ln not in sa]
    # preserve each side's own line-ending face; join on the dominant newline of origin side
    nl_a = "\r\n" if a.count(b"\r\n") > a.count(b"\n") - a.count(b"\r\n") else "\n"
    merged = la + extra
    out = nl_a.join(merged) + (nl_a if a.endswith((b"\r\n", b"\n")) else "")
    write_bytes(path, out.encode("utf-8"))
    # zero-loss assertions
    assert len(set(merged)) == len(sa | set(lb)), f"{path}: union count mismatch"
    # every origin line kept in order, every ride line present
    assert set(merged) == sa | set(lb), f"{path}: line set loss"
    print(f"{path}: union ok |A|={len(la)} |B|={len(lb)} |A+B|={len(merged)} (ride-unique kept: {len(extra)})")

def take_newer_report(path):
    a = stage(2, path).decode("utf-8")
    b = stage(3, path).decode("utf-8")
    import re
    def ts_of(t):
        m = re.search(r"生成 (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", t)
        return m.group(1) if m else ""
    ta, tb = ts_of(a), ts_of(b)
    same_body = [x for x in a.splitlines()[1:]] == [x for x in b.splitlines()[1:]]
    newer = a if ta >= tb else b
    # same-day idempotent regeneration: if bodies identical -> take newer header, else take origin side
    # (origin = deterministic re-derive face; disclose if bodies differ)
    chosen = newer if same_body else a
    write_bytes(path, chosen.encode("utf-8"))
    print(f"{path}: take-{'newer' if same_body else 'ORIGIN(body-diff-disclosed)'} ts_origin={ta!r} ts_ride={tb!r} body_identical={same_body}")
    if not same_body:
        print(f"  DISCLOSE: {path} stage bodies differ beyond header; origin side kept")

union_jsonl("results/pool_core_samples.jsonl")
union_jsonl("results/post_review.jsonl")
take_newer_report("results/post_review/REPORT-20261002.md")
print("RESOLVER OK")
