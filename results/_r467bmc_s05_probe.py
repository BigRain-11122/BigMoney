"""r467 bm-c S0.5 probe: orders set-diff (same-caliber) + D-19 group watermarks
(decisions SHA-256 + group orders SHA-1, per-key caliber per r458 law) + inbox
unread count. Reuse of r466 probes, round-numbered per r461 law. Raw-blob
git-show bytes, zero PS pipeline. File-out, zero console CJK print."""
import subprocess
import hashlib
import json
import os
import glob

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
DEC_SHA256 = "EB14B510D304A1D0A30175447CF9360D6BAB6DC20972CEEBCE35D47EF8935BFA"
ORD_SHA1 = "68947C178D21814FBB5B20C3497F1DC28D42D50C"
OUT = os.path.join(REPO, "results", "_r467bmc_s05_out.txt")


def run(args, cwd):
    return subprocess.run(
        args, capture_output=True, cwd=cwd,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def main():
    lines = []
    # 1) orders set-diff (disk O-*.md vs heartbeat ack O-*.md entries)
    disk = set(os.path.basename(p) for p in glob.glob(os.path.join(REPO, "fleet", "orders", "O-*.md")))
    hb = json.load(open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
    ack = set(x for x in hb.get("orders_ack", []) if x.startswith("O-") and x.endswith(".md"))
    unacked = sorted(disk - ack)
    lines.append(f"ORDERS_DISK {len(disk)} ACK {len(ack)} UNACKED {len(unacked)}")
    lines.extend("UNACKED: " + u for u in unacked)
    # 2) inbox unread (files not yet in processed/)
    inbox_dir = os.path.join(REPO, "fleet", "inbox")
    proc_dir = os.path.join(inbox_dir, "processed")
    inbox = []
    if os.path.isdir(inbox_dir):
        proc = set(os.path.basename(p) for p in glob.glob(os.path.join(proc_dir, "*")))
        for p in glob.glob(os.path.join(inbox_dir, "*")):
            b = os.path.basename(p)
            if b == "processed" or b in proc or not b.lower().endswith((".md", ".txt", ".json")):
                continue
            name, ext = os.path.splitext(b)
            inbox.append(b if not any(name.endswith(s) for s in ("-ack", "-re")) else b)
    lines.append(f"INBOX_UNREAD {len(inbox)} {sorted(inbox)[:10]}")
    # 3) D-19 group watermarks
    r = run(["git", "fetch", "origin"], GROUP)
    if r.returncode != 0:
        lines.append(f"FETCH_RC {r.returncode} {r.stderr.decode('utf-8', 'replace')[:200]}")
    r = run(["git", "show", "origin/main:docs/decisions.md"], GROUP)
    if r.returncode != 0:
        lines.append("DECISIONS_READ_FAIL")
    else:
        d = hashlib.sha256(r.stdout).hexdigest().upper()
        if d == DEC_SHA256:
            lines.append(f"DECISIONS_MATCH {d[:8]}")
        else:
            lines.append(f"DECISIONS_CHANGED {d}")
            text = r.stdout.decode("utf-8", "replace")
            olines = text.splitlines()
            lines.append("--- decisions diff area: tail 30 lines ---")
            lines.extend(olines[-30:])
    r = run(["git", "show", "origin/main:docs/orders.md"], GROUP)
    if r.returncode != 0:
        lines.append("ORDERS_READ_FAIL")
    else:
        raw = r.stdout
        o = hashlib.sha1(raw).hexdigest().upper()
        if o == ORD_SHA1:
            lines.append(f"GROUP_ORDERS_MATCH {o[:8]}")
        else:
            lines.append(f"GROUP_ORDERS_CHANGED {o}")
            text = raw.decode("utf-8", "replace")
            olines = text.splitlines()
            hit = False
            for i, ln in enumerate(olines):
                if "CEO" in ln and ("待办" in ln or "物理" in ln):
                    hit = True
                    lines.append("--- CEO pending physical-items area ---")
                    lines.extend(olines[i:i + 40])
                    break
            if not hit:
                lines.append("(no CEO-pending marker; tail 40 lines)")
                lines.extend(olines[-40:])
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    print("PROBE_DONE UNACKED", len(unacked), "OUT", OUT)


if __name__ == "__main__":
    main()
