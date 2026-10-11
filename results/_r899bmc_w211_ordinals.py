"""r899: N1_BANDS ordinal forensics -- locate the missing owner row vs W211 freeze anchor 201/40."""
import subprocess
import re


def rows(rev):
    src = subprocess.run(
        ["git", "-C", r"K:\Fluxgroup\FluxGroup\quant\bigmoney", "show", rev + ":scripts/perpetual_faces.py"],
        capture_output=True,
    ).stdout.decode("utf-8", errors="replace")
    m = re.search(r"N1_BANDS\s*=\s*\{(.*?)\n\}", src, re.S)
    body = m.group(1)
    pairs = re.findall(r"^\s{4}(\d+):\s*(\{[^{}]*\})", body, re.M | re.S)
    keys = [int(k) for k, _ in pairs]
    with_owner = {int(k) for k, t in pairs if "engine_owner" in t}
    bmc = {int(k) for k, t in pairs if re.search(r"engine_owner[^,]*bm-c", t)}
    no_owner = sorted(set(keys) - with_owner)
    missing = [w for w in range(1, 212) if w not in set(keys)]
    return keys, sorted(with_owner), sorted(bmc), no_owner, missing


for rev, label in [
    ("d5ec83b72~1", "parent(pre-takeover)"),
    ("d5ec83b72", "r898freeze"),
    ("87b81f973", "r886(W209)"),
    ("HEAD", "now"),
]:
    keys, own, bmc, noown, miss = rows(rev)
    print(f"{label}: keys={len(keys)} owner={len(own)} bmc={len(bmc)} no-owner={noown} missing(1..211)={miss}")

# delta: which waves changed owner-set between parent and r898freeze
k_p, own_p, b_p, _, _ = rows("d5ec83b72~1")
k_f, own_f, b_f, _, _ = rows("d5ec83b72")
print("owner-set added at r898freeze:", sorted(set(own_f) - set(own_p)))
print("owner-set removed at r898freeze:", sorted(set(own_p) - set(own_f)))
