# r591 addendum line append (bytes-safe, EOL preserved)
rb = open('logs/iteration-loop/round_reports.md', 'rb').read()
eol = b'\r\n' if b'\r\n' in rb[-200:] else b'\n'
line = ("2026-10-02T19:57+08:00 | r591 addendum | push window origin advanced x2 mid-round "
        "(bm-c r381 closeout reland#4 6253015d4 + W113 seat baa0c3888): first push intercepted by pre-push claw "
        "as r374 diverged-base deletion-set artifact (bm-c's 4 new _r381bmc_* tool files misjudged as my deletions) "
        "-> integrated per r589 reset-FF-reland loop (no rebase no force, zero content change), repush = only published face; "
        "W113 seat MSG-20261002-1949-bmc read+cross-verified (A 269_004..271_003 hops=0 CLEAN / B 62_001..62_200 "
        "jump-past SEED_REGISTRY cta_wave1=62_000 tail-endpoint per D-20261002-05 -- consistent with bm-a W112 seat tail "
        "projection consumed at r590 = double-window derive identity, not transcription); seat MSG stays in inbox for bm-c's "
        "freeze-window archiving (freezer consumes, bm-a W112 precedent); W114+ tail projection noted for MY next freeze "
        "(A 271_004..273_003 / B 62_201..62_400 both CLEAN per bm-c disclosure) -- self-probe mandatory per r587 seat law, "
        "transcription forbidden; bm-c's parallel W112-seat inbox deletion = same archive-move completion I had staged "
        "(their blob-identity proof r586 law), duplicate deletions converge at FF zero conflict "
        "| verification: ff-only to baa0c3888 clean, deletion-set empty at repush "
        "| next: r591 main line + W113 freeze watch (bm-c active, seat hard-landed) [via bm-b r591]")
open('logs/iteration-loop/round_reports.md', 'ab').write(line.encode('utf-8').replace(b'\n', eol) + eol)
print('addendum appended')
