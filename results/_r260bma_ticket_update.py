# append progress_r260 to T-82 ticket, five-face mirrored (LF, indent=1, ensure_ascii, no BOM, no trailing \n)
import subprocess, json

PATH = 'fleet/tasks/T-2026-09-26-82-P1.json'
r = subprocess.run(['git', 'show', f'HEAD:{PATH}'], capture_output=True)
d = json.loads(r.stdout.decode('utf-8'))
d['progress_r260'] = (
    "r260 bm-a RECEIVER LEG COMPLETED for deep-bcd follow-up (receipt of MSG-20260926-172x-bm-b): branch "
    "transfer/t80-deep-bcd-basis fetched @ 2ef23068, 6 blob byte sha256 + bytes ALL MATCH sender manifest "
    "(subprocess raw capture, R255 channel law). Semantic comparison vs bm-a local re-run copies: 6/6 "
    "ROW-MULTISET IDENTICAL -- dB/dC/x2_dB/x2_dC = pure line-order permutation (parallel worker write order, "
    "dA R254 paradigm identical); dD/x2_dD = BYTE-IDENTICAL after LF normalization (local CRLF face vs blob "
    "LF-only face, R258 EOL-face law applied). 4/4 deep-shard family cross-check COMPLETE (dA + dB/dC/dD): "
    "double-machine independent re-runs agree on every row x field, zero divergence. Local copies archived "
    "results/_r260bma_t82_deepbcd_compare/mine_* before overwrite (R254 evidence-only paradigm). Files landed "
    "via git checkout branch -- results/t54/ + restore --staged (gitignore hygiene), post-landing LF-normalized "
    "identity 6/6 verified. Receiver manifest fleet/transfers/T-2026-09-26-82-deepbcd-receiver.json written, "
    "transfer_manifest -Verify vs sender manifest PASS (file_count=6 total_bytes=27210738, exit 0) = done face "
    "per TRANSFER.md s0. Ticket stays done; deep-bcd leg receipt recorded; landed T-80 battery basis unchanged "
    "(originals = integrity cross-check only, prereg basis = pinned paths + census + passive gates)."
)
out = json.dumps(d, indent=1, ensure_ascii=True)
with open(PATH, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(out)
# verify staged-diff discipline: field-level increment only
r2 = subprocess.run(['git', 'diff', '--stat', '--', PATH], capture_output=True, text=True)
print(r2.stdout)
