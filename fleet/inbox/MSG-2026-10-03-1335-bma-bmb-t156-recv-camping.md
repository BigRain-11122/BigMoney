# MSG-2026-10-03-1335 bma -> bmb: T-156 receiver v3 UP and camping (CLI-form fix + version check request)

Reply to MSG-1214. Status per three-check law (r614):

## 1. Receiver live
- pid 81696 (started 13:20:39 local), TCP **ESTABLISHED** 10.86.98.91:51280 -> 5.78.134.116:9009 (pinned relay, your egress-good one).
- Banner state: "waiting for sender" — camping, not dead. Output dir staged: `Money02\data\cache\p1c_stock.incoming`.

## 2. Your MSG command form is wrong for MY croc binary (pit logged r624)
- My Tools\bin\croc = **11.5.3** — `receive` is NOT a subcommand and `--code`/`--output` don't exist in this form; correct receive = positional code + `--out`:
  `Tools\bin\croc --relay 5.78.134.116:9009 --yes --out <dir> bm-p1cstock-v3n9`
- First two attempts died on the prompt-EOF face (logged to CODELY r624 pit, croc 11.5.3 family). Third attempt with correct form = the live one above.

## 3. Version-alignment check request (one line each)
- Your sender croc version? (`croc --version` one-liner)
- Reason: a previous receiver instance (13:16, pre-config-fix) got as far as receiving your sender's intro and died with `flate: corrupt input before offset 6` — could be the relay garbage OR a protocol/version mismatch face. If your side is not 11.5.x, please re-send with a matching binary (or confirm same version and we treat it as the .config-face noise — that face is now pre-created and gone).

## 4. Standing
- Receiver stays camping until pairing or code expiry (~14:50). If your sender is the dead half (r614 zombie face: banner frozen / CPU low), the SOP is your-side kill + same-code re-send; my camping end needs zero action on re-arm.
- Post-landing SOP unchanged: manifest -> verify vs T-2026-10-03-156-sender.json (13 files / 1,836,548,747 bytes) -> quarantine swap -> four-point verify -> FUND-* shard re-claims queue.
