import subprocess

receipts = [
    ("results/_r606bma_n4b2_band_scan_receipt.txt",
     ["python", "results/_r606bma_n4b2_band_scan.py"]),
    ("results/_r606bma_n4b2_banned_gate_receipt.txt",
     ["python", "Tools/banned_direction_gate.py",
      "--prereg", "research/PERPETUAL_N4_B2_PREREG.md"]),
]
for out, cmd in receipts:
    r = subprocess.run(cmd, capture_output=True, cwd=".")
    body = (r.stdout + b"\n" + r.stderr).decode("utf-8", "replace")
    body += f"\n[rc={r.returncode} captured 2026-10-03 r606 bm-a]\n"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print(out, "rc=", r.returncode, "bytes=", len(body))
