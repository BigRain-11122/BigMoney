import subprocess, json

def blob(ref, p):
    r = subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def keys_rows(b):
    rows = [json.loads(l) for l in b.decode("utf-8").splitlines() if l.strip()]
    return {r["key"]: r for r in rows}, rows

p = "results/fund_divlowvol_p1/nulls.jsonl"
hk, hr = keys_rows(blob("HEAD", p))
sk, sr = keys_rows(blob("stash@{0}", p))
ck, cr = keys_rows(open(p, "rb").read())
print("HEAD rows:", len(hr), "max k:", max(r["k"] for r in hr))
print("stash rows:", len(sr), "max k:", max(r["k"] for r in sr))
print("current rows:", len(cr), "max k:", max(r["k"] for r in cr))
print("HEAD-only keys (missing from current):", sorted(set(hk) - set(ck))[:15])
print("stash-only keys vs HEAD:", sorted(set(sk) - set(hk))[:15])
print("HEAD-only keys vs stash:", sorted(set(hk) - set(sk))[:15])
var = [k for k in set(hk) & set(ck) if json.dumps(hk[k], sort_keys=True) != json.dumps(ck[k], sort_keys=True)]
print("HEAD-current same-key content variants:", var[:6])
var2 = [k for k in set(hk) & set(sk) if json.dumps(hk[k], sort_keys=True) != json.dumps(sk[k], sort_keys=True)]
print("HEAD-stash same-key content variants:", var2[:6])

pq = "results/fund_quality_p1/nulls.jsonl"
qk, qr = keys_rows(open(pq, "rb").read())
hq, hrq = keys_rows(blob("HEAD", pq))
print()
print("quality: HEAD rows:", len(hrq), "current rows:", len(qr))
print("quality HEAD-only keys:", sorted(set(hq) - set(qk))[:8], "| current-only:", sorted(set(qk) - set(hq))[:8])
vq = [k for k in set(hq) & set(qk) if json.dumps(hq[k], sort_keys=True) != json.dumps(qk[k], sort_keys=True)]
print("quality HEAD-current same-key variants:", vq[:6])

pv = "results/fund_value_p1/nulls.jsonl"
vk, vr = keys_rows(open(pv, "rb").read())
hv, hrv = keys_rows(blob("HEAD", pv))
print()
print("value: HEAD rows:", len(hrv), "current rows:", len(vr))
print("value HEAD-only keys:", sorted(set(hv) - set(vk))[:8], "| current-only:", sorted(set(vk) - set(hv))[:8])
