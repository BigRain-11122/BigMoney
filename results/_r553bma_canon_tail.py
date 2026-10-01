import io
c = io.open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
i = c.rfind('- N1 \u6ce243')
seg = c[i:]
# find the end of the W43 bullet line (next blank line)
j = seg.find('\n\n')
out = io.open('results/_r553bma_canon_w43row.txt', 'w', encoding='utf-8')
out.write('W43ROW_LAST_300>>>\n')
out.write(seg[max(0, j-300):j])
out.write('\n<<<END\nAFTER_120>>>\n')
out.write(seg[j:j+120])
out.write('\n<<<END')
out.close()
print('written; row len:', j)
