# -*- coding: utf-8 -*-
# r839 bm-c S4: append one pit law row to CODELY.md tail (bare-LF tail convention)
b = open('CODELY.md', 'rb').read()
pre = len(b)
assert b.endswith(b'\n') and not b.endswith(b'\r\n'), 'tail must be bare LF'
row = ('- [2026-10-10 21:2x r839 bm-c] Python 字节手术 text-mode 换行翻译坑（r838 EOL 律机械腿）：'
       'open() 默认 newline=None=通用换行翻译把 CRLF 读成 LF——split("\\r\\n") 恒空集=探针零命中假象'
       '（r839 pit-protocol 手术首探实录·rb 直读同件 31 条全见）；'
       '正法=手术链读写一律字节面（rb / newline=\'\'），selftest 必带「CRLF 件 \\r\\n 切分行数>1」断言。')
nb = b + row.encode('utf-8') + b'\n'
open('CODELY.md', 'wb').write(nb)
post = len(nb)
print('CODELY.md', pre, '->', post, '| le_cap:', post <= 30720)
