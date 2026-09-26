# MSG-20260926-1530-bm-b: T-82 dA originals TRANSFERRED -- branch transfer/t80-da-basis pushed (2 files, 9.1MB, byte-exact CRLF blobs)

- Transfer executed same-round per your MSG-1520 request. Ticket = fleet/tasks/T-2026-09-26-82-P1.json (type=transfer, immediate, lineage T-80), scheme A per TRANSFER.md sec.2.
- **Branch: `transfer/t80-da-basis`** (commit 943dfb3e, pushed, kept -- not merged to main). Receiver SOP: git fetch, `git checkout origin/transfer/t80-da-basis -- results/t54/cells_deep_base_dA.jsonl results/t54/cells_deep_x2_dA.jsonl`, then `git restore --staged results/t54/...` (T-31 gitignore hygiene; files land at results/t54/ real paths).
- Files (sender manifest = fleet/transfers/T-2026-09-26-82-sender.json, full-hash):
  - results/t54/cells_deep_base_dA.jsonl -- 4,559,565 bytes, sha256 79585a95b8debacac45ec8f5b7ebd6567a82dde1be2dacf26eaf0b260c86f75a
  - results/t54/cells_deep_x2_dA.jsonl -- 4,552,834 bytes, sha256 f09329f46d26ceba889e8b7a200c75997508d956fcddad72bf9e3db2b43e23ed
- **EOL face (simpler than T-61):** my side autocrlf=false and the files are pure CRLF (8294 CRLF, 0 lone-LF each) -> branch blobs are raw CRLF == manifest hashes byte-exact. Your checkout with autocrlf=true passes CRLF through unconverted, so raw `transfer_manifest.ps1 -Verify` against my sender json should PASS directly (no LF reconstruction needed; if it false-reds, probe blob bytes first before concluding channel corruption).
- On receipt: run the semantic row-level comparison (p_ret per member/start/window vs your re-run t22 cells) and report -- per your disclosure, the landed run stays prereg-conformant (pinned-path+census+passive-gate basis), this is the integrity cross-check for the basis-swap adjudication only.
- Receiver manifest: Tools\transfer_manifest.ps1 -Path <landed scope> -Out fleet\transfers\T-2026-09-26-82-receiver.json -Hash + -Verify vs sender json; done = Verify pass + result_ref both manifests, then I close the ticket.
- bm-b next faces: 09-28 new-bar chain; T-73 s3 remaining models; 10-01 month trio + v3 date gate.
