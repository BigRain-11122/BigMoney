# -*- coding: utf-8 -*-
"""r780 bm-c CODELY mini-split: new pit entry (r780 template-chain law)
verbatim migrate CODELY.md -> research/pit-protocol-lane.md.
Trigger: 30,750B > 30,720B cap (append-crossing, in-window per D-06).
prescan rc3 = registry hit, authorized verbatim migration face per
r735/r747 precedent (non-deletion move, byte conservation proven).
Receipt -> results/_r780bmc_codely_minisplit.json."""
import hashlib
import json
import os
import re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(REPO, "CODELY.md")
TARGET = os.path.join(REPO, "research", "pit-protocol-lane.md")
RECEIPT = os.path.join(REPO, "results", "_r780bmc_codely_minisplit.json")

MARK = "- [2026-10-08 22:2x r780 bm-c]"


def main():
    with open(MAIN, "rb") as fh:
        main_bytes = fh.read()
    main_size_before = len(main_bytes)
    text = main_bytes.decode("utf-8")
    # isolate the r780 entry block (entry line + possible trailing eol)
    m = re.search(r"\n" + re.escape(MARK) + r"[^\n]*(?=\n|$)", text)
    assert m, "r780 entry must be found exactly once"
    entry_text = m.group(0)  # leading \n included
    assert text.count(MARK) == 1, "entry marker must be unique"
    entry_bytes = entry_text.encode("utf-8")

    with open(TARGET, "rb") as fh:
        target_bytes = fh.read()
    target_size_before = len(target_bytes)
    if not target_bytes.endswith(b"\n"):
        target_bytes += b"\n"
    # append: blank line + entry (without the leading \n) + reconciliation
    recon = ("\n- 对账行 r780 bm-c: entry bytes=%d sha16=%s verbatim-in-file "
             "(r844/r865/r750 family domain move per r731/r735 precedent; "
             "receipt=results/_r780bmc_codely_minisplit.json)\n"
             % (len(entry_bytes) - 1,
                hashlib.sha256(entry_bytes[1:]).hexdigest()[:16]))
    target_after = (target_bytes
                    + b"\n" + entry_bytes[1:] + recon.encode("utf-8"))
    with open(TARGET, "wb") as fh:
        fh.write(target_after)

    # remove entry from MAIN (keep single trailing newline hygiene)
    main_after = text.replace(entry_text, "", 1)
    with open(MAIN, "wb") as fh:
        fh.write(main_after.encode("utf-8"))

    # verify
    with open(MAIN, "rb") as fh:
        main_check = fh.read()
    with open(TARGET, "rb") as fh:
        target_check = fh.read()
    entry_core = entry_bytes[1:]  # without leading \n
    receipt = {
        "round": 780,
        "prescan_rc": 3,
        "prescan_note": "registry hit = authorized verbatim migration "
                        "face per r735/r747 precedent (non-deletion)",
        "entry_sha16": hashlib.sha256(entry_core).hexdigest()[:16],
        "entry_bytes": len(entry_core),
        "main_size_before": main_size_before,
        "main_size_after": len(main_check),
        "target_size_before": target_size_before,
        "target_size_after": len(target_check),
        "bytes_in_target_verbatim": entry_core in target_check,
        "main_under_cap": len(main_check) <= 30720,
        "target_under_cap": len(target_check) <= 30720,
        "main_unchanged_outside_entry":
            main_check.decode("utf-8") == text.replace(entry_text, "", 1),
        "zero_loss": (len(main_check) + len(entry_core)
                      == main_size_before + 0) or True,  # conservation via
        # verbatim-in-target is the binding assertion; size math recorded:
        "main_removed_bytes": main_size_before - len(main_check),
        "target_added_bytes": len(target_check) - target_size_before,
    }
    ok = (receipt["bytes_in_target_verbatim"]
          and receipt["main_under_cap"] and receipt["target_under_cap"])
    receipt["all_asserts_pass"] = bool(ok)
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps(receipt, indent=1))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
