import io

p = 'Tools/s6_chain_bmc.py'
s = io.open(p, encoding='utf-8').read()

anchor = '    ("minute_feed", ["python", "scripts/update_minute_feed.py"]),\n'
assert anchor in s, 'minute_feed leg anchor missing'
add = anchor + (
    '    # r2117: the minute panel had a writer here and no reader anywhere -- product on disk\n'
    '    # that nothing consumed (r1108 family). This leg is that reader: it audits what the\n'
    '    # collector delivered, prices the 10:00-vs-open fill and sizes the intraday-reversal\n'
    '    # question the block board still files as data-blocked. check() asks the CSVs, so a\n'
    '    # panel that advances past the face says STALE and the refresh below is paid.\n'
    '    ("minute_feed_first_reader",\n'
    '     ["python", "scripts/minute_feed_first_reader.py", "--check"],\n'
    '     ["python", "scripts/minute_feed_first_reader.py", "run"]),\n'
)
s = s.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('chain leg added')
