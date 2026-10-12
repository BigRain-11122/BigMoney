# PART 3 of derive: protected-region restoration + postchecks + write. Concatenate after p2.

# ---- restore protected regions with programmatic transforms ----
seg = PROTECT["KEPTLIST"]
last = seg[seg.rfind("assert n1_t4.count('    # --- W219 materializer face')"):]
w220line = last.replace("W219", "W220").replace("r920 window", "r923 window")
out = out.replace("@@KEPTLIST@@", seg + "\n" + w220line)

seg = PROTECT["LIVENESS"]
assert '"w219_block_kept": 1}' in seg
out = out.replace("@@LIVENESS@@", seg.replace('"w219_block_kept": 1}', '"w219_block_kept": 1, "w220_block_kept": 1}'))

seg = PROTECT["TRANSITIVE"]
lines = [l for l in seg.split("\n") if '"w215_transitive"' not in l]
w218line = [l for l in lines if '"w218_transitive"' in l][0]
w219line = w218line.replace("w218_transitive", "w219_transitive").replace("n1_w218_results.json", "n1_w219_results.json").replace("903,389 / K=477,520", "905,589 / K=479,720")
idx = lines.index(w218line)
lines.insert(idx, w219line)
new_tr = "\n".join(lines)
if new_tr.endswith(","):
    new_tr = new_tr[:-1]  # the file kept the block's trailing comma after the placeholder
out = out.replace("@@TRANSITIVE@@", new_tr)

seg = PROTECT["PREREGNOTE"]
new_note = ('"note": "prereg derived+committed in the r925 dead window (2e251d084, five-level lineage replay '
            '+ editor_gen fix replay, preflight 46/46; anchor-verification scratch from the r926 zero-commit '
            'dead window absorbed); splice editor derived from the committed W220 editor template by '
            'count-asserted ordered transform (protect-restore regions, fail-closed pair law) in this r927 '
            'absorb window; upstream W220 already landed (clean-precondition tenth consecutive window); '
            'zero transcription"')
out = out.replace("@@PREREGNOTE@@", new_note)

seg = PROTECT["PARITYNOTE"]
out = out.replace("@@PARITYNOTE@@", seg.replace(
    "+ W215 + W216 + W217 legs -> W220 block = 78 rows ending at W219",
    "+ W215 + W216 + W217 + W218 legs -> W221 block = 79 rows ending at W220"))

out = out.replace("@@STRUCTROWS@@",
    "(79 rows: estate 69 + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg + W220 leg).")

out = out.replace("@@PARFULL@@",
    'assert par_full.count("assert pf.N1_BANDS[") == 78, \\\n'
    "    f\"full parity span {par_full.count('assert pf.N1_BANDS[')} != 78 (69 estate + W211 leg + W212 leg + W213 leg + W214 leg + W215 leg + W216 leg + W217 leg + W218 leg + W219 leg)\"")

out = out.replace("@@OWNLEGS@@",
    "+ own W211 leg + own W212 leg + own W213 leg + own W214 leg + own W215 leg + own W216 leg + own W217 leg + own W218 leg + own W219 leg)")

out = out.replace("@@PARSEC@@",
    'assert par_sec.count("assert pf.N1_BANDS[") == 77 \\\n'
    "    and [int(w) for w in _estate_ws[:69]] == list(range(138, 207)) \\\n"
    "    and [int(_estate_ws[69]), int(_estate_ws[70]), int(_estate_ws[71]), int(_estate_ws[72]), int(_estate_ws[73]), int(_estate_ws[74]), int(_estate_ws[75]), int(_estate_ws[76])] == [211, 212, 213, 214, 215, 216, 217, 218], \\\n"
    "    f\"estate segment not W138..W206 full-span 69 rows + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218 legs: n={par_sec.count('assert pf.N1_BANDS[')} range={(_estate_ws[:2], _estate_ws[-8:])}\"")

out = out.replace("@@CUT76@@",
    "Extraction self-asserts the 77-row cut (69 estate + W211 + W212 + W213 + W214 + W215 + W216 + W217 + W218)")

# ---- postchecks ----
def want(tag, s, n):
    c = out.count(s)
    ok = (c == n) if isinstance(n, int) else (n[0] <= c <= n[1])
    print(("POST-OK " if ok else "POST-FAIL ") + "[%s] %r count=%d want=%s" % (tag, s[:50], c, n))
    if not ok:
        fails.append("post:" + tag)

want("no-placeholder", "@@", 0)
want("no-EIGHTIETH", "EIGHTIETH", 0)
want("no-w220-probe-residue", "_w220bmc_20261012", 0)
want("EIGHTY-FIRST", "EIGHTY-FIRST", (5, 9))
want("EIGHTY-SECOND", "EIGHTY-SECOND instance anticipated", 2)
want("no-905_589", "905_589", 0)
want("no-479_720", "479_720", 0)
want("907_789", "907_789", 1)
want("481_920", "481_920", 1)
want("907,789", "907,789", 2)
want("receipt-w219-ledger", "905,589 / K=479,720", 1)
want("no-r922", "r922", 0)
want("r920-only-keptlist", "r920", 1)
want("no-w218_leg", "w218_leg", 0)
want("no-w215_transitive", "w215_transitive", 0)
want("w220_leg", "w220_leg", (1, 6))
want("no-W221p", "W221p_", 0)
want("w220-seat-msg-refs", "MSG-20261012-1025", 2)
want("no-fiftieth", "fiftieth", 0)
want("no-TWENTIETH-bare", "TWENTIETH ", 0)
want("221-receipt", "_w221bmc_20261012_probe_receipt.json", 9)
want("221-freeze-receipt", "_w221bmc_freeze_receipt.json", 1)
want("221-prereg", "PERPETUAL_N1_W221_PREREG.md", 5)
want("220-prereg-upstream", "PERPETUAL_N1_W220_PREREG.md", 3)
want("batch221", '"batch": "PERPETUAL-N1-W221"', 4)
want("n1w221", "n1_w221", (4, 6))
want("no-n1_w220", "n1_w220\"", 0)
want("kept220", "'    # --- W220 materializer face') == 1  # prior block kept (W220 splice landed r923 window)", 1)
want("liveness220", '"w220_block_kept": 1', 1)

if fails:
    print("DERIVE FAILED:", fails)
    sys.exit(1)

open(r"results\_w221bmc_freeze_edits.py", "w", encoding="utf-8", newline="").write(out)
import py_compile
py_compile.compile(r"results\_w221bmc_freeze_edits.py", doraise=True)
print("DERIVE OK -- wrote results/_w221bmc_freeze_edits.py (%d bytes, py_compile green)" % len(out))
