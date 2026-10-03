# r663 bm-a: ticket T-166 progress append (python json -- PS5.1 ConvertFrom-Json crashes on this file)
import json

fp = r'fleet\tasks\T-2026-10-04-166-P1.json'
with open(fp, 'r', encoding='utf-8') as f:
    t = json.load(f)

t['progress_r663_adopt'] = (
    "r663 adoption (bm-a, dead-session estate per r471/r656): prior r663 session died 07:1x-07:2x "
    "post-launch pre-commit (process gone, state/round-report untouched, products verified). "
    "Adoption leg THIS round: (1) collector live-crash root-caused -- backfill died at "
    "cashflow:20080630 'ValueError: NaTType does not support strftime' (pd.NaT is a datetime "
    "subclass -> strftime branch; 7 face-periods 2005Q1..2007Q3 landed pre-crash, checkpoint intact); "
    "(2) fix landed in scripts/update_fund_statements.py norm_avail_date (try/except ValueError -> "
    "None, absent-avail honesty) + selftest F5 regression leg (pd.NaT -> None) -- selftest ALL-PASS "
    "rc0 + py_compile ok; (3) relaunch via gate deferred to throttle expiry 07:44:11 (30min spawn "
    "throttle; gate self-heal path), checkpoint resume from cashflow:20080630."
)
t['status'] = 'claimed'  # stays claimed: backfill in flight, finalize on completion

with open(fp, 'w', encoding='utf-8') as f:
    json.dump(t, f, ensure_ascii=False, indent=1)
with open(fp, 'r', encoding='utf-8') as f:
    json.load(f)  # reparse self-proof
print('ticket updated + reparsed OK')
