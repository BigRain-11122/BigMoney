"""r496 bm-c S0.5 probe: D-19 dual watermark (dynamic state calibers) +
local orders ack-diff + inbox listing. Read-only, zero console CJK.
Lineage: _r495bmc_s05_check.py verbatim adaptation (read per r461), only
round-scoped output paths changed. Laws: r458 per-key caliber / r672
value-length self-proof / r660 raw-blob bytes / r477 full-filename
both-sides ack diff / r446 probe-to-file."""
import subprocess
import hashlib
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
STATE = os.path.join(REPO, "state-bm-c.json")
HEARTBEAT = os.path.join(REPO, "fleet", "machines", "bm-c.json")
ORDERS_DIR = os.path.join(REPO, "fleet", "orders")
INBOX = os.path.join(REPO, "fleet", "inbox")
OUT = os.path.join(REPO, "results", "_r496bmc_s05_out.txt")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def run(args, cwd):
    return subprocess.run(args, capture_output=True, cwd=cwd, creationflags=CNW)


def main():
    lines = []

    st = json.load(open(STATE, encoding="utf-8"))
    dec_wm = st.get("last_decisions_sha", "").upper()
    ord_wm = st.get("last_orders_sha", "").upper()
    dec_m = st.get("last_decisions_sha_method", "")
    ord_m = st.get("last_orders_sha_method", "")
    lines.append(f"state wm: dec={dec_wm} (len={len(dec_wm)}) method={dec_m}")
    lines.append(f"state wm: ord={ord_wm} (len={len(ord_wm)}) method={ord_m}")
    dec_len = len(dec_wm)
    ord_len = len(ord_wm)
    lines.append(f"calibers: dec-{'sha256' if dec_len == 64 else 'sha1' if dec_len == 40 else 'UNKNOWN'}, ord-{'sha1' if ord_len == 40 else 'sha256' if ord_len == 64 else 'UNKNOWN'}")

    r = run(["git", "fetch", "origin"], GROUP)
    if r.returncode != 0:
        lines.append(f"FETCH_RC {r.returncode} {r.stderr.decode('utf-8', 'replace')[:200]}")

    # decisions (SHA-256 caliber)
    r = run(["git", "show", "origin/main:docs/decisions.md"], GROUP)
    if r.returncode != 0:
        lines.append("DECISIONS_READ_FAIL")
        dec_raw = None
    else:
        dec_raw = r.stdout
        d = hashlib.sha256(dec_raw).hexdigest().upper()
        lines.append("DECISIONS_MATCH" if d == dec_wm else f"DECISIONS_CHANGED {d}")

    # orders (SHA-1 caliber)
    r = run(["git", "show", "origin/main:docs/orders.md"], GROUP)
    if r.returncode != 0:
        lines.append("GROUP_ORDERS_READ_FAIL")
    else:
        raw = r.stdout
        o = hashlib.sha1(raw).hexdigest().upper()
        if o == ord_wm:
            lines.append(f"GROUP_ORDERS_MATCH {o}")
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

    # if decisions changed, dump new blob for read_file consumption
    if dec_raw is not None and "DECISIONS_CHANGED" in "\n".join(lines):
        dec_path = os.path.join(REPO, "results", "_r496bmc_decisions_new.md")
        with open(dec_path, "wb") as f:
            f.write(dec_raw)
        lines.append(f"DECISIONS_NEW_BLOB_WROTE {dec_path} ({len(dec_raw)} bytes)")

    # local orders ack diff (r477: both sides full filenames)
    hb = json.load(open(HEARTBEAT, encoding="utf-8"))
    acked = set(hb.get("orders_ack", []))
    disk = {fn for fn in os.listdir(ORDERS_DIR) if fn.startswith("O-") and fn.endswith(".md")}
    unacked = sorted(disk - acked)
    extra = sorted(acked - disk)
    lines.append(f"orders: disk={len(disk)} acked={len(acked)} unacked={len(unacked)} ack_extra={len(extra)}")
    for fn in unacked:
        lines.append(f"UNACKED {fn}")
    for fn in extra:
        lines.append(f"ACK_EXTRA {fn}")

    # inbox unread (to bm-c or ALL)
    if os.path.isdir(INBOX):
        msgs = sorted(fn for fn in os.listdir(INBOX) if fn.endswith(".md"))
        lines.append(f"inbox_unread_files={len(msgs)}")
        for fn in msgs:
            lines.append(f"INBOX {fn}")
    else:
        lines.append("inbox dir missing")

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    print("PROBE_DONE_WROTE", OUT)


if __name__ == "__main__":
    main()
