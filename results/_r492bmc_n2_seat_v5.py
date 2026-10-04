"""r492 bm-c N2 slice-3 freeze-window pre-write recheck (r687 law): fresh
fetch + origin single-point blob checks BEFORE the SEED_REGISTRY write.
Checks: (1) three N2 keys absent on origin registry blob; (2) registry
values near the 31_000..32_499 zone listed for collision eyeball; (3)
origin prereg still DRAFT (no other machine froze it); (4) no other
slice-3 seat-claim MSG on origin inbox; (5) local SEED_REGISTRY live
import + count sanity (must equal origin count). Receipt ->
results/_r492bmc_n2_seat_v5.txt. Zero console CJK (r458 family)."""
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = REPO + r"\results\_r492bmc_n2_seat_v5.txt"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
KEYS = ["perpetual_n2_w15_gen", "perpetual_n2_w15_scrnull", "perpetual_n2_w15_unc"]


def run(args):
    return subprocess.run(args, capture_output=True, cwd=REPO, creationflags=CNW)


def registry_region(text):
    i = text.find("SEED_REGISTRY = {")
    assert i >= 0, "SEED_REGISTRY not found"
    j = text.find("\n    }\n", i)
    assert j >= 0, "registry close not found"
    return text[i:j]


def pairs(region):
    out = {}
    for m in re.finditer(r'"([A-Za-z0-9_]+)"\s*:\s*([0-9_]+)', region):
        out[m.group(1)] = int(m.group(2).replace("_", ""))
    return out


def main():
    lines = []
    r = run(["git", "fetch", "origin"])
    lines.append(f"FETCH_RC {r.returncode}")
    r = run(["git", "rev-parse", "origin/main"])
    tip = r.stdout.decode().strip()
    lines.append(f"ORIGIN_TIP {tip}")
    r = run(["git", "rev-list", "--count", "HEAD..origin/main"])
    lines.append(f"BEFORE_WRITE_BEHIND {r.stdout.decode().strip()}")

    # (1)+(2) origin registry blob
    r = run(["git", "show", "origin/main:scripts/science_gates.py"])
    assert r.returncode == 0, "origin science_gates show failed"
    otext = r.stdout.decode("utf-8", "replace")
    oreg = pairs(registry_region(otext))
    lines.append(f"ORIGIN_REGISTRY_N {len(oreg)}")
    for k in KEYS:
        lines.append(f"ORIGIN_KEY_{k} {'ABSENT-OK' if k not in oreg else 'PRESENT-COLLIDE=' + str(oreg[k])}")
    near = sorted((v, k) for k, v in oreg.items() if 25000 <= v <= 40000)
    lines.append("ORIGIN_VALUES_25000_40000 " + repr(near))
    inzone = [(k, v) for k, v in oreg.items() if 31000 <= v <= 32499]
    lines.append(f"ORIGIN_IN_ZONE_31000_32499 {inzone if inzone else 'none-CLEAN'}")

    # (3) origin prereg status
    r = run(["git", "show", "origin/main:research/PERPETUAL_N2_W15_PREREG.md"])
    ptext = r.stdout.decode("utf-8", "replace")
    draft = "DRAFT-NOT-FROZEN" in ptext
    frozen_word = "FROZEN" in ptext
    lines.append(f"ORIGIN_PREREG draft_marker={draft} any_frozen_word={frozen_word}")

    # (4) origin inbox seat-claim scan (any slice-3 claim not mine)
    r = run(["git", "ls-tree", "--name-only", "origin/main", "fleet/inbox/"])
    names = [x.split("/")[-1] for x in r.stdout.decode().splitlines() if x.strip()]
    lines.append(f"ORIGIN_INBOX {names}")
    claims = [n for n in names if "slice-3" in n or ("19" in n and "bma" in n and "bmc" not in n)]
    lines.append(f"OTHER_CLAIM_MSG_CANDIDATES {claims if claims else 'none'}")

    # (5) local live import sanity == origin count
    sys.path.insert(0, REPO)  # knowledge.cost_spec lives at repo root
    sys.path.insert(0, REPO + r"\scripts")
    import science_gates as sg
    lreg = {k: v for k, v in sg.SEED_REGISTRY.items() if isinstance(v, int)}
    lines.append(f"LOCAL_REGISTRY_N {len(lreg)}")
    lines.append("LOCAL_EQ_ORIGIN_N " + str(len(lreg) == len(oreg)))
    for k in KEYS:
        lines.append(f"LOCAL_KEY_{k} {'ABSENT-OK' if k not in lreg else 'PRESENT'}")
    lnear = sorted((v, k) for k, v in lreg.items() if 25000 <= v <= 40000)
    lines.append("LOCAL_VALUES_25000_40000 " + repr(lnear))

    ok = (
        all(k not in oreg for k in KEYS)
        and not inzone
        and draft
        and len(lreg) == len(oreg)
        and all(k not in lreg for k in KEYS)
    )
    lines.append(f"V5_VERDICT {'ADMIT-PROCEED-WRITE' if ok else 'REFUSE-STOP'}")
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    print("V5_VERDICT " + ("ADMIT-PROCEED-WRITE" if ok else "REFUSE-STOP"))


if __name__ == "__main__":
    main()
