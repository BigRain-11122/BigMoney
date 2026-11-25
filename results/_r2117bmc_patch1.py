import io

p = 'scripts/minute_feed_first_reader.py'
s = io.open(p, encoding='utf-8').read()

old = '''    full = [s for s in sessions if s["full"]]
    return {
        "sessions": len(sessions),
        "full_sessions": len(full),
        "fragment_sessions": len(sessions) - len(full),
        "median_bars_full": int(statistics.median([s["bars"] for s in full])) if full else 0,
        "sessions_missing_0930": sum(1 for s in full if not s["has_0930"]),
        "duplicate_minutes": dup_total,
'''
new = '''    full = [s for s in sessions if s["full"]]
    # the grid a complete session should occupy, and what is missing from it
    hole_counts = {}
    for s in full:
        got = set(b[0] for b in by_session[s["session"]])
        for m in SESSION_GRID:
            if m not in got:
                hole_counts[m] = hole_counts.get(m, 0) + 1
    holes = sorted(hole_counts.items(), key=lambda kv: -kv[1])
    return {
        "sessions": len(sessions),
        "full_sessions": len(full),
        "fragment_sessions": len(sessions) - len(full),
        "median_bars_full": int(statistics.median([s["bars"] for s in full])) if full else 0,
        "sessions_missing_0930": sum(1 for s in full if not s["has_0930"]),
        "sessions_missing_0930_share": (round(sum(1 for s in full if not s["has_0930"]) / len(full), 3)
                                       if full else None),
        "grid_minutes_expected": len(SESSION_GRID),
        "holes": [{"minute": m, "sessions": n} for m, n in holes[:8]],
        "duplicate_minutes": dup_total,
'''
assert old in s, 'audit anchor missing'
s = s.replace(old, new)

old2 = 'FULL_SESSION_BARS = 200      # below this the session is a window fragment, not a session'
new2 = '''FULL_SESSION_BARS = 200      # below this the session is a window fragment, not a session
# what a complete session should occupy once the collector's rolling window is full
SESSION_GRID = (["%02d:%02d" % divmod(m, 60) for m in range(9 * 60 + 30, 11 * 60 + 31)]
                + ["%02d:%02d" % divmod(m, 60) for m in range(13 * 60 + 1, 15 * 60 + 1)])'''
assert old2 in s, 'grid anchor missing'
s = s.replace(old2, new2)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched audit+grid')
