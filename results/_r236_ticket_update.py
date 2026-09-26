# R236 bm-a: T-72 ticket closure text surgery (r230 law: text-level insert,
# byte-precise, indent=2/CRLF preserved -- no json rewrite, minimal diff).
import sys

P = "fleet/tasks/T-2026-09-26-72-P1.json"
b = open(P, "rb").read()
t = b.decode("utf-8")
orig = t

# 1. status flip claimed -> done
a = '  "status": "claimed",'
assert t.count(a) == 1, f"status anchor {t.count(a)}"
t = t.replace(a, '  "status": "done",')

# 2. result_ref fill
a = '  "result_ref": "",'
assert t.count(a) == 1, f"result_ref anchor {t.count(a)}"
t = t.replace(a, '  "result_ref": "results/sina_mf_accept.json (s2 five-line '
                 'PASS verdict) + scripts/update_sina_mf.py (s1 collector + R236 '
                 'amendment) + Tools/iteration_prompt.txt update_sina_mf leg (s3 '
                 'wiring); see progress_r236",')

# 3. progress_r236 insert after progress_r235 line (file tail:
#    ...re-derive."\r\n})
tail_a = 'pending post_review re-derive."\r\n}'
assert t.count(tail_a) == 1, f"tail anchor {t.count(tail_a)}"
row = ('pending post_review re-derive.",\r\n'
       ' "progress_r236": "R236 09:1x (dept:\u6570\u636e) s3 COMPLETE = ticket '
       'done: (1) R236 amendment landed in collector (_is_repull + _todo_for '
       'done-reset re-pull semantics for the refresh-repull subcommand; '
       '_terminal_cutoff/_panel_cutoff_from_bytes terminal cutoff derived from '
       'panel bytes; selftest S11 fixtures mirror production shapes incl. '
       'dead-code todo face + malformed/header-only/schema-foreign neighbors, '
       'all green; gate live probe no-op zero-network, mirror healthy '
       'cutoff=2026-09-24/5228/5228) -- closes BOTH R235-disclosed latent '
       'defects (empty-todo None-clobber churn + re-pull dead code) ahead of '
       'the ~2026-10-27 first re-pull window; prereg sec-5 R236 amendment '
       'note landed; (2) s3 S6-chain wiring: update_sina_mf gate leg inserted '
       'into Tools/iteration_prompt.txt after update_moneyflow (byte-precise '
       'single-line insert, no BOM, CRLF preserved); (3) post_review registry '
       'row encoded from spec-frozen verification lines only (accept '
       'verdict=PASS, fresh_covered>=5000, collector script, prompt leg, '
       'amendment helper), re-derive run this round. Three-state: '
       '\u7acb\u6cd5=git verifiable this commit, \u751f\u6548=selftest+gate '
       'probe green, \u9a8c\u6536=post_review verdict."\r\n}')
t = t.replace(tail_a, row)

assert t != orig and t.count('"progress_r236"') == 1
open(P, "wb").write(t.encode("utf-8"))
import json
d = json.load(open(P, encoding="utf-8-sig"))
print("status:", d["status"], "| result_ref head:", d["result_ref"][:60])
print("progress_r236 head:", d["progress_r236"][:80])
print("parse OK, minimal diff lines:",
      (orig.count("\r\n") , t.count("\r\n")))
