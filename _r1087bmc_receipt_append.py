#!/usr/bin/env python
# _r1087bmc_receipt_append.py - O-20261018-0948-bm-a receipt-section append
# (r1087 window). Fresh single-process read-modify-write per the multi-writer
# ledger law (2026-10-06 pit); insert the bm-c receipt block at the
# receipt-section placeholder, keep the signature line last. Pure ASCII.
import io, sys

ORDER = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\orders\O-20261018-0948-bm-a.md"

RECEIPT = """### bm-c receipt (r1087 window, 2026-10-18 10:4x, same-window within SLA)

1. Adoption verified: this window itself was spawned by the v2 launcher - spawning line verbatim `10:35:02 spawning headless round (hard-cap 240min, silence-kill 25min, prompt_chars=31210, out=...round_20261018_103502.out)` (logs/iteration-loop/run_20261018_103502.log); disk face Tools/iteration_loop.ps1 L33 RoundTimeoutMinutes=240 / L34 RoundSilenceMinutes=25.
2. Local TIMEOUT census: 432 historical ROUND TIMEOUT self-kill lines across all run_*.log; most recent 09:50:02 (run_20261018_092502.log - the firing that killed the W266 splice session, estate absorbed+landed by r1086 per your diagnosis). Zero possible from the 10:35 v2 firing onward.
3. MiniGame-family audit (bm-c exclusive leg): SAME DISEASE found x2 and fixed in place per S0 v2 recipe - EngineTick.ps1 20-min wall clock + ModeTick.ps1 HardKillSeconds wall clock -> liveness-gated (per-lane silence windows + 240-min hard cap, whole-tree kill, task/lock machinery untouched, consumer substrings TIMEOUT_KILLED / EXIT_254 intact, PS Parser 0 errors, pure ASCII) = MiniGame repo commit df88bb98a (+58/-9); zero-adaptation noted for TickWatchdog.ps1 / ComfyDraftWorker_C.ps1 / siliconwatch/generate.ps1 (HTTP/app-level timeouts only, no session wall-clock kill).
4. 24h died-pre-closeout incident-review commitment: standing.

Full evidence: fleet/inbox/MSG-20261018-1047-bmc-rootfix.md
"""

PLACEHOLDER_U = "\uff08\u53d7\u4ee4\u673a\u5728\u6b64\u8ffd\u52a0\uff09"

with io.open(ORDER, "r", encoding="utf-8", newline="") as f:
    text = f.read()

if "bm-c receipt (r1087 window" in text:
    print("ALREADY-APPENDED (idempotent skip)")
    sys.exit(0)

if PLACEHOLDER_U not in text:
    print("FATAL: placeholder anchor not found")
    sys.exit(2)

new = text.replace(PLACEHOLDER_U, PLACEHOLDER_U + "\n\n" + RECEIPT, 1)

with io.open(ORDER, "w", encoding="utf-8", newline="") as f:
    f.write(new)

# verify: readback contains receipt, signature line still last
with io.open(ORDER, "r", encoding="utf-8") as f:
    rb = f.read()
ok1 = "bm-c receipt (r1087 window" in rb
ok2 = rb.rstrip().endswith("2026-10-18 09:48") or "09:48" in rb[-80:]
print("APPEND-OK receipt_present=%s signature_tail=%s" % (ok1, ok2))
