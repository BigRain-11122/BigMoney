import io

p = 'scripts/minute_feed_first_reader.py'
s = io.open(p, encoding='utf-8').read()

start = s.index('    lines.append("## What buying later than the open costs")')
end = s.index('    lines.append("## The question the board still calls data-blocked")')
new_block = '''    lines.append("## What the feed cannot price at all")
    lines.append("")
    missing = {}
    for sym in payload["symbols"]:
        a = sym.get("audit") or {}
        for h in a.get("holes", []):
            missing.setdefault(h["minute"], []).append(sym["symbol"])
    zero_auction = [sym["symbol"] for sym in payload["symbols"]
                    if sym.get("audit", {}).get("sessions_missing_0930_share") == 1.0]
    lines.append("- no **09:30** print in any session of %s — the auction print the book actually "
                 "fills against is not in this panel, so every ladder number below is measured "
                 "from the first *continuous* print instead" % (", ".join(zero_auction) or "no symbol"))
    for minute, syms in sorted(missing.items(), key=lambda kv: -len(kv[1]))[:4]:
        lines.append("- %s missing in %d symbol(s)" % (minute, len(syms)))
    lines.append("")
    lines.append("## What buying later than the open costs")
    lines.append("")
    lines.append("Measured against each session's first continuous print, in bp. Positive = you "
                 "paid more by waiting; negative = waiting was cheaper. The %d deep symbols (%s) "
                 "are averaged inside each session first, so `n` is sessions, not rows."
                 % (len(payload["ladder_deep_symbols"]), ", ".join(payload["ladder_deep_symbols"])))
    lines.append("")
    lines.append("| minute | n | mean bp | median bp | sd bp | t | share above zero |")
    lines.append("|---|---|---|---|---|---|---|")
    for t in payload["ladder_minutes"]:
        a = payload["ladder_session_stats"].get(t) or {}
        if "mean_bp" not in a:
            lines.append("| %s | %d | — | — | — | — | — |" % (t, a.get("n", 0)))
            continue
        lines.append("| %s | %d | %+.2f | %+.2f | %.2f | %s | %.0f%% |" % (
            t, a["n"], a["mean_bp"], a["median_bp"], a["sd_bp"],
            ("%+.2f" % a["t"]) if a.get("t") is not None else "—", a["share_above"] * 100))
    lines.append("")
    lines.append("Read it as a dispersion problem, not a forecast: the mean is the size of the "
                 "toll and the sd is why a person cannot pick the good minute in advance. A t "
                 "under 2 on %d sessions says the average toll is not distinguishable from zero, "
                 "not that waiting is free." % payload["ladder_session_n"])
    lines.append("")
'''
s = s[:start] + new_block + s[end:]

# the reversal table: add the multiple-testing line after it
old = '''    lines.append("`MDE mean bp` is the smallest rest-of-day move a %g bp/session claim could '''
new = '''    lines.append("")
    lines.append("Five slopes are tested at once here. A single |t| near 2.5 among five tests sits "
                 "on the line a Bonferroni-style correction draws, and 44 sessions from one "
                 "autumn regime is not a robustness check -- quote the slope as a measurement "
                 "of this sample only.")
    lines.append("`MDE mean bp` is the smallest rest-of-day move a %g bp/session claim could '''
assert old in s, 'mde anchor missing'
s = s.replace(old, new, 1)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched render')
