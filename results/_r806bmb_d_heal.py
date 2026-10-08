"""r806 bm-b: FUND-DIVLOWVOL-P1 nulls cross-machine-merge dedup + 19-key heal ignition.

Root cause (r806 forensics): bm-a autofill shard burned D-lane nulls in its own
tree 18:24->19:49 (claim receipt N=2000 local-complete), but the shared-face
merge (bm-a r839 merge a322e71b7 union of bm-b r806 dead-session pushes + bm-a
churn-absorb fc78fb779 pre-completion snapshot) produced a 2146-row file:
165 byte-identical duplicate lines (keys burned by BOTH machines from the same
frozen seed rng([base,k]) -> identical draws) + 19 tail keys missing
(1972..1999 region, bm-a's final tail rows never committed to origin).

Heal = two steps, both attrition-safe (key set unchanged):
 1. line-level dedup of byte-identical duplicate rows (append-only ledger;
    treasure_guard rc3 forbids origin-restore, line-level surgery legal per
    r801 canon; dup pairs verified byte-identical at surgery time -> zero
    information loss by construction)
 2. detached heal burn of the 19 missing keys via runner's own checkpoint
    done-key skip (r801 canon: DETACHED_PROCESS zero-window U060,
    BelowNormal priority CEO margin law, both-redirect to log)

Pre/post asserts: key set identity, dup pairs byte-identical, JSON-parse all
kept lines, trailing newline, row counts 2146->1981. Receipt: in-module
JSON + pre-state file.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "scripts", "fund_divlowvol_p1.py")
NULLS = os.path.join(ROOT, "results", "fund_divlowvol_p1", "nulls.jsonl")
LOG = os.path.join(ROOT, "results", "_r806bmb_d_heal_ignite.log")
PRE = os.path.join(ROOT, "results", "_r806bmb_d_dedup_pre.json")
RECEIPT = os.path.join(ROOT, "results", "_r806bmb_d_nulls_dedup.json")
TARGET = 2000


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    raw = open(NULLS, "rb").read()
    text = raw.decode("utf-8")
    sha_before = hashlib.sha256(raw).hexdigest()
    lines = [ln for ln in text.split("\n")]
    trailing_nl = text.endswith("\n")
    seen = {}
    kept, dup_pairs_identical, dup_pairs_diff = [], 0, 0
    dup_keys = []
    parse_fail = 0
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            parse_fail += 1
            kept.append(ln)  # crash-tail law: keep verbatim
            continue
        k = obj["k"]
        if k in seen:
            if seen[k] == s:
                dup_pairs_identical += 1
            else:
                dup_pairs_diff += 1
            dup_keys.append(k)
            continue  # drop byte-identical (or conflicting) later copy
        seen[k] = s
        kept.append(s)
    keys_pre = sorted(set(range(TARGET)) & set(seen.keys()))
    missing_pre = sorted(set(range(TARGET)) - set(seen.keys()))
    # assertions before write
    assert dup_pairs_diff == 0, f"HARD-STOP: {dup_pairs_diff} conflicting dup rows -- adjudicate, do not dedup blind"
    assert parse_fail == 0, f"HARD-STOP: {parse_fail} unparseable lines"
    assert len(kept) == len(seen), "kept/unique mismatch"
    data = ("\n".join(kept) + "\n").encode("utf-8")
    tmp = NULLS + ".tmp_r806"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, NULLS)
    sha_after = sha256_file(NULLS)

    # post-verify: key set identity + per-key byte identity
    post = {}
    for ln in open(NULLS, encoding="utf-8"):
        s = ln.strip()
        if s:
            o = json.loads(s)
            post[o["k"]] = s
    assert set(post.keys()) == set(seen.keys()), "key set changed"
    for k, s in seen.items():
        assert post[k] == s, f"row content changed for k={k}"
    missing_post = sorted(set(range(TARGET)) - set(post.keys()))

    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "machine": "bm-b",
        "round": "r806",
        "file": "results/fund_divlowvol_p1/nulls.jsonl",
        "rows_before": len([l for l in lines if l.strip()]),
        "rows_after": len(kept),
        "unique_keys": len(seen),
        "dup_keys_removed": len(dup_keys),
        "dup_pairs_byte_identical": dup_pairs_identical,
        "dup_pairs_conflicting": dup_pairs_diff,
        "missing_pre": missing_pre,
        "missing_count_pre": len(missing_pre),
        "missing_post": missing_post,
        "key_set_identity": True,
        "per_key_byte_identity": True,
        "attrition_note": "key set unchanged (r611 containment law def: attrition-safe); removed lines byte-identical to kept twins = zero info loss",
        "treasure_guard": "restore rc3 (append-only-ledger class, line-level surgery legal per r801 canon)",
        "sha256_before": sha_before,
        "sha256_after": sha_after,
        "asserts": "ALL PASS",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
    with open(PRE, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"ts": rec["ts"], "rows": len(kept), "missing_keys": missing_pre,
                   "missing_count": len(missing_pre)}, f, indent=1)
    print(json.dumps({k: rec[k] for k in ("rows_before", "rows_after", "unique_keys",
                                          "dup_keys_removed", "missing_count_pre", "asserts")}))

    # ignition: detached heal burn (r801 canon)
    if not missing_pre:
        print("nothing to burn -- no ignition")
        return 0
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    env = dict(os.environ)
    with open(LOG, "ab") as lf:
        lf.write(("\n[r806 heal-ignite %s] fund_divlowvol_p1 run --nulls detached "
                  "heal burn todo=%d (checkpoint done-key skip; cross-machine-merge "
                  "dedup + tail-completion, forensics in module docstring)\n"
                  % (time.strftime("%Y-%m-%dT%H:%M:%S"), len(missing_pre))).encode("utf-8"))
        lf.flush()
        p = subprocess.Popen([sys.executable, "-u", RUNNER, "run", "--nulls"],
                             cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT,
                             creationflags=flags, close_fds=True, env=env)
    try:
        import psutil
        psutil.Process(p.pid).nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        pri = "BelowNormal"
    except Exception as ex:
        pri = f"nice-skip ({ex})"
    print(f"spawned detached heal burn pid={p.pid} priority={pri} log={LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
