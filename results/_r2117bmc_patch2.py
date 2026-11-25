import io

p = 'scripts/minute_feed_first_reader.py'
s = io.open(p, encoding='utf-8').read()

# ---- 1. build(): keep per-session ladders and add a session-level (honest n) table ----
old = '''        lad = ladder(rows)
        symbols.append({
            "symbol": name[:-4],
            "audit": audit(rows),
            "ladder": ladder_stats(lad),
            "reversal": reversal(rows),
        })

    usable = [s for s in symbols if s.get("audit", {}).get("full_sessions", 0) > 0]
    cutoff = max((s["audit"]["last_session"] for s in usable), default=None)
'''
new = '''        lad = ladder(rows)
        sym = name[:-4]
        per_symbol_ladder[sym] = lad
        symbols.append({
            "symbol": sym,
            "audit": audit(rows),
            "ladder": ladder_stats(lad),
            "reversal": reversal(rows),
        })

    usable = [s for s in symbols if s.get("audit", {}).get("full_sessions", 0) > 0]
    cutoff = max((s["audit"]["last_session"] for s in usable), default=None)

    # Honest n: five broad ETFs share one session, so pooling their rows would multiply the
    # observation count by five while the noise is the same five times. The deep symbols are
    # averaged within each session first; n is then the number of sessions, not of rows.
    deep = [s["symbol"] for s in symbols
            if s.get("audit", {}).get("full_sessions", 0) >= 40]
    per_session = {}
    for sym in deep:
        for rec in per_symbol_ladder.get(sym, []):
            per_session.setdefault(rec["session"], {}).setdefault(sym, rec)
    ladder_sessions = []
    for sess in sorted(per_session):
        rec = {"session": sess}
        for t in LADDER:
            vals = [v[t] for v in per_session[sess].values() if t in v]
            if vals:
                rec[t] = statistics.fmean(vals)
        ladder_sessions.append(rec)
'''
assert old in s, 'build anchor A missing'
s = s.replace(old, new)

old = '''def build(feed_dir=FEED_DIR):
    symbols = []
'''
new = '''def build(feed_dir=FEED_DIR):
    symbols = []
    per_symbol_ladder = {}
'''
assert old in s, 'build anchor B missing'
s = s.replace(old, new)

old = '''        "symbols": symbols,
        "symbols_with_full_sessions": [s["symbol"] for s in usable],
'''
new = '''        "symbols": symbols,
        "ladder_deep_symbols": deep,
        "ladder_session_stats": ladder_stats(ladder_sessions),
        "ladder_session_n": len(ladder_sessions),
        "symbols_with_full_sessions": [s["symbol"] for s in usable],
'''
assert old in s, 'build anchor C missing'
s = s.replace(old, new)

old = '''        "notes": [
            "the 09:30 bar is the book's fill assumption; sessions without it are counted, "
            "not silently dropped",
            "ladder bp is measured against each session's own first open, so a roll in price "
            "level between session and session cancels out",
            "the reversal block is a census with n, slope and the sessions still missing -- "
            "it is not a verdict and must not be quoted as one",
        ],'''
new = '''        "notes": [
            "the feed carries no 09:30 (auction) print in any session, so the ladder's baseline "
            "is each session's first continuous print -- the book's real fill is the auction "
            "print this panel cannot see",
            "ladder bp is measured against each session's own first print, so a roll in price "
            "level between session and session cancels out",
            "the session-level table averages the deep symbols within one session before "
            "averaging sessions; the per-symbol rows in this JSON share that session noise",
            "the reversal block is a census with n, slope and the sessions still missing -- "
            "it is not a verdict and must not be quoted as one",
            "five reversal slopes are tested at once; |t| has to clear the per-test line that "
            "controls for that, and 44 sessions of one regime is not a robustness check",
        ],'''
assert old in s, 'build anchor D missing'
s = s.replace(old, new)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched build: session-level ladder + notes')
