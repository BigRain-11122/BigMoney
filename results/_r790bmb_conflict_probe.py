import subprocess, json, sys, os
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, cwd=ROOT)
    return r.stdout, r.returncode

UU = [
    "results/p1d_gates.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
]

def ts_probe(obj, depth=0, out=None):
    """collect top-level and nested ts-like keys"""
    if out is None: out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if isinstance(v, str) and any(t in kl for t in ("ts", "time", "date", "generated", "updated", "since", "at")):
                out[k] = v
            elif isinstance(v, (dict,)) and depth < 2:
                ts_probe(v, depth+1, out)
            elif isinstance(v, list) and v and isinstance(v[0], dict) and depth < 1:
                out[f"{k}[last]"] = {kk: vv for kk, vv in v[-1].items() if isinstance(vv, (str, int, float)) and any(t in str(kk).lower() for t in ("ts","time","generated","updated","since","at"))}
    return out

for p in UU:
    print("="*80)
    print("PATH:", p)
    b2, rc2 = blob(":2", p)   # rebase: onto/origin side
    b3, rc3 = blob(":3", p)   # rebase: replayed ours (bm-b)
    print(f"stage2(origin) rc={rc2} bytes={len(b2)} | stage3(ours-replay) rc={rc3} bytes={len(b3)}")
    if p.endswith(".jsonl"):
        for name, b in (("stage2", b2), ("stage3", b3)):
            lines = [l for l in b.decode("utf-8", "replace").splitlines() if l.strip()]
            print(f"  {name}: {len(lines)} lines; first={lines[0][:120] if lines else None}")
            print(f"  {name}: last ={lines[-1][:200] if lines else None}")
        s2 = set(b2.decode("utf-8","replace").splitlines()); s3 = set(b3.decode("utf-8","replace").splitlines())
        print(f"  union_lines={len(s2|s3)} s2_only={len(s2-s3)} s3_only={len(s3-s2)}")
        for l in sorted(s2-s3)[:3]: print("   S2-ONLY:", l[:200])
        for l in sorted(s3-s2)[:3]: print("   S3-ONLY:", l[:200])
    else:
        for name, b in (("stage2", b2), ("stage3", b3)):
            try:
                o = json.loads(b.decode("utf-8"))
                keys = list(o.keys()) if isinstance(o, dict) else f"list[{len(o)}]"
                print(f"  {name}: keys={keys}")
                print(f"  {name}: ts_probe={json.dumps(ts_probe(o), ensure_ascii=False)[:600]}")
            except Exception as e:
                print(f"  {name}: PARSE FAIL: {e}")

print("="*80)
print("UNSTAGED CHURN CHECK (nulls.jsonl x2):")
for p in ["results/fund_divlowvol_p1/nulls.jsonl", "results/fund_quality_p1/nulls.jsonl"]:
    wt = open(os.path.join(ROOT, p), "rb").read()
    h, rc = blob("HEAD", p)
    wl = [l for l in wt.decode("utf-8","replace").splitlines() if l.strip()]
    hl = [l for l in h.decode("utf-8","replace").splitlines() if l.strip()]
    print(f"  {p}: HEAD {len(hl)} lines -> worktree {len(wl)} lines (append-only: {set(hl) <= set(wl)})")

print("="*80)
print("STATE round_no:")
try:
    st = json.loads(open(os.path.join(ROOT, "state.json"), encoding="utf-8").read())
    print("  state.json keys:", list(st.keys()))
    print("  round_no:", st.get("round_no"))
except Exception as e:
    print("  state.json read fail:", e)
