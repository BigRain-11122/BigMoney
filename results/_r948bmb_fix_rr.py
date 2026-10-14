import subprocess, sys
bm = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
p = bm + r'\logs\iteration-loop\round_reports.md'
b = open(p, 'rb').read()
print('first4', b[:4].hex(), 'len', len(b))
orig = subprocess.run(['git','-C',bm,'cat-file','blob','HEAD:logs/iteration-loop/round_reports.md'],capture_output=True).stdout
print('orig_len', len(orig), 'prefix_match', b[:len(orig)] == orig)
if b[:len(orig)] != orig:
    print('ABORT prefix mismatch'); sys.exit(1)
tail = b[len(orig):]
print('tail_len', len(tail), 'tail_head', tail[:16].hex())
line = ("\r\n2026-10-14 20:41 | r948 | \u707e\u5907\u7eed\u884c\uff1a\u5b64\u513f git \u771f\u4f53 9236\uff08\u6309\u51fa\u751f\u65f6\u95f4+cmdline \u9a8c\u660e=\u9501\u4e3b\uff0cr947 worker \u53ea\u6740\u4e86 cmd-shim 7320 \u6f0f\u771f\u4f53\uff09\u51fb\u6740+\u53cc\u9648\u9501(index.lock/tmp-index-r947.lock)\u663e\u5f0f\u6e05\u9664+3 \u6839 face(.gitignore/CODELY.md/HQ-FEEDBACK.md) 0.1s \u590d\u6d3b+\u88ab\u6740\u8f6e\u5168\u90e8 25 \u6761\u5b9e\u5f39\u547d\u4ee4\u5ba1\u8ba1+sli-reconcile \u4e24\u811a\u672c\u5ba1\u8ba1=\u53cc\u6e05\u767d(results/_r948bmb_forensics_addendum.md)+MSG-20261014-2015/\u53d6\u8bc1/state \u5b9a\u5411\u63d0\u4ea4\u63a8\u9001(Bundle \u540e\u624b\u4ee4\u5bf9\u7aef\u53ef\u89c1)+restore worker \u8865\u4e01(\u6811\u6740+\u8bda\u5b9e\u9501)\u5206\u79bb\u7eed\u8dd1 fleet/docs/engine/firm/knowledge/legacy/live | \u8bc1\u636e\uff1aworker log 20:27 \u5168 face rc128=\u9501\u6b8b\u5b9e\u9524+cat-file blob 0.1s=promisor \u590d\u6d3b+push \u56de\u6267 | \u65b0\u53d1\u73b0\uff1aDATA \u9762\u5b9e\u9645\u88ab\u6bc1(daily/eligibility/zt_pool \u5168\u5931\u4ec51\u5b50\u76ee\u5f55\uff0cr947\u300c\u5e78\u5b58\u300d=\u9876\u5c42\u5b58\u5728\u6027\u8bef\u5224)\u2014\u2014S6 \u94fe\u91cd\u62c9+\u524d\u5411\u72ec\u5360\u9762(zt_pool/minute_feed)\u53f2\u6599\u4e0d\u53ef\u9006 | \u8bda\u5b9e\u8df3\u8fc7\uff1asmoke/S6/orders\u5168ack/heartbeat\uff08faces \u672a\u5b8c\u5907\uff0cr949 \u8bbe\u8ba1\u6027\u540e\u5ef6\uff09 | \u4e0b\u8f6e r949\uff1afaces \u5b8c\u6574\u9a8c\u8bc1\u2192heartbeat+smoke49/49+claws x2+orders \u5168 ack \u5dee\u96c6(\u542b b202b9510+SLI \u56de\u6267 bm-a)+S6 \u94fe(\u542b data \u91cd\u62c9)+unshallow+USN 19:36-19:55 \u7a97+\u4ed6 lane transcript \u626b\r\n")
if b[:2] == b'\xff\xfe':
    enc = 'utf-16-le'
    newtail = line.encode(enc)
else:
    enc = 'utf-8'
    newtail = line.encode(enc)
out = b[:len(orig)] + newtail
open(p, 'wb').write(out)
print('fixed_enc', enc, 'new_len', len(out))
